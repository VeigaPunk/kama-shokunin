#!/bin/bash
# EXTRA="--runs 1 --skip-load" run_batch.sh LABEL:PROBE [LABEL:PROBE ...]
# -> one frozen-counter run per pair, concurrent, then wait.
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
OUT=$LANE/.ufo/waves/round-95/w1/out/MT01ProbeMutants
S=/fast/scratch/hyaku/kama-r95/MT01ProbeMutants
EXTRA=${EXTRA:---runs 1 --skip-load}
mkdir -p "$OUT/receipts" "$S/tmp"
for spec in "$@"; do
  label=${spec%%:*}; probe=${spec#*:}
  (
    w="$S/work-$label"; mkdir -p "$w"
    t0=$(date +%s)
    # shellcheck disable=SC2086
    TMPDIR="$S/tmp" timeout 3000 python3 "$LANE/tools/round95-router-budget.py" \
      --repo "$LANE" --rev f6325660 --work "$w" --probe-file "$probe" $EXTRA \
      > "$OUT/receipts/counter-$label.out" 2>&1
    rc=$?
    t1=$(date +%s)
    printf 'label=%s rc=%s wall=%ss started=%s probe_sha256=%s extra=%s\n' "$label" "$rc" \
      "$((t1 - t0))" "$(date -d @$t0 -Is)" "$(sha256sum "$probe" | cut -d' ' -f1)" "$EXTRA" \
      >> "$OUT/receipts/counter-exit-codes.txt"
  ) &
done
wait
echo "BATCH-DONE $* $(date -Is)" >> "$OUT/receipts/counter-exit-codes.txt"
