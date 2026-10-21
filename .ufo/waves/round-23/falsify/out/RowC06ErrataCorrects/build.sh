#!/bin/bash
# Hand-built equivalent of grid row C06-errata-corrects-omission.
# Fresh /tmp repos; no import of repo-state-grid.py.
set -u
ROOT=/tmp/kama-r23w2/c06/fx
rm -rf "$ROOT"; mkdir -p "$ROOT"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x
export GIT_AUTHOR_NAME=fixture GIT_COMMITTER_NAME=fixture

git init -q -b master "$ROOT/lane"
git init -q -b master "$ROOT/fleet"

# lane commit 1: cited round-1 work
printf 'round-1: work\n' >> "$ROOT/lane/f"
git -C "$ROOT/lane" add -- f
GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin \
GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000' \
git -C "$ROOT/lane" -c commit.gpgsign=false commit -q -m 'round-1: work'
LC=$(git -C "$ROOT/lane" rev-parse HEAD)

# fleet report citing LC at t=2000
mkdir -p "$ROOT/fleet/.ufo/reports/round-1"
printf '# kama round 1\n\n## Landed changes\n\n- %s\n' "$LC" \
  > "$ROOT/fleet/.ufo/reports/round-1/kama.md"
git -C "$ROOT/fleet" add -- .ufo/reports/round-1/kama.md
GIT_AUTHOR_NAME=fleet GIT_COMMITTER_NAME=fleet \
GIT_AUTHOR_DATE='@2000 +0000' GIT_COMMITTER_DATE='@2000 +0000' \
git -C "$ROOT/fleet" -c commit.gpgsign=false commit -q -m 'round-1: report'

# lane omission: uncited round-1 commit at t=1500
printf 'round-1: more\n' >> "$ROOT/lane/f"
git -C "$ROOT/lane" add -- f
GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin \
GIT_AUTHOR_DATE='@1500 +0000' GIT_COMMITTER_DATE='@1500 +0000' \
git -C "$ROOT/lane" -c commit.gpgsign=false commit -q -m 'round-1: more'
X=$(git -C "$ROOT/lane" rev-parse HEAD)

# lane errata row: 1<TAB>landed-omitted<TAB>X<TAB>X<TAB>ev
mkdir -p "$ROOT/lane/registry"
printf '1\tlanded-omitted\t%s\t%s\tev\n' "$X" "$X" \
  > "$ROOT/lane/registry/report-landing-errata.tsv"
git -C "$ROOT/lane" add -- registry/report-landing-errata.tsv
GIT_AUTHOR_NAME=fixture GIT_COMMITTER_NAME=fixture \
GIT_AUTHOR_DATE='@1600 +0000' GIT_COMMITTER_DATE='@1600 +0000' \
git -C "$ROOT/lane" -c commit.gpgsign=false commit -q -m 'errata'

printf 'LC=%s\nX=%s\nLANE_TIP=%s\nFLEET_TIP=%s\n' \
  "$LC" "$X" "$(git -C "$ROOT/lane" rev-parse HEAD)" \
  "$(git -C "$ROOT/fleet" rev-parse HEAD)"
git -C "$ROOT/lane" log --format='%H %an %at %s' --all
git -C "$ROOT/lane" show HEAD:registry/report-landing-errata.tsv | od -c | head -5
