#!/usr/bin/env bash
# $1 = command producing counter output. Passes iff the summary tokens appear.
out=$("$@" 2>&1); code=$?
printf '%s\n' "$out"
if printf '%s' "$out" | grep -q 'mismatches=0' && printf '%s' "$out" | grep -q 'maxN=56' && printf '%s' "$out" | grep -q 'met=True'; then
  echo "naive_gate=pass exit=$code"; exit 0
fi
echo "naive_gate=fail exit=$code"; exit 1
