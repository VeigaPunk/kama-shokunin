#!/bin/sh
# Probe: missing ancestor commit in a promisor-marked lane repo.
set -e
W=/fast/scratch/hyaku/kama-r24/OracleMultipleRoots/probe3
rm -rf "$W"; mkdir -p "$W"; cd "$W"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
git init -q -b master lane
cd lane
export GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin
export GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x
export GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000"
printf 'a\n' > f; git add f; git commit -qm 'round-1: root'
C1=$(git rev-parse HEAD)
export GIT_AUTHOR_DATE="@1100 +0000" GIT_COMMITTER_DATE="@1100 +0000"
printf 'b\n' > g; git add g; git commit -qm 'round-1: child'
C2=$(git rev-parse HEAD)
mkdir -p ../absent-remote
git config core.repositoryformatversion 1
git config extensions.partialclone origin
git config remote.origin.url "$W/absent-remote"
git config remote.origin.promisor true
git config remote.origin.partialclonefilter blob:none
rm -f ".git/objects/${C1:0:2}/${C1:2}"
echo "C1=$C1 C2=$C2"
echo "== git log C2 --no-lazy-fetch"; git --no-lazy-fetch log --format=%H "$C2" 2>&1 | tail -3; echo "rc=$?"
echo "== git log C2 (no flag)"; timeout 15 git log --format=%H "$C2" 2>&1 | tail -3; echo "rc=$?"
echo "== rev-list --objects --missing=print --no-lazy-fetch"; git --no-lazy-fetch rev-list --objects --missing=print "$C2" 2>&1 | tail -4; echo "rc=$?"
echo "== rev-list --objects --missing=print (no flag)"; timeout 15 git rev-list --objects --missing=print "$C2" 2>&1 | tail -4; echo "rc=$?"
echo "== cat-file --batch-check missing commit (no flag)"; printf '%s\n' "$C1" | timeout 15 git cat-file --batch-check 2>&1; echo "rc=$?"
echo "== cat-file --batch-check missing commit (--no-lazy-fetch)"; printf '%s\n' "$C1" | git --no-lazy-fetch cat-file --batch-check 2>&1; echo "rc=$?"
