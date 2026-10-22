#!/usr/bin/env python3
"""Observer-granularity probes on the replay-v3 strict_match + git-floor checks.

1. Does strict_match compare every DECLARED field? (exit, kinds, errata_invalid)
2. Ceiling: strict_match is kind-SET level, not token level. Show that a
   synthetic observation naming the WRONG token with the right kind still
   matches -> the token identity of the unresolved citation is NOT covered
   by the driver's declared expectation.
3. Git floor: the after source must not raise the documented git floor.
"""
import re
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer03")
DRIVER = S / "clone/.ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py"
AFTER = S / "clone/tools/report-landing-audit.py"
sys.path.insert(0, str(DRIVER.parent))
import importlib.util

spec = importlib.util.spec_from_file_location("replay3", DRIVER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

EXP = m.EXPECTED["fleet-only-tag"]
CTL = m.CONTROL["fleet-only-tag"]
print("EXPECTED['fleet-only-tag'] =", EXP)
print("CONTROL['fleet-only-tag']  =", CTL)
print("with-ledger expectation == no-ledger control expectation:",
      EXP == CTL)

# 1. field coverage: perturb each declared field one at a time
base = {"exit": EXP["exit"], "kinds": sorted(EXP["kinds"]),
        "errata_invalid": EXP["errata_invalid"]}
print("\n[1] declared-field coverage of strict_match")
for field, bad in (("exit", 0), ("kinds", ["landed-omitted"]),
                   ("errata_invalid", 1)):
    obs = dict(base)
    obs[field] = bad
    print(f"  perturb {field:15s} -> matches_expectation = "
          f"{m.strict_match(obs, EXP)}")
print("  baseline               -> matches_expectation =",
      m.strict_match(base, EXP))

# 2. ceiling: right kind, wrong token
print("\n[2] ceiling: kind-set granularity (token identity not declared)")
obs_wrong_token = {"exit": 1, "kinds": ["landed-unresolved"],
                   "errata_invalid": 0}
print("  synthetic observation, right kind, arbitrary token -> match =",
      m.strict_match(obs_wrong_token, EXP))
print("  NOTE: the driver's EXPECTED declares kinds only; the token is")
print("        not part of the declared expectation.")

# 3. git floor
print("\n[3] git-floor check on the after source")
src = AFTER.read_text(encoding="utf-8", errors="replace")
for pat in (r"--missing=print-info", r"--missing-only", r"--filter=blob:none"):
    print(f"  {pat:26s} present = {bool(re.search(pat, src))}")
ver = subprocess.run(["git", "--version"], capture_output=True).stdout.decode().strip()
print("  installed git:", ver)
mv = re.search(r"git >= ([\d.]+) is required", src)
print("  documented floor in source:", mv.group(1) if mv else "not found")
