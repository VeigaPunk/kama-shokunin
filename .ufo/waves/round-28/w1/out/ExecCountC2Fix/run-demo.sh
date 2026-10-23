#!/usr/bin/env bash
# Reproduce the round-28 count-c2 repair demonstrations from the committed lane
# evidence. Read-only with respect to the lane; scratch lives under /fast.
# Usage: bash run-demo.sh   (expected total runtime: seconds)
set -euo pipefail
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
OUT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S=/fast/scratch/hyaku/kama-r28/w1/ExecCountC2Fix-demo
rm -rf "$S"
mkdir -p "$S/fixtures" "$S/logs"
mkdir -p "$S/tree/.ufo/waves/round-25"
cp -a "$LANE/.ufo/waves/round-25/final" "$S/tree/.ufo/waves/round-25/final"
cp "$LANE/.ufo/waves/round-25/count-c2.py" "$S/tree/.ufo/waves/round-25/count-c2-before.py"
cp "$OUT/count-c2.py" "$S/tree/.ufo/waves/round-25/count-c2-after.py"
cd "$S/tree"
echo "lane counter sha256: $(sha256sum .ufo/waves/round-25/count-c2-before.py | cut -d' ' -f1)"
echo "patched counter sha256: $(sha256sum .ufo/waves/round-25/count-c2-after.py | cut -d' ' -f1)"
echo "committed receipt sha256: $(sha256sum .ufo/waves/round-25/final/context-capacity-receipt.json | cut -d' ' -f1)"

echo "=== (a) unchanged committed receipt ==="
echo "\$ python3 .ufo/waves/round-25/count-c2-before.py"
timeout 120 /usr/bin/python3 .ufo/waves/round-25/count-c2-before.py
echo "\$ python3 .ufo/waves/round-25/count-c2-after.py"
timeout 120 /usr/bin/python3 .ufo/waves/round-25/count-c2-after.py

timeout 120 /usr/bin/python3 "$OUT/make-fixtures.py" \
    .ufo/waves/round-25/final/context-capacity-receipt.json "$S/fixtures"

echo "=== (b) forged receipt cell fields, raw files untouched ==="
F="$S/fixtures/forged-cells.receipt.json"
echo "\$ python3 .ufo/waves/round-25/count-c2-before.py $F"
timeout 120 /usr/bin/python3 .ufo/waves/round-25/count-c2-before.py "$F"
echo "\$ python3 .ufo/waves/round-25/count-c2-after.py $F"
timeout 120 /usr/bin/python3 .ufo/waves/round-25/count-c2-after.py "$F"

cp -a "$S/tree" "$S/tree-raw1"
cp "$S/fixtures/forged-K3.props.body" \
   "$S/tree-raw1/.ufo/waves/round-25/final/raw/K3.props.body"
cd "$S/tree-raw1"
echo "=== (c1) forged raw file, committed receipt, hash not rebound ==="
echo "forged K3.props.body sha256: $(sha256sum .ufo/waves/round-25/final/raw/K3.props.body | cut -d' ' -f1)"
echo "\$ python3 .ufo/waves/round-25/count-c2-before.py"
timeout 120 /usr/bin/python3 .ufo/waves/round-25/count-c2-before.py
echo "\$ python3 .ufo/waves/round-25/count-c2-after.py"
timeout 120 /usr/bin/python3 .ufo/waves/round-25/count-c2-after.py

cp -a "$S/tree" "$S/tree-raw2"
cp "$S/fixtures/forged-K3.props.body" \
   "$S/tree-raw2/.ufo/waves/round-25/final/raw/K3.props.body"
cd "$S/tree-raw2"
echo "=== (c2) forged raw file AND receipt raw hash rebound to it ==="
echo "forged K3.props.body sha256: $(sha256sum .ufo/waves/round-25/final/raw/K3.props.body | cut -d' ' -f1)"
echo "receipt-bound raw_props: $(/usr/bin/python3 -c "import json;d=json.load(open('$S/fixtures/forged-raw-receipt.json'));print([c['raw']['raw_props'] for c in d['cells'] if c['id']=='K3'][0])")"
echo "\$ python3 .ufo/waves/round-25/count-c2-before.py $S/fixtures/forged-raw-receipt.json"
timeout 120 /usr/bin/python3 .ufo/waves/round-25/count-c2-before.py "$S/fixtures/forged-raw-receipt.json"
echo "\$ python3 .ufo/waves/round-25/count-c2-after.py $S/fixtures/forged-raw-receipt.json"
timeout 120 /usr/bin/python3 .ufo/waves/round-25/count-c2-after.py "$S/fixtures/forged-raw-receipt.json"
echo "done: scratch tree $S"
