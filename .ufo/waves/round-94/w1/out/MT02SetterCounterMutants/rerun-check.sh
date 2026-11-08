#!/usr/bin/env bash
# Re-run the full mutation harness and capture its exit status + determinism of the table.
set +e
cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/out/MT02SetterCounterMutants || exit 9
export TMPDIR=/fast/scratch/hyaku/kama-r94/MT02SetterCounterMutants
cp runs/summary.tsv runs/summary.run1.tsv
python3 mutation-run.py > runs/mutation-run.stdout
echo "harness_rc=$?"
cp runs/summary.tsv runs/summary.run2.tsv
cmp -s runs/summary.run1.tsv runs/summary.run2.tsv
echo "table_cmp_rc=$?"
uptime
exit 0
