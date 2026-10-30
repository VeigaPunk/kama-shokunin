#!/bin/bash
# END-TO-END write-through mutant (direction B, mutated TIP file).
#
# The tip export carries 8 COMMITTED symlinks whose targets are absolute
# paths in the REAL lane:
#   .ufo/waves/round-36/w3/out/MutRowPipe/probe/{tools,registry,tests,...}
# The counter runs the bound commands with cwd = the tip export (tip rows)
# or cwd = an overlay whose top-level entries are symlinks INTO the tip
# export (regression/printer rows).  A bound command that writes a relative
# path therefore reaches THROUGH those links.
#
# This mutant plants, in the UNPINNED registry/capability-regress-r64.tsv,
# a one-line regression that writes into the tree via a RELATIVE path, and
# it points the write at the MutRowPipe/probe path whose committed symlink
# resolves into the real lane.
#
# SAFETY: the write target is redirected to a SCRATCH victim directory, not
# the real lane.  The mutant replaces the committed symlink's target with a
# scratch path in the clone (a commit in the scratch clone), so the
# mechanism is exercised end to end while the real lane is never written.
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2
D=$S/clone
TIP=23b3fdb1a925129a9961cf551f6d40bf251602cb
VICT=$S/victim-lane
MUT=$S/mutants

echo "== preparing the scratch victim (stands in for the lane)"
rm -rf "$VICT"; mkdir -p "$VICT/tools" "$VICT/registry"

echo "== re-pointing the committed symlink at the victim (scratch clone only)"
python3 - "$D" "$VICT" <<'PYEOF'
import os, subprocess, sys
D, VICT = sys.argv[1], sys.argv[2]
rel = '.ufo/waves/round-36/w3/out/MutRowPipe/probe/tools'
p = os.path.join(D, rel)
assert os.path.islink(p), p
cur = os.readlink(p)
print('  committed symlink target was:', cur)
os.remove(p)
os.symlink(os.path.join(VICT, 'tools'), p)
print('  now points at (scratch victim):', os.readlink(p))
PYEOF

echo "== planting the one-line regression that writes through it"
python3 - "$D" <<'PYEOF'
import os
import sys
D = sys.argv[1]
p = os.path.join(D, 'registry/capability-regress-r64.tsv')
lines = open(p).read().splitlines(True)
out, done = [], False
for ln in lines:
    cells = ln.rstrip('\n').split('\t')
    if not done and cells and cells[0] == 'sources-registry':
        assert len(cells) == 4, cells
        cells[3] = ("if open('.ufo/waves/round-36/w3/out/MutRowPipe/probe/tools/EVIL-WRITETHROUGH', 'w') or new is None:")
        ln = '\t'.join(cells) + '\n'
        done = True
    out.append(ln)
assert done
open(p, 'w').write(''.join(out))
print('  regress row for sources-registry now writes EVIL-WRITETHROUGH')
PYEOF

git -C $D add -A
git -C $D -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "mutant t3 symlink write-through"
T=$(git -C $D rev-parse HEAD)
echo "  tip=$T"

work=$S/work-mut-t3
rm -rf "$work"
( cd $D/tools && python3 round64-c2-counter.py --repo $D --tip "$T" --work "$work" ) \
    > $S/out-mut/t3_symlink_writethrough.out 2> $S/out-mut/t3_symlink_writethrough.err
echo "exit=$?"
cat $S/out-mut/t3_symlink_writethrough.out
echo
echo "== WHERE did EVIL-WRITETHROUGH land?"
echo "  victim (outside --work, the lane stand-in): $(find $VICT -name 'EVIL-WRITETHROUGH' | wc -l) entry"
find $VICT -name 'EVIL-WRITETHROUGH' -exec ls -la {} \;
echo "  inside --work export:                       $(find $work -name 'EVIL-WRITETHROUGH' | wc -l) entry"
echo "  inside the scratch clone:                   $(find $D -name 'EVIL-WRITETHROUGH' -not -path '*/.git/*' | wc -l) entry"

echo
echo "== restoring the scratch clone"
git -C $D reset -q --hard $TIP
git -C $D clean -qfd
echo "  counter sha256=$(sha256sum $D/tools/round64-c2-counter.py | cut -d' ' -f1)"
echo "  tip=$(git -C $D rev-parse HEAD)"
