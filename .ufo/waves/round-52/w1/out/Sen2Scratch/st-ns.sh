#!/bin/sh
# selftest scratch audit inside bwrap (fresh tmpfs /tmp)
set -u
S=/fast/scratch/hyaku/kama-r52/Sen2Scratch
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
watch() { # $1 label, rest: command
  label=$1; shift
  : > "$S/st-$label-peak.txt"
  "$@" > "$S/st-$label.txt" 2>&1 &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    find /tmp -mindepth 1 -maxdepth 2 >> "$S/st-$label-peak.txt" 2>/dev/null
    sleep 0.1
  done
  wait "$pid"; rc=$?
  sort -u "$S/st-$label-peak.txt" > "$S/st-$label-peak-uniq.txt"
  echo "== $label exit=$rc /tmp-paths=$(wc -l < "$S/st-$label-peak-uniq.txt") residue=$(find /tmp -mindepth 1 | wc -l)"
  sed -n '1,8p' "$S/st-$label-peak-uniq.txt"
  tail -2 "$S/st-$label.txt"
}
echo "ns initial /tmp entries = $(find /tmp -mindepth 1 | wc -l)"
watch live-selftest-notmpdir env -u TMPDIR python3 "$LANE/tools/kama-llamacpp-live.py" --selftest
watch live-selftest-tmpdir env TMPDIR="$S/t" python3 "$LANE/tools/kama-llamacpp-live.py" --selftest
watch klr-selftest-tmpdir env TMPDIR="$S/t" python3 "$LANE/tools/kama-live-replay.py" --selftest --scratch "$S/t"
watch klr-selftest-notmpdir env -u TMPDIR python3 "$LANE/tools/kama-live-replay.py" --selftest
echo "ns final /tmp entries = $(find /tmp -mindepth 1 | wc -l)"
ls -la "$S/t"
