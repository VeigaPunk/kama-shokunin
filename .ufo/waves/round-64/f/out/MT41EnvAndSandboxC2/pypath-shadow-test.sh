#!/bin/bash
# Does the C2 counter's VERDICT depend on the caller's PYTHONPATH?
#
# The counter sanitises the environment it hands to the 12 bound commands
# (PATH HOME LANG LC_ALL TMPDIR PYTHONDONTWRITEBYTECODE) and its own
# clean_env() strips GIT_* for the git calls it makes.  It does NOT sanitise
# its own interpreter environment: it is launched as
#     python3 tools/round64-c2-counter.py
# so a module in the caller's PYTHONPATH shadows the stdlib module the
# counter imports (here: subprocess).
#
# The shadow rewrites the git REF argument, so the counter believes it
# scores the BASE tip while every byte it reads comes from the measured
# tip.  The base tip has no registry r64 / canonical round-64 list, so the
# honest counter prints met=False there (controls/c2-base.txt).  If the
# shadowed run prints met=True, the verdict is caller-environment
# dependent.
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2
D=$S/clone
BASE=0c1eff3cb9ac4c11402ab0124c35842f06a436fc
MEASURED=23b3fdb1a925129a9961cf551f6d40bf251602cb
SHADOW=$S/fixtures/pypath-shadow

echo "== A. honest counter at the BASE tip (expect met=False)"
work=$S/work-shadow-base
rm -rf "$work"
( cd $D/tools && python3 round64-c2-counter.py --repo $D --tip $BASE --work "$work" ) \
    > $S/out-shadow-base.out 2> $S/out-shadow-base.err
echo "exit=$?"
cat $S/out-shadow-base.out
echo
echo "== B. same base tip, with a PYTHONPATH shadow of subprocess that"
echo "      redirects the ref to the measured tip $MEASURED"
work=$S/work-shadow-pypath
rm -rf "$work"
( cd $D/tools && env PYTHONPATH=$SHADOW MT41_FAKE_TIP=$MEASURED MT41_BASE_REF=$BASE \
    python3 round64-c2-counter.py --repo $D --tip $BASE --work "$work" ) \
    > $S/out-shadow-pypath.out 2> $S/out-shadow-pypath.err
echo "exit=$?"
cat $S/out-shadow-pypath.out
echo "stderr tail:"; tail -4 $S/out-shadow-pypath.err
echo
echo "== C. control: the same shadow with a harmless rewrite (no tip change)"
work=$S/work-shadow-ctl
rm -rf "$work"
( cd $D/tools && env PYTHONPATH=$SHADOW MT41_FAKE_TIP=$BASE MT41_BASE_REF=$BASE \
    python3 round64-c2-counter.py --repo $D --tip $BASE --work "$work" ) \
    > $S/out-shadow-ctl.out 2> $S/out-shadow-ctl.err
echo "exit=$?"
cat $S/out-shadow-ctl.out
echo "stderr tail:"; tail -3 $S/out-shadow-ctl.err
