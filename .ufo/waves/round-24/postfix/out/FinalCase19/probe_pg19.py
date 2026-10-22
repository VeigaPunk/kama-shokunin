#!/usr/bin/env python3
"""FinalCase19 bounded probe: PG19-missing-fleet-tree-promisor (+ graded twin
PG20-missing-fleet-tree-plain) against the pinned tools/report-landing-audit.py.

It reuses the pinned grid's own builder and audit invocation so the fixture
and the argv are byte-identical to the registered cell, and it additionally
records the full stderr/stdout, the premise facts (promisor mark, missing
fleet tip tree, cited lane commit) and the object inventory before/after.

Nothing here edits the pinned tree or the expectation manifest.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
TMP = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/tmp")

spec = importlib.util.spec_from_file_location("pgrid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

CASES = ["PG19-missing-fleet-tree-promisor", "PG20-missing-fleet-tree-plain"]
table, manifest_digest = grid.load_manifest()
by_case = {c["case"]: c for c in table["cases"]}

out_dir = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/out")
out_dir.mkdir(parents=True, exist_ok=True)
root = Path(grid.tempfile.mkdtemp(prefix="probe-", dir=str(TMP)))
report = {"root": str(root), "manifest_sha256": manifest_digest,
          "auditor_sha256": grid.hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
          "grid_sha256": grid.hashlib.sha256(GRID.read_bytes()).hexdigest(),
          "cases": {}}

for index, case_id in enumerate(CASES):
    case = by_case[case_id]
    tmp = root / "current" / f"{index:03d}"
    tmp.mkdir(parents=True, exist_ok=True)
    built = grid.BUILDERS[case["builder"]](root, tmp)
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]

    before = {"lane": grid.object_inventory(lane),
              "fleet": grid.object_inventory(fleet)}
    code, out, err, timed_out = grid.run_auditor(AUDIT, lane, fleet, tmp,
                                                 bool(built.get("errata")))
    after = {"lane": grid.object_inventory(lane),
             "fleet": grid.object_inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}

    # premise facts, read with --no-lazy-fetch so nothing can be fetched
    def gitq(repo, *args):
        p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                           capture_output=True, text=True,
                           env=grid.env())
        return {"rc": p.returncode, "out": p.stdout.strip(),
                "err": p.stderr.strip()}

    promisor_cfg = (Path(fleet, ".git/config").read_text()
                    if Path(fleet, ".git/config").exists() else "")
    tip_tree = shas.get("fleet_tip_tree")
    premise = {
        "builder": case["builder"],
        "fleet_mark_in_config": [ln.strip() for ln in promisor_cfg.splitlines()
                                 if "promisor" in ln or "partialclonefilter"
                                 in ln],
        "fleet_tip_tree_oid": tip_tree,
        "fleet_tip_tree_present": bool(gitq(fleet, "cat-file", "-e",
                                            f"{tip_tree}^{{tree}}")["rc"] == 0),
        "fleet_tip_tree_catfile": gitq(fleet, "cat-file", "-t", tip_tree),
        "fleet_head_commit": gitq(fleet, "rev-parse", "HEAD"),
        "lane_commit_cited": shas.get("lane_commit"),
        "fleet_head_tree_in_header": gitq(fleet, "log", "-1", "--format=%T",
                                          "HEAD"),
        "objects_before": {k: len(v) for k, v in before.items()},
    }
    names = [grid.resolve_token(n, shas)
             for n in case.get("names_any_of", [])]
    forbidden = case.get("reason_forbidden", [])
    live = case.get("amended", case["original"])
    obs = grid.run_case(AUDIT, built, case, tmp, "current", shas)
    obs["full_stderr"] = err
    obs["full_stdout"] = out
    obs["premise"] = premise
    obs["objects_acquired"] = acquired
    obs["names_resolved"] = names
    obs["stderr_starts_cne"] = err.startswith("could-not-evaluate:")
    obs["stderr_is_internal_error"] = "could-not-evaluate: internal:" in err
    obs["stdout_nonempty"] = bool(out.strip())
    obs["stdout_parses_as_json"] = None
    try:
        json.loads(out)
        obs["stdout_parses_as_json"] = True
    except ValueError:
        obs["stdout_parses_as_json"] = False
    obs["stderr_contains_names"] = {n: (n in err) for n in names if n}
    obs["stderr_contains_forbidden"] = {f: (f in err) for f in forbidden}
    obs["reason_class_terms_hit"] = sorted(
        {t for t in grid.REASON_CLASSES[live["reason_class"]]
         if t in err.lower()})
    obs["live_expectation"] = live
    obs["frozen_expectation"] = case["frozen"]
    obs["original_expectation"] = case["original"]
    report["cases"][case_id] = obs
    (out_dir / f"probe-{case_id}.json").write_text(
        json.dumps(obs, indent=1, sort_keys=True) + "\n", encoding="utf-8")

shutil.rmtree(root, ignore_errors=True)
(out_dir / "probe-report.json").write_text(
    json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({c: {k: v for k, v in o.items()
                      if k not in ("full_stderr", "full_stdout")}
                  for c, o in report["cases"].items()},
                 indent=1, sort_keys=True))
print("=== PG19 stderr ===")
print(report["cases"][CASES[0]]["full_stderr"])
print("=== PG19 stdout ===")
print(report["cases"][CASES[0]]["full_stdout"])
print("=== PG20 stderr ===")
print(report["cases"][CASES[1]]["full_stderr"])
print("=== PG20 stdout ===")
print(report["cases"][CASES[1]]["full_stdout"])
