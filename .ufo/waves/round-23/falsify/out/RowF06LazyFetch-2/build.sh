#!/bin/bash
# Hand-built replica of repo-state-grid F06-lazy-fetch-command, independent of
# the grid module. Mirrors tests/report-audit/repo-state-grid.py:271-286.
set -eu
ROOT=/tmp/f06-hand/arch
rm -rf "$ROOT"
mkdir -p "$ROOT"
BASE_ENV="env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=a@x"
FROZEN=${FROZEN:-/tmp/frozen-r23-f06.py}
CURRENT=${CURRENT:-$(cd "$(dirname "$0")" && pwd)/current-auditor-f228f174.py}
LANE="$ROOT/lane"
FLEET="$ROOT/fleet"
FAKE2=abcdefabcdefabcdefabcdefabcdefabcdefabcd

$BASE_ENV git init -q -b master "$LANE"
printf 'round-1: work\n' >> "$LANE/f"
$BASE_ENV git -C "$LANE" add -- f
$BASE_ENV GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000" \
  git -C "$LANE" -c commit.gpgsign=false commit -q -m 'round-1: work' \
  --author='kama-shokunin <a@x>'
LC=$($BASE_ENV git -C "$LANE" rev-parse HEAD)
echo "lane lc=$LC"

$BASE_ENV git init -q -b master "$FLEET"
mkdir -p "$FLEET/.ufo/reports/round-1"
printf '# kama round 1\n\n## Landed changes\n\n- %s\n- %s\n' "$LC" "$FAKE2" \
  > "$FLEET/.ufo/reports/round-1/kama.md"
$BASE_ENV git -C "$FLEET" add -- .ufo/reports/round-1/kama.md
$BASE_ENV GIT_AUTHOR_DATE="@2000 +0000" GIT_COMMITTER_DATE="@2000 +0000" \
  git -C "$FLEET" -c commit.gpgsign=false commit -q -m 'round-1: report' \
  --author='fleet <a@x>'
echo "fleet tip=$($BASE_ENV git -C "$FLEET" rev-parse HEAD)"

MARKER="$ROOT/lazy-fetch-ran"
$BASE_ENV git -C "$LANE" config extensions.partialClone origin
$BASE_ENV git -C "$LANE" config remote.origin.url ssh://example.invalid/x.git
$BASE_ENV git -C "$LANE" config remote.origin.promisor true
$BASE_ENV git -C "$LANE" config core.sshCommand "touch $MARKER; false"

rm -f "$MARKER"
set +e
$BASE_ENV git -C "$LANE" cat-file -e "$FAKE2" >/dev/null 2>"$ROOT/premise.err"
RC=$?
set -e
echo "premise cat-file rc=$RC marker=$([ -e "$MARKER" ] && echo present || echo absent)"
echo "premise stderr: $(tr '\n' ' ' < "$ROOT/premise.err" | cut -c1-200)"
[ "$RC" -ne 0 ] || { echo "PREMISE FAILED: missing object resolved"; exit 2; }
[ -e "$MARKER" ] || { echo "PREMISE FAILED: sshCommand did not run"; exit 2; }
rm -f "$MARKER"
echo "--- lane config after premise fetch"
$BASE_ENV git -C "$LANE" config --list --name-only

run_arm() {
  NAME=$1
  AUD=$2
  rm -f "$MARKER"
  set +e
  ( cd "$ROOT" && $BASE_ENV python3 "$AUD" --lane-repo "$LANE" \
      --fleet-repo "$FLEET" --json --rounds 1 --no-errata \
      > "$ROOT/$NAME.out" 2> "$ROOT/$NAME.err" )
  CODE=$?
  set -e
  EXEC=no
  [ -e "$MARKER" ] && EXEC=yes
  TB=no
  grep -q 'Traceback (most recent call last)' "$ROOT/$NAME.err" && TB=yes
  echo "ARM $NAME exit=$CODE executed=$EXEC traceback=$TB"
  echo "  kinds: $(python3 -c 'import json,sys
try:
    d=json.load(open(sys.argv[1])); print(sorted({x["kind"] for r in d["results"] for x in r["defects"]}))
except Exception: print("unparseable")' "$ROOT/$NAME.out")"
  echo "  stderr: $(tr '\n' ' ' < "$ROOT/$NAME.err" | cut -c1-200)"
}
run_arm frozen "$FROZEN"
run_arm current "$CURRENT"
