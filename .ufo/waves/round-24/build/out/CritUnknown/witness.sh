#!/usr/bin/env bash
# Historical witness: real lane rounds 10-22 against the real fleet (read-only),
# unmarked vs a complete promisor-marked scratch copy of the lane.
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
FLEET=/home/vgpnk/Projects/shokunin
S=${1:?scratch root}
CAND=${2:?candidate tool}
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
I=(--no-replace-objects --no-lazy-fetch)
rm -rf "$S"; mkdir -p "$S"
git -C "$LANE" show 0df800e:tools/report-landing-audit.py > "$S/r23.py"
git clone -q --no-hardlinks "$LANE" "$S/marked"
[ "$(git -C "$S/marked" rev-parse --show-toplevel)" = "$S/marked" ] || { echo guard; exit 9; }
git -C "$S/marked" branch -q -f master origin/master 2>/dev/null
git "${I[@]}" -C "$S/marked" repack -adq
cp -a "$S/marked" "$S/twin"
for p in "$S"/marked/.git/objects/pack/*.pack; do : > "${p%.pack}.promisor"; done
echo "marker: $(ls "$S"/marked/.git/objects/pack/*.promisor)"
for r in marked twin; do
  echo "closure $r --all missing: $(git "${I[@]}" -C "$S/$r" rev-list --objects --no-object-names --all --missing=print | grep -c '^?')"
  echo "0957ce61 spliced token in $r: $(echo 0957ce619789d13d894ef21bc863486bcb35b56c | git "${I[@]}" -C "$S/$r" cat-file --batch-check)"
done
run() { local label=$1 tool=$2 lane=$3; out=$(python3 -B "$tool" --lane-repo "$lane" \
    --fleet-repo "$FLEET" --rounds 10-22 --json 2>"$S/err"); rc=$?
  sum=$(printf '%s' "$out" | python3 -c 'import json,sys
try: d=json.load(sys.stdin)["summary"]; print({k:d[k] for k in ("status","defects","corrected","uncorrected","errata_unmatched","errata_invalid")})
except Exception: print("-")')
  echo "$label rc=$rc $sum $(head -c 200 "$S/err")"; }
run "r23 real-lane      " "$S/r23.py" "$LANE"
run "r23 twin-unmarked  " "$S/r23.py" "$S/twin"
run "r23 marked-complete" "$S/r23.py" "$S/marked"
run "cand real-lane      " "$CAND" "$LANE"
run "cand twin-unmarked  " "$CAND" "$S/twin"
run "cand marked-complete" "$CAND" "$S/marked"
