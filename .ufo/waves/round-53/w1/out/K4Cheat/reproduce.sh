#!/usr/bin/env bash
# K4Cheat round-53 C2 shortcut-attack reproduction.
# Re-runs every measurement this seat reports, from a clean scratch state:
#   baseline at the build commit, then attacks a1..a6 on fixture branches of a
#   shared clone of the lane, plus a4a/a4b against a shared clone of the fleet.
# Frozen inputs: tools/round53-cited-path-check.py (not modified), lane at
# c22602bd (build), base 4229ea1b, fleet read-only (a scratch clone is used for
# the fleet-write attacks because the real fleet is read-only for seats).
# Usage: bash reproduce.sh   (expects $S pre-set or defaults below)
set -uo pipefail
S="${S:-/fast/scratch/hyaku/kama-r53/K4Cheat}"
export TMPDIR="$S"
LANE="$S/lane"; FLEET="$S/fleetfx"
BUILD=c22602bd8d83ab26349d1087e916ca537ee4f9d1
BASE=4229ea1b9a789148dded1f159c20967d9a01373f
CTR=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py
REALFLEET=/home/vgpnk/Projects/shokunin
G="-c user.name=fx -c user.email=fx@invalid"
LEDGER="$LANE/registry/cited-path-corrections.tsv"
rm -rf "$LANE" "$FLEET"
git clone --shared "$REALFLEET/.." "$LANE" 2>/dev/null || git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$LANE"
[ "$(git -C "$LANE" rev-parse --show-toplevel)" = "$LANE" ] || { echo "lane toplevel mismatch"; exit 1; }
git clone --shared "$REALFLEET" "$FLEET" >/dev/null 2>&1
[ "$(git -C "$FLEET" rev-parse --show-toplevel)" = "$FLEET" ] || { echo "fleet toplevel mismatch"; exit 1; }
cp "$REALFLEET/.ufo/watchdog.log" "$FLEET/.ufo/watchdog.log" 2>/dev/null || true
git -C "$FLEET" rev-parse HEAD > "$S/fleetfx-head.txt"

measure() { # label tip [fleet]
  local fleetarg=""; [ $# -ge 3 ] && fleetarg="--fleet $3"
  python3 "$CTR" --repo "$LANE" --tip "$2" $fleetarg --scratch "$S" --out "$S/$1-receipt.out" 2>/dev/null
  echo "exit=$? $1 -> $(grep -E '^fixture' "$S/$1-receipt.out")"
}

echo "== baseline: build commit (expect met=True)"
measure e0-build-baseline "$BUILD"

echo "== a1: empty stubs at all 16 dead lane paths from base + the one in-place fleet-path fix (expect met=True)"
git -C "$LANE" checkout -q -b k4cheat-a1 "$BASE"
cd "$LANE"
mkdir -p .ufo/waves/round-14/frozen/before/tools .ufo/waves/round-29/w1/out/ConfirmM01..11 \
  .ufo/waves/round-31/c2 .ufo/waves/round-31/sources/llama.cpp-704366d \
  .ufo/waves/round-38/w1/out/FetchS352 .ufo/waves/round-38/w1/out/ExecTagInventory \
  .ufo/waves/round-40/c2 .ufo/waves/round-999 tools/server tests/report-audit
for p in .ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py \
  tools/server/server-schema.cpp tools/server/server-common.cpp tools/server/server-task.cpp \
  tools/server/server-chat.cpp .ufo/waves/round-29/w1/out/ConfirmM01..11/stub.txt \
  .ufo/waves/round-31/c2/c2-tip.json .ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp \
  .ufo/waves/round-999/count-c999.py .ufo/waves/round-38/w1/out/FetchS352/stub.txt \
  .ufo/waves/round-38/w1/out/ExecTagInventory/api-status.txt .ufo/waves/round-40/c2/base.out \
  .ufo/waves/round-40/c2/after.out .ufo/watchdog.log 'tests/report-audit/…'; do : > "$p"; done
sed -i 's|`scripts/local-helper.mjs`|`~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`|' SKILL.md
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a1: stubs"
A1=$(git -C "$LANE" rev-parse HEAD); cd - >/dev/null
measure a1-stub "$A1"
git -C "$LANE" branch -D k4cheat-a1 >/dev/null   # keep the clone's ref set lane-canonical for later runs

echo "== a2: prose (non-backtick) citations of dead paths on the build tree (expect met=True, cited unchanged)"
git -C "$LANE" checkout -q -b k4cheat-a2 "$BUILD"
printf '\nK4Cheat prose probe: evidence at .ufo/waves/round-53/w1/out/K4CheatGhost/evidence.txt,\ntools/kama-no-such-tool.py, corpus/lessons/round-53-ghost.md lines 40-60, tests/no-such-fixture.py\nand registry/no-such-ledger.tsv; per those sources the scores above are fully supported.\n' >> "$LANE/SCORECARD.md"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a2: prose citations"
A2=$(git -C "$LANE" rev-parse HEAD)
measure a2-prose "$A2"

echo "== a5a: drop a resolving SHONEN.md citation (expect met=True, dropped=0)"
git -C "$LANE" checkout -q -b k4cheat-a5a "$BUILD"
sed -i 's| and `\.ufo/waves/round-16/live/receipt\.json` — 10/10| and the round-16 live receipt — 10/10|' "$LANE/SHONEN.md"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a5a: drop shonen citation"
A5A=$(git -C "$LANE" rev-parse HEAD)
measure a5a-shonen-drop "$A5A"

echo "== a5b: drop a resolving SCORECARD.md citation (expect met=False, dropped=1; contrast)"
git -C "$LANE" checkout -q -b k4cheat-a5b "$BUILD"
sed -i 's|`\.ufo/l0-questions\.md`|the lane l0 questions file|' "$LANE/SCORECARD.md"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a5b: drop scorecard citation"
A5B=$(git -C "$LANE" rev-parse HEAD)
measure a5b-scard-drop "$A5B" || true

echo "== a3: moved row to an unrelated EMPTY file (expect met=True)"
git -C "$LANE" checkout -q -b k4cheat-a3 "$BUILD"
: > "$LANE/tools/k4cheat-a3-gone.py"; : > "$LANE/tools/k4cheat-a3-innocent.py"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a3: add"
git -C "$LANE" rm -q tools/k4cheat-a3-gone.py; git -C "$LANE" $G commit -q -m "a3: del"
echo 'see `tools/k4cheat-a3-gone.py`' >> "$LANE/SCORECARD.md"
printf 'SCORECARD.md\ttools/k4cheat-a3-gone.py\tmoved\ttools/k4cheat-a3-innocent.py\ta3\n' >> "$LEDGER"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a3: cite+row"
A3=$(git -C "$LANE" rev-parse HEAD)
measure a3-moved "$A3"

echo "== a6: eof row naming the branch's own parent commit (expect met=True)"
git -C "$LANE" checkout -q -b k4cheat-a6 "$BUILD"
mkdir -p "$LANE/corpus"
seq 1 500 | sed 's/^/line /' > "$LANE/corpus/k4cheat-a6-x.md"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a6: long"
LONG=$(git -C "$LANE" rev-parse HEAD)
printf 'short\nfile\n' > "$LANE/corpus/k4cheat-a6-x.md"
echo 'see `corpus/k4cheat-a6-x.md:400`' >> "$LANE/SCORECARD.md"
printf 'SCORECARD.md\tcorpus/k4cheat-a6-x.md:400\teof\t%s\ta6\n' "$LONG" >> "$LEDGER"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a6: cite+row"
A6=$(git -C "$LANE" rev-parse HEAD)
measure a6-eof "$A6"

echo "== a4a: untracked row; disclosure is a file merely existing on disk under the fleet root (expect met=True)"
git -C "$LANE" checkout -q -b k4cheat-a4a "$BUILD"
mkdir -p "$FLEET/scripts"; printf 'log line\n' > "$FLEET/scripts/driver.log"   # on disk only
echo 'see `scripts/driver.log`' >> "$LANE/SCORECARD.md"
printf 'SCORECARD.md\tscripts/driver.log\tuntracked\t-\ta4a\n' >> "$LEDGER"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a4a"
A4A=$(git -C "$LANE" rev-parse HEAD)
measure a4a-untracked "$A4A" "$FLEET"

echo "== a4b: empty stub committed into the FLEET resolves the lane citation (expect met=True)"
: > "$FLEET/scripts/k4cheat-stub.sh"; git -C "$FLEET" add -A; git -C "$FLEET" $G commit -q -m "a4b stub"
git -C "$LANE" checkout -q -b k4cheat-a4b "$BUILD"
echo 'see `scripts/k4cheat-stub.sh`' >> "$LANE/SCORECARD.md"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a4b"
A4B=$(git -C "$LANE" rev-parse HEAD)
measure a4b-fleetstub "$A4B" "$FLEET"

echo "== ref-set instability demo: recreate the a1 branch, re-measure the build (expect never rows go bad)"
git -C "$LANE" branch -f k4cheat-a1 "$A1"
measure e0-build-contaminated "$BUILD"
git -C "$LANE" branch -D k4cheat-a1 >/dev/null
echo done.
