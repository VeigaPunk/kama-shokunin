#!/usr/bin/env bash
# case49 fixtures: one scratch repo from lane tip 8640e34c, then named mutations.
set -euo pipefail
S=/fast/scratch/hyaku/kama-r57/R57Item28ScorecardAudit/case49
L=/home/vgpnk/Projects/shokunin/kama-shokunin
FX=$S/fx
AUDIT=$S/calib-count-audit.py

rm -rf "$FX"; mkdir -p "$FX"
git -C "$L" archive --format=tar 8a7f1976 | tar -x -C "$FX"
cd "$FX"
git init -q .
TOP=$(git rev-parse --show-toplevel)
[ "$TOP" = "$FX" ] || { echo "FATAL: toplevel $TOP != $FX"; exit 1; }
git -c user.email=seat@local -c user.name=seat add -A
git -c user.email=seat@local -c user.name=seat commit -qm "case49 base = lane 8a7f1976"
BASE=$(git rev-parse HEAD)
echo "fixture_toplevel=$TOP base=$BASE"

run() {
  echo "--- $1"
  set +e
  python3 "$AUDIT" --repo "$FX" --tip "$2"
  echo "exit=$?"
  set -e
}

run "F1-fixture-base-fresh" "$BASE"

python3 "$S/mutate.py" "$FX" claim+1
git -c user.email=seat@local -c user.name=seat add -A
git -c user.email=seat@local -c user.name=seat commit -qm "mutation claim+1"
run "F2-claim-44-vs-tree-43" HEAD
git reset -q --hard "$BASE"

python3 "$S/mutate.py" "$FX" cmd-noop
git -c user.email=seat@local -c user.name=seat add -A
git -c user.email=seat@local -c user.name=seat commit -qm "mutation cmd-noop"
run "F3-counting-command-emits-no-integer" HEAD
git reset -q --hard "$BASE"

git rm -q corpus/lessons/round-56-verifier-spotcheck.md
git -c user.email=seat@local -c user.name=seat commit -qm "mutation delete one spotcheck blob"
run "F4-one-blob-deleted-tree-42-vs-claim-43" HEAD
git reset -q --hard "$BASE"

run "F5-reset-back-to-base-fresh" HEAD

EMPTY=$S/empty-repo
rm -rf "$EMPTY"; mkdir -p "$EMPTY"
cd "$EMPTY"
git init -q .
[ "$(git rev-parse --show-toplevel)" = "$EMPTY" ] || { echo "FATAL toplevel"; exit 1; }
echo placeholder > placeholder.txt
git -c user.email=seat@local -c user.name=seat add -A
git -c user.email=seat@local -c user.name=seat commit -qm "empty fixture with no SCORECARD"
echo "--- F6-commit-with-no-SCORECARD"
set +e
python3 "$AUDIT" --repo "$EMPTY" --tip HEAD
echo "exit=$?"
