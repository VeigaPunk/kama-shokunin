#!/bin/bash
# Probe: does git lazy-fetch with extensions.partialClone set to an empty
# value (no promisor remote), or with a valueless promisor key?
set -eu
ROOT=/tmp/f06-hand
BASE_ENV="env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=a@x"
FAKE2=abcdefabcdefabcdefabcdefabcdefabcdefabcd
MARKER="$ROOT/probe4-ran"
mk() {
  D=$1
  rm -rf "$D"; $BASE_ENV git init -q -b master "$D"
  printf 'round-1: work\n' >> "$D/f"
  $BASE_ENV git -C "$D" add -- f
  $BASE_ENV GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000" \
    git -C "$D" -c commit.gpgsign=false commit -q -m 'round-1: work' \
    --author='kama-shokunin <a@x>'
  $BASE_ENV git -C "$D" config core.sshCommand "touch $MARKER; false"
}
probe() {
  D=$1
  rm -f "$MARKER"
  set +e
  timeout 10 $BASE_ENV git -C "$D" cat-file -e "$FAKE2" >/dev/null 2>&1
  RC=$?
  set -e
  echo "  probe $(basename "$D"): rc=$RC marker=$([ -e "$MARKER" ] && echo PRESENT || echo absent)"
}

mk "$ROOT/p1"
$BASE_ENV git -C "$ROOT/p1" config extensions.partialClone ""
$BASE_ENV git -C "$ROOT/p1" config remote.origin.url ssh://example.invalid/x.git
echo "P1 (empty partialClone):"; $BASE_ENV git -C "$ROOT/p1" config --list --name-only | sed 's/^/  /'
probe "$ROOT/p1"

mk "$ROOT/p2"
$BASE_ENV git -C "$ROOT/p2" config remote.origin.url ssh://example.invalid/x.git
printf '\tpromisor\n' >> "$ROOT/p2/.git/config"
echo "P2 (valueless promisor key):"; $BASE_ENV git -C "$ROOT/p2" config --list --name-only | sed 's/^/  /'
echo "  bool: $($BASE_ENV git -C "$ROOT/p2" config --type=bool --get remote.origin.promisor || echo ERR)"
probe "$ROOT/p2"
