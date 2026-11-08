#!/usr/bin/env bash
# Frozen-predicate run: no --skill-file/--sources-file, so SKILL.md and corpus/SOURCES.md
# come from git at M2 and the counter must exit 0 with met=True.
set +e
cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/out/MT02SetterCounterMutants || exit 9
export TMPDIR=/fast/scratch/hyaku/kama-r94/MT02SetterCounterMutants
python3 counter.M2.py --repo "$TMPDIR/wt" --rev 6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623 \
  --work "$TMPDIR/work" --archive "$TMPDIR/b12177.tar.gz" > runs/predicate-nofiles.out
echo "predicate_rc=$?"
cmp -s runs/predicate-nofiles.out runs/baseline.out
echo "same_as_control_mode=$?"
tail -3 runs/predicate-nofiles.out
exit 0
