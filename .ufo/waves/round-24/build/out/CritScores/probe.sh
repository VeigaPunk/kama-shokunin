#!/usr/bin/env bash
# CritScores r24 bounded offline probe (git primitives only; no auditor run,
# no network). Fresh root required; every fixture root is checked before
# any .git write.
set -eu
R=${1:?fresh absolute scratch root}
test ! -e "$R"
mkdir -p "$R"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
G="git --no-replace-objects --no-lazy-fetch -c log.follow=false -c log.showRoot=true"
mk() {  # repo, n commits rewriting the same path f
    git init -q -b master "$1"
    test "$(git -C "$1" rev-parse --show-toplevel)" = "$1"
    for i in $(seq 1 "$2"); do
        echo "round-$i" >> "$1/f"; git -C "$1" add f
        GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x \
        GIT_COMMITTER_NAME=kama-shokunin GIT_COMMITTER_EMAIL=a@x \
        GIT_AUTHOR_DATE="@$((1000+i)) +0000" GIT_COMMITTER_DATE="@$((1000+i)) +0000" \
            git -C "$1" -c commit.gpgsign=false commit -q -m "round-1: work $i"
    done
}

echo "### P1 multi-commit blobless clone: full closure vs auditor-shaped reads"
mk "$R/lane" 3
git -C "$R/lane" config uploadpack.allowFilter true
git -c protocol.file.allow=always clone -q --filter=blob:none --no-local \
    "file://$R/lane" "$R/clone"
test "$(git -C "$R/clone" rev-parse --show-toplevel)" = "$R/clone"
C="$G -C $R/clone"
git -C "$R/clone" config --local --list | grep -i -E 'promisor|partial'
$C log --format='%H %s' master; echo "log rc=$?"
$C ls-tree master -- f; $C cat-file -e master:f; echo "tip blob rc=$?"
$C log --diff-filter=A --format=%at -- f; echo "diff-filter=A rc=$?"
echo "-- rev-list --objects --missing=print (full closure); '?' = missing"
$C rev-list --objects --missing=print --no-object-names master
echo "-- same with --filter=blob:none (commits+trees only); missing lines:"
$C rev-list --objects --missing=print --no-object-names --filter=blob:none master \
    | grep '^?' || echo "(none)"
$C show master~2:f || echo "old non-required blob read rc=$? (fails closed)"
test ! -e "$R/clone/.git/FETCH_HEAD" && echo "no fetch occurred"

echo "### P2 missing required commit / tree in a promisor-configured repo"
mk "$R/loose" 3
git -C "$R/loose" config remote.origin.url "file:///nonexistent-crit-$$"
git -C "$R/loose" config remote.origin.promisor true
L="$G -C $R/loose"
MID=$(git -C "$R/loose" rev-parse master~1)
TREE1=$(git -C "$R/loose" rev-parse 'master~2^{tree}')
cp -a "$R/loose/.git/objects" "$R/loose-objects-backup"
rm "$R/loose/.git/objects/${MID:0:2}/${MID:2}"
$L log --format=%H master || echo "missing commit: log rc=$?"
echo "$MID" | $L cat-file --batch-check
cp "$R/loose-objects-backup/${MID:0:2}/${MID:2}" "$R/loose/.git/objects/${MID:0:2}/"
rm -f "$R/loose/.git/objects/${TREE1:0:2}/${TREE1:2}"
$L log --diff-filter=A --format=%at -- f || echo "missing tree: diff-filter=A rc=$?"

echo "### P4 fleet-shaped repo, missing .ufo/reports subtree"
git init -q -b master "$R/lstree"
test "$(git -C "$R/lstree" rev-parse --show-toplevel)" = "$R/lstree"
mkdir -p "$R/lstree/.ufo/reports/round-1"
echo x > "$R/lstree/.ufo/reports/round-1/kama.md"
git -C "$R/lstree" add .
GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=a@x \
    git -C "$R/lstree" -c commit.gpgsign=false commit -q -m r
git -C "$R/lstree" config remote.origin.promisor true
git -C "$R/lstree" config remote.origin.url "file:///nonexistent-crit-$$"
SUB=$(git -C "$R/lstree" rev-parse HEAD:.ufo/reports)
rm "$R/lstree/.git/objects/${SUB:0:2}/${SUB:2}"
$G -C "$R/lstree" ls-tree -r --name-only HEAD -- .ufo/reports \
    || echo "missing subtree: ls-tree rc=$?"
