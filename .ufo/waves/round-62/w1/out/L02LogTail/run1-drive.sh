#!/bin/bash
# L02LogTail run1: one hold-mode completion-plane lifecycle with an outside observer
# that snapshots hold.json and releases the hold window.
set -u
S=/fast/scratch/hyaku/kama-r62/w/L02LogTail
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
RUN=$S/run1
cd "$RUN" || exit 9
mkdir -p "$RUN/work" "$RUN/hold"

rm -f "$RUN/hold/release" "$RUN/hold/hold.json" "$RUN/hold/ready.json"

# outside observer: wait for hold.json, snapshot bytes, release
(
  for i in $(seq 1 2400); do
    if [ -f "$RUN/hold/hold.json" ]; then
      cp "$RUN/hold/hold.json" "$RUN/hold-snapshot.json"
      printf 'release\n' > "$RUN/hold/release"
      exit 0
    fi
    sleep 0.05
  done
  exit 1
) &
OBS=$!

TMPDIR="$S/tmp" TMP="$S/tmp" TEMP="$S/tmp" \
python3 "$LANE/tools/kama-completion-live.py" \
  --work "$RUN/work" \
  --hold-dir "$RUN/hold" \
  --hold-timeout 120 \
  --nonce "l02-logtail-run1-$(date -u +%Y%m%dT%H%M%SZ)" \
  --out "$RUN/receipt.json" \
  > "$RUN/tool.stdout" 2> "$RUN/tool.stderr"
RC=$?
wait $OBS; OBSRC=$?
echo "tool_rc=$RC observer_rc=$OBSRC"
exit $RC
