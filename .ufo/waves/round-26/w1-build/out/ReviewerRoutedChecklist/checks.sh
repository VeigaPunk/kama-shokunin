#!/usr/bin/env bash
# Routed-defect acceptance checks (round-25 spot-check defects 1-8, round-24 items 1-5).
# Usage: checks.sh [REV] [SCRATCH]
#   REV      lane revision to check (default: HEAD of the lane)
#   SCRATCH  scratch dir for the D5 git-archive extract
#            (default /fast/scratch/hyaku/kama-r26/ReviewerRoutedChecklist/checks)
# Reads committed bytes with `git show REV:path`; D1 and D7 read live state.
# Writes only under SCRATCH. Starts no server.
set -u
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
L=/home/vgpnk/Projects/shokunin/kama-shokunin
REV=$(git -C "$L" rev-parse "${1:-HEAD}")
SCRATCH=${2:-/fast/scratch/hyaku/kama-r26/ReviewerRoutedChecklist/checks}
BASE=1560e4d83f42b04f40336357de6f9637eafa0f4b
R24FINAL=5cb46efcfeb55382ce44fb23f247300e5b1a2abb
g() { git -C "$L" "$@"; }
run() { local id=$1; shift; echo "### $id"; echo "\$ $*"; bash -c "$*"; echo "exit=$?"; echo; }
echo "REV=$REV"; echo

run D1a "git -C $L status --porcelain -- .ufo/waves/round-25"
run D1b "git -C $L ls-files .ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/replication-run3/raw | wc -l"

run D2a "git -C $L diff --numstat $BASE $REV -- corpus/QUALITY.md"
run D2b "git -C $L diff $BASE $REV -- corpus/QUALITY.md | grep -E '^\+' | grep -v '^+++' | grep -c -i 'landed tip'"
run D2c "git -C $L diff --numstat $BASE $REV -- corpus/lessons/round-25.md SKILL.md"
run D2d "git -C $L diff $BASE $REV -- corpus/lessons/round-25.md SKILL.md | grep -E '^\+' | grep -v '^+++' | grep -c 'M17'"
run D2e "git -C $L show $REV:SKILL.md | grep -n -i -E 'M17[^|]*surviv'"

run D3a "git -C $L show $REV:corpus/SOURCES.md | grep -oE '\| supersedes S1(06|09|13) —' | sort | uniq -c"
run D3b "git -C $L diff $BASE $REV -- corpus/SOURCES.md | grep -cE '^-\|[[:space:]]*S[0-9]{3}[[:space:]]*\|'"
run D3c "cd /home/vgpnk/Projects/shokunin && bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama | tail -1"

run D4a "git -C $L show $REV:corpus/knowledge/context-capacity.md | grep -n 'the only trace'"
run D4b "git -C $L show $REV:corpus/knowledge/context-capacity.md | grep -n -c 'exceeds the training context'"
run D4c "git -C $L show $REV:corpus/knowledge/context-capacity.md | grep -n -E '1024 cells|held 1024'"
run D4d "git -C $L show $REV:.ufo/waves/round-25/final/raw/K5.server.log | sed -n 1083p"

rm -rf "$SCRATCH" && mkdir -p "$SCRATCH/tip"
g archive "$REV" | tar -x -C "$SCRATCH/tip"
cp -a "$SCRATCH/tip" "$SCRATCH/mut"
printf 'TAMPERED\n' >> "$SCRATCH/mut/.ufo/waves/round-25/final/raw/K1.server.log"
rm "$SCRATCH/mut/.ufo/waves/round-25/final/raw/L3.server.log"
run D5a "cd $SCRATCH/tip && timeout 60 python3 .ufo/waves/round-25/count-c2.py"
run D5b "cd $SCRATCH/mut && timeout 60 python3 .ufo/waves/round-25/count-c2.py"
run D5c "git -C $L show $REV:.ufo/waves/round-25/count-c2.py | grep -n -i -E 'hashlib|raw hash|not check'"

run D6a "git -C $L diff --numstat $BASE $REV -- SCORECARD.md"
run D6b "git -C $L show $REV:SCORECARD.md | sed -n '1306,1310p'"
run D6c "git -C $L diff $BASE $REV -- SCORECARD.md | grep -E '^\+' | grep -v '^+++' | grep -n -i -E 'discernment|quality' | grep -i unchanged"

run D7a "grep -n 'kama kama-r26' \$HOME/.local/state/shokunin-hyaku/wave-slots"
run D7b "python3 -c \"import json;print(len(json.load(open('$L/.ufo/waves/round-26/w1-build/spec.json'))['items']))\""
run D7c "ls $L/.ufo/waves/round-26/w1-build/advice | grep -c '\.md\$'"

run D8a "git -C $L show $REV:.ufo/waves/round-26/preregistration.json | python3 -c \"import json,sys;d=json.load(sys.stdin);print(d['claims']['C1']['axis'])\""
run D8b "git -C $L show $REV:SCORECARD.md | grep -n 'Other scores held'"

run R24-1 "git -C $L diff --stat $R24FINAL $REV -- .ufo/waves/round-24 corpus/lessons/round-24.md"
run R24-2 "git -C $L show $REV:SKILL.md | grep -n -o 'PM08 is a manual review-only note, unexecuted, uncredited'"
run R24-3 "git -C $L show $REV:corpus/lessons/round-25.md | grep -n 'append lineage stays unresolved'"
run R24-5 "git --version"
