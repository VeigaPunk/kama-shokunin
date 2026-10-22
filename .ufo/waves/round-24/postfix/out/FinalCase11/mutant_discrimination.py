#!/usr/bin/env python3
"""FinalCase11: does PG11/PG10 discriminate the change under review?

The pinned candidate changed tools/report-landing-audit.py lookup() in two
places (commit 92063cf):

  M1  the bare-name presence became PER-STORE (bare_objects): a store's own
      answer, never the merge of every store.
  M2  a canonical-object reconciliation block was added: a store that
      PROVES a non-commit mismatch wins over another store's inability to
      serve the same object.

Two local mutants of the pinned auditor revert those two decisions (one at a
time).  Both mutants are run on the SAME two fixtures the grid used
(PG11-omission-fleet-promisor and its twin PG10-omission-lane-plain), with
the pinned builder and the pinned argv.  A mutant that changes the verdict
proves the cell discriminates that decision; an unchanged verdict is a
coverage observation, not a mutant kill.

Nothing here is a grid cell run and nothing is a producer: the auditor copies
live only under this seat's own scratch.
"""
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r24/postfix/FinalCase11/out")
import importlib.util  # noqa: E402

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase11/clone")
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase11/out")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase11/tmp/mut")
PINNED = CLONE / "tools" / "report-landing-audit.py"

_spec = importlib.util.spec_from_file_location(
    "promisor_grid", CLONE / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

# ---- M1: restore the merged bare-name answer ---------------------------
M1_OLD = """    # token -> {canonical object id: {what the stores proved about it}}
    proved = {}
    for store in stores:"""
M1_NEW = """    # token -> {canonical object id: {what the stores proved about it}}
    proved = {}
    merged_bare = lookup(stores, tokens) if peel else None
    for store in stores:"""
M1_COND_OLD = """                if (here is not None and here[token][0] == "found"
                        and status[token] != "found"):"""
M1_COND_NEW = """                if (merged_bare is not None
                        and merged_bare[token] == "found"
                        and status[token] == "absent"):"""

# ---- M2: drop the canonical-object reconciliation -----------------------
M2_OLD = """    for token, per_object in proved.items():
        conclusive = False
        unsure = False
        for states in per_object.values():
            if "wrongtype" in states:
                conclusive = True
            else:
                unsure = True
        if conclusive and not unsure:
            offer(token, "wrongtype")
        elif unsure:
            offer(token, "unknown")
    return status"""
M2_NEW = """    for token, per_object in proved.items():
        for states in per_object.values():
            if "wrongtype" in states:
                offer(token, "wrongtype")
            else:
                offer(token, "unknown")
    return status"""


def make_mutant(name, edits):
    src = PINNED.read_text(encoding="utf-8")
    for old, new in edits:
        if src.count(old) != 1:
            raise SystemExit(f"{name}: anchor count {src.count(old)} != 1")
        src = src.replace(old, new)
    path = SCRATCH / name
    path.write_text(src, encoding="utf-8")
    return path


def run(auditor, lane, fleet, tmp):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    before = {"lane": G.object_inventory(lane),
              "fleet": G.object_inventory(fleet)}
    proc = subprocess.run(argv, capture_output=True, env=G.env(), cwd=str(tmp))
    after = {"lane": G.object_inventory(lane),
             "fleet": G.object_inventory(fleet)}
    doc = None
    try:
        doc = json.loads(proc.stdout)
    except ValueError:
        pass
    return {
        "argv": argv,
        "exit": proc.returncode,
        "stderr": proc.stderr.decode(errors="replace")[-400:],
        "defects": [[d.get("kind"), d.get("token")]
                    for r in (doc or {}).get("results", [])
                    for d in r.get("defects", [])],
        "status": ((doc or {}).get("summary") or {}).get("status"),
        "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
    }


def main():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)

    m1 = make_mutant("m1-merged-bare-audit.py",
                     [(M1_OLD, M1_NEW), (M1_COND_OLD, M1_COND_NEW)])
    m2 = make_mutant("m2-no-canonical-merge-audit.py", [(M2_OLD, M2_NEW)])

    diffs = {}
    for label, path in (("M1-merged-bare", m1),
                        ("M2-no-canonical-merge", m2)):
        diffs[label] = "".join(difflib.unified_diff(
            PINNED.read_text(encoding="utf-8").splitlines(True),
            path.read_text(encoding="utf-8").splitlines(True),
            fromfile="pinned/tools/report-landing-audit.py",
            tofile=f"scratch/{label}"))

    results = {}
    cases = {
        "PG11-omission-fleet-promisor":
            ("c_omission_fleet_promisor", "pg11"),
        "PG10-omission-lane-plain":
            ("c_omission_lane_plain", "pg10"),
    }
    for case, (builder, tag) in cases.items():
        root = SCRATCH / tag
        tmp = root / "current" / "000"
        tmp.mkdir(parents=True, exist_ok=True)
        built = G.BUILDERS[builder](root, tmp)
        lane, fleet = built["lane"], built["fleet"]
        results[case] = {
            "premise": built["premise"],
            "pinned": run(PINNED, lane, fleet, tmp),
            "M1-merged-bare": run(m1, lane, fleet, tmp),
            "M2-no-canonical-merge": run(m2, lane, fleet, tmp),
        }

    doc = {
        "pinned_auditor_sha256": hashlib.sha256(PINNED.read_bytes()).hexdigest(),
        "mutant_sha256": {k: hashlib.sha256(v.read_bytes()).hexdigest()
                          for k, v in (("M1-merged-bare", m1),
                                       ("M2-no-canonical-merge", m2))},
        "grid_sha256": hashlib.sha256(
            (CLONE / "tests/report-audit/promisor-grid.py").read_bytes()
        ).hexdigest(),
        "results": results,
        "mutant_diffs": diffs,
    }
    (OUT / "mutant_discrimination.json").write_text(
        json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for label, path in (("M1-merged-bare", m1),
                        ("M2-no-canonical-merge", m2)):
        (OUT / f"{label}.diff").write_text(diffs[label], encoding="utf-8")
    summary = {}
    for case, rows in results.items():
        base = rows["pinned"]
        summary[case] = {
            label: {"exit": r["exit"], "defects": r["defects"],
                    "status": r["status"],
                    "differs_from_pinned": (r["exit"] != base["exit"]
                                            or r["defects"] != base["defects"])}
            for label, r in rows.items() if label != "premise"
        }
    print(json.dumps(summary, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
