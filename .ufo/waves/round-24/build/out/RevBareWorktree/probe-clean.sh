#!/usr/bin/env bash
# Probe 7: a CLEAN pair (report cites every required lane commit) audited
# through every layout must give exit 0 in all of them. This is the
# no-harm control the r24 candidate must preserve for promisor-marked
# clones that hold every required object locally.
set -u
ROOT=/fast/scratch/hyaku/kama-r24/RevBareWorktree/fixtures2
W=/fast/scratch/hyaku/kama-r24/RevBareWorktree/probe7
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
rm -rf "$W"; mkdir -p "$W"
for v in $(env | sed -n 's/^\(GIT_[A-Za-z_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

commit() { # repo path msg author when
  local repo=$1 path=$2 msg=$3 author=$4 when=$5
  mkdir -p "$(dirname "$repo/$path")"; printf '%s\n' "$msg" >> "$repo/$path"
  git -C "$repo" add "$path"
  GIT_AUTHOR_NAME="$author" GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME="$author" \
  GIT_COMMITTER_EMAIL=a@x GIT_AUTHOR_DATE="@$when +0000" GIT_COMMITTER_DATE="@$when +0000" \
    git -C "$repo" -c commit.gpgsign=false commit -q -m "$msg"
}

git init -q -b master "$W/lane"
commit "$W/lane" f.txt "round-1: work" kama-shokunin 1000
A=$(git -C "$W/lane" rev-parse HEAD)
commit "$W/lane" f.txt "round-1: measure" kama-shokunin 1100
B=$(git -C "$W/lane" rev-parse HEAD)
commit "$W/lane" f.txt "checkpoint(r1) save" kama-shokunin 1150
C=$(git -C "$W/lane" rev-parse HEAD)

git init -q -b master "$W/fleet"
mkdir -p "$W/fleet/.ufo/reports/round-1"
cat > "$W/fleet/.ufo/reports/round-1/kama.md" <<EOF
# round 1 kama report
## Work performed
measured $A
## Landed changes
- \`$A\` work
- \`$B\` measure
- \`$C\` save
EOF
git -C "$W/fleet" add .ufo/reports/round-1/kama.md
GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=kama-shokunin \
GIT_COMMITTER_EMAIL=a@x GIT_AUTHOR_DATE='@1200 +0000' GIT_COMMITTER_DATE='@1200 +0000' \
  git -C "$W/fleet" -c commit.gpgsign=false commit -q -m "round-1: kama report"

git clone -q --bare "$W/lane" "$W/bare-lane"; git clone -q --bare "$W/fleet" "$W/bare-fleet"
git clone -q "$W/lane" "$W/lk-lane"; git clone -q "$W/fleet" "$W/lk-fleet"
git -C "$W/lk-lane" worktree add -q --detach "$W/lk-lane-wt" HEAD
git -C "$W/lk-fleet" worktree add -q --detach "$W/lk-fleet-wt" HEAD

audit() { # label lane fleet
  out=$(python3 "$TOOL" --lane-repo "$2" --fleet-repo "$3" --branch master \
        --lane kama --rounds 1 --no-errata 2>&1); rc=$?
  printf '  %-26s rc=%s  %s\n' "$1" "$rc" "$(printf '%s' "$out" | tail -1 | cut -c1-90)"
}
echo "clean pair (all required commits cited):"
audit "plain"            "$W/lane"          "$W/fleet"
audit "bare"             "$W/bare-lane"     "$W/bare-fleet"
audit "linked worktree"  "$W/lk-lane-wt"    "$W/lk-fleet-wt"
audit "linked main"      "$W/lk-lane"       "$W/lk-fleet"
