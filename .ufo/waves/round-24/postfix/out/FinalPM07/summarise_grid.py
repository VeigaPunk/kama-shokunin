#!/usr/bin/env python3
"""Summarise the two bounded grid runs (pristine vs canonical PM07 mutant)
for the exact case ids that were run."""
import json
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM07")

def load(name):
    return json.loads((S / "out" / name).read_text())

def rows(doc):
    out = {}
    for arm, adoc in (doc.get("arms") or {}).items():
        for r in adoc.get("rows") or []:
            out[(arm, r["case"])] = r
    return out

pristine = load("grid-pristine-PG31-PG32.json")
mutant = load("grid-mutant-PM07-PG31-PG32.json")
pp, mm = rows(pristine), rows(mutant)

print("pristine: grid_sha256=%s expectations_sha256=%s population_sha256=%s population_size=%s"
      % (pristine["grid_sha256"][:16], pristine["expectations_sha256"][:16],
         pristine["population_sha256"][:16], pristine["population_size"]))
print("mutant  : grid_sha256=%s expectations_sha256=%s population_sha256=%s population_size=%s"
      % (mutant["grid_sha256"][:16], mutant["expectations_sha256"][:16],
         mutant["population_sha256"][:16], mutant["population_size"]))
print("auditor_sha256 pristine:", pristine.get("auditor_sha256"))
print("auditor_sha256 mutant  :", mutant.get("auditor_sha256"))
for arm, res in (pristine.get("arms") or {}).items():
    print("pristine arm %s: graded=%s violations=%s tracebacks=%s timeouts=%s leaks=%s"
          % (arm, res.get("graded"), res.get("violations"), res.get("tracebacks"),
             res.get("timeouts"), res.get("harness_leaks")))
for arm, res in (mutant.get("arms") or {}).items():
    print("mutant   arm %s: graded=%s violations=%s tracebacks=%s timeouts=%s leaks=%s"
          % (arm, res.get("graded"), res.get("violations"), res.get("tracebacks"),
             res.get("timeouts"), res.get("harness_leaks")))

keys = sorted(set(pp) | set(mm))
print()
for key in keys:
    p, m = pp.get(key), mm.get(key)
    print("=" * 72)
    print("case:", key)
    for label, r in (("pristine", p), ("mutant  ", m)):
        if r is None:
            print(f"  {label}: ABSENT")
            continue
        print(f"  {label}: exit={r['exit']} expected_exit={r.get('expected_exit')} "
              f"met={r.get('met')} met_amended={r.get('met_amended')} "
              f"twin_equal={r.get('twin_equal')} twins={r.get('twins')}")
        print(f"           kinds={r.get('kinds')} defects={r.get('defects')} "
              f"raw_defects={r.get('raw_defects')}")
        print(f"           problems(graded view)={r.get('problems')}")
        print(f"           amended_problems={r.get('amended_problems')}")
        print(f"           original_problems={r.get('original_problems')}")
        print(f"           traceback={r.get('traceback')} internal_error={r.get('internal_error')} "
              f"timed_out={r.get('timed_out')} leaked={r.get('leaked')} "
              f"objects_acquired={r.get('objects_acquired')}")
        print(f"           stderr_tail={r.get('stderr_tail')!r}")
    if p and m:
        print("  document identical:", p.get("document") == m.get("document"))
        print("  exit pristine->mutant:", p.get("exit"), "->", m.get("exit"))
