#!/usr/bin/env bash
# Repro for seat EX02NoPythonPath (kama round 91, C1 on the python-free path).
# Everything runs in scratch; the lane is read-only. Set S to your own scratch root.
set -uo pipefail
S=${S:-/fast/scratch/hyaku/kama-r91/EX02NoPythonPath}
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
B=c06838c5b94576971ea33ac465bf2c935e9037f9
M=3decfa36b0eba7e5197c034dd1547146bca1568a
mkdir -p "$S/pbin" "$S/tmp" "$S/work-m" "$S/work-b"
export TMPDIR=$S/tmp

# 1. python-free PATH dir: symlink every executable except python*, so `command -v python3` fails
for d in /usr/bin /usr/local/bin /bin /usr/sbin; do
  [ -d "$d" ] || continue
  for f in "$d"/*; do
    b=$(basename -- "$f")
    case "$b" in python*) continue;; esac
    [ -x "$f" ] || continue
    [ -e "$S/pbin/$b" ] && continue
    ln -s -- "$f" "$S/pbin/$b"
  done
done
PATH=$S/pbin bash -c 'command -v python3 || echo "python3 absent (rc=$?)"'

# 2. frozen C1 counter, probe subprocess python-free: M then base
PATH=$S/pbin /usr/bin/python3 "$LANE/tools/round91-answer-time.py" --repo "$LANE" --rev "$M" --work "$S/work-m"
echo "M rc=$?"
PATH=$S/pbin /usr/bin/python3 "$LANE/tools/round91-answer-time.py" --repo "$LANE" --rev "$B" --work "$S/work-b"
echo "B rc=$?"

# 3. escaped vs raw id bodies, both revs, both PATH modes (probe_matrix.py + stub.py)
mkdir -p "$S/probes" "$S/bodies" "$S/tmp2"
git -C "$LANE" show "$B:tools/kama-probe.sh" > "$S/probes/b.sh"
git -C "$LANE" show "$M:tools/kama-probe.sh" > "$S/probes/m.sh"
/usr/bin/python3 - <<'PYBODIES'
import json, pathlib
d = pathlib.Path(__import__("os").environ.get("S", "/fast/scratch/hyaku/kama-r91/EX02NoPythonPath")) / "bodies"
uni = "modele-\u00e8-\u65e5\u672c-\u00fc"
spec = 'q"b\\s'
(d / "u1-raw-utf8.json").write_bytes(('{"object":"list","data":[{"id":"%s"}]}' % uni).encode())
(d / "u2-escaped-utf8.json").write_bytes(json.dumps({"object":"list","data":[{"id":uni}]}, separators=(",", ":")).encode())
(d / "u3-specials.json").write_bytes(json.dumps({"object":"list","data":[{"id":spec}]}, separators=(",", ":")).encode())
PYBODIES
S=$S /usr/bin/python3 "$S/probe_matrix.py"

# 4. the two harm suites with the probe python-free (they themselves need python3)
git clone --shared -q "$LANE" "$S/wt" && git -C "$S/wt" checkout --detach -q "$M"
cd "$S/wt" || exit 8
for r in b m; do
  PATH=$S/pbin /usr/bin/python3 tests/probe-verdicts/check.py --probe "$S/probes/$r.sh" | tail -1
done
