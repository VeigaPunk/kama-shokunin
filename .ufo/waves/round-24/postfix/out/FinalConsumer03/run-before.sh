#!/bin/bash
S=/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer03
F="$S/fix"
export TMPDIR="$S/tmp"
set +e
python3 "$S/out/before-2e254a1.py" --lane-repo "$F/lane" --fleet-repo "$F/fleet" \
  --branch master --rounds 1 --report "1=$F/draft.md" --no-errata --json \
  > "$S/out/before-direct.json" 2> "$S/out/before-direct.stderr"
rc=$?
{
  echo "BEFORE_EXIT=$rc"
  echo "--- stdout (600) ---"
  head -c 600 "$S/out/before-direct.json"
  echo
  echo "--- stderr ---"
  cat "$S/out/before-direct.stderr"
} > "$S/out/before-direct.txt" 2>&1
true
