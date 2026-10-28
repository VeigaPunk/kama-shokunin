#!/bin/bash
# L02LogTail run5: does the one whitelisted LLAMA_ARG_* env var (THREADS) alter the
# graded run, i.e. can the log contradict the receipt's argv?
set -u
S=/fast/scratch/hyaku/kama-r62/w/L02LogTail
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
R=$S/run5
mkdir -p "$R/work" "$R/hold"
export TMPDIR=$S/tmp TMP=$S/tmp TEMP=$S/tmp
rm -f "$R/hold/release" "$R/hold/hold.json"
(
  LLAMA_ARG_THREADS=4 \
  python3 "$LANE/tools/kama-completion-live.py" --work "$R/work" --hold-dir "$R/hold" \
    --hold-timeout 120 --nonce "l02-logtail-run5-threadsenv" \
    --out "$R/receipt.json" > "$R/tool.stdout" 2> "$R/tool.stderr"
) &
TOOLPID=$!
for i in $(seq 1 2400); do
  if [ -f "$R/hold/hold.json" ]; then
    cp "$R/hold/hold.json" "$R/hold-snapshot.json"
    printf 'release\n' > "$R/hold/release"
    break
  fi
  sleep 0.05
done
wait $TOOLPID; RC=$?
echo "run5 rc=$RC"
