#!/usr/bin/env python3
"""Causal check: the tip M17 anchor applied to the ed1cc3a auditor.

Run from the scratch clone checked out at ed1cc3a (clone-r23). The tip
registry's M17 anchor and replacement are read from the pinned tip registry
copy; the ed1cc3a auditor is read from the clone's working tree (a throwaway
checkout in scratch, never the lane). The mutated auditor is written to the
scratch tmp directory and fed to the registered grid's current arm, exactly as
tests/report-audit/isolation-mutants.py does. Exit code: 0 when the grid ran
and the mutant was evaluated; 2 when the anchor did not match exactly once.
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

SCRATCH = pathlib.Path("/fast/scratch/hyaku/kama-r25a2/RevengerM17Sites")
CLONE = SCRATCH / "clone-r23"
TIP_REG = SCRATCH / "tip-mutants.py"
TMP = SCRATCH / "tmp2"
TMP.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("tipmut", TIP_REG)
tipmut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tipmut)
name, old, new = next(m for m in tipmut.MUTANTS if m[0].startswith("M17"))

src = (CLONE / "tools/report-landing-audit.py").read_text(encoding="utf-8")
count = src.count(old)
print(f"anchor {name} occurrences in ed1cc3a auditor: {count}")
if count != 1:
    sys.exit(2)

mutated = TMP / "ed1cc3a-with-tip-M17.py"
mutated.write_text(src.replace(old, new), encoding="utf-8")
env = dict(os.environ, TMPDIR=str(TMP))
p = subprocess.run([sys.executable, "tests/report-audit/repo-state-grid.py", "--arm", "current",
                    "--current", str(mutated), "--json"],
                   cwd=CLONE, capture_output=True, env=env)
print(f"grid exit={p.returncode} stderr={p.stderr.decode(errors='replace').strip()[-200:]!r}")
if p.returncode == 2:
    sys.exit(2)
doc = json.loads(p.stdout)
arm = doc["arms"]["current"]
failed = [r["case"] for r in arm["rows"] if r["kind"] in ("fault", "contract", "control") and not r["met"]]
print(f"failed rows: {failed}")
print(f"killed: {p.returncode == 1}")
out = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/RevengerM17Sites/ed1cc3a-tipM17-causal.json")
out.write_text(json.dumps({"grid_exit": p.returncode, "failed_rows": failed,
                           "anchor": name, "auditor": "ed1cc3a"}, indent=1, sort_keys=True) + "\n",
               encoding="utf-8")
sys.exit(0)
