#!/bin/bash
# Near-variant probes for the F06 channel: does git actually treat these
# repo-local configs as promisor (i.e. would a missing-object read attempt a
# fetch and run core.sshCommand)? Decision is empirical, not assumed.
set -eu
ROOT=/tmp/f06-hand
BASE_ENV="env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=a@x"
FAKE2=abcdefabcdefabcdefabcdefabcdefabcdefabcd
MARKER="$ROOT/probe-ran"

mk() {
  D=$1
  rm -rf "$D"; $BASE_ENV git init -q -b master "$D"
  printf 'round-1: work\n' >> "$D/f"
  $BASE_ENV git -C "$D" add -- f
  $BASE_ENV GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000" \
    git -C "$D" -c commit.gpgsign=false commit -q -m 'round-1: work' \
    --author='kama-shokunin <a@x>'
  $BASE_ENV git -C "$D" config remote.origin.url ssh://example.invalid/x.git
  $BASE_ENV git -C "$D" config core.sshCommand "touch $MARKER; false"
}
probe() {
  D=$1
  rm -f "$MARKER"
  set +e
  $BASE_ENV git -C "$D" cat-file -e "$FAKE2" >/dev/null 2>"$ROOT/probe-$(basename "$D").err"
  RC=$?
  set -e
  echo "probe $(basename "$D"): rc=$RC marker=$([ -e "$MARKER" ] && echo PRESENT || echo absent) stderr=$(tr '\n' ' ' < "$ROOT/probe-$(basename "$D").err" | cut -c1-120)"
}

# V1: promisor explicitly disabled, no extensions.partialClone, no pack
mk "$ROOT/v1"
$BASE_ENV git -C "$ROOT/v1" config remote.origin.promisor false
echo "V1 config:"; $BASE_ENV git -C "$ROOT/v1" config --list --name-only
probe "$ROOT/v1"
echo "V1 config uses bool: $($BASE_ENV git -C "$ROOT/v1" config --type=bool --get remote.origin.promisor)"

# V2: promisor=true only (no extensions.partialClone, no filter key)
mk "$ROOT/v2"
$BASE_ENV git -C "$ROOT/v2" config remote.origin.promisor true
echo "V2 config:"; $BASE_ENV git -C "$ROOT/v2" config --list --name-only
probe "$ROOT/v2"

# V3: extensions.partialClone only, promisor=false explicit
mk "$ROOT/v3"
$BASE_ENV git -C "$ROOT/v3" config extensions.partialClone origin
$BASE_ENV git -C "$ROOT/v3" config remote.origin.promisor false
echo "V3 config:"; $BASE_ENV git -C "$ROOT/v3" config --list --name-only
probe "$ROOT/v3"

# V4: promisor=false value but with promisor pack marker present
mk "$ROOT/v4"
$BASE_ENV git -C "$ROOT/v4" config remote.origin.promisor false
mkdir -p "$ROOT/v4/.git/objects/pack"
: > "$ROOT/v4/.git/objects/pack/pack-deadbeef.promisor"
probe "$ROOT/v4"
