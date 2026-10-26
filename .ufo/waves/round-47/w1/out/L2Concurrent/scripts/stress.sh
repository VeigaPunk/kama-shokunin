#!/bin/bash
# L2Concurrent natural-collision hunt: N-way simultaneous invocations of the REAL lane live
# tool (unmodified), stopping early on any non-zero exit or a duplicate port inside one round.
# No downloads (server/model taken from the assigned replay pair's work dir).
set -u
S=/fast/scratch/hyaku/kama-r47/L2Concurrent
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
LIVE=$LANE/tools/kama-llamacpp-live.py
SRV=$S/wA/server/llama-b11909/llama-server
MDL=$S/wA/download/stories260K.gguf
RMSHA=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
R=${OUT:-$S/stress}; mkdir -p "$R"
N=${N:-12}; MAXR=${MAXR:-200}
: >"$R/rounds.txt"; : >"$R/stop.txt"
runs=0
for r in $(seq 1 "$MAXR"); do
  pids=()
  for i in $(seq 1 "$N"); do
    ( python3 "$LIVE" --server "$SRV" --model "$MDL" --model-sha256 "$RMSHA" \
        --alias kama-r47-live --ctx 256 --threads 1 \
        --out "$R/r$r-$i.json" >"$R/r$r-$i.log" 2>&1; echo "$?" >"$R/r$r-$i.rc" ) &
    pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p"; done
  runs=$((runs+N))
  line=$(python3 - "$R" "$r" "$N" <<'PY'
import json,os,sys
d,r,n=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
ports=[];bad=[];setup=[]
for i in range(1,n+1):
    try: rec=json.load(open(f"{d}/r{r}-{i}.json"))
    except Exception as e: bad.append(f"{i}:noreceipt"); continue
    ports.append(rec.get("port"))
    if rec.get("outcome")!="pass": bad.append(f"{i}:{rec.get('outcome')}")
    if rec.get("setup_error"): setup.append(f"{i}:{rec['setup_error']}")
dup=sorted({p for p in ports if ports.count(p)>1 and p})
print(f"round={r} n={n} ports={len(ports)} dup_within_round={dup} bad={bad} setup_error={setup}")
PY
)
  echo "$line" >>"$R/rounds.txt"
  if ! grep -q "dup_within_round=\[\] bad=\[\] setup_error=\[\]" <<<"$line"; then
    echo "STOP at round $r: $line" | tee -a "$R/stop.txt"
    break
  fi
done
sleep 1
ss -ltnpH 2>/dev/null | grep -c llama-server >"$R/listeners-after.txt" || echo 0 >"$R/listeners-after.txt"
pgrep -af "$S" >"$R/pgrep-after.txt" 2>/dev/null || true
echo "runs=$runs rounds_done=$(wc -l <"$R/rounds.txt")"
echo "rounds_with_dup_or_bad=$(grep -vc 'dup_within_round=\[\] bad=\[\] setup_error=\[\]' "$R/rounds.txt")"
echo "total ports chosen=$(grep -o 'ports=[0-9]*' "$R/rounds.txt" | cut -d= -f2 | paste -sd+ | bc)"
echo "listeners_after=$(cat "$R/listeners-after.txt")"
echo "procs_after:"; grep -v pgrep "$R/pgrep-after.txt" || echo none
