#!/bin/sh
# C1 scratch audit inside bwrap (fresh tmpfs /tmp): full /tmp poll, authoritative attribution.
set -u
S=/fast/scratch/hyaku/kama-r52/Sen2Scratch
TIP=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
CNT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-replay-memfd-audit.py
POLL="$S/c1-ns-tmp-peak.txt"
: > "$POLL"
echo "ns: initial /tmp entries = $(find /tmp -mindepth 1 | wc -l)"
start=$(date +%s)
TMPDIR="$S/t" python3 "$CNT" --repo "$S/lane" --tip "$TIP" --out "$S/c1-ns.out" \
    > "$S/c1-ns.txt" 2>&1 &
pid=$!
while kill -0 "$pid" 2>/dev/null; do
  find /tmp -mindepth 1 -maxdepth 3 >> "$POLL" 2>/dev/null
  sleep 0.2
done
wait "$pid"; rc=$?
end=$(date +%s)
sort -u "$POLL" > "$S/c1-ns-tmp-peak-uniq.txt"
echo "c1 ns: exit=$rc wall=$((end-start))s"
echo "--- counter stdout head/tail ---"; sed -n '1,3p' "$S/c1-ns.txt"; sed -n '$p' "$S/c1-ns.txt"
echo "--- every distinct /tmp path the tree created (count=$(wc -l < "$S/c1-ns-tmp-peak-uniq.txt")) ---"
sed -n '1,60p' "$S/c1-ns-tmp-peak-uniq.txt"
echo "--- residue in /tmp after the run ---"; find /tmp -mindepth 1 | wc -l
echo "--- residue under TMPDIR ---"; ls -la "$S/t"
echo "--- llama-server processes ---"; pgrep -af '(^|/)llama-server( |$)' || echo none
