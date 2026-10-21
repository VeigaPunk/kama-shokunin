#!/usr/bin/env bash
# Bounded offline fixture 2 for lane RevDraft.
# D: draft round whose fleet history cannot be walked (missing tree object):
#    the fleet demonstrably holds NO round-3 report, yet the draft audit is
#    refused because report_cutoff()'s git log fails.
# E: does a draft override mask a defective COMMITTED fleet report for the
#    same round?
set -u
AUDIT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
BASE=/fast/scratch/hyaku/kama-r24/RevDraft/fx2
rm -rf "$BASE"; mkdir -p "$BASE"
lane="$BASE/lane"; fleet="$BASE/fleet"
git init -q -b master "$lane"; git init -q -b master "$fleet"

cd "$lane"; printf 'work\n' > f; git add f
GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=kama-shokunin \
GIT_COMMITTER_EMAIL=a@x GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000' \
  git -c commit.gpgsign=false commit -q -m 'round-3: work'
LC=$(git rev-parse HEAD)

cd "$fleet"
mkdir -p .ufo/reports/round-1
printf '# kama round 1\n\n## Landed changes\n\n- `%s` work\n' "$LC" > .ufo/reports/round-1/kama.md
git add .ufo/reports/round-1/kama.md
GIT_AUTHOR_NAME=fleet GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fleet GIT_COMMITTER_EMAIL=a@x \
GIT_AUTHOR_DATE='@2000 +0000' GIT_COMMITTER_DATE='@2000 +0000' \
  git -c commit.gpgsign=false commit -q -m 'round-1: kama report'
printf 'other\n' > other; git add other
GIT_AUTHOR_NAME=fleet GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fleet GIT_COMMITTER_EMAIL=a@x \
GIT_AUTHOR_DATE='@2100 +0000' GIT_COMMITTER_DATE='@2100 +0000' \
  git -c commit.gpgsign=false commit -q -m 'round-1: other'

printf '# kama round 3\n\n## Landed changes\n\n- `%s` work\n' "$LC" > "$BASE/draft3.md"

# ---- D: fleet with the tree of its HEAD commit removed (treeless shape)
cp -a "$fleet" "$BASE/fleet-notree"
tree=$(cd "$BASE/fleet-notree" && git rev-parse "HEAD^{tree}")
rm -f "$BASE/fleet-notree/.git/objects/${tree:0:2}/${tree:2}"
echo "removed fleet tree $tree"
echo "-- direct cutoff query on the tree-less fleet:"
git --no-replace-objects --no-lazy-fetch -C "$BASE/fleet-notree" log --diff-filter=A --format=%at -- .ufo/reports/round-3/kama.md; echo "   direct git log rc=$?"
out="$BASE/D.out"; err="$BASE/D.err"
python3 "$AUDIT" --lane-repo "$lane" --fleet-repo "$BASE/fleet-notree" --branch master \
  --no-errata --rounds 1 --report "3=$BASE/draft3.md" --json > "$out" 2> "$err"
echo "== D rc=$?  stdout bytes=$(wc -c < "$out")"; sed -n '1,10p' "$err"; echo

# ---- E: defective committed fleet report vs a clean draft for the same round
cd "$fleet"
printf '# kama round 1\n\n## Landed changes\n\n- `%s` work\n- `deadbee1` typo\n' "$LC" > .ufo/reports/round-1/kama.md
git add .ufo/reports/round-1/kama.md
GIT_AUTHOR_NAME=fleet GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fleet GIT_COMMITTER_EMAIL=a@x \
GIT_AUTHOR_DATE='@2200 +0000' GIT_COMMITTER_DATE='@2200 +0000' \
  git -c commit.gpgsign=false commit -q -m 'round-1: kama report v2'
printf '# kama round 1\n\n## Landed changes\n\n- `%s` work\n' "$LC" > "$BASE/draft1.md"
for label in E1 E2; do
  if [ "$label" = E1 ]; then extra=(); else extra=(--report "1=$BASE/draft1.md"); fi
  out="$BASE/$label.out"; err="$BASE/$label.err"
  python3 "$AUDIT" --lane-repo "$lane" --fleet-repo "$fleet" --branch master \
    --no-errata --rounds 1 "${extra[@]}" --json > "$out" 2> "$err"
  echo "== $label rc=$?"; grep -o '"kind": "[a-z-]*"' "$out" | sort | uniq -c; sed -n '1,5p' "$err"; echo
done
echo "lane commit $LC"
