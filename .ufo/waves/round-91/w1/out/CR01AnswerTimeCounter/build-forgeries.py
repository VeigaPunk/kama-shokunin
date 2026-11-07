#!/usr/bin/env python3
"""Build round-91 C1 forgery probes from the probe bytes at M (3decfa36)."""
import hashlib
import pathlib
import sys

SRC = pathlib.Path(sys.argv[1])          # probe-M.sh
OUT = pathlib.Path(sys.argv[2])          # output dir
src = SRC.read_text()


def sub(text, old, new, name):
    if text.count(old) != 1:
        raise SystemExit(f"{name}: anchor count {text.count(old)} for {old!r}")
    return text.replace(old, new)


MM = "  printf '%s\\n' \"$served\" | KAMA_EXP=$exp_n LC_ALL=C awk \"$AWK_NORM\"'"
RM = "router_match() {\n  KAMA_EXP=$1 LC_ALL=C awk -F '\\t' \"$AWK_NORM\"'"
GUT = "  RT_VERDICT='' RT_REASON=''\n"
SERVED = '    C_SERVED=$(printf \'%s\\n\' "$ids" | paste -sd, -)\n'

forgeries = {}

# g1: only the LAST served id is ever examined (O(1) matching; the rule is met on that one id)
t = sub(src, MM, "  printf '%s\\n' \"$served\" | tail -n 1 | KAMA_EXP=$exp_n LC_ALL=C awk \"$AWK_NORM\"'", "g1-mm")
t = sub(t, RM, "router_match() {\n  tail -n 1 | KAMA_EXP=$1 LC_ALL=C awk -F '\\t' \"$AWK_NORM\"'", "g1-rm")
forgeries["g1-last-only"] = t

# g2: count cap at 250 000 served ids (above every cell: max is 200 001)
t = sub(src, MM, "  printf '%s\\n' \"$served\" | head -n 250000 | KAMA_EXP=$exp_n LC_ALL=C awk \"$AWK_NORM\"'", "g2-mm")
t = sub(t, RM, "router_match() {\n  head -n 250000 | KAMA_EXP=$1 LC_ALL=C awk -F '\\t' \"$AWK_NORM\"'", "g2-rm")
forgeries["g2-cap250k"] = t

# g3: large lists skip the per-id rule entirely; a substring test on the raw id text decides
CHEAT = """  # FORGERY: big answers are decided by a substring test, not by the normalize rule
  if [ "${#served}" -gt 1000000 ]; then
    if printf '%s\\n' "$served" | LC_ALL=C grep -qF -- "$exp_n"; then return 0; else return 1; fi
  fi
  printf '%s\\n' "$served" | KAMA_EXP=$exp_n LC_ALL=C awk "$AWK_NORM"'"""
t = sub(src, MM, CHEAT, "g3-mm")
forgeries["g3-big-substring"] = t

# g4: O(n log n) instead of one linear pass (sort before the awk scan)
t = sub(src, MM, "  printf '%s\\n' \"$served\" | LC_ALL=C sort | KAMA_EXP=$exp_n LC_ALL=C awk \"$AWK_NORM\"'", "g4-mm")
forgeries["g4-sort-nlogn"] = t

# g5: router_refine gutted (never refines a MODEL_OK from router status) -- net no-op on these cells
t = sub(src, GUT, GUT + "  return 0  # FORGERY: router status refinement deleted\n", "g5-gut")
forgeries["g5-router-gutted"] = t

# g6: served_model truncated to 200 ids (observability broken, verdict/time unchanged)
t = sub(src, SERVED, "    C_SERVED=$(printf '%s\\n' \"$ids\" | head -n 200 | paste -sd, -)  # FORGERY: truncates\n", "g6-served")
forgeries["g6-served-truncated"] = t

# g7: correct rule, but 17 s of dead time on big answers (budget slack, ~9x the M max)
t = sub(src, MM, "  [ \"${#served}\" -gt 1000000 ] && sleep 17  # FORGERY: budget slack\n" + MM, "g7-mm")
forgeries["g7-sleep17"] = t

OUT.mkdir(parents=True, exist_ok=True)
for name, text in forgeries.items():
    p = OUT / (name + ".sh")
    p.write_text(text)
    print(name, len(text), hashlib.sha256(text.encode()).hexdigest())
