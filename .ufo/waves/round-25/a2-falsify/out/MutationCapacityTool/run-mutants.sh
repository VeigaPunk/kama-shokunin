#!/bin/bash
# Mutation test driver for the round-25 C2 capacity tool.
# Each mutant runs the affected cells only (--only), the pristine full
# receipt is spliced with the mutant cells, and the committed counter
# (clone/.ufo/waves/round-25/count-c2.py at fa3b62a) scores both.
set -u
BASE=/fast/scratch/hyaku/kama-r25a2w2/MutationCapacityTool
CLONE=$BASE/clone
COUNTER=$CLONE/.ufo/waves/round-25/count-c2.py
PRISTINE=$BASE/receipts/base-all.json
RANGE=47460-47479
mkdir -p "$BASE/receipts" "$BASE/out"

run_mut () {
  name=$1; script=$2; cells=$3
  echo "=== MUTANT $name (cells: $cells) ==="
  python3 "$CLONE/tools/kama-context-capacity-mutants/$script" \
      --only "$cells" --port-range $RANGE \
      --scratch "$BASE/scratch/$name" \
      --out "$BASE/receipts/$name.json"
  echo "tool_exit=$?"
}

score () {
  python3 "$COUNTER" "$1"; echo "counter_exit=$?"
}

# splice: replace the named cells in the pristine receipt with the mutant's
# own cell records, so the counter sees a full 14-cell receipt where only
# the mutated cells differ.
splice () {
  name=$1; cells=$2
  python3 - "$PRISTINE" "$BASE/receipts/$name.json" "$BASE/receipts/$name-spliced.json" "$cells" <<'PY'
import json, sys
pris, mut, out, cells = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(',')
p = json.load(open(pris)); m = json.load(open(mut))
by = {c['id']: c for c in m['cells']}
replaced = []
for c in p['cells']:
    if c['id'] in by:
        replaced.append(c['id']); c.update(by[c['id']])
json.dump(p, open(out, 'w'), indent=2, sort_keys=True)
print('spliced_cells', sorted(replaced))
PY
}

for spec in \
  "m1-first-pool:m1-first-pool.py:X1" \
  "m2-drop-v:m2-drop-v.py:K1,K2,K3,K4,K5,K6,K7,K8,X1,X2,X3,L1,L2,L3" \
  "m3-drop-teardown:m3-drop-teardown.py:K1,K2,K3,K4,K5,K6,K7,K8,X1,X2,X3,L1,L2,L3" \
  "m4-sequential-concurrent:m4-sequential-concurrent.py:L1,L2" \
  "m5-fixed-status:m5-fixed-status.py:L1,L2,L3" ; do
  name=${spec%%:*}; rest=${spec#*:}; script=${rest%%:*}; cells=${rest#*:}
  run_mut "$name" "$script" "$cells"
  echo "--- $name: counter on mutant-only receipt ---"
  score "$BASE/receipts/$name.json"
  splice "$name" "$cells"
  echo "--- $name: counter on pristine-spliced receipt ---"
  score "$BASE/receipts/$name-spliced.json"
  echo
done
echo "=== PRISTINE re-score (control) ==="
score "$PRISTINE"
