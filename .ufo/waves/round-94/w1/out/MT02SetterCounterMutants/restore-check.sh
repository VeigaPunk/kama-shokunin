#!/usr/bin/env bash
# Restoration check: pristine counter bytes, same control input, compare to baseline.
set +e
cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/out/MT02SetterCounterMutants || exit 9
export TMPDIR=/fast/scratch/hyaku/kama-r94/MT02SetterCounterMutants
python3 counter.M2.py --repo "$TMPDIR/wt" --rev 6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623 \
  --work "$TMPDIR/work" --archive "$TMPDIR/b12177.tar.gz" \
  --skill-file SKILL.M2.md --sources-file SOURCES.M2.md > runs/restored.out
echo "counter_rc=$?"
cmp -s runs/restored.out runs/baseline.out
echo "cmp_rc=$?"
sha256sum counter.M2.py runs/restored.out runs/baseline.out
uptime
exit 0
