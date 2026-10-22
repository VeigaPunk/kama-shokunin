#!/usr/bin/env python3
"""Independent bounded check of the UnrelatedFakeLanded family.

Rebuilds PG22 and PG37 with the PINNED grid builders (imported from the
pinned clone, read-only), then verifies the premises and the observations
directly, without trusting the grid runner's own grading:

  * which objects are actually missing / present in each store
  * that the fabricated token is absent and is NOT in the missing set
  * that the missing object is a blob (not an opaque tree/commit hole)
  * the exact finding/token pairs of the auditor's verdict document
  * that no object was acquired by the audit
  * every git command the auditor actually executed (git shim), so a
    lazy fetch / transport invocation would be visible
  * that the PG22 and PG37 verdict documents are equal

Offline only: local fixtures, no network, no repository program.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeLanded/clone")
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeLanded/verify")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
FAKE = "0123456789abcdef0123456789abcdef01234567"

spec = importlib.util.spec_from_file_location("pgrid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

REAL_GIT = shutil.which("git")


def shim_dir():
    d = ROOT / "shim"
    d.mkdir(parents=True, exist_ok=True)
    log = ROOT / "git-calls.log"
    shim = d / "git"
    shim.write_text(
        "#!/bin/sh\n"
        f'printf "%s\\n" "$*" >> "${{KAMA_GIT_LOG:-{log}}}"\n'
        f'exec {REAL_GIT} "$@"\n', encoding="utf-8")
    shim.chmod(0o755)
    return d, log


def build_one(builder, name):
    tmp = ROOT / name
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    built = grid.BUILDERS[builder](ROOT, tmp)
    return built, tmp


def inventory(repo):
    out = grid.git_nofetch(repo, "cat-file", "--batch-all-objects",
                           "--batch-check=%(objectname)")
    return set(out.split())


def walks(repo):
    """(unfiltered missing, blob:none-filtered missing) exactly as the
    auditor's missing_reachable computes them."""
    roots = grid.git(repo, "cat-file", "--batch-all-objects",
                     "--batch-check=%(objectname) %(objecttype)")
    names = [l.split()[0] for l in roots.split("\n")
             if l.split() and l.split()[1] in ("commit", "tree", "tag")]
    stdin = "".join(f"{n}\n" for n in names)

    def walk(extra):
        out = grid.git(repo, "-c", "core.commitGraph=false", "rev-list",
                       "--objects", "--missing=print", "--no-object-names",
                       *extra, "--stdin", data=stdin.encode())
        return sorted(l[1:] for l in out.split("\n") if l.startswith("?"))
    return walk(()), walk(("--filter=blob:none",))


def run_auditor(lane, fleet, tmp, log):
    log = Path(log)
    log.write_text("", encoding="utf-8")
    env = grid.env(PATH=f"{ROOT / 'shim'}:{os.environ['PATH']}",
                   KAMA_GIT_LOG=str(log))
    p = subprocess.run([sys.executable, str(AUDIT), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1", "--json",
                        "--no-errata"],
                       capture_output=True, env=env, cwd=str(tmp), timeout=60)
    calls = [l for l in log.read_text(encoding="utf-8").split("\n") if l]
    return p.returncode, p.stdout.decode(), p.stderr.decode(), calls


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    shim_dir()
    results = {}
    for name, builder in (("PG22", "c_unknown_citation_incomplete"),
                          ("PG37", "c_unused_missing_blob_fabricated_plain")):
        built, tmp = build_one(builder, name)
        lane, fleet = built["lane"], built["fleet"]
        shas = built["shas"]
        prem = built["premise"]
        missing, opaque = walks(lane)
        fmissing, fopaque = walks(fleet)
        before = {"lane": inventory(lane), "fleet": inventory(fleet)}
        code, out, err, calls = run_auditor(lane, fleet, tmp,
                                            ROOT / f"git-calls-{name}.log")
        after = {"lane": inventory(lane), "fleet": inventory(fleet)}
        acquired = {k: sorted(after[k] - before[k]) for k in after}
        doc = json.loads(out) if out.strip() else None
        defects = []
        if doc:
            for res in doc.get("results", []):
                for d in res.get("defects", []):
                    defects.append((d.get("kind"), d.get("token")))
        results[name] = {
            "builder": builder,
            "lane_promisor": prem["lane_promisor"],
            "fleet_promisor": prem["fleet_promisor"],
            "premise_lane_missing": prem["lane_missing"],
            "premise_fleet_missing": prem["fleet_missing"],
            "premise_fake_present": prem["fake_present"],
            "independent_lane_missing": missing,
            "independent_lane_opaque": opaque,
            "independent_fleet_missing": fmissing,
            "independent_fleet_opaque": fopaque,
            "dropped_unused_blob": shas.get("unused_blob"),
            "lane_tip_tree": shas.get("tip_tree"),
            "lane_commit": shas.get("lane_commit"),
            "sources_blob": shas.get("sources_blob"),
            "fleet_report_blob": shas.get("report_blob"),
            "fake_token": FAKE,
            "present": {
                "lane_commit_in_lane": shas.get("lane_commit") in before["lane"],
                "tip_tree_in_lane": shas.get("tip_tree") in before["lane"],
                "sources_blob_in_lane": shas.get("sources_blob") in before["lane"],
                "unused_blob_in_lane": shas.get("unused_blob") in before["lane"],
                "fake_in_lane": FAKE in before["lane"],
                "fake_in_fleet": FAKE in before["fleet"],
                "fleet_report_blob_in_fleet": shas.get("report_blob") in before["fleet"],
            },
            "exit": code,
            "stderr": err.strip(),
            "stdout_forbidden_metadata_strings": [
                w for w in ("partial clone (", "promisor pack")
                if w in out],
            "stderr_could_not_evaluate": "could-not-evaluate" in err,
            "defects": sorted(defects),
            "status": doc["summary"]["status"] if doc else None,
            "objects_acquired": acquired,
            "git_call_count": len(calls),
            "git_calls_without_no_lazy_fetch": [c for c in calls
                                                if "--no-lazy-fetch" not in c],
            "git_calls_transport": [c for c in calls
                                    if any(w in c.replace("--no-lazy-fetch", " ")
                                           for w in
                                           ("fetch", "ls-remote", "upload-pack",
                                            "clone", "remote ", "push"))],
            "document": doc,
        }
    a, b = results["PG22"], results["PG37"]
    verdict = {
        "PG22_fake_in_missing_set": FAKE in a["independent_lane_missing"],
        "PG37_fake_in_missing_set": FAKE in b["independent_lane_missing"],
        "PG22_fake_present_anywhere": FAKE in (a["independent_lane_missing"] or []),
        "PG22_missing_is_blob_not_opaque":
            bool(a["independent_lane_missing"])
            and not a["independent_lane_opaque"],
        "PG22_missing_oid_is_the_dropped_unused_blob":
            a["independent_lane_missing"] == [a["dropped_unused_blob"]],
        "PG22_present_objects": a["present"],
        "PG37_present_objects": b["present"],
        "PG22_exit": a["exit"],
        "PG37_exit": b["exit"],
        "PG22_defects": a["defects"],
        "PG37_defects": b["defects"],
        "documents_equal_raw": a["document"] == b["document"],
        "documents_equal_normalised":
            grid.normalise_document(json.dumps(a["document"]), {"lane": str(ROOT / "PG22" / "lane"), "fleet": str(ROOT / "PG22" / "fleet")})
            == grid.normalise_document(json.dumps(b["document"]), {"lane": str(ROOT / "PG37" / "lane"), "fleet": str(ROOT / "PG37" / "fleet")}),
        "PG22_no_acquisition": not any(a["objects_acquired"].values()),
        "PG37_no_acquisition": not any(b["objects_acquired"].values()),
        "PG22_no_transport": not a["git_calls_transport"],
        "PG37_no_transport": not b["git_calls_transport"],
        "PG22_all_git_calls_isolated": not a["git_calls_without_no_lazy_fetch"],
        "PG37_all_git_calls_isolated": not b["git_calls_without_no_lazy_fetch"],
    }
    out = {"results": results, "verdict": verdict}
    (ROOT / "verify.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                                      encoding="utf-8")
    print(json.dumps(verdict, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
