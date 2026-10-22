#!/usr/bin/env python3
"""FinalCase12 direct probe: PG12-omission-marker-lane and its PG10 twin.

Builds the two fixtures with the PINNED grid builders (imported from the
pinned clone), runs the PINNED tools/report-landing-audit.py directly with a
logging `git` shim on PATH (argv + rc only, transparent forwarding), and
records premise facts, exit, verdict document, acquisition and twin
equality.  Nothing outside the seat's own scratch is written.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase12/clone")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase12")
OUT = SCRATCH / "out"
MYTMP = SCRATCH / "tmp"

spec = importlib.util.spec_from_file_location(
    "pg", CLONE / "tests/report-audit/promisor-grid.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

AUDIT = CLONE / "tools/report-landing-audit.py"
REAL_GIT = shutil.which("git")


def shim_dir(root, log):
    d = root / "shim"
    d.mkdir(parents=True, exist_ok=True)
    sh = d / "git"
    sh.write_text(
        "#!/bin/sh\n"
        f'printf "%s\\n" "$*" >> "{log}"\n'
        f'exec "{REAL_GIT}" "$@"\n', encoding="utf-8")
    sh.chmod(0o755)
    return d


def build(root, builder, name):
    tmp = root / name
    tmp.mkdir(parents=True, exist_ok=True)
    return pg.BUILDERS[builder](root, tmp)


def inventory(repo):
    out = pg.git_nofetch(repo, "cat-file", "--batch-all-objects",
                         "--batch-check=%(objectname)")
    return set(out.split())


def run_auditor(auditor, lane, fleet, cwd, log):
    shim = shim_dir(cwd, log)
    env = pg.env()
    env["PATH"] = f"{shim}:{env['PATH']}"
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=env, cwd=str(cwd),
                       timeout=120)
    return {"argv": argv, "exit": p.returncode,
            "stdout": p.stdout.decode(errors="replace"),
            "stderr": p.stderr.decode(errors="replace")}


def norm(out, built):
    try:
        doc = json.loads(out)
    except ValueError:
        return None
    text = json.dumps(doc, sort_keys=True)
    text = text.replace(str(built["fleet"]), "<fleet>")
    text = text.replace(str(built["lane"]), "<lane>")
    return json.loads(text)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(pg.tempfile.mkdtemp(prefix="fc12-", dir=str(MYTMP)))
    report = {"clone_head": subprocess.run(
        ["git", "-C", str(CLONE), "rev-parse", "HEAD"], capture_output=True,
        text=True).stdout.strip(),
        "auditor_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
        "grid_sha256": hashlib.sha256(
            (CLONE / "tests/report-audit/promisor-grid.py").read_bytes()
        ).hexdigest(),
        "root": str(root), "cases": {}}

    specs = [("PG12-omission-marker-lane", "c_omission_marker_lane"),
             ("PG10-omission-lane-plain", "c_omission_lane_plain")]
    for case, builder in specs:
        tmp = root / case
        built = build(root, builder, case)
        lane, fleet = built["lane"], built["fleet"]
        shas = built["shas"]
        before = {"lane": inventory(lane), "fleet": inventory(fleet)}
        log = root / f"{case}-git-calls.log"
        log.write_text("", encoding="utf-8")
        res = run_auditor(AUDIT, lane, fleet, tmp, log)
        after = {"lane": inventory(lane), "fleet": inventory(fleet)}
        acquired = {k: sorted(after[k] - before[k]) for k in after}
        doc = norm(res["stdout"], built)
        # premise facts
        lane_facts = pg.promisor_facts(lane)
        fleet_facts = pg.promisor_facts(fleet)
        lane_missing = pg.missing_objects(lane, "refs/heads/master")
        fleet_missing = pg.missing_objects(fleet, "HEAD")
        # store membership of every cited / relevant token
        tokens = {k: v for k, v in shas.items() if isinstance(v, str)
                  and len(v) == 40}
        membership = {}
        for name, sha in sorted(tokens.items()):
            membership[name] = {
                "sha": sha,
                "lane": bool(pg.object_exists(lane, sha)),
                "fleet": bool(pg.object_exists(fleet, sha)),
            }
        calls = [l for l in log.read_text(encoding="utf-8").splitlines()]
        batch = [c for c in calls if "cat-file --batch-check" in c]
        report["cases"][case] = {
            "builder": builder,
            "exit": res["exit"],
            "argv": res["argv"],
            "stderr": res["stderr"],
            "stdout_bytes": len(res["stdout"]),
            "document": doc,
            "defects": sorted(
                (d.get("kind"), d.get("token"))
                for r in (doc or {}).get("results", [])
                for d in r.get("defects", [])),
            "summary": (doc or {}).get("summary"),
            "objects_acquired": acquired,
            "premise": {
                "lane_promisor_facts": lane_facts,
                "fleet_promisor_facts": fleet_facts,
                "lane_missing": lane_missing,
                "fleet_missing": fleet_missing,
                "grid_premise": built["premise"],
            },
            "token_membership": membership,
            "git_calls_total": len(calls),
            "batch_check_calls": batch,
            "fleet_report": pg.git(fleet, "show", "HEAD:.ufo/reports/round-1/"
                                   "kama.md"),
            "lane_log": pg.git(lane, "log", "--format=%H %at %s",
                               "refs/heads/master"),
        }
    d12 = report["cases"]["PG12-omission-marker-lane"]["document"]
    d10 = report["cases"]["PG10-omission-lane-plain"]["document"]
    report["twin_equal"] = (d12 is not None and d10 is not None
                            and d12 == d10)
    report["twin_documents_present"] = (d12 is not None, d10 is not None)
    # diff of the two documents, field by field
    if d12 is not None and d10 is not None:
        diffs = {}
        def walk(a, b, path):
            if type(a) is not type(b):
                diffs[path] = [a, b]
                return
            if isinstance(a, dict):
                for k in sorted(set(a) | set(b)):
                    walk(a.get(k), b.get(k), f"{path}.{k}")
            elif isinstance(a, list):
                if a != b:
                    diffs[path] = [a, b]
            elif a != b:
                diffs[path] = [a, b]
        walk(d12, d10, "")
        report["twin_document_diffs"] = diffs
    (OUT / "direct-probe.json").write_text(
        json.dumps(report, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "cases"}, indent=1))
    for case, r in report["cases"].items():
        print("==", case, "exit", r["exit"], "defects", r["defects"],
              "acquired", r["objects_acquired"])
        print("   premise lane_missing", r["premise"]["lane_missing"],
              "fleet_missing", r["premise"]["fleet_missing"],
              "lane_markers", r["premise"]["lane_promisor_facts"]["markers"])
        print("   membership", json.dumps(r["token_membership"]))
        print("   git_calls", r["git_calls_total"])
    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
