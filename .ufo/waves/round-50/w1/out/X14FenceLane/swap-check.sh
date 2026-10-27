#!/usr/bin/env bash
# X14FenceLane swap-check: re-create the parent swap for the lane's two merge commits,
# show the swapped parent order, run the frozen tool under it, and prove the output is
# byte-identical to the unswapped run. All objects land in the caller's clone; the
# replace refs are removed before exit. Nothing outside the clone is written.
set -u
CLONE=${1:?usage: swap-check.sh <scratch-clone> <tip>}
TIP=${2:?}
MERGE1=2f7303c242319c1dc96c6bcf7702ac18b3ca1aad
MERGE2=5396a876c466fcaa2c0b78715793ec280dfced6a
TOOL=${TOOL:-/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py}
BASE=refs/r50swap/
OUT=${3:-.}

test "$(git -C "$CLONE" rev-parse --show-toplevel)" = "$CLONE" || { echo "toplevel mismatch"; exit 1; }

run_tool() {
  python3 "$TOOL" --repo "$CLONE" --to "$TIP" --json "$@"
}

unset GIT_REPLACE_REF_BASE
run_tool > "$OUT/swap-baseline.json" || exit 1
# threshold-1 baseline must be taken BEFORE the swap exists, or it is not a baseline
run_tool --threshold 1 > "$OUT/swap-baseline-t1.json"; test -s "$OUT/swap-baseline-t1.json" || exit 1

export GIT_REPLACE_REF_BASE=$BASE
export GIT_AUTHOR_NAME=r50swap GIT_AUTHOR_EMAIL=r50swap@invalid
export GIT_COMMITTER_NAME=r50swap GIT_COMMITTER_EMAIL=r50swap@invalid
cleanup() {
  for m in "$MERGE1" "$MERGE2"; do
    GIT_REPLACE_REF_BASE=$BASE git -C "$CLONE" replace -d "$m" >/dev/null 2>&1
  done
  git -C "$CLONE" for-each-ref "$BASE" | wc -l | sed 's/^/replace-refs-left: /'
}
trap cleanup EXIT

for M in "$MERGE1" "$MERGE2"; do
  P1=$(git -C "$CLONE" rev-parse "$M^1") || exit 1
  P2=$(git -C "$CLONE" rev-parse "$M^2") || exit 1
  T=$(git -C "$CLONE" rev-parse "$M^{tree}") || exit 1
  N=$(git -C "$CLONE" commit-tree "$T" -p "$P2" -p "$P1" -m "r50swap: $M with parents swapped") || exit 1
  git -C "$CLONE" replace "$M" "$N" || exit 1
  echo "swapped: $M p1=$P1 p2=$P2 tree=$T replacement=$N"
done
echo "--- rev-list --parents -1 under the replace base:"
git -C "$CLONE" rev-list --parents -1 "$MERGE1"
git -C "$CLONE" rev-list --parents -1 "$MERGE2"
echo "--- tool under swapped parents (frozen threshold):"
run_tool > "$OUT/swap-swapped.json" || exit 1
git -C "$CLONE" for-each-ref "$BASE" | wc -l | sed 's/^/replace-refs-active: /'
sha256sum "$OUT/swap-baseline.json" "$OUT/swap-swapped.json"
cmp -s "$OUT/swap-baseline.json" "$OUT/swap-swapped.json" && echo BYTE-IDENTICAL || echo DIFFERS
echo "--- plumbing teeth: same run with --threshold 1 under the swap (not the frozen measurement)"
run_tool --threshold 1 > "$OUT/swap-swapped-t1.json"; test -s "$OUT/swap-swapped-t1.json" || exit 1
python3 - "$OUT/swap-baseline-t1.json" "$OUT/swap-swapped-t1.json" <<'PY2'
import json, sys
b = json.load(open(sys.argv[1])); s = json.load(open(sys.argv[2]))
kb = {(e["commit"], e["file"]) for e in b["events"]}
ks = {(e["commit"], e["file"]) for e in s["events"]}
print("threshold1 events baseline/swapped:", len(b["events"]), len(s["events"]))
print("threshold1 events only under swapped parents:")
for c, f in sorted(ks - kb):
    e = [x for x in s["events"] if (x["commit"], x["file"]) == (c, f)][0]
    print(" ", c[:12], f, "deleted", e["deleted"], "graded", e["graded"], "ungraded", e["ungraded"], e["status"])
print("threshold1 events only under original parents:", len(kb - ks))
PY2
