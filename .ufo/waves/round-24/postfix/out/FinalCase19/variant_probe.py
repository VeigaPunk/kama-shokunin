#!/usr/bin/env python3
"""FinalCase19 fourth probe: the same PG19 (and PG20) fixture under the
auditor's other round selections, to test whether the NEW required-read
wrappers and the fatal-cause diagnostic keep the unavailable-object refusal
and its strong identity on every invocation path.

Variants (same fixture, same auditor, only --rounds differs):
  V1  --rounds 1        (what the graded cell uses)
  V2  --rounds 10-      (open range -> the fleet report listing read)
  V3  no --rounds       (the auditor's own argparse default)
Each variant is graded with the pinned grid's own check_exit2_form() and
REASON_CLASSES, so the verdict is the harness's, not mine.
"""
import importlib.util
import json
from pathlib import Path
import shutil

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
TMP = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/tmp")
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/out")

spec = importlib.util.spec_from_file_location("pgrid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

table, manifest_digest = grid.load_manifest()
by_case = {c["case"]: c for c in table["cases"]}
root = Path(grid.tempfile.mkdtemp(prefix="variants-", dir=str(TMP)))
result = {"root": str(root), "manifest_sha256": manifest_digest, "variants": {}}

VARIANTS = {
    "V1-rounds-1": ["--rounds", "1"],
    "V2-rounds-open-10-": ["--rounds", "10-"],
    "V3-no-rounds-arg": [],
}


def run_auditor_variant(auditor, lane, fleet, tmp, rounds_args):
    import subprocess
    argv = [grid.sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), *rounds_args, "--json", "--no-errata"]
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=grid.env(),
                            cwd=str(tmp), start_new_session=True)
    out, err = proc.communicate(timeout=grid.TIMEOUT)
    return argv, proc.returncode, out.decode(errors="replace"), \
        err.decode(errors="replace")


for index, case_id in enumerate(["PG19-missing-fleet-tree-promisor",
                                 "PG20-missing-fleet-tree-plain"]):
    case = by_case[case_id]
    tmp = root / case_id
    tmp.mkdir(parents=True, exist_ok=True)
    built = grid.BUILDERS[case["builder"]](root, tmp)
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    names = [grid.resolve_token(n, shas)
             for n in case.get("names_any_of", [])]
    forbidden = case.get("reason_forbidden", [])
    live = case.get("amended", case["original"])
    rows = {}
    for vname, rounds_args in VARIANTS.items():
        before = {"lane": grid.object_inventory(lane),
                  "fleet": grid.object_inventory(fleet)}
        argv, code, out, err = run_auditor_variant(AUDIT, lane, fleet, tmp,
                                                   rounds_args)
        after = {"lane": grid.object_inventory(lane),
                 "fleet": grid.object_inventory(fleet)}
        acquired = {k: sorted(after[k] - before[k]) for k in after}
        form = grid.check_exit2_form(err, out, names, forbidden)
        reasons = sorted({t for t in grid.REASON_CLASSES[live["reason_class"]]
                          if t in err.lower()})
        rows[vname] = {
            "argv": argv,
            "exit": code,
            "stderr": err.strip(),
            "stdout_len": len(out.strip()),
            "form_problems": form,
            "names_in_stderr": {n: (n in err) for n in names if n},
            "forbidden_in_stderr": {f: (f in err) for f in forbidden},
            "reason_class_terms_hit": reasons,
            "objects_acquired": acquired,
            "internal_error": "could-not-evaluate: internal:" in err,
            "traceback": "Traceback (most recent call last)" in err,
        }
    result["variants"][case_id] = rows

shutil.rmtree(root, ignore_errors=True)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "invocation-variants.json").write_text(
    json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
for case_id, rows in result["variants"].items():
    for vname, row in rows.items():
        print(case_id, vname, "exit", row["exit"],
              "form_problems", row["form_problems"],
              "names", row["names_in_stderr"],
              "forbidden", row["forbidden_in_stderr"],
              "acquired", row["objects_acquired"])
        print("   stderr:", row["stderr"][:260])
