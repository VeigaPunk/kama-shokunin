#!/bin/bash
# L2Concurrent amplification: N-way concurrent invocations of the REAL lane live tool
# (tools/kama-llamacpp-live.py, unmodified) on the same receipt-1 parameters, no downloads
# (server+model already acquired by the assigned replay pair). Each run picks its own port
# through pick_port() exactly as the replay does. Samples ss/pgrep between rounds.
set -u
S=/fast/scratch/hyaku/kama-r47/L2Concurrent
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
LIVE=$LANE/tools/kama-llamacpp-live.py
SRV=$S/wA/server/llama-b11909/llama-server
MDL=$S/wA/download/stories260K.gguf
RMSHA=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
R=$S/amp; rm -rf "$R"; mkdir -p "$R"
N=${N:-6}
ROUNDS=${ROUNDS:-8}
: >"$R/rounds.txt"
for r in $(seq 1 "$ROUNDS"); do
  pids=()
  for i in $(seq 1 "$N"); do
    ( python3 "$LIVE" --server "$SRV" --model "$MDL" --model-sha256 "$RMSHA" \
        --alias kama-r47-live --ctx 256 --threads 1 \
        --out "$R/r$r-$i.json" >"$R/r$r-$i.log" 2>&1; echo "$?" >"$R/r$r-$i.rc" ) &
    pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p"; done
  line="round=$r"
  for i in $(seq 1 "$N"); do
    port=$(python3 - "$R/r$r-$i.json" <<'PY'
import json,sys
try: r=json.load(open(sys.argv[1]))
except Exception: print("NORECEIPT"); raise SystemExit
a=r.get("argv") or []
print(a[a.index("--port")+1] if "--port" in a else "NOPORT")
PY
)
    rc=$(cat "$R/r$r-$i.rc" 2>/dev/null || echo NORC)
    line="$line $i:port=$port,exit=$rc"
  done
  echo "$line" >>"$R/rounds.txt"
done
# leftovers after the amplification
sleep 1
ss -ltnp >"$R/ss-post.txt" 2>/dev/null
pgrep -af "$S" >"$R/pgrep-post.txt" 2>/dev/null || true
echo "--- rounds"; cat "$R/rounds.txt"
echo "--- ports"; grep -o 'port=[0-9]*' "$R/rounds.txt" | cut -d= -f2 | sort | uniq -c | awk '$1>1{print "DUPLICATE",$2,$1}END{}'
echo "port occurrences: $(grep -o 'port=[0-9]*' "$R/rounds.txt" | wc -l), distinct: $(grep -o 'port=[0-9]*' "$R/rounds.txt" | sort -u | wc -l)"
echo "exits: $(grep -o 'exit=[0-9]*' "$R/rounds.txt" | sort | uniq -c | tr '\n' ' ')"
echo "--- leftover listeners"; grep -c llama "$R/ss-post.txt" || echo 0
echo "--- leftover procs under my scratch"; grep -v "pgrep -af" "$R/pgrep-post.txt" || echo none
