#!/usr/bin/env bash
# Probe 3:
#  (1) a linked worktree of a BARE repository (bare + linked combined),
#  (2) what `cat-file --batch-check` answers for an absent object in a
#      promisor-marked repo under --no-lazy-fetch (no fetch may happen),
#  (3) whether the promisor `.promisor` marker is found when the pack
#      directory is reached through the common dir of a linked worktree.
set -u
ROOT=/fast/scratch/hyaku/kama-r24/RevBareWorktree/fixtures2
for v in $(env | sed -n 's/^\(GIT_[A-Za-z_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
W=/fast/scratch/hyaku/kama-r24/RevBareWorktree/probe3
rm -rf "$W"; mkdir -p "$W"

echo "=== (1) linked worktree of a BARE repo"
git clone -q --bare "$ROOT/plain/lane" "$W/bare-lane"
git -C "$W/bare-lane" worktree add -q --detach "$W/bare-wt" HEAD 2>&1 || \
  echo "  worktree add from bare failed"
for q in --git-dir --git-common-dir --is-bare-repository --show-prefix; do
  printf '  %-22s %s\n' "$q" "$(git -C "$W/bare-wt" rev-parse "$q" 2>&1 | tr '\n' '|')"
done
printf '  %-22s %s\n' "--git-path objects/pack" "$(git -C "$W/bare-wt" rev-parse --git-path objects/pack)"
echo "  config keys: $(git -C "$W/bare-wt" config --null --list 2>/dev/null | tr '\0' ' ' | tr -s ' ')"

echo
echo "=== (2) cat-file --batch-check on an absent object, promisor-marked repo"
git -C "$ROOT/promisor/lane" config remote.origin.url ssh://example.invalid/x.git
MISSING=0123456789abcdef0123456789abcdef01234567
for flags in "--no-lazy-fetch" "--no-lazy-fetch --no-replace-objects"; do
  out=$(git -C "$ROOT/promisor/lane" $flags -c i18n.logOutputEncoding=UTF-8 \
        cat-file --batch-check <<< "$MISSING" 2>&1)
  echo "  flags[$flags] -> [$out] rc=$?"
done
echo "  (repo has no reachable object for that id; the answer must be 'missing', not an error)"

echo
echo "=== (3) promisor marker reachability: linked worktree of a promisor repo"
git -C "$ROOT/promisor-linked/lane" repack -a -q -d 2>/dev/null || true
pp=$(git -C "$ROOT/promisor-linked/lane-wt" rev-parse --git-path objects/pack)
case "$pp" in /*) d="$pp";; *) d="$ROOT/promisor-linked/lane-wt/$pp";; esac
echo "  linked-wt resolves pack dir to: $d"
ls -1 "$d" 2>/dev/null | sed 's/^/    /'
echo "  promisor markers: $(ls "$d"/*.promisor 2>/dev/null | wc -l)"
pp2=$(git -C "$ROOT/promisor-bare/lane" rev-parse --git-path objects/pack)
case "$pp2" in /*) d2="$pp2";; *) d2="$ROOT/promisor-bare/lane/$pp2";; esac
echo "  bare resolves pack dir to: $d2"
ls -1 "$d2" 2>/dev/null | sed 's/^/    /'
echo "  promisor markers: $(ls "$d2"/*.promisor 2>/dev/null | wc -l)"
