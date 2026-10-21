#!/usr/bin/env bash
# Probe 4: detection-gap measurement.
#  (a) config-only promisor marking (no .promisor pack marker) in the
#      bare and linked layouts -> which refusal branch fires?
#  (b) a promisor pack reachable only through objects/info/alternates
#      -> is it detected?
#  (c) worktree-scoped config visibility from a linked worktree.
set -u
ROOT=/fast/scratch/hyaku/kama-r24/RevBareWorktree/fixtures2
W=/fast/scratch/hyaku/kama-r24/RevBareWorktree/probe4
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
rm -rf "$W"; mkdir -p "$W"
for v in $(env | sed -n 's/^\(GIT_[A-Za-z_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

echo "=== (a) config-only promisor marking (marker files removed)"
for v in promisor promisor-bare promisor-linked; do
  rm -f "$ROOT/$v"/*/.git/objects/pack/*.promisor "$ROOT/$v"/*/objects/pack/*.promisor 2>/dev/null || true
done
for pair in "promisor:$ROOT/promisor/lane" "promisor-bare:$ROOT/promisor-bare/lane" \
            "promisor-linked:$ROOT/promisor-linked/lane-wt"; do
  label=${pair%%:*}; lane=${pair#*:}
  msg=$(python3 "$TOOL" --lane-repo "$lane" --fleet-repo "${lane%lane*}${lane##*/lane}" \
        --branch master --lane kama --rounds 1 --no-errata 2>&1 >/dev/null) || true
  echo "  $label -> $msg"
done

echo
echo "=== (b) promisor pack reachable only through objects/info/alternates"
git clone -q --bare "$ROOT/plain/lane" "$W/alt-lane"
git clone -q --bare "$ROOT/plain/fleet" "$W/alt-fleet"
git -C "$W/alt-lane" repack -a -q -d
mkdir -p "$W/altstore/objects/pack"
cp "$W/alt-lane/objects/pack"/*.pack "$W/altstore/objects/pack/" 2>/dev/null || true
cp "$W/alt-lane/objects/pack"/*.idx "$W/altstore/objects/pack/" 2>/dev/null || true
for p in "$W/altstore/objects/pack"/*.pack; do [ -e "$p" ] && : > "${p%.pack}.promisor"; done
echo "$W/altstore/objects" > "$W/alt-lane/objects/info/alternates"
echo "  alternates file: $(cat "$W/alt-lane/objects/info/alternates")"
echo "  altstore markers: $(ls "$W/altstore/objects/pack"/*.promisor 2>/dev/null | wc -l)"
out=$(python3 "$TOOL" --lane-repo "$W/alt-lane" --fleet-repo "$W/alt-fleet" \
      --branch master --lane kama --rounds 1 --no-errata 2>&1)
echo "  tool rc=$? ->"
printf '%s\n' "$out" | sed 's/^/    /'
echo "  (a refusal here would mean the alternates channel is covered)"

echo
echo "=== (c) worktree-scoped config visibility from a linked worktree"
git -C "$ROOT/linked/lane" config extensions.worktreeConfig true
git -C "$ROOT/linked/lane" config --worktree foo.bar baz 2>&1 | sed 's/^/  /'
echo "  git config --list in linked worktree:"
git -C "$ROOT/linked/lane-wt" config --null --list 2>/dev/null | tr '\0' '\n' | sed 's/^/    /'
git -C "$ROOT/linked/lane" config --unset extensions.worktreeConfig 2>/dev/null || true
