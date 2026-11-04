#!/usr/bin/env bash
# Minimal reconstruction of CRT01 F3 fixtures; original scratch was removed.
# Run from any cwd. Prints receipt header, fixture state and counter output.
# Does not modify lane files. Counter exit 1 is the expected repaired result.
set -eu
export PYTHONDONTWRITEBYTECODE=1
L=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/fast/scratch/hyaku/kama-r73/CRT01ClaimCritic-F3Replay
mkdir -p "$S"
trap 'rm -rf -- "$S"' EXIT
printf '# rev=%s\n' "$(git -C "$L" rev-parse master)"
init_repo() {
  git -C "$1" init -q -b master
  test "$(git -C "$1" rev-parse --show-toplevel)" = "$1"
}
mut() {
  local d=$1; shift
  test "$(git -C "$d" rev-parse --show-toplevel)" = "$d"
  git -C "$d" -c user.name=fixture -c user.email=fixture@invalid -c commit.gpgsign=false "$@"
}
commit_all() { mut "$1" add -A; mut "$1" commit -q -m "$2"; }
seed() {
  init_repo "$1"
  mkdir -p "$1/plans"
  printf '# kama round 73 - frozen claims\n' > "$1/plans/round-73-claims.md"
  printf '*.log\n' > "$1/.gitignore"
  commit_all "$1" seed
}
run_counter() {
  printf '# command: python3 %s/tools/round73-round-scope-cases.py --repo %s --round 73 --tip master\n' "$L" "$1"
  local rc=0
  python3 "$L/tools/round73-round-scope-cases.py" --repo "$1" --round 73 --tip master || rc=$?
  printf '# exit=%s expected=1\n' "$rc"
  test "$rc" = 1
}

# Hybrid A5/A6: ignored future-round payload exists only in linked worktree.
D=$(mktemp -d -p "$S")
seed "$D"
WT="$S/linked-worktree"
mut "$D" worktree add -q --detach "$WT"
mkdir -p "$WT/.ufo/waves/round-74"
printf 'ignored only in linked worktree\n' > "$WT/.ufo/waves/round-74/hidden.log"
printf '# hybrid primary plain status (expected empty)\n'
git -C "$D" status --porcelain -uall
printf '# hybrid linked ignored status\n'
git -C "$WT" status --porcelain -uall --ignored -- .ufo/waves
run_counter "$D"

# Nested A7: direct submodule clean under default status; initialized inner
# submodule has untracked content hidden by committed inner ignore=all.
INNER=$(mktemp -d -p "$S")
init_repo "$INNER"
printf 'inner\n' > "$INNER/inner.txt"
commit_all "$INNER" inner
SUB=$(mktemp -d -p "$S")
init_repo "$SUB"
printf 'child\n' > "$SUB/child.txt"
commit_all "$SUB" child
mut "$SUB" -c protocol.file.allow=always submodule add -q "$INNER" inner
mut "$SUB" config -f .gitmodules submodule.inner.ignore all
commit_all "$SUB" 'inner ignore=all'
D=$(mktemp -d -p "$S")
seed "$D"
mut "$D" -c protocol.file.allow=always submodule add -q "$SUB" sub
mut "$D" -c protocol.file.allow=always submodule update -q --init --recursive
commit_all "$D" 'parent records final sub commit'
printf 'nested dirty payload\n' > "$D/sub/inner/untracked-inner.txt"
printf '# nested parent forced status (expected empty)\n'
git -C "$D" status --porcelain -uall --ignore-submodules=none
printf '# nested direct submodule default status (expected empty)\n'
git -C "$D/sub" status --porcelain -uall
printf '# initialized inner own status (expected ?? untracked-inner.txt)\n'
git -C "$D/sub/inner" status --porcelain -uall
run_counter "$D"
