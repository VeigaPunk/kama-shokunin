#!/bin/sh
# Probe: does a lazy fetch from a local donor repo restore a deleted object
# into the lane's object store (so a store snapshot can detect it)?
set -e
W=/fast/scratch/hyaku/kama-r24/OracleMultipleRoots/probe4
rm -rf "$W"; mkdir -p "$W"; cd "$W"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
git init -q -b master lane
cd lane
export GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin
export GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x
export GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000"
printf 'a\n' > f; git add f; git commit -qm 'round-1: root'
C1=$(git rev-parse HEAD)
B=$(git rev-parse HEAD:f)
# donor: full copy before deletion
cd "$W"; cp -a lane donor
cd lane
rm -f ".git/objects/${B:0:2}/${B:2}"
git config core.repositoryformatversion 1
git config extensions.partialclone origin
git config remote.origin.url "$W/donor"
git config remote.origin.promisor true
git config remote.origin.partialclonefilter blob:none
before=$(find .git/objects -type f | wc -l)
echo "objects before=$before"
echo "== cat-file WITHOUT --no-lazy-fetch (expect fetch)"
printf '%s\n' "$B" | timeout 20 git cat-file --batch-check 2>&1; echo "rc=$?"
after=$(find .git/objects -type f | wc -l)
echo "objects after=$after"
find .git/objects -type f | sort
echo "== now with --no-lazy-fetch on a second deletion"
rm -f ".git/objects/${B:0:2}/${B:2}"
printf '%s\n' "$B" | timeout 20 git --no-lazy-fetch cat-file --batch-check 2>&1; echo "rc=$?"
echo "objects final=$(find .git/objects -type f | wc -l)"
find .git/objects -type f | sort
