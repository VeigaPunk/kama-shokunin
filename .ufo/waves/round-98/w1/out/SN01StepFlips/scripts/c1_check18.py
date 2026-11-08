#!/usr/bin/env python3
"""SN01StepFlips - does C1 check 18's charge-site set equality actually reject the mutants?

Check 18 of tools/round98-self-assessment-audit.py claims (docstring):
  "The probe's tensor loop charges exactly the four declared call sites (name, nd, dims, type
   + offset) and its preamble exactly three reads (magic, version, n_tensors/n_kv); a flat-6,
   6+nd or +1/header parser fails the set equality."

This harness reproduces check 18's own expression verbatim and runs it against the probe bytes
after each of the FIVE frozen MUTANTS patches (applied by the counter's own apply_mutant),
to see which mutants the source-shape check actually rejects.
"""
import importlib.util
import re
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
spec = importlib.util.spec_from_file_location(
    "r98budget", LANE / "tools/round98-router-budget.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BASE_PROBE = (LANE / "tools/round98-router-budget.py").read_bytes()  # unused, kept for clarity


def check18(probe_text: str):
    """Verbatim reproduction of tools/round98-self-assessment-audit.py check 18."""
    lines = probe_text.splitlines()
    loop = []
    li = next((i for i, l in enumerate(lines)
               if l.startswith("            for _ in range(n_tensors):")), None)
    if li is not None:
        for l in lines[li + 1:]:
            if l.strip().startswith("infos.append"):
                break
            loop.append(l.strip())

    def charge_line(l: str) -> str:
        l = l.split("#")[0].strip()
        return l if any(t in l for t in ("need(", "rd(", "u64()", "u32()", "skip(")) else ""

    charged = [charge_line(l) for l in loop]
    charged = [c for c in charged if c]
    want_charged = ["skip(u64())", "nd = u32()", "ne = [u64() for _ in range(nd)] or [1]",
                    "tt, off = u32(), u64()"]
    pre = probe_text.split("def gguf_parse", 1)[-1].split("for _ in range(n_kv):", 1)[0]
    pre_ok = ('rd(4) != b"GGUF"' in pre and "ver = u32()" in pre
              and "n_tensors, n_kv = u64(), u64()" in pre)
    return charged, want_charged, pre_ok, charged == want_charged and pre_ok


# the probe bytes at the freeze commit
import subprocess
probe_bytes = subprocess.run(
    ["git", "-C", str(LANE), "show", "HEAD:tools/kama-probe.sh"],
    capture_output=True).stdout

print(f"{'mutant':<14} {'check18_ok':<11} {'mismatches_c1_18':<17} charged")
print("-" * 100)
results = {}
for name in ("none", "flat6", "undercharge", "maxmeta", "nopreamble", "overcharge"):
    mbytes = mod.apply_mutant(probe_bytes, name)
    charged, want, pre_ok, ok = check18(mbytes.decode())
    results[name] = ok
    shown = " | ".join(c[:34] for c in charged)
    print(f"{name:<14} {str(ok):<11} {str(not ok):<17} {shown}")

print()
print("check 18 REJECTS (mismatches):", sorted(k for k, v in results.items() if not v and k != "none"))
print("check 18 ACCEPTS (green):     ", sorted(k for k, v in results.items() if v and k != "none"))
print()
print("counter's own docstring claim (check 18):")
doc = mod.__doc__
print("  'a flat-6, 6+nd or +1/header parser fails the set equality'")
over = results.get("overcharge")
print(f"  the +1/header (overcharge) mutant is rejected by check 18: {not over}")
print("  -> the docstring claim about +1/header is", "TRUE" if not over else "FALSE")
