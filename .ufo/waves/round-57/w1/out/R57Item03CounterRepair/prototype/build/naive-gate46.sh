#!/usr/bin/env bash
# Circular gate: expects the frozen claim's maxN literal (46).
out=$("$@" 2>&1); code=$?
printf '%s\n' "$out"
if printf '%s' "$out" | grep -q 'mismatches=0' && printf '%s' "$out" | grep -q 'maxN=46' && printf '%s' "$out" | grep -q 'met=True'; then
  echo "naive_gate46=pass exit=$code"; exit 0
fi
echo "naive_gate46=fail exit=$code"; exit 1
