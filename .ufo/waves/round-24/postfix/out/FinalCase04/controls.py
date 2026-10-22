#!/usr/bin/env python3
"""Reviewer-constructed falsification controls for PG04 (round-24 postfix).

Every control is a perturbation of the PINNED PG04 fixture built by the
pinned grid builder code (tests/report-audit/promisor-grid.py, sha256
30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270) and is
run against the PINNED auditor (tools/report-landing-audit.py, sha256
b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f).

These are NOT manifest grid cells: no grid cell other than PG04/PG08 is
executed.  They exist to show whether PG04's clean verdict is earned by a
real per-store resolution or is vacuous.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase04/clone")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24"
           "/postfix/out/FinalCase04")
ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase04/controls-root")
AUDIT = CLONE / "tools/report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"
FAKE = "0123456789abcdef0123456789abcdef01234567"

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "promisor_grid", CLONE / "tests/report-audit/promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

assert hashlib.sha256(Path(G.__file__).read_bytes()).hexdigest() == \
    "30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270"


def git(repo, *args, stdin=None, check=True, **extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    p = subprocess.run(["git", "-C", str(repo), *args], input=stdin,
                       capture_output=True, env=e)
    if check and p.returncode:
        raise SystemExit(f"git {args} failed: {p.stderr.decode()}")
    return p.stdout.decode(errors="surrogateescape")


def amend_report(fleet, extra_shas):
    """Add citations to the fleet report, keeping the cutoff date."""
    text = (Path(fleet) / REL).read_text()
    lines = text.rstrip("\n").split("\n")
    out = []
    for line in lines:
        out.append(line)
        if line.strip() == "## Landed changes":
            pass
    # insert the extra citations right after the existing "- <sha>" entry
    idx = max(i for i, l in enumerate(out) if l.startswith("- "))
    for sha in extra_shas:
        out.insert(idx + 1, f"- {sha}")
    Path(fleet, REL).write_text("\n".join(out) + "\n")
    git(fleet, "add", "--", REL)
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: report", GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
        GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")


def inventory(repo):
    return git(repo, "cat-file", "--batch-all-objects", "--batch-check").split()


def run_auditor(lane, fleet, cwd):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=env, cwd=str(cwd),
                       timeout=60)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace"), argv


def build_case(name, mutate=None):
    base = ROOT / name
    shutil.rmtree(base, ignore_errors=True)
    tmp = base / "case"
    tmp.mkdir(parents=True)
    built = G.BUILDERS["c_complete_fleet_marker"](base, tmp)
    if mutate:
        mutate(built)
    before = {"lane": set(inventory(built["lane"])),
              "fleet": set(inventory(built["fleet"]))}
    code, out, err, argv = run_auditor(built["lane"], built["fleet"], tmp)
    after = {"lane": set(inventory(built["lane"])),
             "fleet": set(inventory(built["fleet"]))}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    defects = []
    if doc:
        for res in doc.get("results", []):
            for d in res.get("defects", []):
                defects.append({"kind": d.get("kind"), "token": d.get("token"),
                                "corrected_by": d.get("corrected_by")})
    norm = None
    if doc:
        t = json.dumps(doc, sort_keys=True)
        t = t.replace(str(built["fleet"]), "<fleet>")
        t = t.replace(str(built["lane"]), "<lane>")
        norm = hashlib.sha256(t.encode()).hexdigest()
    return {"control": name, "exit": code, "argv": argv, "stderr": err,
            "stdout_bytes": len(out), "document_sha256": norm,
            "summary": (doc or {}).get("summary"),
            "results": (doc or {}).get("results"),
            "defects": defects, "objects_acquired": acquired,
            "premise": built["premise"], "shas": built["shas"]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ROOT.mkdir(parents=True, exist_ok=True)
    controls = []

    # C0: the untouched PG04 fixture (control for the control set).
    controls.append(build_case("C0-pg04-asis"))

    # C1: the fabricated token, absent from BOTH stores, added to the
    # marked fleet's report.  A proved absence must stay exit 1 (not a
    # refusal): the per-store merge must not turn "nobody has it" into
    # "unreadable".
    def add_fake(built):
        amend_report(built["fleet"], [FAKE])
    controls.append(build_case("C1-fabricated-token-absent-everywhere",
                               add_fake))

    # C2: a citation that exists ONLY in the second store (the marked
    # fleet).  The first store (lane) lacks it: the merge must find it in
    # the second store and keep the verdict clean.
    def add_fleet_only(built):
        f0 = built["shas"]["fleet_commit"]
        amend_report(built["fleet"], [f0])
    controls.append(build_case("C2-citation-only-in-second-marked-store",
                               add_fleet_only))

    # C3: the same object present in BOTH stores (canonical merge): the
    # lane commit is copied into the marked fleet store.  The verdict must
    # stay clean and the document must equal the PG04 document.
    def copy_object_to_fleet(built):
        lane = built["lane"]
        fleet = built["fleet"]
        sha = built["shas"]["lane_commit"]
        for oid in git(lane, "cat-file", "--batch-all-objects",
                       "--batch-check").split():
            o = oid.split()[0]
        # copy every object the lane has into the fleet store
        for sub in (Path(lane, ".git/objects").iterdir(),):
            for d in sub:
                if d.is_dir() and len(d.name) == 2:
                    for f in d.iterdir():
                        tgt = Path(fleet, ".git/objects", d.name, f.name)
                        tgt.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, tgt)
    controls.append(build_case("C3-same-object-in-both-stores",
                               copy_object_to_fleet))

    path = OUT / "controls.json"
    path.write_text(json.dumps(controls, indent=1, sort_keys=True) + "\n")
    for c in controls:
        print(c["control"], "exit=", c["exit"],
              "defects=", [(d["kind"], d["token"]) for d in c["defects"]],
              "acquired=", c["objects_acquired"],
              "doc=", c["document_sha256"],
              "stderr=", c["stderr"][:160].replace("\n", " | "))
    print("wrote", path)


if __name__ == "__main__":
    main()
