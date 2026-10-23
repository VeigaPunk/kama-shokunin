#!/bin/bash
# MutC1Dup harness: run one counter against one tip in the scratch clone.
# usage: run.sh LABEL COUNTER TIP
set -u
label=$1
counter=$2
tip=$3
lane=/home/vgpnk/Projects/shokunin/kama-shokunin
repo=/tmp/kama-r31w2/MutC1Dup/repo
cd /tmp/kama-r31w2/MutC1Dup || exit 90
printf '%s\t%s\t%s\t%s\n' "$label" "$(sha256sum "$counter" | cut -d' ' -f1)" "$tip" \
  "/usr/bin/python3 $counter --lane $lane --repo $repo --tip $tip --out receipts/$label.json" \
  >> receipts/commands.log
/usr/bin/python3 "$counter" --lane "$lane" --repo "$repo" --tip "$tip" \
  --out "receipts/$label.json" >"receipts/$label.out" 2>"receipts/$label.err"
rc=$?
echo "== $label exit $rc"
echo "-- stdout:"; cat "receipts/$label.out"
echo "-- stderr:"; cat "receipts/$label.err"
exit 0
