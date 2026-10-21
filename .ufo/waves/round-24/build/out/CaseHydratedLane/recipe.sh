#!/bin/sh
# Round-24 oracle case "CaseHydratedLane" - exact recipe.
#
# Everything happens under $W (a scratch root). Nothing outside it is
# written; no network transport and no git program is used.
#
#   W=/fast/scratch/hyaku/kama-r24/CaseHydratedLane/work-recipe
#   sh recipe.sh "$W"
#
# The script builds ONE genuine blob:none lane clone, hydrates it offline
# and prints the closure of every step. The full arm matrix and the
# expected exits live in hydrated_lane_case.py (EXPECTED) and in
# ../advice/CaseHydratedLane.md.
set -eu
W=${1:?scratch root}
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_ALLOW_PROTOCOL=file          # file:// only; no network transport
rm -rf "$W"; mkdir -p "$W/lane"
cd "$W"

# 1. lane origin: two round-1 commits by kama-shokunin, fixed dates
git init -q -b master "$W/lane"
printf 'work\n' > "$W/lane/f"
git -C "$W/lane" add f
GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=kama@shokunin.local \
GIT_COMMITTER_NAME=kama-shokunin GIT_COMMITTER_EMAIL=kama@shokunin.local \
GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000' \
  git -C "$W/lane" -c commit.gpgsign=false commit -q -m 'round-1: work'
printf 'extra\n' > "$W/lane/g"
git -C "$W/lane" add g
GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=kama@shokunin.local \
GIT_COMMITTER_NAME=kama-shokunin GIT_COMMITTER_EMAIL=kama@shokunin.local \
GIT_AUTHOR_DATE='@1500 +0000' GIT_COMMITTER_DATE='@1500 +0000' \
  git -C "$W/lane" -c commit.gpgsign=false commit -q -m 'round-1: extra'
git -C "$W/lane" config uploadpack.allowFilter true   # genuine filtering

# 2. genuine file:// blob:none clone (--no-checkout: a checkout would ask
#    the promisor remote for the tip blobs and hydrate the fixture)
git -c protocol.file.allow=always clone -q --no-local \
    --filter=blob:none --no-checkout "file://$W/lane" "$W/lane-blobless"

echo "--- promisor metadata:"
git -C "$W/lane-blobless" config --list | grep -E 'promisor|partialclone' || true
echo "--- closure before hydration (missing objects are named ?<oid>):"
git --no-lazy-fetch -C "$W/lane-blobless" rev-list --objects --all --missing=print

# 3. hydrate LOCALLY: copy the origin object store into the clone.
#    No transport, no program: a plain file copy. The promisor marks stay.
for d in "$W/lane/.git/objects"/??; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  mkdir -p "$W/lane-blobless/.git/objects/$name"
  for f in "$d"/*; do
    [ -f "$f" ] || continue
    cp -n "$f" "$W/lane-blobless/.git/objects/$name/" || true
  done
done

echo "--- closure after hydration:"
git --no-lazy-fetch -C "$W/lane-blobless" rev-list --objects --all --missing=print
echo "--- plain walk (rc 0 means the content is complete):"
git --no-lazy-fetch -C "$W/lane-blobless" rev-list --objects --all >/dev/null \
  && echo "content complete"
echo "--- promisor metadata still there:"
git -C "$W/lane-blobless" config --list | grep -E 'promisor|partialclone' || true
echo "--- object counts (clone vs origin):"
git -C "$W/lane-blobless" cat-file --batch-all-objects --batch-check='%(objectname)' 2>/dev/null | wc -l
git -C "$W/lane" cat-file --batch-all-objects --batch-check='%(objectname)' 2>/dev/null | wc -l
