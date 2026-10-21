set -u
ROOT=$(mktemp -d /fast/scratch/hyaku/kama-r24/SimplifyPolicy/probe3.XXXXXX)
cd "$ROOT" || exit 1
say() { printf '\n=== %s ===\n' "$*"; }
run() { printf '$ %s\n' "$*"; "$@" 2>&1 | sed 's/^/    /'; printf '    [rc=%s]\n' "${PIPESTATUS[0]}"; }
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x
export GIT_COMMITTER_NAME=kama-shokunin GIT_COMMITTER_EMAIL=a@x
export GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000'
AUDIT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
git init -q -b master src; cd src
git config uploadpack.allowFilter true
printf 'work\n' > f; git add f; git -c commit.gpgsign=false commit -q -m 'round-1: work'
C1=$(git rev-parse HEAD)
export GIT_AUTHOR_DATE='@1500 +0000' GIT_COMMITTER_DATE='@1500 +0000'
printf 'more\n' > g; git add g; git -c commit.gpgsign=false commit -q -m 'round-1: more'
C2=$(git rev-parse HEAD)
cd "$ROOT"
git init -q -b master fleet; cd fleet; mkdir -p .ufo/reports/round-1
printf '# kama round 1\n\n## Landed changes\n\n- %s\n' "$C1" > .ufo/reports/round-1/kama.md
git add .ufo/reports/round-1/kama.md
GIT_AUTHOR_DATE='@2000 +0000' GIT_COMMITTER_DATE='@2000 +0000' git -c commit.gpgsign=false commit -q -m 'round-1: report'
cd "$ROOT"
git -c protocol.file.allow=always clone -q --no-checkout --filter=blob:none --no-local "file://$ROOT/src" lane-partial
cd lane-partial
git -c remote.origin.partialclonefilter= -c protocol.file.allow=always fetch -q origin '+refs/heads/*:refs/remotes/origin/*'
cd "$ROOT"
git clone -q --no-local "$ROOT/src" lane-plain
say "P17 lane history and audit verdicts (author kama-shokunin)"
echo "C1=$C1 C2=$C2"
run python3 "$AUDIT" --lane-repo "$ROOT/lane-plain" --fleet-repo "$ROOT/fleet" --rounds 1 --no-errata --json
run python3 "$AUDIT" --lane-repo "$ROOT/lane-partial" --fleet-repo "$ROOT/fleet" --rounds 1 --no-errata --json
say "P18 silent absence: cat-file --batch-check on a missing blob under --no-lazy-fetch"
cd "$ROOT/lane-partial"
GITBL=$(git rev-parse "$C2:g")
echo "blob of g = $GITBL"
run git --no-lazy-fetch cat-file --batch-check <<<"$GITBL"
run git --no-lazy-fetch show "HEAD:g"
run git --no-lazy-fetch cat-file -e "$GITBL"
run git --no-lazy-fetch log --diff-filter=A --format=%at -- f
printf '\nROOT=%s\n' "$ROOT"
