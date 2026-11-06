#!/usr/bin/env python3
"""Generate one-change revert mutants of tools/kama-probe.sh at M=f968fb19."""
from pathlib import Path
import sys

src = Path("probe-M.sh").read_text()
outdir = Path("mutants")
outdir.mkdir(exist_ok=True)


def rep(t, old, new, name):
    n = t.count(old)
    if n != 1:
        sys.exit(f"{name}: expected 1 occurrence, got {n}\n---\n{old}")
    return t.replace(old, new)


FETCH_MAX = '        --max-filesize "$MAX_BODY" -o "$FBODY" -D "$FHDR" \\\n'
FETCH_WC = ('  # older curl ignores --max-filesize for a body of unknown length: re-check what was written\n'
            '  if [ "$rc" -eq 0 ] && [ -f "$FBODY" ] && [ "$(wc -c < "$FBODY")" -gt "$MAX_BODY" ]; then F_RC=63; fi\n')
AUTO_MAX = '    --max-filesize "$MAX_BODY" -o "$pbody" "http://127.0.0.1:$port/props" 2>/dev/null || return 1\n'
AUTO_WC = '  [ "$(wc -c < "$pbody")" -le "$MAX_BODY" ] || return 1\n'
SERV = "s/\\r$//' | strip_ctl || true)"
CT = 'F_CT=$(printf \'%s\' "${w%%|*}" | strip_ctl)'
CLEAN_USE = 'print("\\n".join(dict.fromkeys(clean(v) for v in g)))'
ID_FILTER = '            or any(ord(c) < 0x20 or 0x7F <= ord(c) <= 0x9F for c in e["id"]):'
VAL_FILTER = '        val = v if isinstance(v, str) and v and not any(ord(c) < 0x20 or 0x7F <= ord(c) <= 0x9F for c in v) else "?"'
JSTR_LOOP = '''  # Round 90 (S588 RFC 8259 section 7): every other control character U+0001-U+001F and DEL is
  # escaped too, so a listener-supplied byte can never make the generated JSON unparseable.
  local i c
  if [[ $s == *[$'\\x01'-$'\\x1f'$'\\x7f']* ]]; then
    for i in {1..31} 127; do
      printf -v c "\\\\x$(printf '%02x' "$i")"
      printf -v c "$c"
      s=${s//"$c"/$(printf '\\\\u%04x' "$i")}
    done
  fi
'''

muts = {}

muts["M1"] = rep(src, FETCH_MAX, '        -o "$FBODY" -D "$FHDR" \\\n', "M1")
muts["M2"] = rep(src, FETCH_WC, "", "M2")
muts["M3"] = rep(muts["M1"], FETCH_WC, "", "M3")
muts["M4"] = rep(src, AUTO_MAX, '    -o "$pbody" "http://127.0.0.1:$port/props" 2>/dev/null || return 1\n', "M4")
muts["M5"] = rep(src, AUTO_WC, "", "M5")
muts["M6"] = rep(src, SERV, "s/\\r$//' || true)", "M6")
muts["M7"] = rep(src, CT, 'F_CT=${w%%|*}', "M7")
muts["M8"] = rep(src, CLEAN_USE, 'print("\\n".join(dict.fromkeys(g)))', "M8")
muts["M9"] = rep(src, ID_FILTER, '            or any(c in e["id"] for c in "\\t\\r\\n"):', "M9")
muts["M10"] = rep(src, VAL_FILTER, '        val = v if isinstance(v, str) and v and "\\t" not in v and "\\n" not in v else "?"', "M10")
muts["M11"] = rep(src, JSTR_LOOP, "", "M11")
muts["M12"] = rep(src, "MAX_BODY=4194304\n", "MAX_BODY=67108864\n", "M12")
muts["M13"] = rep(src, '''    63)
      C_VERDICT=FOREIGN_SERVICE
      C_REASON=body-too-large''', '''    63)
      C_VERDICT=MODEL_OK
      C_REASON=body-too-large''', "M13")

for k, v in muts.items():
    p = outdir / f"{k}.sh"
    p.write_text(v)
    print(k, len(v), "bytes")
