#!/usr/bin/env bash
# C2SetupErrorGrading (round 21, FALSIFY): gate verdict lines and exit codes
# for every hand-built fixture, plus the scratch mutant. Pure gate runs only.
# Usage: run_gate_matrix.sh GATE OUT_DIR MUTANT_GATE
set -u
GATE="$1"
OUT="$2"
MUT="$3"
LINKS=5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060
TREE=6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c

g() {
  echo "\$ python3 check-receipt.py $*"
  python3 "$GATE" "$@" 2>&1
  echo "exit=$?"
}

for f in base-copy setup-error-faithful setup-error-only \
         setup-error-null-links setup-error-outcome-pass \
         complete-null-links complete-null-tree-digest \
         empty-checks-setup-null internal-fault-nonstring; do
  g "$OUT/$f.json"
done
g "$OUT/complete-null-links.json" --require-install-links
g "$OUT/complete-null-links.json" --expect-install-links-sha256 "$LINKS"
g "$OUT/complete-null-tree-digest.json" --expect-install-tree-sha256 "$TREE"
g "$OUT/base-copy.json" --expect-install-links-sha256 "$LINKS"
g "$OUT/setup-error-null-links.json" --require-install-links --require-schema v3
g "$OUT/setup-error-faithful.json" --require-install-links \
  --require-schema v3 --expect-install-links-sha256 "$LINKS"

echo "\$ python3 check-receipt.py (mutant, setup_error rule removed) --selftest"
python3 "$MUT" --selftest 2>&1
echo "exit=$?"
for f in setup-error-only setup-error-null-links setup-error-outcome-pass \
         setup-error-faithful; do
  echo "\$ python3 check-receipt.py (mutant) $f.json"
  python3 "$MUT" "$OUT/$f.json" 2>&1
  echo "exit=$?"
done
