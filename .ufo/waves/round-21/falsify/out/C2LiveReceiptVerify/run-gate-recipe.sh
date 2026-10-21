#!/usr/bin/env bash
# C2LiveReceiptVerify: re-run the gate with the recipe's pinned argv (no launches).
# Gate source = COMMITTED check-receipt.py at b76727f3 in a scratch clone (not the drifted worktree).
# Receipt = COMMITTED live-receipt.json blob at a6617149 (first commit holding it), plus the worktree path.
# Every case records stdout, stderr and exit under $RUNS; summary.tsv lists want/got per case.
set -u
PY=/usr/bin/python3
LANE=/tmp/kama-r21-C2LiveReceiptVerify/lane
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2LiveReceiptVerify
COMMITTED=$OUT/fixtures/live-receipt.committed.json
WT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/runs/b76727f3/live-receipt.json
G=$LANE/tests/llamacpp-live/check-receipt.py
RUNS=$OUT/gate-runs
MODEL=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
TREE=6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c
LINKS=5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060
ZERO=0000000000000000000000000000000000000000000000000000000000000000
mkdir -p "$RUNS"
: > "$RUNS/summary.tsv"
fail_count=0
run() {  # run <name> <want-exit> <args...>
  local name=$1 want=$2
  shift 2
  "$PY" "$@" >"$RUNS/$name.stdout" 2>"$RUNS/$name.stderr"
  local rc=$?
  echo "$rc" >"$RUNS/$name.exit"
  local verdict=PASS
  if [ "$rc" != "$want" ]; then verdict=FAIL; fail_count=$((fail_count + 1)); fi
  printf '%s\twant=%s\tgot=%s\t%s\n' "$name" "$want" "$rc" "$verdict" >>"$RUNS/summary.tsv"
}
# Recipe c2-gate-selftest
run c2-gate-selftest 0 "$G" --selftest
# Recipe c2-live-gate-pinned (committed copy, then the worktree path used by the official run)
PINNED=(--require-schema v3 --require-install-links --expect-model-sha256 "$MODEL"
        --expect-install-tree-sha256 "$TREE" --expect-install-links-sha256 "$LINKS")
run c2-live-gate-pinned 0 "$G" "$COMMITTED" "${PINNED[@]}"
run c2-live-gate-pinned-worktree 0 "$G" "$WT" "${PINNED[@]}"
# Recipe c2-live-gate-wrong-links-pin
run c2-live-gate-wrong-links-pin 1 "$G" "$COMMITTED" --require-install-links --expect-install-links-sha256 "$ZERO"
# Extra pins (not in the recipe): every identity the receipt carries, each must bind
run c2-live-gate-all-pins 0 "$G" "$COMMITTED" "${PINNED[@]}" \
  --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 \
  --expect-server-impl-sha256 e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed \
  --expect-tool-sha256 e4cc6d8885c7755717157fd23bfce3be39288990a9cf5985cb1c56a4b11cf68f \
  --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3
run c2-live-gate-wrong-tool-pin 1 "$G" "$COMMITTED" "${PINNED[@]}" --expect-tool-sha256 "$ZERO"
run c2-live-gate-wrong-tree-pin 1 "$G" "$COMMITTED" --require-schema v3 --require-install-links \
  --expect-install-tree-sha256 "$ZERO"
run c2-live-gate-wrong-model-pin 1 "$G" "$COMMITTED" --require-schema v3 --require-install-links \
  --expect-model-sha256 "$ZERO"
# Recipe c2-legacy-receipt-1..3 (round-18 receipts at the committed lane path)
for n in 1 2 3; do
  run "c2-legacy-receipt-$n" 0 "$G" "$LANE/.ufo/waves/round-18/live-recovery/receipt-$n.json"
done
# Recipe c2-legacy-receipt-1-required; the same --require-install-links check for 2 and 3
run c2-legacy-receipt-1-required 1 "$G" "$LANE/.ufo/waves/round-18/live-recovery/receipt-1.json" --require-install-links
run c2-legacy-receipt-2-required 1 "$G" "$LANE/.ufo/waves/round-18/live-recovery/receipt-2.json" --require-install-links
run c2-legacy-receipt-3-required 1 "$G" "$LANE/.ufo/waves/round-18/live-recovery/receipt-3.json" --require-install-links
echo "gate_cases_failed=$fail_count" >>"$RUNS/summary.tsv"
echo "gate_cases_failed=$fail_count"
exit 0
