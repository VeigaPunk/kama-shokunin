#!/usr/bin/env bash
# Score one forged tool against the UNMUTATED round-64 C1 counter.
#   score.sh <forged-tool.py> <label> [helper-script]
# The forged tool replaces tools/kama-completion-live.py in the scratch
# clone; the counter itself is never modified.
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT30AdaptiveForgeProc
O=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-64/f/out/MT30AdaptiveForgeProc
D=$S/clone
FORGE=$1
LABEL=$2
HELPER=${3:-}

test "$(git -C "$D" rev-parse --show-toplevel)" = "$D" || { echo "WRONG REPO"; exit 9; }

# restore the pristine tool, then install the forgery
git -C "$D" checkout -q 23b3fdb1a925129a9961cf551f6d40bf251602cb -- tools/kama-completion-live.py
cp "$FORGE" "$D/tools/kama-completion-live.py"
# record the diff (base -> forgery) in the out dir
git -C "$D" show 23b3fdb1a925129a9961cf551f6d40bf251602cb:tools/kama-completion-live.py > "$S/base-tool.py"
git -C "$D" diff --no-index -- "$S/base-tool.py" "$D/tools/kama-completion-live.py" > "$O/diff-$LABEL.patch" 2>/dev/null

git -C "$D" add -A
git -C "$D" -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "wip $LABEL"
T=$(git -C "$D" rev-parse HEAD)
W=$S/work-$LABEL
rm -rf "$W"

if [ -n "$HELPER" ]; then
  rm -f "$S/helper.sock"
  nohup python3 "$HELPER" "$S/helper.sock" > "$S/helper-$LABEL.log" 2>&1 &
  HPID=$!
  for _ in $(seq 1 50); do
    grep -q helper-ready "$S/helper-$LABEL.log" 2>/dev/null && break
    sleep 0.1
  done
  echo "helper started pid=$HPID"
fi

cd "$D" && python3 tools/round64-c1-counter.py --repo "$D" --tip "$T" --work "$W" \
  > "$S/out-$LABEL.txt" 2> "$S/err-$LABEL.txt"
RC=$?
echo "exit=$RC"
cat "$S/out-$LABEL.txt"
echo "--- stderr:"
head -c 2000 "$S/err-$LABEL.txt"
if [ -n "$HELPER" ]; then
  kill "$HPID" 2>/dev/null
  echo "--- helper log:"; cat "$S/helper-$LABEL.log"
fi
