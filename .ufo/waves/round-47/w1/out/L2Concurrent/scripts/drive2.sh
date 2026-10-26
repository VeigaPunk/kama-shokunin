#!/bin/bash
# L2Concurrent second assigned-condition pair, pinned: tools from the shared clone at lane
# commit 3a09a1d9, receipt = the c2/live/receipt-1.json copy (sha256 a4caf311...).
set -u
S=/fast/scratch/hyaku/kama-r47/L2Concurrent
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
TOOL=$S/lane/tools/kama-live-replay.py
REC=$S/receipt-1.pinned.json
rm -rf "$S/wC" "$S/wD" "$S/c.json" "$S/d.json"
echo "pair2_start $(date -u +%FT%T.%NZ)"
ss -ltnp >"$S/ss2-pre.txt" 2>/dev/null
pgrep -af "L2Concurrent" >"$S/pgrep2-pre.txt" 2>/dev/null || true
run() { local t0 t1 rc
  t0=$(date +%s.%N)
  python3 "$TOOL" --receipt "$REC" --work "$2" --out "$3" >"$S/$1.log" 2>&1
  rc=$?; t1=$(date +%s.%N)
  printf '%s start=%s end=%s exit=%s\n' "$1" "$t0" "$t1" "$rc" >>"$S/timing2.txt"
}
: >"$S/timing2.txt"
run C "$S/wC" "$S/c.json" &
PC=$!
run D "$S/wD" "$S/d.json" &
PD=$!
i=0; : >"$S/ss2-during.txt"
while kill -0 $PC 2>/dev/null || kill -0 $PD 2>/dev/null; do
  i=$((i+1)); printf '%s listeners=%s children=%s\n' "$(date -u +%FT%T.%NZ)" \
    "$(ss -ltnpH 2>/dev/null | grep -c llama-server)" \
    "$(pgrep -fc "$S/w[CD]/server" 2>/dev/null || echo 0)" >>"$S/ss2-during.txt"
  sleep 0.2
done
wait $PC; wait $PD
echo "pair2_end $(date -u +%FT%T.%NZ)"
sleep 1
ss -ltnp >"$S/ss2-post.txt" 2>/dev/null
pgrep -af llama-server >"$S/pgrep2-post.txt" 2>/dev/null || true
cat "$S/timing2.txt"
for f in c d; do
  echo "--- $f.json"; python3 -c "
import json;d=json.load(open('$S/$f.json'));print({k:d.get(k) for k in ('match','refused','mismatches','live_exit','rerun_receipt')})"
done
for f in wC wD; do python3 - "$S/$f/rerun-receipt.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1])); a=r["argv"]
print(sys.argv[1], "port", a[a.index("--port")+1], "outcome", r["outcome"],
      "checks", len(r["checks"]), "evaluated", sum(1 for c in r["checks"] if c["evaluated"]),
      "ownership", r.get("port_listener_ownership"), "child", r.get("child_pid"),
      "started", r.get("started_utc"), "ended", r.get("ended_utc"),
      "log_path", (r.get("teardown") or {}).get("log_path"),
      "port_refuses", (r.get("teardown") or {}).get("port_refuses"))
PY
done
echo "listeners_post=$(grep -c llama-server "$S/ss2-post.txt" || echo 0)"
