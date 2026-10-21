#!/usr/bin/env bash
# Probes int(%ct) reachability and numeric-token handling for tools/report-landing-audit.py.
# Usage: timestamp-probe.sh FLEET_REPO AUDIT_PY
# Read-only on FLEET_REPO; fixtures live in a mktemp dir removed on exit.
set -u
FLEET=${1:?usage: timestamp-probe.sh FLEET_REPO AUDIT_PY}
AUD=${2:?usage: timestamp-probe.sh FLEET_REPO AUDIT_PY}
PY=${PY:-/usr/bin/python3}
W=$(mktemp -d /tmp/aud-ts-probe.XXXXXX)
trap 'rm -rf "$W"' EXIT
export GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin GIT_AUTHOR_EMAIL=x@x GIT_COMMITTER_EMAIL=x@x
i=0
OK_REPO=""
for when in "@-1 +0000" "@99999999999999999999 +0000" "@1700000000 +9999" "@0 +0000"; do
  i=$((i+1))
  R="$W/r$i"; mkdir "$R"; git -C "$R" init -q -b master
  if GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" git -C "$R" -c commit.gpgsign=false commit -q --allow-empty -m 'round-1: work' 2>"$W/gerr$i"; then
    OK_REPO="$R"
    SHA9=$(git -C "$R" rev-parse --short=9 HEAD)
    CT=$(git -C "$R" log -1 --format=%ct)
    printf '## Landed changes\n- `%s` work\n## End\n' "$SHA9" > "$W/d$i.md"
    echo "== commit date '$when' -> git %ct=$CT (expect no traceback; int() reached for this lane round-1 commit)"
    "$PY" "$AUD" --lane-repo "$R" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/d$i.md" --no-errata 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"
  else
    echo "== commit date '$when' -> git commit refused: $(tail -n 1 "$W/gerr$i")"
  fi
done
echo "== numeric tokens in Landed changes that are not commits (expect landed-unresolved lines for both)"
printf '## Landed changes\n- `20261021` date-like\n- `1234567` count-like\n## End\n' > "$W/num.md"
"$PY" "$AUD" --lane-repo "$OK_REPO" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/num.md" --no-errata 2>&1 | tail -n 6; echo "   exit=${PIPESTATUS[0]}"
echo "done"
