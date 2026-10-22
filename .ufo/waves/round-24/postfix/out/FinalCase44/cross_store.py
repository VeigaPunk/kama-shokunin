#!/usr/bin/env python3
"""FinalCase44: cross-store probe (does an unrelated store's hole gate the
other store's unresolved citation?) + determinism repeat.

X-1  lane has the PG45 unused-tree hole; the FLEET report carries the
     fabricated token.  Does the lane's hole refuse the fleet's citation?
X-2  the same fixture WITHOUT the lane hole (the control).
X-3  PG45 fixture rebuilt and re-audited three times -> the verdict and the
     object inventory are stable (no order/state dependence).
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pgrid", GRID)
pg = importlib.util.module_from_spec(spec)
sys.modules["pgrid"] = pg
spec.loader.exec_module(pg)

aspec = importlib.util.spec_from_file_location("audit", AUDIT)
aud = importlib.util.module_from_spec(aspec)
sys.modules["audit"] = aud
aspec.loader.exec_module(aud)

root = Path(pg.make_root())
print("control_root:", root)


def run_audit(lane, fleet, tmp):
    before = {k: pg.object_inventory(v) for k, v in (("lane", lane),
                                                    ("fleet", fleet))}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, cwd=str(tmp),
                          env=pg.env(), timeout=60)
    after = {k: pg.object_inventory(v) for k, v in (("lane", lane),
                                                   ("fleet", fleet))}
    acq = {k: sorted(after[k] - before[k]) for k in after}
    doc = None
    try:
        doc = json.loads(proc.stdout.decode())
    except ValueError:
        pass
    defects = [d for r in (doc or {}).get("results", [])
               for d in r.get("defects", [])]
    return {"exit": proc.returncode,
            "stderr": proc.stderr.decode().strip()[:300],
            "document": doc is not None, "defects": defects,
            "acquired": acq, "argv": argv,
            "summary_status": (doc or {}).get("summary", {}).get("status")}


res = []
for label, opt, note in (
    ("X-1-lane-hole-plus-fleet-fabricated-token",
     {"unused_tree": True, "fake_landed": True,
      "drop": ("unused_tree",)},
     "lane hole, fabricated token in the FLEET report"),
    ("X-2-no-lane-hole-plus-fleet-fabricated-token",
     {"fake_landed": True},
     "control: same fabricated token, no lane hole"),
):
    tmp = root / label
    built = pg.build(root, tmp, **opt)
    lane, fleet = built["lane"], built["fleet"]
    tip = subprocess.run(["git", "-C", str(lane), "rev-parse",
                           "refs/heads/master"],
                          capture_output=True).stdout.decode().strip()
    missing, opaque = aud.missing_reachable(lane, tip)
    r = run_audit(lane, fleet, tmp)
    print(f"== {label} ({note})")
    print("   lane missing:", sorted(missing), "opaque:", sorted(opaque))
    print("   EXIT:", r["exit"], "STDERR:", r["stderr"] or "(empty)")
    print("   document_present:", r["document"], "defects:",
          json.dumps(r["defects"]), "status:", r["summary_status"])
    print("   objects_acquired:", json.dumps(r["acquired"]))
    r.update({"label": label, "missing": sorted(missing),
              "opaque": sorted(opaque)})
    res.append(r)

# X-3: determinism of the PG45 cell
docs = []
for i in range(3):
    tmp = root / f"X-3-pg45-{i}"
    built = pg.build(root, tmp, unused_tree=True, drop=("unused_tree",))
    r = run_audit(built["lane"], built["fleet"], tmp)
    docs.append(r)
    print(f"== X-3-pg45 run{i}: EXIT", r["exit"], "status",
          r["summary_status"], "defects", json.dumps(r["defects"]),
          "acquired", json.dumps(r["acquired"]))
print("X-3 all exits equal:", len({d["exit"] for d in docs}) == 1,
      "| all acquired empty:",
      all(not d["acquired"]["lane"] and not d["acquired"]["fleet"]
          for d in docs),
      "| all defect lists equal:",
      len({json.dumps(d["defects"]) for d in docs}) == 1)
res.extend(docs)
Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/out/cross-store.json"
     ).write_text(json.dumps(res, indent=1), encoding="utf-8")
print("wrote cross-store.json")
