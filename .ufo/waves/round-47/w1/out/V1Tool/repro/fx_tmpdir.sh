#!/usr/bin/env bash
# F8: TMPDIR / --scratch honoured; fixture dirs removed on exit.
set -u
S=/fast/scratch/hyaku/kama-r47/V1Tool
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py
mkdir -p "$S/tmps" "$S/sc"
echo "== selftest with TMPDIR=$S/tmps (no --scratch) =="
TMPDIR="$S/tmps" python3 "$TOOL" --selftest | tail -3
echo "leftovers in tmps:"; find "$S/tmps" -maxdepth 1 -name 'aoa-*' | wc -l
echo "== selftest with --scratch $S/sc =="
python3 "$TOOL" --selftest --scratch "$S/sc" | tail -3
echo "leftovers in sc:"; find "$S/sc" -maxdepth 1 -name 'aoa-*' | wc -l
echo "== --scratch pointing at a nonexistent dir =="
python3 "$TOOL" --selftest --scratch "$S/no-such-dir" 2>&1 | tail -3
echo "exit=$?"
