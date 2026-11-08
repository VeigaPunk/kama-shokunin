#!/usr/bin/env bash
# Run the frozen C1 counter, the scratch per-check observer and the C3 counter
# against the fixture clone at HEAD, and save the receipt under the out dir.
set -u
D=/fast/scratch/hyaku/kama-r97/EX01SelfAssessControl/lane-clone
S=/fast/scratch/hyaku/kama-r97/EX01SelfAssessControl
L=/home/vgpnk/Projects/shokunin/kama-shokunin
O=$L/.ufo/waves/round-97/w1/out/EX01SelfAssessControl
tag=$1
rev=$(git -C "$D" rev-parse HEAD)
{
  echo "mutant=$tag"
  echo "fixture_toplevel=$(git -C "$D" rev-parse --show-toplevel)"
  echo "rev=$rev subject=$(git -C "$D" log -1 --format=%s)"
  echo
  echo "--- fixture diff vs master ---"
  git -C "$D" diff master.."$rev"
  echo
  echo "--- canonical tools/round97-self-assessment-audit.py (lane tool, fixture tree) ---"
  python3 "$L/tools/round97-self-assessment-audit.py" --repo "$D" --rev "$rev"
  echo "c1_exit=$?"
  echo
  echo "--- scratch per-check observer (copy of the frozen tool with P/F reporting) ---"
  python3 "$S/audit-instrumented.py" --repo "$D" --rev "$rev"
  echo "observer_exit=$?"
  echo
  echo "--- cross-check only: tools/round97-depth-boundary-audit.py (C3) ---"
  python3 "$L/tools/round97-depth-boundary-audit.py" --repo "$D" --rev "$rev"
  echo "c3_exit=$?"
} > "$O/mutant-$tag.txt" 2>&1
cat "$O/mutant-$tag.txt"
