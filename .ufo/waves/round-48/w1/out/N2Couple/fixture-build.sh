#!/bin/sh
# Round-48 separability fixtures (N2Couple). Evidence: exact commands used.
# Lane read-only; all mutations happen in scratch clones.
set -eu
S=/fast/scratch/hyaku/kama-r48/N2Couple
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
FREEZE=12284ba39fb1b46b43d43ee82423bebe08c700dc
BUILD=380bcdff9c8af06997c482f6eb03db926a794a2b
mkdir -p "$S"
rm -rf "$S/fdA" "$S/fdB"
git clone -q --shared "$LANE" "$S/fdA"
git clone -q --shared "$LANE" "$S/fdB"
test "$(git -C "$S/fdA" rev-parse --show-toplevel)" = "$S/fdA"
test "$(git -C "$S/fdB" rev-parse --show-toplevel)" = "$S/fdB"
# C1-only fixture
git -C "$S/fdA" checkout -q "$FREEZE"
git -C "$S/fdA" checkout -q "$BUILD" -- tools/append-only-audit.py registry/append-only-contract.tsv SCORECARD.md
GIT_AUTHOR_NAME=r48-n2cpl GIT_AUTHOR_EMAIL=n2cpl@fixture.invalid \
GIT_COMMITTER_NAME=r48-n2cpl GIT_COMMITTER_EMAIL=n2cpl@fixture.invalid \
git -C "$S/fdA" commit -q -m "C1-only fixture: freeze 12284ba39 + C1 build paths from 380bcdff"
# C2-only fixture
git -C "$S/fdB" checkout -q "$FREEZE"
git -C "$S/fdB" checkout -q "$BUILD" -- tools/kama-llamacpp-live.py tools/kama-live-replay.py corpus/SOURCES.md .ufo/waves/round-48/c2/live
GIT_AUTHOR_NAME=r48-n2cpl GIT_AUTHOR_EMAIL=n2cpl@fixture.invalid \
GIT_COMMITTER_NAME=r48-n2cpl GIT_COMMITTER_EMAIL=n2cpl@fixture.invalid \
git -C "$S/fdB" commit -q -m "C2-only fixture: freeze 12284ba39 + C2 build paths from 380bcdff"
echo "fdA tip: $(git -C "$S/fdA" rev-parse HEAD)"
echo "fdB tip: $(git -C "$S/fdB" rev-parse HEAD)"
# Counter runs (frozen counters from the lane)
# C1 on fdA:  python3 "$LANE/tools/round48-append-audit-v3-check.py" --repo "$S/fdA" --tip "$(git -C "$S/fdA" rev-parse HEAD)" --scratch "$S" --out "$OUT/sep-c1-only.c1.out"
# C2 on fdB:  python3 "$LANE/tools/round48-live-replay-v5-audit.py" --repo "$S/fdB" --tip "$(git -C "$S/fdB" rev-parse HEAD)" --scratch "$S" --out "$OUT/sep-c2-only.c2.out"
# Cross/controls: same counters with swapped fixtures, and --tip $FREEZE.
