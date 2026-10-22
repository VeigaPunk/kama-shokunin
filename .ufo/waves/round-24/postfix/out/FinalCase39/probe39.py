#!/usr/bin/env python3
"""FinalCase39 bounded probe (scratch only, no production writes).

Hypothesis under falsification:
  H  the two-root missing-object diagnosis must not turn unrelated,
     unselected or unused holes into an audit-completeness precondition;
     a resolved or conclusively wrong-type/absent citation keeps the
     registered result.

The frozen47 cell PG39 (c_wrong_type_citation_promisor) has NO hole at all,
so it cannot by itself exercise the "hole present" half of H.  These probes
reuse the PINNED grid builders (imported, not modified) to add one hole at a
time to the PG39 fixture shape and run the PINNED auditor directly.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase39/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDITOR = CLONE / "tools/report-landing-audit.py"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
           "round-24/postfix/out/FinalCase39")
TMP = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase39/tmp1")

spec = importlib.util.spec_from_file_location("promisor_grid", GRID)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

MARK = dict(lane_mark="config", fleet_mark="config")

PROBES = [
    ("P1-baseline-wrong-type-promisor", dict(MARK, wrong_type=True)),
    ("P2-wrong-type+unused-missing-blob",
     dict(MARK, wrong_type=True, unused_file=True,
          drop=("unused_blob",))),
    ("P3-wrong-type+unused-missing-tree",
     dict(MARK, wrong_type=True, unused_tree=True,
          drop=("unused_tree",))),
    ("P4-wrong-type+opaque-missing-subtree",
     dict(MARK, wrong_type=True, opaque_tree=True,
          drop=("opaque_tree",))),
    ("P5-wrong-type+unselected-branch-hole",
     dict(MARK, wrong_type=True, unselected_hole=True,
          drop=("unselected_blob",))),
    ("P6-wrong-type+absent-fabricated+unrelated-blob-hole",
     dict(MARK, wrong_type=True, fake_landed=True, unused_file=True,
          drop=("unused_blob",))),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, opt in PROBES:
        root = TMP / ("probe-" + name)
        root.mkdir(parents=True, exist_ok=True)
        rec = {"probe": name, "options": {k: str(v) for k, v in opt.items()}}
        try:
            built = G.build(str(root), str(root / "case"), **opt)
        except Exception as exc:  # a premise failure is evidence, not a kill
            rec["premise_error"] = f"{type(exc).__name__}: {exc}"
            results.append(rec)
            continue
        lane, fleet = built["lane"], built["fleet"]
        shas = built["shas"]
        rec["premise"] = built["premise"]
        rec["blob_oid"] = shas.get("f_blob")
        rec["fake_oid"] = shas.get("fake")
        before = {"lane": G.object_inventory(lane),
                  "fleet": G.object_inventory(fleet)}
        argv = [sys.executable, str(AUDITOR), "--lane-repo", str(lane),
                "--fleet-repo", str(fleet), "--rounds", "1", "--json",
                "--no-errata"]
        rec["argv"] = argv
        proc = subprocess.run(argv, capture_output=True, timeout=120)
        after = {"lane": G.object_inventory(lane),
                 "fleet": G.object_inventory(fleet)}
        rec["exit"] = proc.returncode
        rec["stdout"] = proc.stdout.decode("utf-8", "replace")
        rec["stderr"] = proc.stderr.decode("utf-8", "replace")
        rec["objects_acquired"] = {k: sorted(after[k] - before[k])
                                    for k in after}
        try:
            doc = json.loads(rec["stdout"])
            rec["defects"] = [[d["kind"], d["token"]]
                              for d in doc["results"][0]["defects"]]
            rec["summary_status"] = doc["summary"]["status"]
            rec["by_kind"] = doc["summary"]["by_kind"]
        except ValueError:
            rec["defects"] = None
        (OUT / (name + ".json")).write_text(
            json.dumps(rec, indent=1, sort_keys=True) + "\n",
            encoding="utf-8")
        results.append(rec)
    (OUT / "probe-summary.json").write_text(
        json.dumps(results, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for rec in results:
        print(rec["probe"], "exit=", rec.get("exit"),
              "defects=", rec.get("defects"),
              "acquired=", rec.get("objects_acquired"),
              "stderr=", (rec.get("stderr") or "").strip()[:160])
    return 0


if __name__ == "__main__":
    sys.exit(main())
