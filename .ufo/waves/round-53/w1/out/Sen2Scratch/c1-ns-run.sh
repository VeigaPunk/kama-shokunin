#!/bin/sh
# Runs INSIDE bwrap: bwrap --bind / / --dev /dev --proc /proc --tmpfs /tmp [--remount-ro /tmp]
# Usage: c1-ns-run.sh <label: ro|ns>
set -u
S=/fast/scratch/hyaku/kama-r53/Sen2Scratch
CNT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py
TIP=c22602bd8d83ab26349d1087e916ca537ee4f9d1
LABEL=$1
SCR=$S/t-$LABEL
POLL=$S/c1-$LABEL-tmp-poll.txt
mkdir -p "$SCR"
: > "$POLL"
echo "label=$LABEL /tmp stat=$(stat -c '%A %a' /tmp) mountline=$(awk '$2=="/tmp"{print $1, $3, $4}' /proc/self/mounts)"
echo "initial /tmp entries=$(find /tmp -mindepth 1 | wc -l)"
if mktemp -d /tmp/r53probe.XXXXXX >/dev/null 2>&1; then
  echo "TMP-WRITABLE (mktemp succeeded)"; rmdir /tmp/r53probe.?* 2>/dev/null
else
  echo "TMP-READONLY (mktemp -d /tmp/r53probe.XXXXXX failed)"
fi
start=$(date +%s)
TMPDIR="$SCR" python3 "$CNT" --repo "$S/lane" --tip "$TIP" --scratch "$SCR" \
    --out "$S/c1-$LABEL.out" > "$S/c1-$LABEL.txt" 2>&1 &
pid=$!
while kill -0 "$pid" 2>/dev/null; do
  find /tmp -mindepth 1 -maxdepth 3 >> "$POLL" 2>/dev/null
  sleep 0.2
done
wait "$pid"; rc=$?
end=$(date +%s)
sort -u "$POLL" > "$S/c1-$LABEL-tmp-poll-uniq.txt"
echo "c1 $LABEL: exit=$rc wall=$((end-start))s"
echo "--- head ---"; sed -n '1,2p' "$S/c1-$LABEL.txt"
echo "--- tail ---"; tail -n 2 "$S/c1-$LABEL.txt"
echo "tmp-paths-during-run=$(wc -l < "$S/c1-$LABEL-tmp-poll-uniq.txt")"
sed -n '1,20p' "$S/c1-$LABEL-tmp-poll-uniq.txt"
echo "final /tmp entries=$(find /tmp -mindepth 1 | wc -l)"
echo "--- llama-server ---"; pgrep -af '(^|/)llama-server( |$)' || echo none
echo "--- scratch residue ---"; find "$SCR" -maxdepth 1 | sed -n '1,10p'
