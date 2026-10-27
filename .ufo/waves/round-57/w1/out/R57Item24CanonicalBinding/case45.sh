#!/usr/bin/env bash
# case45.sh - distinct case 45: the assigned-case verdict, re-derived here.
# Every reading is recomputed from the tree; nothing is copied from the prototype run.
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
BASE=b89bdab2cc114735ec5d331c6c610134258f7864
HEAD_SHA=$(git -C "$LANE" rev-parse HEAD)
TMP=$(mktemp -d /fast/scratch/hyaku/kama-r57/R57Item24CanonicalBinding/c45.XXXXXX)
trap 'rm -rf "$TMP"' EXIT
git -C "$LANE" show "$BASE:SCORECARD.md" > "$TMP/base.md"

echo "== claim under test (seat prompt, verbatim) =="
echo "C1 calibration - repair the stale canonical capability row count, counter currently"
echo "reports maxN=56 instead of expected 46; before output mismatch=1."
echo

echo "== 1. the frozen receipt the claim rests on =="
echo '$ sed -n 1,4p .ufo/waves/round-57/controls/base-c1.out'
sed -n '1,4p' "$LANE/.ufo/waves/round-57/controls/base-c1.out"
echo

echo "== 2. maxN re-derived independently at the frozen base =="
echo '$ grep -oE "^## Round [0-9]+" base.md | grep -oE "[0-9]+" | sort -n | tail -1'
grep -oE '^## Round [0-9]+' "$TMP/base.md" | grep -oE '[0-9]+' | sort -n | tail -1
echo '$ grep -cE "^## Round [0-9]+" base.md'
grep -cE '^## Round [0-9]+' "$TMP/base.md"
echo '$ ... round headings that occur more than once (count, round)'
grep -oE '^## Round [0-9]+' "$TMP/base.md" | grep -oE '[0-9]+' | sort -n | uniq -c | awk '$1>1'
echo

echo "== 3. every other round-bearing surface at the base, as a 46 candidate =="
for pat in '^## Round ([0-9]+)' '^### Round-([0-9]+) measured' '^### Planned [(]round ([0-9]+)[)]' 'canonical list as of round ([0-9]+)[*][*]'; do
  printf '%-44s -> ' "$pat"
  grep -oE "$pat" "$TMP/base.md" | grep -oE '[0-9]+' | sort -n | tail -1
done
printf '%-44s -> ' 'head banner Latest measured round'
grep -oE 'Latest measured round: [0-9]+' "$TMP/base.md" | head -1
echo

echo "== 4. where the number 46 does appear at the base =="
echo '$ grep -nE "^## Round 46" base.md | cut -c1-78'
grep -nE '^## Round 46' "$TMP/base.md" | cut -c1-78
echo '$ canonical table rows whose first-working-round cell is 46 (name, cell)'
awk -F'|' '/^\| [a-z-]+ \|/ && $5 ~ / 46 / {gsub(/^ +| +$/,"",$2); gsub(/^ +| +$/,"",$5); print "  " $2 " -> " $5}' "$TMP/base.md"
echo '$ git show 89dc4f52:.ufo/waves/round-57/controls/noop-c2.out | grep -n maxN=46'
git -C "$LANE" show 89dc4f52:.ufo/waves/round-57/controls/noop-c2.out | grep -n 'maxN=46'
echo '$ git show 89dc4f52:.ufo/waves/round-57/controls/c1-noop.py | grep -n maxN=46'
git -C "$LANE" show 89dc4f52:.ufo/waves/round-57/controls/c1-noop.py | grep -n 'maxN=46'
echo

echo "== 5. the counter at the current HEAD =="
echo "\$ python3 tools/round42-selfdesc-reconcile.py --repo LANE --tip $HEAD_SHA"
python3 "$LANE/tools/round42-selfdesc-reconcile.py" --repo "$LANE" --tip "$HEAD_SHA" 2>&1 | sed -n '1,2p'
echo

echo "== verdict =="
cat <<'TXT'
maxN=56 is the greatest "^## Round N" heading at the frozen base, which is the counter's
own definition (tools/round42-selfdesc-reconcile.py: maxN = greatest N over SCORECARD
lines matching "^## Round (digits)"), re-derived above from the frozen bytes.
No surface of the SCORECARD yields 46 as a round maximum: canonical markers stop at 49,
first-working rounds at 47, "### Round-N measured" headings at 52, "### Planned (round N)"
at 57, and "## Round N" at 56. 46 occurs only as append-only-audit's *first-working*
round - a column value, not a maximum - and as the literal typed into the frozen
do-nothing controls (noop-c2.out and c1-noop.py at the freeze, both `maxN=46`).
So the claim's second half is FALSIFIED: maxN=56 is correct, not stale.  Its first half
is CONFIRMED: the frozen output carries mismatch=1, and the single mismatch is the r41
calibration arm (expected `42`, observed `43` verifier-spotcheck lessons).
TXT
