#!/bin/bash
# Round-95 C1 mutation grading queue. Each mutant is graded with the frozen counter,
# with the identical invocation, in batches of CONC. Receipts under $OUT/receipts.
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
OUT=$LANE/.ufo/waves/round-95/w1/out/MT01ProbeMutants
S=/fast/scratch/hyaku/kama-r95/MT01ProbeMutants
CONC=${CONC:-3}
mkdir -p "$OUT/receipts" "$S/tmp"

run_one() {
  local label=$1 probe=$2; shift 2
  local w="$S/work-$label"
  mkdir -p "$w"
  local t0 t1 rc
  t0=$(date +%s)
  TMPDIR="$S/tmp" timeout 3000 python3 "$LANE/tools/round95-router-budget.py" \
    --repo "$LANE" --rev f6325660 --work "$w" --probe-file "$probe" "$@" \
    > "$OUT/receipts/counter-$label.out" 2>&1
  rc=$?
  t1=$(date +%s)
  printf 'label=%s rc=%s wall=%ss started=%s probe_sha256=%s args=%s\n' "$label" "$rc" "$((t1 - t0))" \
    "$(date -d @$t0 -Is)" "$(sha256sum "$probe" | cut -d' ' -f1)" "$*" >> "$OUT/receipts/counter-exit-codes.txt"
}

MODIR=$OUT/mutants
# M06 without --allow-clock first: records the counter's byte-level clock guard (fast).
run_one M06-guard "$MODIR/M06-residue-clock-readded.sh" --runs 1 --burners 0

BATCHES=(
  "pristine:$MODIR/pristine.sh M10-filestate-dash-as-invalid:$MODIR/M10-filestate-dash-as-invalid.sh M07-wrapper-limit-15:$MODIR/M07-wrapper-limit-15.sh"
  "M08-wrapper-limit-ncand:$MODIR/M08-wrapper-limit-ncand.sh M12-step-bound-lowered:$MODIR/M12-step-bound-lowered.sh M03-step-budget-shared-per-pass:$MODIR/M03-step-budget-shared-per-pass.sh"
  "M01-step-bound-removed:$MODIR/M01-step-bound-removed.sh M02-step-bound-raised:$MODIR/M02-step-bound-raised.sh M04-max-meta-removed:$MODIR/M04-max-meta-removed.sh"
  "M05-max-meta-doubled:$MODIR/M05-max-meta-doubled.sh M09-memo-key-drops-ctime:$MODIR/M09-memo-key-drops-ctime.sh M11-skip-strings-uncounted:$MODIR/M11-skip-strings-uncounted.sh"
)
for batch in "${BATCHES[@]}"; do
  for job in $batch; do
    label=${job%%:*}; probe=${job#*:}
    run_one "$label" "$probe" --runs 1 --burners 0 &
  done
  wait
  echo "batch-done $(date -Is)" >> "$OUT/receipts/counter-exit-codes.txt"
done
# M06 with --allow-clock (the counter refuses its bytes without it).
run_one M06-residue-clock-readded "$MODIR/M06-residue-clock-readded.sh" --runs 1 --burners 0 --allow-clock
echo "QUEUE-DONE $(date -Is)" >> "$OUT/receipts/counter-exit-codes.txt"
