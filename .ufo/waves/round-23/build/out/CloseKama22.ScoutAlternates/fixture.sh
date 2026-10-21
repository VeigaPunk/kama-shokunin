#!/bin/sh
# Alternates fault grid: does objects/info/alternates flip the audit verdict?
set -u
BASE=/tmp/kama-r23/CloseKama22.ScoutAlternates
AUDIT=${AUDIT:-/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py}
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
cd "$BASE" || exit 9
rm -rf donor lane fleet shared badalt
git init -q donor && git init -q lane && git init -q fleet

commit_in() { # repo name when msg file content
  repo=$1; name=$2; when=$3; msg=$4; file=$5; content=$6
  mkdir -p "$(dirname "$repo/$file")"
  printf '%s\n' "$content" > "$repo/$file"
  git -C "$repo" add "$file"
  GIT_AUTHOR_NAME="$name" GIT_AUTHOR_EMAIL=a@x \
  GIT_COMMITTER_NAME="$name" GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$when +0000" GIT_COMMITTER_DATE="@$when +0000" \
    git -C "$repo" -c commit.gpgsign=false commit -q -m "$msg"
  git -C "$repo" rev-parse HEAD
}

DONOR=$(commit_in donor x 900 "unrelated history" g donor)
LANE=$(commit_in lane kama-shokunin 1000 "round-1: work" f work)
REPORT=".ufo/reports/round-1/kama.md"
mkdir -p "$(dirname "fleet/$REPORT")"
{
  printf '# r1\n## Work performed\n'
  printf '## Landed changes\n- `%s` work\n- `%s` fabricated\n' "$LANE" "$DONOR"
} > fleet/$REPORT
git -C fleet add "$REPORT"
FLEET=$(GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x \
  GIT_COMMITTER_NAME=kama-shokunin GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@1200 +0000" GIT_COMMITTER_DATE="@1200 +0000" \
  git -C fleet -c commit.gpgsign=false commit -q -m "round-1: kama report" \
  && git -C fleet rev-parse HEAD)

echo "BASE=$BASE"
echo "DONOR=$DONOR"
echo "LANE=$LANE"
echo "FLEET=$FLEET"
echo "donor-in-lane=$(git -C lane cat-file -e "$DONOR" 2>/dev/null; echo rc=$?)"

run_audit() { # label [env assignments...]
  label=$1; shift
  out=$(env "$@" python3 "$AUDIT" --lane-repo lane --fleet-repo fleet \
        --branch master --lane kama --rounds 1 --no-errata 2>&1)
  rc=$?
  echo "== $label rc=$rc"
  printf '%s\n' "$out" | sed -n '/^round=/p;/^  /p;/^summary/p;/^errata/p'
}

run_audit "A control: no alternates"

mkdir -p lane/.git/objects/info
printf '%s\n' "$BASE/donor/.git/objects" > lane/.git/objects/info/alternates
echo "== alternates file: $(cat lane/.git/objects/info/alternates)"
run_audit "B lane alternates -> donor (absolute path)"

# The same planted object on the fleet side, lane clean.
rm -f lane/.git/objects/info/alternates
mkdir -p fleet/.git/objects/info
printf '%s\n' "$BASE/donor/.git/objects" > fleet/.git/objects/info/alternates
run_audit "C fleet alternates -> donor"
rm -f fleet/.git/objects/info/alternates

# Relative path form (what clone --shared writes: ../../<src>/.git/objects).
printf '../../donor/.git/objects\n' > lane/.git/objects/info/alternates
run_audit "D lane alternates (relative, clone --shared style)"
rm -f lane/.git/objects/info/alternates

# Does GIT_ALTERNATE_OBJECT_DIRECTORIES="" suppress the info/alternates file?
printf '%s\n' "$BASE/donor/.git/objects" > lane/.git/objects/info/alternates
echo "== E1 cat-file plain, alt present:"
printf '%s\n' "$DONOR" | git -C lane cat-file --batch-check; echo "rc=$?"
echo "== E2 cat-file GIT_ALTERNATE_OBJECT_DIRECTORIES= (empty):"
printf '%s\n' "$DONOR" | GIT_ALTERNATE_OBJECT_DIRECTORIES= git -C lane cat-file --batch-check; echo "rc=$?"
echo "== E3 cat-file GIT_ALTERNATE_OBJECT_DIRECTORIES=/nonexistent:"
printf '%s\n' "$DONOR" | GIT_ALTERNATE_OBJECT_DIRECTORIES=/nonexistent git -C lane cat-file --batch-check; echo "rc=$?"
echo "== E4 cat-file --no-replace-objects --no-lazy-fetch:"
printf '%s\n' "$DONOR" | git -C lane --no-replace-objects --no-lazy-fetch cat-file --batch-check; echo "rc=$?"
echo "== E5 audit with the candidate flags only (no code change) rc:"
# candidate direction is not yet in the base script; nothing to run there.
run_audit "F audit under env GIT_ALTERNATE_OBJECT_DIRECTORIES= (stripped by git_env)" GIT_ALTERNATE_OBJECT_DIRECTORIES=

# Broken alternate path: nonexistent dir and a regular file.
printf '/tmp/definitely-not-here-xyz/objects\n' > lane/.git/objects/info/alternates
run_audit "G alternates -> nonexistent dir"
printf '%s\n' "$BASE/donor/f" > lane/.git/objects/info/alternates
run_audit "H alternates -> regular file"
rm -f lane/.git/objects/info/alternates

# Corrupt object in the alternate store (valid filename, garbage bytes).
mkdir -p badalt/objects/$(printf '%s' "$DONOR" | cut -c1-2)
printf 'not a zlib stream' > badalt/objects/$(printf '%s' "$DONOR" | cut -c1-2)/$(printf '%s' "$DONOR" | cut -c3-)
printf '%s\n' "$BASE/badalt/objects" > lane/.git/objects/info/alternates
run_audit "I alternates -> corrupt object store"
rm -f lane/.git/objects/info/alternates

# Legitimate scratch clone: clone --shared of the lane, then audit against it.
git clone -q --shared lane shared
echo "== shared alternates: $(cat shared/.git/objects/info/alternates)"
out=$(python3 "$AUDIT" --lane-repo shared --fleet-repo fleet --branch master \
      --lane kama --rounds 1 --no-errata 2>&1); rc=$?
echo "== J audit lane_repo=clone --shared rc=$rc"
printf '%s\n' "$out" | sed -n '/^round=/p;/^  /p;/^summary/p'
echo "== J2 shared, info/alternates forcibly emptied (simulated disable):"
: > shared/.git/objects/info/alternates
out=$(python3 "$AUDIT" --lane-repo shared --fleet-repo fleet --branch master \
      --lane kama --rounds 1 --no-errata 2>&1); rc=$?
echo "rc=$rc"
printf '%s\n' "$out" | sed -n '/^  /p;/^summary/p' | head -5
