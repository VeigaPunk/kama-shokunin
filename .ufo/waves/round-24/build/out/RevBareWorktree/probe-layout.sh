#!/usr/bin/env bash
# Bounded, offline, no-transport fixture probe:
# how git rev-parse resolves the object store and promisor markers in
# (a) a normal worktree repo, (b) a bare repo, (c) a linked worktree,
# (d) each of those marked promisor-like by hand-written local config/markers.
# No network, no file:// transport, no repo-configured program is executed.
set -u
ROOT=/fast/scratch/hyaku/kama-r24/RevBareWorktree/fixtures
rm -rf "$ROOT"; mkdir -p "$ROOT"
for v in $(env | sed -n 's/^\(GIT_[A-Za-z_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
export GIT_AUTHOR_DATE='100000000 +0000' GIT_COMMITTER_DATE='100000000 +0000'

git init -q "$ROOT/base"
cd "$ROOT/base"
echo hello > f.txt
git add f.txt
git commit -q -m 'round-1: base'
BASE=$(git rev-parse HEAD)
echo "base=$BASE"

git clone -q "$ROOT/base" "$ROOT/normal"
git clone -q --bare "$ROOT/base" "$ROOT/bare"
git -C "$ROOT/normal" worktree add -q --detach "$ROOT/linked" HEAD

report() {
  local label=$1 repo=$2
  echo "### $label  ($repo)"
  for q in --git-dir --git-common-dir --is-bare-repository --is-inside-work-tree \
           --show-toplevel --show-prefix --show-object-format --is-shallow-repository; do
    out=$(git -C "$repo" rev-parse "$q" 2>&1 | tr '\n' '|')
    printf '  %-34s %s\n' "$q" "$out"
  done
  for p in objects objects/pack objects/info/alternates info/grafts HEAD; do
    out=$(git -C "$repo" rev-parse --git-path "$p" 2>&1 | tr '\n' '|')
    printf '  %-34s %s\n' "--git-path $p" "$out"
  done
  echo "  -- local-scope config keys:"
  git -C "$repo" config --null --list 2>/dev/null | tr '\0' '\n' | sed 's/^/     /'
  echo "  -- contents of resolved objects/pack:"
  pp=$(git -C "$repo" rev-parse --git-path objects/pack)
  case "$pp" in /*) d="$pp";; *) d="$repo/$pp";; esac
  ls -1 "$d" 2>/dev/null | sed 's/^/     /'
  echo "  -- resolved dir: $d"
  echo
}

report NORMAL "$ROOT/normal"
report BARE "$ROOT/bare"
report LINKED "$ROOT/linked"

# ---- mark promisor-like by hand (no transport, no fetch)
mark_promisor() {
  local repo=$1
  git -C "$repo" config core.repositoryformatversion 1
  git -C "$repo" config extensions.partialClone blob:none
  git -C "$repo" config remote.origin.promisor true
  git -C "$repo" config remote.origin.partialclonefilter blob:none
  local pp d pack
  pp=$(git -C "$repo" rev-parse --git-path objects/pack)
  case "$pp" in /*) d="$pp";; *) d="$repo/$pp";; esac
  for pack in "$d"/*.pack; do
    [ -e "$pack" ] || continue
    : > "${pack%.pack}.promisor"
  done
}
mark_promisor "$ROOT/normal"   # linked worktree shares normal's config + objects
mark_promisor "$ROOT/bare"
report "NORMAL+promisor" "$ROOT/normal"
report "BARE+promisor" "$ROOT/bare"
report "LINKED+promisor(shared cfg)" "$ROOT/linked"

echo "### worktree metadata"
ls -1 "$ROOT/normal/.git/worktrees/linked/" 2>/dev/null | sed 's/^/  /'
echo "  commondir: $(cat "$ROOT/normal/.git/worktrees/linked/commondir" 2>/dev/null)"
echo "  gitdir:    $(cat "$ROOT/normal/.git/worktrees/linked/gitdir" 2>/dev/null)"
echo "### promisor marker files"
find "$ROOT" -name '*.promisor' | sed 's/^/  /'
