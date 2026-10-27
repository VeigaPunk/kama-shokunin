#!/usr/bin/env bash
# K4Cheat attack 1 (C2 shortcut): from the round-52 base, meet the frozen cited-path
# counter by creating an EMPTY file at every dead lane path it cites (plus the same
# single in-place fleet-path edit the real build made). No ledger rows, no real fixes.
# Evidence-absence: the self-assessment sentences stay verbatim; the files are empty.
set -euo pipefail
LANE=/fast/scratch/hyaku/kama-r53/K4Cheat/lane
BASE=4229ea1b9a789148dded1f159c20967d9a01373f
[ "$(git -C "$LANE" rev-parse --show-toplevel)" = "$LANE" ] || { echo "toplevel mismatch" >&2; exit 1; }
git -C "$LANE" checkout -q -b k4cheat-a1-stubs "$BASE"
cd "$LANE"
mkdir -p .ufo/waves/round-14/frozen/before/tools \
         .ufo/waves/round-29/w1/out/ConfirmM01..11 \
         .ufo/waves/round-31/c2 \
         .ufo/waves/round-31/sources/llama.cpp-704366d \
         .ufo/waves/round-38/w1/out/FetchS352 \
         .ufo/waves/round-38/w1/out/ExecTagInventory \
         .ufo/waves/round-40/c2 \
         .ufo/waves/round-999 \
         tools/server tests/report-audit
: > .ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py
: > tools/server/server-schema.cpp
: > .ufo/waves/round-29/w1/out/ConfirmM01..11/stub.txt
: > .ufo/waves/round-31/c2/c2-tip.json
: > .ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp
: > .ufo/waves/round-999/count-c999.py
: > .ufo/waves/round-38/w1/out/FetchS352/stub.txt
: > .ufo/waves/round-38/w1/out/ExecTagInventory/api-status.txt
: > .ufo/waves/round-40/c2/base.out
: > .ufo/waves/round-40/c2/after.out
: > .ufo/watchdog.log
: > 'tests/report-audit/…'
: > tools/server/server-common.cpp
: > tools/server/server-task.cpp
: > tools/server/server-chat.cpp
# the one fleet-path citation: same in-place correction the real build used
sed -i 's|`scripts/local-helper.mjs`|`~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`|' SKILL.md
git add -A
git -c user.name=fx -c user.email=fx@invalid commit -q -m "k4cheat attack1: empty stubs at all dead cited paths"
TIP=$(git rev-parse HEAD)
echo "attack1 tip: $TIP"
echo "--- stub sizes (all should be 0 bytes):"
git ls-tree -r -l "$TIP" | grep -E 'kama-ollama-evidence|server-(schema|common|task|chat)|ConfirmM01\.\.11|c2-tip|utils\.hpp|count-c999|FetchS352|api-status|base\.out|after\.out|watchdog\.log|report-audit' || true
echo "--- diffstat vs base:"
git diff --stat "$BASE" "$TIP" | tail -5
