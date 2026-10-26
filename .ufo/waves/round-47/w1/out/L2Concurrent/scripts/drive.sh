#!/bin/bash
# L2Concurrent driver: two kama-live-replay.py runs on the same receipt, same start instant,
# separate --work dirs. Records per-run start/end epochs, exit codes, and listener/child
# snapshots before, during (0.5 s cadence) and after.
set -u
S=/fast/scratch/hyaku/kama-r47/L2Concurrent
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
TOOL=$LANE/tools/kama-live-replay.py
REC=$LANE/.ufo/waves/round-47/c2/live/receipt-1.json
rm -rf "$S/wA" "$S/wB" "$S/a.json" "$S/b.json"

echo "driver_start $(date -u +%FT%T.%NZ)"
ss -ltnp >"$S/ss-pre.txt" 2>/dev/null
pgrep -af llama-server >"$S/pgrep-pre.txt" 2>/dev/null || true

# barrier: both children exec the replay in the same instant
run() { # name work out
  local t0 t1 rc
  t0=$(date +%s.%N)
  python3 "$TOOL" --receipt "$REC" --work "$2" --out "$3" >"$S/$1.log" 2>&1
  rc=$?
  t1=$(date +%s.%N)
  printf '%s start=%s end=%s exit=%s\n' "$1" "$t0" "$t1" "$rc" >>"$S/timing.txt"
}
: >"$S/timing.txt"
run A "$S/wA" "$S/a.json" &
PA=$!
run B "$S/wB" "$S/b.json" &
PB=$!

# sample listeners/children while the pair runs
i=0
while kill -0 $PA 2>/dev/null || kill -0 $PB 2>/dev/null; do
  i=$((i+1))
  printf '@%s ' "$(date -u +%FT%T.%NZ)" >>"$S/ss-during.txt"
  ss -ltnpH 2>/dev/null | grep -c llama-server >>"$S/ss-during.txt" 2>/dev/null || echo 0 >>"$S/ss-during.txt"
  pgrep -af "llama-server" >>"$S/pgrep-during.txt" 2>/dev/null || true
  sleep 0.5
done
wait $PA; wait $PB

echo "driver_end $(date -u +%FT%T.%NZ)"
sleep 2
ss -ltnp >"$S/ss-post.txt" 2>/dev/null
pgrep -af llama-server >"$S/pgrep-post.txt" 2>/dev/null || true
sort -u "$S/pgrep-during.txt" >"$S/pgrep-during.uniq.txt" 2>/dev/null || true
cat "$S/timing.txt"
echo "--- a.json"; cat "$S/a.json" 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print({k:d.get(k) for k in ("match","refused","mismatches","live_exit")})'
echo "--- b.json"; cat "$S/b.json" 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print({k:d.get(k) for k in ("match","refused","mismatches","live_exit")})'
for n in A B; do
  f=$([ $n = A ] && echo "$S/wA/rerun-receipt.json" || echo "$S/wB/rerun-receipt.json")
  echo "--- $n rerun $(basename $f)"
  python3 - "$f" <<'PY'
import json,sys
try:
    r=json.load(open(sys.argv[1]))
except Exception as e:
    print("absent:", e); raise SystemExit
port=None
a=r.get("argv") or []
if "--port" in a: port=a[a.index("--port")+1]
print("port", port, "outcome", r.get("outcome"), "checks", len(r.get("checks") or []),
      "failed", [c["id"] for c in r.get("checks") or [] if c.get("evaluated") and not c.get("passed")])
PY
done
echo "--- during samples $(wc -l <"$S/ss-during.txt" 2>/dev/null || echo 0)"
