#!/bin/bash
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT22ListenerShapes
cd "$S"
: > "$S/summary.txt"
ambient() {
python3 - <<'PYEOF'
import os
me = os.getuid()
n = 0
for name in os.listdir('/proc'):
    if not name.isdigit():
        continue
    try:
        st = os.stat('/proc/%s' % name)
        if st.st_uid != me:
            continue
        try:
            os.listdir('/proc/%s/fd' % name)
        except PermissionError:
            n += 1
        except OSError:
            pass
    except OSError:
        pass
print(n)
PYEOF
}
run_shape() {
  local SHAPE=$1
  local A=$(ambient)
  local OUT=$(python3 "$S/mt22-build.py" "$SHAPE")
  local TIP=$(echo "$OUT" | awk '{print $2}')
  rm -f "$S/forge-on"; printf '{"mode": "%s"}\n' "$SHAPE" > "$S/forge-on"
  python3 "$CLONE/tools/round64-c1-counter.py" --repo "$CLONE" --tip "$TIP" \
    --work "$S/work-$SHAPE" > "$S/run-$SHAPE.out" 2> "$S/run-$SHAPE.err"
  local RC=$?
  local A2=$(ambient)
  rm -f "$S/forge-on"; printf '{"mode": "%s"}\n' "$SHAPE" > "$S/forge-on"
  MT22_DIAG="$S/diag-$SHAPE.jsonl" python3 "$S/mt22-diag.py" \
    "$CLONE/tools/round64-c1-counter.py" --repo "$CLONE" --tip "$TIP" \
    --work "$S/diag-$SHAPE" > "$S/diag-$SHAPE.out" 2> "$S/diag-$SHAPE.err"
  {
    echo "== $SHAPE tip=$TIP rc=$RC ambient_before=$A ambient_after=$A2"
    grep -o 'tool_present=.*' "$S/run-$SHAPE.out" | head -1
    echo "  err: $(tail -1 "$S/run-$SHAPE.err")"
    echo "  diag: $(cat "$S/diag-$SHAPE.jsonl" 2>/dev/null | head -1 | cut -c1-400)"
    echo "  diagline: $(grep -o 'tool_present=.*' "$S/diag-$SHAPE.out" | head -1 | cut -c1-160)"
  } >> "$S/summary.txt"
  echo "done $SHAPE (rc=$RC)"
}
CLONE=$S/clone
export CLONE
# daemon shapes share one pre-started daemon
sudo -n python3 "$S/mt22-daemon.py" "$S/mt22-daemon.sock" 2>"$S/daemon.err" &
DPID=$!
for i in $(seq 1 100); do [[ -S "$S/mt22-daemon.sock" ]] && break; sleep 0.1; done
for s in reuseport v6 v6root v6daemon mappeddaemon; do run_shape "$s"; done
sudo -n kill "$DPID" 2>/dev/null
sleep 0.3
for s in ns unixfront fwd; do run_shape "$s"; done
pkill -f "mt22-helper.py" 2>/dev/null
rm -f "$S/forge-on"
echo ALL_DONE
