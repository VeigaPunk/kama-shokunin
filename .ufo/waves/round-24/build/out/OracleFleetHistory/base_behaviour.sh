#!/usr/bin/env bash
# Frozen-base (r23, 0df800e) behaviour on the OracleFleetHistory fixtures.
# The candidate implementation does not exist yet; this is the "before" arm.
set -u
ROOT=/fast/scratch/hyaku/kama-r24/OracleFleetHistory/fixtures/out
TOOL=/fast/scratch/hyaku/kama-r24/OracleFleetHistory/repo/tools/report-landing-audit.py
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

for r in fleet_plain fleet_marked_cfg fleet_marked_pack fleet_hist fleet_hist_marked_cfg fleet_hist_missing; do
  printf '\n### base 0df800e --fleet-repo %s\n' "$r"
  python3 "$TOOL" --lane-repo "$ROOT/lane" --fleet-repo "$ROOT/$r" \
      --branch master --lane kama --rounds 1 --no-errata --json
  printf 'exit=%s\n' "$?"
done

for r in fleet_skew fleet_skew_marked_cfg; do
  printf '\n### base 0df800e --lane-repo lane_skew --fleet-repo %s\n' "$r"
  python3 "$TOOL" --lane-repo "$ROOT/lane_skew" --fleet-repo "$ROOT/$r" \
      --branch master --lane kama --rounds 1 --no-errata --json
  printf 'exit=%s\n' "$?"
done
