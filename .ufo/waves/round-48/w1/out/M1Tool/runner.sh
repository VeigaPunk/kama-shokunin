#!/bin/sh
# selftest one mutant; log stdout+stderr+exit
S=/fast/scratch/hyaku/kama-r48/M1Tool
f="$1"
id=$(basename "$f" .py)
mkdir -p "$S/st-$id"
TMPDIR="$S" python3 "$f" --selftest --scratch "$S/st-$id" > "$S/logs/$id.txt" 2>&1
echo "$id exit=$?"
rm -rf "$S/st-$id"
