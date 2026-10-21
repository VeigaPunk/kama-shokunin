#!/usr/bin/env bash
# Round-24 SimplifyPolicy probe 2: a real blobless partial clone (filter
# honoured), a hydrated promisor-marked clone, and the CURRENT auditor's
# baseline verdicts on them. Local fixtures only; the only remote is file://.
set -u
ROOT=$(mktemp -d /fast/scratch/hyaku/kama-r24/SimplifyPolicy/probe2.XXXXXX)
cd "$ROOT" || exit 1
say() { printf '\n=== %s ===\n' "$*"; }
run() { printf '$ %s\n' "$*"; "$@" 2>&1 | sed 's/^/    /'; printf '    [rc=%s]\n' "${PIPESTATUS[0]}"; }

export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=a@x
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=a@x

AUDIT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py

say "P10 build a lane with two commits and a fleet report"
git init -q -b master src
cd src
git config uploadpack.allowFilter true
printf 'work\n' > f
git add f
git -c commit.gpgsign=false commit -q -m 'round-1: work'
C1=$(git rev-parse HEAD)
BLOB=$(git rev-parse HEAD:f)
printf 'more\n' > g
git add g
git -c commit.gpgsign=false commit -q -m 'round-1: more'
C2=$(git rev-parse HEAD)
cd "$ROOT"
git init -q -b master fleet
cd fleet
mkdir -p .ufo/reports/round-1
printf '# kama round 1\n\n## Landed changes\n\n- %s\n' "$C1" \
    > .ufo/reports/round-1/kama.md
git add .ufo/reports/round-1/kama.md
git -c commit.gpgsign=false commit -q -m 'round-1: report'
cd "$ROOT"
echo "C1=$C1 C2=$C2 BLOB=$BLOB"

say "P11 real blobless partial clone of the lane"
git -c protocol.file.allow=always clone -q --no-checkout --filter=blob:none \
    --no-local "file://$ROOT/src" lane-partial
cd lane-partial
git config --list --local | sed 's/^/    /'
ls .git/objects/pack | sed 's/^/    pack: /'
run git cat-file -e "$BLOB"
run git --no-lazy-fetch cat-file --batch-check <<<"$BLOB"
run git show "HEAD:f"
run git ls-tree -r --name-only HEAD
run git log --format=%H%x00%at%x00%s master
run git --no-lazy-fetch rev-list --objects --all --missing=print
cd "$ROOT"

say "P12 current auditor on the blobless lane (report cites C1 only)"
run python3 "$AUDIT" --lane-repo "$ROOT/lane-partial" \
    --fleet-repo "$ROOT/fleet" --rounds 1 --no-errata --json

say "P13 hydrate the partial clone (fetch without the filter)"
cd lane-partial
git -c remote.origin.partialclonefilter= -c protocol.file.allow=always \
    fetch -q origin '+refs/heads/*:refs/remotes/origin/*'
run git cat-file -e "$BLOB"
git config --list --local | sed 's/^/    /'
ls .git/objects/pack | sed 's/^/    pack: /'
run git --no-lazy-fetch rev-list --objects --all --missing=print
cd "$ROOT"

say "P14 current auditor on the hydrated promisor-marked lane"
run python3 "$AUDIT" --lane-repo "$ROOT/lane-partial" \
    --fleet-repo "$ROOT/fleet" --rounds 1 --no-errata --json

say "P15 same hydrated clone with the promisor config removed (marker only)"
cp -a "$ROOT/lane-partial" "$ROOT/lane-marker"
cd "$ROOT/lane-marker"
git config --unset remote.origin.promisor || true
git config --unset remote.origin.partialclonefilter || true
git config --unset extensions.partialclone || true
git config --list --local | sed 's/^/    /'
ls .git/objects/pack | sed 's/^/    pack: /'
cd "$ROOT"
run python3 "$AUDIT" --lane-repo "$ROOT/lane-marker" \
    --fleet-repo "$ROOT/fleet" --rounds 1 --no-errata --json

say "P16 control: a plain (non-promisor) clone of the same lane"
git clone -q --no-local "$ROOT/src" "$ROOT/lane-plain"
run python3 "$AUDIT" --lane-repo "$ROOT/lane-plain" \
    --fleet-repo "$ROOT/fleet" --rounds 1 --no-errata --json

printf '\nROOT=%s\n' "$ROOT"
