#!/usr/bin/env bash
# OldGitFloor probe (kama round-23 build wave). Measures fail-closed behaviour of the
# global options --no-lazy-fetch and --no-replace-objects on git binaries older than
# 2.44, with env/config alternatives as controls. Scratch only: every fixture is a fresh
# temp repo under $ROOT; GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_NOSYSTEM=1; the
# promisor remote is ssh://example.invalid whose core.sshCommand only touches a marker
# file. Nothing contacts a network host. Each label runs exactly one git binary, and
# PATH resolves `git` to that same binary so lazy-fetch child processes match it.
#
# usage: ROOT=<scratch dir> OUT=<artifact dir> probe-floor.sh LABEL=GIT_BIN[:GIT_EXEC_PATH] ...
set -u
ROOT=${ROOT:?set ROOT to a scratch directory}
OUT=${OUT:?set OUT to an artifact directory}
mkdir -p "$ROOT/bin" "$OUT/cases"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=a GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=a GIT_COMMITTER_EMAIL=a@x
export GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000'
FAKE=abcdefabcdefabcdefabcdefabcdefabcdefabcd   # fabricated, absent object id
ORIG_PATH=$PATH

# wrapper LABEL BIN [EXEC_PATH]: $ROOT/bin/LABEL/git runs exactly that binary
wrapper() {
  local w=$ROOT/bin/$1/git
  if [ -n "${3:-}" ]; then
    printf '#!/bin/sh\nGIT_EXEC_PATH=%s\nexport GIT_EXEC_PATH\nexec %s "$@"\n' "$3" "$2" >"$w"
  else
    printf '#!/bin/sh\nexec %s "$@"\n' "$2" >"$w"
  fi
  chmod +x "$w"
}

# mk_lazy DIR W: armed promisor fixture; marker exists only if a lazy fetch ran the remote command
mk_lazy() {
  "$2" init -q "$1"
  "$2" -C "$1" config core.repositoryformatversion 1
  "$2" -C "$1" config extensions.partialClone origin
  "$2" -C "$1" config remote.origin.url ssh://example.invalid/x.git
  "$2" -C "$1" config remote.origin.promisor true
  "$2" -C "$1" config core.sshCommand "touch $1/marker; false"
  "$2" -C "$1" commit -q --allow-empty -m c1
}

# mk_replace DIR W: X = original commit; refs/replace/X -> Y (different size); prints X
mk_replace() {
  local t x y
  "$2" init -q "$1"
  t=$("$2" -C "$1" mktree </dev/null)
  x=$("$2" -C "$1" commit-tree "$t" -m orig)
  y=$("$2" -C "$1" commit-tree "$t" -m replacement-replacement-longer)
  "$2" -C "$1" replace "$x" "$y"
  printf '%s\n' "$x"
}

# run_case LABEL KIND ID -- ARGV...   (object id is fed on stdin; ARGV runs inside the fixture)
run_case() {
  local label=$1 kind=$2 id=$3 d obj out rc mk=n/a
  shift 3
  [ "$1" = -- ] && shift
  d=$(mktemp -d "$ROOT/$label.$id.XXXX")
  if [ "$kind" = lazy ]; then
    mk_lazy "$d" "$W"
    obj=$FAKE
  else
    obj=$(mk_replace "$d" "$W")
  fi
  out=$(cd "$d" && printf '%s\n' "$obj" | "$@" 2>"$d/stderr"); rc=$?
  cp "$d/stderr" "$OUT/cases/$label.$id.stderr"
  if [ "$kind" = lazy ]; then
    if [ -e "$d/marker" ]; then mk=YES; else mk=no; fi
  fi
  printf '%-10s %-32s exit=%-4s marker=%-4s stdout=[%s] stderr1=[%s]\n' \
    "$label" "$id" "$rc" "$mk" "$(printf '%s' "$out" | tr '\n' '|')" \
    "$(head -n1 "$d/stderr" | cut -c1-110)"
}

for spec in "$@"; do
  label=${spec%%=*}
  rest=${spec#*=}
  bin=${rest%%:*}
  exec_path=
  [ "$rest" != "$bin" ] && exec_path=${rest#*:}
  mkdir -p "$ROOT/bin/$label"
  wrapper "$label" "$bin" "$exec_path"
  W=$ROOT/bin/$label/git
  PATH=$ROOT/bin/$label:$ORIG_PATH
  echo "== $label version: $("$W" --version) | bin=$bin exec_path=${exec_path:-default}"
  ldd "$bin" | grep 'not found' || echo "   shared libs: all resolved"
  run_case "$label" lazy L0-control-noflag -- "$W" cat-file --batch-check
  run_case "$label" lazy L1-global-no-lazy-fetch -- "$W" --no-lazy-fetch cat-file --batch-check
  run_case "$label" lazy L2-subcmd-no-lazy-fetch -- "$W" cat-file --batch-check --no-lazy-fetch
  run_case "$label" lazy L3-env-GIT_NO_LAZY_FETCH -- env GIT_NO_LAZY_FETCH=1 "$W" cat-file --batch-check
  run_case "$label" replace R0-control-noflag -- "$W" cat-file --batch-check
  run_case "$label" replace R1-global-no-replace-objects -- "$W" --no-replace-objects cat-file --batch-check
  run_case "$label" replace R2-env-GIT_NO_REPLACE_OBJECTS -- env GIT_NO_REPLACE_OBJECTS=1 "$W" cat-file --batch-check
  run_case "$label" replace R3-config-useReplaceRefs-false -- "$W" -c core.useReplaceRefs=false cat-file --batch-check
done
