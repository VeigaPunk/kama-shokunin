#!/bin/sh
# In-namespace C1 run at an arbitrary tip (control runs). Usage: c1-ns-tip.sh <label> <tip>
set -u
S=/fast/scratch/hyaku/kama-r53/Sen2Scratch
CNT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py
LABEL=$1
TIP=$2
SCR=$S/t-$LABEL
POLL=$S/c1-$LABEL-tmp-poll.txt
mkdir -p "$SCR"
: > "$POLL"
echo "label=$LABEL tip=$TIP /tmp stat=$(stat -c '%A %a' /tmp) mountline=$(awk '$2=="/tmp"{print $1, $3, $4}' /proc/self/mounts | tail -n1)"
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
  find /tmp -maxdepth 2 -name 'kama*' -o -maxdepth 2 -name 'r53c1-*' >> "$POLL" 2>/dev/null
  sleep 0.1
done
wait "$pid"; rc=$?
end=$(date +%s)
sort -u "$POLL" > "$S/c1-$LABEL-tmp-poll-uniq.txt"
echo "c1 $LABEL: exit=$rc wall=$((end-start))s"
echo "--- head ---"; sed -n '1,2p' "$S/c1-$LABEL.txt"
echo "--- bind/code lines ---"; grep -E '^(detail: (bind|code) b1)' "$S/c1-$LABEL.txt"
echo "kama-or-r53c1-paths-in-/tmp=$(wc -l < "$S/c1-$LABEL-tmp-poll-uniq.txt")"
sed -n '1,10p' "$S/c1-$LABEL-tmp-poll-uniq.txt"
echo "--- llama-server (paths under Sen2Scratch only) ---"; pgrep -af 'Sen2Scratch.*llama-server' || echo none
