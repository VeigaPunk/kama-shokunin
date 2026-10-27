#!/bin/sh
# Runs inside: bwrap --bind / / --tmpfs /tmp
set -u
S=/fast/scratch/hyaku/kama-r52/Sen2Scratch
TIP=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
CNT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-append-restore-check.py
echo "ns: initial /tmp entries = $(find /tmp -mindepth 1 | wc -l)"
echo "ns: /tmp mode = $(stat -c '%A' /tmp)"

run_case() {
  label=$1; shift
  : > "$S/ns-$label-peak.txt"
  "$@" > "$S/ns-$label.txt" 2>&1 &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    find /tmp -mindepth 1 -maxdepth 2 >> "$S/ns-$label-peak.txt" 2>/dev/null
    sleep 0.15
  done
  wait "$pid"; rc=$?
  sort -u "$S/ns-$label-peak.txt" > "$S/ns-$label-peak-uniq.txt"
  echo "ns $label: exit=$rc peak-entries=$(wc -l < "$S/ns-$label-peak-uniq.txt") residue-entries=$(find /tmp -mindepth 1 | wc -l)"
  sed -n '1,6p' "$S/ns-$label.txt"
  echo "ns $label residue sample:"; find /tmp -mindepth 1 -maxdepth 2 | sed -n '1,10p'
}

# positive control: no TMPDIR -> tempfile.gettempdir() is /tmp inside the namespace
run_case no-tmpdir env -u TMPDIR python3 "$CNT" --repo "$S/lane" --tip "$TIP"
echo "== positive-control peak listing (proves the watcher sees real writes) =="
sed -n '1,20p' "$S/ns-no-tmpdir-peak-uniq.txt"

# the audited condition: TMPDIR points into the seat scratch
run_case with-tmpdir env TMPDIR="$S/t" python3 "$CNT" --repo "$S/lane" --tip "$TIP"
echo "== TMPDIR-set peak listing (must contain no /tmp entry from the counter) =="
sed -n '1,40p' "$S/ns-with-tmpdir-peak-uniq.txt"
echo "ns final /tmp entries = $(find /tmp -mindepth 1 | wc -l)"
echo "ns final seat scratch:"; ls -la "$S/t"
