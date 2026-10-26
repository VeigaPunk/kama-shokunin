#!/bin/sh
# Reproduce the X2SelftestPower evidence (round 49, append-only-audit selftest power).
# usage: reproduce.sh <scratch dir>   (writes only under it; read-only on the lane)
set -eu
S=${1:?usage: reproduce.sh <scratch dir>}
OUT=$(cd "$(dirname "$0")" && pwd)
L=/home/vgpnk/Projects/shokunin/kama-shokunin
mkdir -p "$S"
export TMPDIR="$S"

# 1. the two frozen blobs this seat used, re-extracted and compared
[ -d "$S/lane" ] || git clone -q --shared "$L" "$S/lane"
git -C "$S/lane" show 74558c71c38ceaeace15fd4cf8aa9d84977584b1:tools/append-only-audit.py > "$S/v4-74558c71.py"
git -C "$S/lane" show 438127bc01ff3b99f98468549d58046f932490ef:tools/append-only-audit.py > "$S/v3.py"
echo "== blob lineage (want 3bae58a3... for v4, 0caf3c7e... for v3) =="
sha256sum "$S/v4-74558c71.py" "$S/v3.py"
cmp "$S/v4-74558c71.py" "$OUT/v4-74558c71.py" && echo "v4 blob matches copy"
cmp "$S/v3.py" "$OUT/v3.py" && echo "v3 blob matches copy"

echo "== 02 as-built v4 at 74558c71: 30 cases =="
python3 "$OUT/v4-74558c71.py" --selftest --scratch "$S/a" | tail -1
echo "== 03 v4 + the 5 proposed cases: 35 cases =="
python3 "$OUT/v4-newcases.py" --selftest --scratch "$S/b" | tail -1
echo "== 04 v3 + the same 5 cases + the defect case (5 must fail) =="
python3 "$OUT/v3-newcases.py" --selftest --scratch "$S/c" | grep -E '^FAIL|AOA_SELFTEST' | cut -c1-60
echo "== 01 v3 + the two frozen round-49 cases (2 must fail) =="
python3 "$OUT/v3-ported.py" --selftest --scratch "$S/d" | grep -E '^FAIL|AOA_SELFTEST' | cut -c1-60
echo "== 05 v4 + 5 cases + defect case (defect case must fail on 74558c71) =="
python3 "$OUT/v4-newcases-defect.py" --selftest --scratch "$S/e" | grep -E '^FAIL|AOA_SELFTEST' | cut -c1-60
