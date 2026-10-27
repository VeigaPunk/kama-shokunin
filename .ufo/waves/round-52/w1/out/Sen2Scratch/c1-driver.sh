#!/bin/sh
# C1 scratch audit driver (host path). Usage: c1-driver.sh <label> <tmpdir-for-counter> [-- ns]
set -u
S=/fast/scratch/hyaku/kama-r52/Sen2Scratch
LABEL=$1
TMPD=$2
TIP=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
CNT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-replay-memfd-audit.py
POLL="$S/c1-$LABEL-tmp-poll.txt"
SPOLL="$S/c1-$LABEL-scratch-poll.txt"
: > "$POLL"; : > "$SPOLL"
start=$(date +%s)
TMPDIR=$TMPD python3 "$CNT" --repo "$S/lane" --tip "$TIP" --out "$S/c1-$LABEL.out" \
    > "$S/c1-$LABEL.txt" 2>&1 &
pid=$!
while kill -0 "$pid" 2>/dev/null; do
  for pat in '/tmp/r52c1-*' '/tmp/r52c2-*' '/tmp/klr-st-*' '/tmp/kama-probe.*' \
             '/tmp/kama-llamacpp-live-*' '/tmp/kama-live-*' '/tmp/tmp.*'; do
    for p in $pat; do [ -e "$p" ] && echo "$p"; done
  done >> "$POLL"
  ls -d "$TMPD"/r52c1-* 2>/dev/null >> "$SPOLL"
  ls "$TMPD"/r52c1-*/ 2>/dev/null >> "$SPOLL"
  sleep 0.2
done
wait "$pid"; rc=$?
end=$(date +%s)
sort -u "$POLL" > "$S/c1-$LABEL-tmp-poll-uniq.txt"
sort -u "$SPOLL" > "$S/c1-$LABEL-scratch-poll-uniq.txt"
echo "c1 $LABEL: exit=$rc wall=$((end-start))s"
echo "--- counter stdout ---"; cat "$S/c1-$LABEL.txt"
echo "--- /tmp entries seen during the run (sorted uniq) ---"
cat "$S/c1-$LABEL-tmp-poll-uniq.txt"
echo "--- scratch seen under TMPDIR=$TMPD (first 25) ---"
sed -n '1,25p' "$S/c1-$LABEL-scratch-poll-uniq.txt"
echo "--- residue: TMPDIR ---"; ls -la "$TMPD"
echo "--- residue: /tmp kama-probe.* ---"; for p in /tmp/kama-probe.*; do [ -e "$p" ] && echo "$p"; done
echo "--- llama-server processes ---"; pgrep -af '(^|/)llama-server( |$)' || echo none
