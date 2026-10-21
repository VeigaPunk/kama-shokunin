#!/usr/bin/env bash
# Bounded offline fixture 3 for lane RevDraft.
# F: the lane-side source-registry blob (corpus/SOURCES.md) is unavailable
#    locally (the blobless/promisor shape). The draft round's own text has
#    NO 40-hex token at all, yet the draft audit is refused, because
#    load_source_urls() reads that one repo-global blob before any round is
#    audited and its failure aborts the whole run.
set -u
AUDIT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
BASE=/fast/scratch/hyaku/kama-r24/RevDraft/fx3
rm -rf "$BASE"; mkdir -p "$BASE"
lane="$BASE/lane"; fleet="$BASE/fleet"
git init -q -b master "$lane"; git init -q -b master "$fleet"

cd "$lane"
mkdir -p corpus
printf '## Registry\n\n| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |\n|---|---|---|---|---|---|---|---|---|---|---|\n' > corpus/SOURCES.md
printf 'work\n' > f
git add f corpus/SOURCES.md
GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=kama-shokunin \
GIT_COMMITTER_EMAIL=a@x GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000' \
  git -c commit.gpgsign=false commit -q -m 'round-3: work'
LC=$(git rev-parse HEAD)
SB=$(git rev-parse HEAD:corpus/SOURCES.md)
echo "lane commit $LC ; SOURCES blob $SB"

cd "$fleet"
printf '# kama round 1\n\n## Landed changes\n\nnone\n' > .ufo/reports/round-1/kama.md 2>/dev/null || {
  mkdir -p .ufo/reports/round-1; printf '# kama round 1\n\n## Landed changes\n\nnone\n' > .ufo/reports/round-1/kama.md; }
git add -A
GIT_AUTHOR_NAME=fleet GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fleet GIT_COMMITTER_EMAIL=a@x \
GIT_AUTHOR_DATE='@2000 +0000' GIT_COMMITTER_DATE='@2000 +0000' \
  git -c commit.gpgsign=false commit -q -m 'round-1: kama report'

# draft with NO 40-hex token anywhere
printf '# kama round 3\n\n## Landed changes\n\n- lane work above\n' > "$BASE/draft3-nohex.md"

cp -a "$lane" "$BASE/lane-nosources"
rm -f "$BASE/lane-nosources/.git/objects/${SB:0:2}/${SB:2}"
echo "-- direct cat-file on the removed SOURCES blob:"
git --no-replace-objects --no-lazy-fetch -C "$BASE/lane-nosources" cat-file blob "$SB" >/dev/null 2>&1; echo "   rc=$?"

for label in F1 F2; do
  if [ "$label" = F1 ]; then L="$BASE/lane-nosources"; else L="$lane"; fi
  out="$BASE/$label.out"; err="$BASE/$label.err"
  python3 "$AUDIT" --lane-repo "$L" --fleet-repo "$fleet" --branch master \
    --no-errata --rounds 3 --report "3=$BASE/draft3-nohex.md" --json > "$out" 2> "$err"
  echo "== $label rc=$?  stdout bytes=$(wc -c < "$out")"; sed -n '1,6p' "$err"; echo
done
