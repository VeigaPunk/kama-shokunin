#!/bin/bash
# Same-channel probes, round 2:
#  H1: promisor config inside an included file (does --list see it? does git fetch?)
#  H2: includeIf gitdir variant
#  V5: real pack + .promisor marker with remote promisor=false
#  V6: .promisor marker alone (no pack) -> git promisor or not?
set -eu
ROOT=/tmp/f06-hand
BASE_ENV="env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=a@x"
FAKE2=abcdefabcdefabcdefabcdefabcdefabcdefabcd
MARKER="$ROOT/probe2-ran"

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
  timeout 10 $BASE_ENV git -C "$D" cat-file -e "$FAKE2" >/dev/null 2>"$ROOT/probe2-$(basename "$D").err"
  RC=$?
  set -e
  echo "  probe $(basename "$D"): rc=$RC marker=$([ -e "$MARKER" ] && echo PRESENT || echo absent) stderr=$(tr '\n' ' ' < "$ROOT/probe2-$(basename "$D").err" | cut -c1-100)"
}

# H1 include file with promisor keys
mk "$ROOT/h1"
cat > "$ROOT/prom.cfg" <<EOF
[remote "origin"]
	url = ssh://example.invalid/x.git
	promisor = true
EOF
$BASE_ENV git -C "$ROOT/h1" config include.path "$ROOT/prom.cfg"
echo "H1 config listing:"
$BASE_ENV git -C "$ROOT/h1" config --list --name-only | sed 's/^/  /'
probe "$ROOT/h1"

# H2 includeIf gitdir
mk "$ROOT/h2"
cat > "$ROOT/prom2.cfg" <<EOF
[remote "origin"]
	url = ssh://example.invalid/x.git
	promisor = true
EOF
$BASE_ENV git -C "$ROOT/h2" config includeIf.gitdir:"$ROOT/h2/.git/".path "$ROOT/prom2.cfg"
echo "H2 config listing:"
$BASE_ENV git -C "$ROOT/h2" config --list --name-only | sed 's/^/  /'
probe "$ROOT/h2"

# V5 real pack with .promisor marker, remote promisor=false
mk "$ROOT/v5"
$BASE_ENV git -C "$ROOT/v5" config remote.origin.url ssh://example.invalid/x.git
$BASE_ENV git -C "$ROOT/v5" config remote.origin.promisor false
$BASE_ENV git -C "$ROOT/v5" repack -adq 2>/dev/null || true
PACK=$($BASE_ENV git -C "$ROOT/v5" rev-parse --git-path objects/pack)
echo "V5 pack dir: $PACK"
ls "$PACK" | sed 's/^/  /'
for p in "$PACK"/pack-*.pack; do : > "${p%.pack}.promisor"; done
echo "V5 after marker:"; ls "$PACK" | sed 's/^/  /'
echo "V5 config:"; $BASE_ENV git -C "$ROOT/v5" config --list --name-only | sed 's/^/  /'
probe "$ROOT/v5"

# V6 lone .promisor marker, no pack, no promisor config
mk "$ROOT/v6"
PACK6=$($BASE_ENV git -C "$ROOT/v6" rev-parse --git-path objects/pack)
: > "$PACK6/pack-deadbeef.promisor"
echo "V6 config:"; $BASE_ENV git -C "$ROOT/v6" config --list --name-only | sed 's/^/  /'
probe "$ROOT/v6"
