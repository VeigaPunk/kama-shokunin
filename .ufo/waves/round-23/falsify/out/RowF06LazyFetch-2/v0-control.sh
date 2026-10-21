#!/bin/bash
# Counterfactual to v1-dirty: identical omission, no promisor config keys.
set -eu
ROOT=/tmp/f06-hand/arch
PAIR="$ROOT/v0-control"
BASE_ENV="env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=a@x"
FROZEN=${FROZEN:-/tmp/frozen-r23-f06.py}
CURRENT=${CURRENT:-$(cd "$(dirname "$0")" && pwd)/current-auditor-f228f174.py}
MARKER="$ROOT/v0-lazy-ran"
rm -rf "$PAIR"; mkdir -p "$PAIR"
LANE="$PAIR/lane"; FLEET="$PAIR/fleet"

$BASE_ENV git init -q -b master "$LANE"
c() {
  printf '%s\n' "$2" >> "$LANE/f"
  $BASE_ENV git -C "$LANE" add -- f
  $BASE_ENV GIT_AUTHOR_DATE="@$1 +0000" GIT_COMMITTER_DATE="@$1 +0000" \
    git -C "$LANE" -c commit.gpgsign=false commit -q -m "$2" \
    --author='kama-shokunin <a@x>'
}
c 900 'round-1: omitted'
c 1000 'round-1: work'
LC=$($BASE_ENV git -C "$LANE" rev-parse HEAD)
$BASE_ENV git -C "$LANE" config core.sshCommand "touch $MARKER; false"

$BASE_ENV git init -q -b master "$FLEET"
mkdir -p "$FLEET/.ufo/reports/round-1"
printf '# kama round 1\n\n## Landed changes\n\n- %s\n' "$LC" \
  > "$FLEET/.ufo/reports/round-1/kama.md"
$BASE_ENV git -C "$FLEET" add -- .ufo/reports/round-1/kama.md
$BASE_ENV GIT_AUTHOR_DATE="@2000 +0000" GIT_COMMITTER_DATE="@2000 +0000" \
  git -C "$FLEET" -c commit.gpgsign=false commit -q -m 'round-1: report' \
  --author='fleet <a@x>'

run_arm() {
  NAME=$1; AUD=$2
  rm -f "$MARKER"
  set +e
  ( cd "$PAIR" && $BASE_ENV python3 "$AUD" --lane-repo "$LANE" \
      --fleet-repo "$FLEET" --json --rounds 1 --no-errata \
      > "$PAIR/$NAME.out" 2> "$PAIR/$NAME.err" )
  CODE=$?
  set -e
  echo "ARM $NAME exit=$CODE kinds=$(python3 -c 'import json,sys
try:
    d=json.load(open(sys.argv[1])); print(sorted({x["kind"] for r in d["results"] for x in r["defects"]}))
except Exception: print("unparseable")' "$PAIR/$NAME.out") executed=$([ -e "$MARKER" ] && echo yes || echo no)"
  echo "  stderr: $(tr '\n' ' ' < "$PAIR/$NAME.err" | cut -c1-160)"
}
run_arm frozen "$FROZEN"
run_arm current "$CURRENT"
