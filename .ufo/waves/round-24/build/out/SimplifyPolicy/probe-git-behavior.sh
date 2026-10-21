#!/usr/bin/env bash
# Round-24 SimplifyPolicy probes: git behaviour that the promisor policy
# alternative depends on. Local synthetic fixtures only; no network host is
# contacted (the only remote is file:// or an unreachable ssh:// placeholder
# whose configured command is a local touch).
set -u
ROOT=$(mktemp -d /fast/scratch/hyaku/kama-r24/SimplifyPolicy/probe.XXXXXX)
cd "$ROOT" || exit 1
say() { printf '\n=== %s ===\n' "$*"; }
run() { printf '$ %s\n' "$*"; "$@" 2>&1 | sed 's/^/    /'; printf '    [rc=%s]\n' "${PIPESTATUS[0]}"; }

export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=a@x
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=a@x

say "P1 source repo"
git init -q -b master src
cd src
printf 'work\n' > f
git add f
git -c commit.gpgsign=false commit -q -m 'round-1: work'
SRC_SHA=$(git rev-parse HEAD)
SRC_BLOB=$(git rev-parse HEAD:f)
cd "$ROOT"
echo "src sha=$SRC_SHA blob=$SRC_BLOB"

say "P2 blobless partial clone (promisor metadata, blob absent)"
git -c protocol.file.allow=always clone -q --no-checkout --filter=blob:none \
    --no-local "file://$ROOT/src" partial
cd partial
git config --list --local | sed 's/^/    /'
ls .git/objects/pack | sed 's/^/    pack: /'
run git cat-file -e "$SRC_BLOB"
run git --no-lazy-fetch cat-file --batch-check <<<"$SRC_BLOB"
cd "$ROOT"

say "P3 hydrate the partial clone: still promisor-marked, now complete"
cd partial
git -c remote.origin.partialclonefilter= -c protocol.file.allow=always \
    fetch -q origin '+refs/heads/*:refs/remotes/origin/*' 2>&1 | sed 's/^/    /'
run git cat-file -e "$SRC_BLOB"
git config --list --local | sed 's/^/    /'
ls .git/objects/pack | sed 's/^/    pack: /'
cd "$ROOT"

say "P4 filter-only promisor remote: does a missing-object lookup fetch?"
git init -q -b master filt
cd filt
printf 'x\n' > f
git add f
git -c commit.gpgsign=false commit -q -m 'round-1: work'
git config remote.origin.url ssh://example.invalid/x.git
git config remote.origin.partialclonefilter blob:none
git config core.sshCommand "touch $ROOT/filter-marker; false"
run git cat-file -e "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
if [ -e "$ROOT/filter-marker" ]; then
    echo "    MARKER CREATED: filter-only remote lazy-fetched"
else
    echo "    no marker: filter-only remote did not fetch"
fi
rm -f "$ROOT/filter-marker"
git config --unset core.sshCommand
git config remote.origin.url "file://$ROOT/src"
git config remote.origin.partialclonefilter blob:none
run git cat-file -e "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
if [ -e "$ROOT/filter-marker" ]; then
    echo "    MARKER CREATED"
else
    echo "    no marker"
fi
cd "$ROOT"

say "P5 promisor=true remote: missing-object lookup fetch?"
git init -q -b master prom
cd prom
printf 'x\n' > f
git add f
git -c commit.gpgsign=false commit -q -m 'round-1: work'
git config remote.origin.url ssh://example.invalid/x.git
git config remote.origin.promisor true
git config core.sshCommand "touch $ROOT/prom-marker; false"
run git cat-file -e "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
if [ -e "$ROOT/prom-marker" ]; then
    echo "    MARKER CREATED: promisor=true remote lazy-fetched"
else
    echo "    no marker"
fi
rm -f "$ROOT/prom-marker"
run git --no-lazy-fetch cat-file -e "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
if [ -e "$ROOT/prom-marker" ]; then
    echo "    MARKER CREATED under --no-lazy-fetch"
else
    echo "    no marker under --no-lazy-fetch"
fi
cd "$ROOT"

say "P6 missing ancestor commit: does git log fail loudly?"
git init -q -b master anc
cd anc
printf 'x\n' > f
git add f
git -c commit.gpgsign=false commit -q -m 'round-1: work'
TREE=$(git rev-parse HEAD^{tree})
BODY="tree $TREE
parent 1234567890123456789012345678901234567890
author fixture <a@x> 1100 +0000
committer fixture <a@x> 1100 +0000

round-1: orphan"
ORPHAN=$(printf '%s' "$BODY" | git hash-object -t commit -w --literally --stdin)
git update-ref refs/heads/master "$ORPHAN"
run git log --format=%H%x00%at%x00%s master
run git --no-lazy-fetch log --format=%H%x00%at%x00%s master
run git rev-list --count master
cd "$ROOT"

say "P7 missing tree: ls-tree / log --diff-filter=A / show"
git init -q -b master tree
cd tree
printf 'x\n' > f
git add f
git -c commit.gpgsign=false commit -q -m 'round-1: work'
TREE=$(git rev-parse HEAD^{tree})
BODY="tree deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
author fixture <a@x> 1100 +0000
committer fixture <a@x> 1100 +0000

round-1: tree-less"
TC=$(printf '%s' "$BODY" | git hash-object -t commit -w --literally --stdin)
git update-ref refs/heads/master "$TC"
run git log --format=%H%x00%at%x00%s master
run git ls-tree -r --name-only master
run git log --diff-filter=A --format=%at -- f
run git show "master:f"
cd "$ROOT"

say "P8 missing blob in a blobless clone: show / ls-tree / log"
cd partial
git checkout -q master 2>/dev/null || true
run git show "HEAD:f"
run git ls-tree -r --name-only HEAD
run git log --format=%H%x00%at%x00%s master
run git --no-lazy-fetch cat-file --batch-check <<<"$SRC_BLOB"
cd "$ROOT"

say "P9 rev-list --missing / --filter promisor detection helpers"
cd partial
run git rev-list --objects --all --missing=print
run git fsck --connectivity-only
cd "$ROOT"

printf '\nROOT=%s\n' "$ROOT"
