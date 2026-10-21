#!/usr/bin/env bash
# Bounded offline fixture for the round-24 C1 review lane RevDraft.
# Question: does missing/unavailable UNRELATED fleet content refuse the
# audit of a draft report (--report N=PATH)?
# No network, no promisor remote, no execution payloads: plain local git.
set -u
AUDIT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
BASE=/fast/scratch/hyaku/kama-r24/RevDraft/fx
rm -rf "$BASE"; mkdir -p "$BASE"
lane="$BASE/lane"; fleet="$BASE/fleet"
git init -q -b master "$lane"
git init -q -b master "$fleet"

# lane: one round-3 commit by kama-shokunin (author time 1000)
cd "$lane"
printf 'work\n' > f
git add f
GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=kama-shokunin \
GIT_COMMITTER_EMAIL=a@x GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000' \
  git -c commit.gpgsign=false commit -q -m 'round-3: work'
LC=$(git rev-parse HEAD)

# fleet: round-1 report committed (author time 2000); NO round-2 or round-3 report
cd "$fleet"
mkdir -p .ufo/reports/round-1
printf '# kama round 1\n\n## Landed changes\n\n- `%s` work\n' "$LC" > .ufo/reports/round-1/kama.md
git add .ufo/reports/round-1/kama.md
GIT_AUTHOR_NAME=fleet GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fleet GIT_COMMITTER_EMAIL=a@x \
GIT_AUTHOR_DATE='@2000 +0000' GIT_COMMITTER_DATE='@2000 +0000' \
  git -c commit.gpgsign=false commit -q -m 'round-1: kama report'

# draft for round 3 citing the lane commit
printf '# kama round 3\n\n## Landed changes\n\n- `%s` work\n' "$LC" > "$BASE/draft3.md"

run() { # label, extra args...
  label=$1; shift
  out="$BASE/$label.out"; err="$BASE/$label.err"
  python3 "$AUDIT" --lane-repo "$lane" --fleet-repo "$fleet" --branch master \
    --no-errata "$@" > "$out" 2> "$err"
  rc=$?
  echo "== $label rc=$rc"
  echo "-- stdout bytes: $(wc -c < "$out")"
  sed -n '1,40p' "$err"
  echo
}

# A: unrelated round 2 has NO fleet report; draft for round 3 requested
run A --rounds 1-3 --report "3=$BASE/draft3.md" --json
# B: control - same fixture, selection omits the absent round 2
run B --rounds 1 --report "3=$BASE/draft3.md" --json
# C: unrelated round 1 report blob is present in the tree but its object is
#    unavailable locally (the shape a blobless/promisor clone has)
cp -a "$fleet" "$BASE/fleet-noblob"
blob=$(cd "$BASE/fleet-noblob" && git rev-parse HEAD:.ufo/reports/round-1/kama.md)
p="$BASE/fleet-noblob/.git/objects/${blob:0:2}/${blob:2}"
rm -f "$p"
out="$BASE/C.out"; err="$BASE/C.err"
python3 "$AUDIT" --lane-repo "$lane" --fleet-repo "$BASE/fleet-noblob" --branch master \
  --no-errata --rounds 1 --report "3=$BASE/draft3.md" --json > "$out" 2> "$err"
echo "== C rc=$?"
echo "-- stdout bytes: $(wc -c < "$out")"
sed -n '1,40p' "$err"
echo
echo "fixture lane commit: $LC"
