#!/usr/bin/env bash
# R42A13 repro: build the C1 fixture (base tree + frozen counters), apply the
# cheapest counter-satisfying shortcut, and run the frozen counter.
# Read-only on /fast/scratch/kama-r42/clone. Writes only under $S.
set -euo pipefail
S=/fast/scratch/kama-r42/seats/R42A13-repro
HERE=$(cd "$(dirname "$0")" && pwd)
CLONE=/fast/scratch/kama-r42/clone
BASE=0b606b03bf0b2a87b791aa537f6c72c941624cf0
FREEZE=0bfd47abdda1f5ac21a0834654122644fc23e861

mkdir -p "$S/tmp"
export TMPDIR="$S/tmp"
D=$(mktemp -d -p "$S" d-XXXXXX)
git -C "$D" init -q
test "$(git -C "$D" rev-parse --show-toplevel)" = "$D"

# 1. base tree + the two frozen counters (they do not exist at base)
git -C "$CLONE" archive "$BASE" | tar -x -C "$D"
git -C "$CLONE" show "$FREEZE:tools/round42-selfdesc-reconcile.py" > "$D/tools/round42-selfdesc-reconcile.py"
git -C "$CLONE" show "$FREEZE:tools/round41-scorecard-reconcile.py" > "$D/tools/round41-scorecard-reconcile.py"
chmod +x "$D/tools/"*.py
git -C "$D" add -A
git -C "$D" -c user.name=repro -c user.email=repro@invalid commit -qm "fixture: base + frozen counters"

# 2. baseline: must reproduce controls/base.c1.out (mismatches=40 met=False)
python3 "$D/tools/round42-selfdesc-reconcile.py" --repo "$D" --tip HEAD || true

# 3. apply the shortcut (15 insertions / 31 deletions, 2 files) and re-run
git -C "$D" apply "$HERE/shortcut-S1b.patch"
git -C "$D" add -A
git -C "$D" -c user.name=repro -c user.email=repro@invalid commit -qm "shortcut S1b"
git -C "$D" diff --numstat HEAD~1 HEAD
python3 "$D/tools/round42-selfdesc-reconcile.py" --repo "$D" --tip HEAD
echo "exit=$?"

# 4. the evidence base the shortcut removed (r41 facts 24 -> 6)
python3 "$D/tools/round41-scorecard-reconcile.py" --repo "$D" --tip HEAD | sed -n 2p
