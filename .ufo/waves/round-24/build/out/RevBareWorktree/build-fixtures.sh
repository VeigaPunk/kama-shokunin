#!/usr/bin/env bash
# Bounded offline fixture: a kama lane repo + a fleet repo holding one
# round-1 report, replicated in several repository layouts:
#   plain worktree / bare / linked worktree, each with and without
#   promisor markers (hand-written local config + .promisor pack marker).
# No network transport, no fetch, no repo-configured program.
set -eu
ROOT=/fast/scratch/hyaku/kama-r24/RevBareWorktree/fixtures2
rm -rf "$ROOT"; mkdir -p "$ROOT/src"
for v in $(env | sed -n 's/^\(GIT_[A-Za-z_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

commit() { # repo path msg author when
  local repo=$1 path=$2 msg=$3 author=$4 when=$5
  mkdir -p "$(dirname "$repo/$path")"
  printf '%s\n' "$msg" >> "$repo/$path"
  git -C "$repo" add "$path"
  GIT_AUTHOR_NAME="$author" GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME="$author" \
  GIT_COMMITTER_EMAIL=a@x GIT_AUTHOR_DATE="@$when +0000" \
  GIT_COMMITTER_DATE="@$when +0000" \
    git -C "$repo" -c commit.gpgsign=false commit -q -m "$msg"
}

# ---- lane
git init -q -b master "$ROOT/src/lane"
commit "$ROOT/src/lane" f.txt "round-1: work"   kama-shokunin 1000
A=$(git -C "$ROOT/src/lane" rev-parse HEAD)
commit "$ROOT/src/lane" f.txt "round-1: measure" kama-shokunin 1100
B=$(git -C "$ROOT/src/lane" rev-parse HEAD)
commit "$ROOT/src/lane" f.txt "checkpoint(r1) save" kama-shokunin 1150
C=$(git -C "$ROOT/src/lane" rev-parse HEAD)
commit "$ROOT/src/lane" f.txt "round-1: late advice" kama-shokunin 1300
LATE=$(git -C "$ROOT/src/lane" rev-parse HEAD)

# ---- fleet with the round-1 report (committed at author time 1200 = cutoff)
git init -q -b master "$ROOT/src/fleet"
mkdir -p "$ROOT/src/fleet/.ufo/reports/round-1"
cat > "$ROOT/src/fleet/.ufo/reports/round-1/kama.md" <<EOF
# round 1 kama report
## Work performed
measured $A
## Landed changes
- \`${A:0:9}\` work
- \`$B\` measure
EOF
git -C "$ROOT/src/fleet" add .ufo/reports/round-1/kama.md
GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=kama-shokunin \
GIT_COMMITTER_EMAIL=a@x GIT_AUTHOR_DATE='@1200 +0000' GIT_COMMITTER_DATE='@1200 +0000' \
  git -C "$ROOT/src/fleet" -c commit.gpgsign=false commit -q -m "round-1: kama report"

# expected: C (checkpoint(r1) save, author 1150 <= cutoff 1200) is NOT cited
# -> landed-omitted; LATE (1300 > cutoff) is post_report.
cat > "$ROOT/expected.txt" <<EOF
A=$A
B=$B
C=$C
LATE=$LATE
EOF
cat "$ROOT/expected.txt"

# ---- layout replicas
mk_layout() { # name
  local name=$1 dir="$ROOT/$1"
  mkdir -p "$dir"
  case "$name" in
    plain) cp -a "$ROOT/src/lane" "$dir/lane"; cp -a "$ROOT/src/fleet" "$dir/fleet";;
    bare)
      git clone -q --bare "$ROOT/src/lane" "$dir/lane"
      git clone -q --bare "$ROOT/src/fleet" "$dir/fleet";;
    linked)
      git clone -q "$ROOT/src/lane" "$dir/lane"; git clone -q "$ROOT/src/fleet" "$dir/fleet"
      git -C "$dir/lane" worktree add -q --detach "$dir/lane-wt" HEAD
      git -C "$dir/fleet" worktree add -q --detach "$dir/fleet-wt" HEAD;;
  esac
}
for l in plain bare linked; do mk_layout "$l"; done

# ---- promisor-marked replicas: copy the plain layout, then hand-mark it
mark_promisor() { # repo
  local repo=$1 pp d pack
  git -C "$repo" config core.repositoryformatversion 1
  git -C "$repo" config extensions.partialClone blob:none
  git -C "$repo" config remote.origin.promisor true
  git -C "$repo" config remote.origin.partialclonefilter blob:none
  git -C "$repo" repack -a -q -d 2>/dev/null || true
  pp=$(git -C "$repo" rev-parse --git-path objects/pack)
  case "$pp" in /*) d="$pp";; *) d="$repo/$pp";; esac
  for pack in "$d"/*.pack; do
    [ -e "$pack" ] || continue
    : > "${pack%.pack}.promisor"
  done
  echo "    marked $repo -> markers: $(ls "$d"/*.promisor 2>/dev/null | wc -l)"
}
for l in promisor promisor-bare promisor-linked; do
  cp -a "$ROOT/plain" "$ROOT/$l"
done
mark_promisor "$ROOT/promisor/lane"; mark_promisor "$ROOT/promisor/fleet"
rm -rf "$ROOT/promisor-bare" "$ROOT/promisor-linked"
mk_layout bare-tmp >/dev/null 2>&1 || true
mkdir -p "$ROOT/promisor-bare" "$ROOT/promisor-linked"
git clone -q --bare "$ROOT/src/lane" "$ROOT/promisor-bare/lane"
git clone -q --bare "$ROOT/src/fleet" "$ROOT/promisor-bare/fleet"
git clone -q "$ROOT/src/lane" "$ROOT/promisor-linked/lane"
git clone -q "$ROOT/src/fleet" "$ROOT/promisor-linked/fleet"
git -C "$ROOT/promisor-linked/lane" worktree add -q --detach "$ROOT/promisor-linked/lane-wt" HEAD
git -C "$ROOT/promisor-linked/fleet" worktree add -q --detach "$ROOT/promisor-linked/fleet-wt" HEAD
mark_promisor "$ROOT/promisor-bare/lane"; mark_promisor "$ROOT/promisor-bare/fleet"
mark_promisor "$ROOT/promisor-linked/lane"; mark_promisor "$ROOT/promisor-linked/fleet"

# ---- record the layout facts each variant presents to git
for d in plain bare linked promisor promisor-bare promisor-linked; do
  for side in lane fleet; do
    repo="$ROOT/$d/$side"
    [ -d "$repo" ] || continue
    wt="$repo"
    case "$d" in
      linked|promisor-linked) wt="$ROOT/$d/$side-wt";;
    esac
    echo "$d/$side"
    echo "  bare=$(git -C "$wt" rev-parse --is-bare-repository)"
    echo "  prefix=[$(git -C "$wt" rev-parse --show-prefix)]"
    echo "  common=$(git -C "$wt" rev-parse --git-common-dir)"
    echo "  packpath=$(git -C "$wt" rev-parse --git-path objects/pack)"
    echo "  promisor_cfg=[$(git -C "$wt" config --get-regexp 'promisor|partialclone' | tr '\n' ' ')]"
  done
done
