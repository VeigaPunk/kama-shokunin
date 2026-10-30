#!/bin/bash
# Mutant battery for the C2 counter's ENVIRONMENT / SANDBOX axis.
# Seat MT41EnvAndSandboxC2, round 64 wave f, tip 23b3fdb1a925.
#
# Direction A (mutated COUNTER, committed tool): the counter file in the
#   scratch clone is patched and COMMITTED; the mutated counter is then run
#   from its clone path with --tip = that commit (the committed tool blobs
#   are untouched, so the pin table still reads 13/13).
# Direction B (mutated TIP FILE, unmutated counter): a tip file in the clone
#   is patched and committed; the PRISTINE counter scores the new tip.
#
# Each direction-A mutant is scored TWICE:
#   base    = the operator's normal environment
#   hostile = HTTP_PROXY/HTTPS_PROXY/http_proxy/https_proxy, PYTHONPATH,
#             PYTHONSTARTUP, GIT_DIR, GIT_CONFIG_COUNT/GIT_CONFIG_KEY_0/
#             GIT_CONFIG_VALUE_0, GIT_CONFIG_GLOBAL, GIT_ASKPASS,
#             GIT_TERMINAL_PROMPT, LANG=C, LC_ALL=C
#
# KILL CONVENTION (round-64 recipe):
#   KILLED   = the pair prints met=False, or the named control/field
#              escapes (the counter's own battery noticed).
#   SURVIVED = the pair still prints met=True (the counter's own battery
#              did not notice -> a coverage finding for C2).
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2
D=$S/clone
TIP=23b3fdb1a925129a9961cf551f6d40bf251602cb
MUT=$S/mutants
OUT=$S/out-mut
mkdir -p $MUT $OUT
CTR=$D/tools/round64-c2-counter.py
PRISTINE_SHA=$(sha256sum $CTR | cut -d' ' -f1)
echo "pristine counter sha256=$PRISTINE_SHA"
FIX=$S/fixtures

hash_tree() {
  ( cd "$1" && find . -type f -not -path './.git/*' -print0 | sort -z | \
      xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 )
}

restore_all() {
  git -C $D reset -q --hard $TIP
  git -C $D clean -qfd
  local s
  s=$(sha256sum $CTR | cut -d' ' -f1)
  echo "RESTORE counter sha256=$s pristine=$PRISTINE_SHA match=$([ "$s" = "$PRISTINE_SHA" ] && echo yes || echo NO)"
}

commit_all() {
  git -C $D add -A
  git -C $D -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "$1"
  git -C $D rev-parse HEAD
}

hostile_env() {
  env HTTP_PROXY=http://127.0.0.1:9 \
      HTTPS_PROXY=http://127.0.0.1:9 \
      http_proxy=http://127.0.0.1:9 \
      https_proxy=http://127.0.0.1:9 \
      NO_PROXY= \
      PYTHONPATH=$FIX/pypath \
      PYTHONSTARTUP=$FIX/pystartup.py \
      GIT_DIR=$FIX/gitdir \
      GIT_CONFIG_COUNT=1 \
      GIT_CONFIG_KEY_0=core.pager \
      GIT_CONFIG_VALUE_0=/bin/false \
      GIT_CONFIG_GLOBAL=$FIX/gitconfig \
      GIT_CONFIG_NOSYSTEM=1 \
      GIT_ASKPASS=/bin/false \
      GIT_TERMINAL_PROMPT=0 \
      LANG=C LC_ALL=C \
      "$@"
}

# ------------------------------------------------- direction A: counter ----
cat > $MUT/e1_env_allowlist.py <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
old = "        self.env = {k: v for k, v in os.environ.items() if k in ENV_KEYS}"
new = "        self.env = dict(os.environ)"
assert s.count(old) == 1
open(p, 'w').write(s.replace(old, new, 1))
PYEOF

cat > $MUT/e2_overlay_to_lane.py <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
old = """                os.symlink(os.path.join(self.tip_tree, name),
                           os.path.join(dest, name))"""
new = """                os.symlink(os.path.join(self.repo, name),
                           os.path.join(dest, name))"""
assert s.count(old) == 1
open(p, 'w').write(s.replace(old, new, 1))
PYEOF

cat > $MUT/e3_tmpdir_outside.py <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
old = "        self.env['TMPDIR'] = self.runroot"
new = "        self.env['TMPDIR'] = '/tmp'"
assert s.count(old) == 1
open(p, 'w').write(s.replace(old, new, 1))
PYEOF

cat > $MUT/e4_recon_tmpdir_outside.py <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
old = "    env['TMPDIR'] = work\n    env['PYTHONDONTWRITEBYTECODE'] = '1'"
new = "    env['TMPDIR'] = '/tmp'\n    env['PYTHONDONTWRITEBYTECODE'] = '1'"
assert s.count(old) == 1
open(p, 'w').write(s.replace(old, new, 1))
PYEOF

cat > $MUT/e5_git_env_leak.py <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
old = "    return {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}"
new = "    return dict(os.environ)"
assert s.count(old) == 1
open(p, 'w').write(s.replace(old, new, 1))
PYEOF

run_counter_mutant() {
  name=$1; patch=$2
  restore_all >/dev/null
  python3 "$patch" "$CTR" || { echo "### mutant=$name PATCH FAILED"; return 1; }
  local s; s=$(sha256sum $CTR | cut -d' ' -f1)
  local T; T=$(commit_all "mutant $name")
  echo "### mutant=$name counter_sha256=$s tip=$T"
  for mode in base hostile; do
    local work=$S/work-mut-$name-$mode
    rm -rf "$work"
    if [ "$mode" = hostile ]; then
      ( cd $D/tools && hostile_env python3 round64-c2-counter.py --repo $D --tip "$T" --work "$work" ) \
          > $OUT/$name.$mode.out 2> $OUT/$name.$mode.err
    else
      ( cd $D/tools && python3 round64-c2-counter.py --repo $D --tip "$T" --work "$work" ) \
          > $OUT/$name.$mode.out 2> $OUT/$name.$mode.err
    fi
    echo "--- mutant=$name mode=$mode exit=$?"
    cat $OUT/$name.$mode.out
  done
  restore_all
}

# ---------------------------------------------- direction B: tip file ------
# B/T1: the executed-but-UNPINNED tool tools/shortcut-tally.py (the tally
#       reader the counter runs three times) writes into the repo under
#       judgment and into the tip export at run time.
cat > $MUT/t1_tally_writes.py <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
old = "    args = ap.parse_args(argv)\n"
new = """    args = ap.parse_args(argv)
    try:
        with open(os.path.join(str(args.repo), 'EVIL-TALLY-IN-LANE-CLONE'), 'w') as _f:
            _f.write('written by shortcut-tally at run time\\n')
        with open('EVIL-TALLY-IN-TIP-EXPORT', 'w') as _f:
            _f.write('written by shortcut-tally at run time (cwd)\\n')
    except OSError:
        pass
"""
assert s.count(old) == 1
s = s.replace(old, new, 1)
assert "import shutil\n" in s
s = s.replace("import shutil\n", "import os\nimport shutil\n", 1)
open(p, 'w').write(s)
PYEOF

# B/T2: the UNPINNED tip file registry/capability-regress-r64.tsv plants a
#       one-line regression that WRITES THROUGH the overlay's symlink into
#       the tip export (cwd of a regression run is the overlay tree).
cat > $MUT/t2_regress_writethrough.py <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
lines = s.splitlines(True)
out = []
done = False
for ln in lines:
    cells = ln.rstrip('\n').split('\t')
    if not done and cells and cells[0] == 'sources-registry':
        assert len(cells) == 4, cells
        cells[3] = ("if open('registry/EVIL-WRITETHROUGH', 'w') or new is None:")
        ln = '\t'.join(cells) + '\n'
        done = True
    out.append(ln)
assert done
open(p, 'w').write(''.join(out))
PYEOF

run_tip_mutant() {
  name=$1; target=$2; patch=$3
  restore_all >/dev/null
  python3 "$patch" "$D/$target" || { echo "### mutant=$name PATCH FAILED"; return 1; }
  local s; s=$(sha256sum "$D/$target" | cut -d' ' -f1)
  local T; T=$(commit_all "mutant $name")
  echo "### mutant=$name file=$target sha256=$s tip=$T"
  local work=$S/work-mut-$name
  rm -rf "$work"
  local before; before=$(hash_tree $D)
  ( cd $D/tools && python3 round64-c2-counter.py --repo $D --tip "$T" --work "$work" ) \
      > $OUT/$name.out 2> $OUT/$name.err
  echo "--- mutant=$name exit=$?"
  cat $OUT/$name.out
  local after; after=$(hash_tree $D)
  echo "lane_clone_tree before=$before after=$after changed=$([ "$before" = "$after" ] && echo no || echo YES)"
  echo "EVIL-TALLY-IN-LANE-CLONE in clone : $(ls $D/EVIL-TALLY-IN-LANE-CLONE 2>/dev/null | wc -l)"
  echo "EVIL-TALLY-IN-TIP-EXPORT in export: $(find $work/tip -name 'EVIL-TALLY-IN-TIP-EXPORT' 2>/dev/null | wc -l)"
  echo "EVIL-WRITETHROUGH in export     : $(find $work/tip -name 'EVIL-WRITETHROUGH' 2>/dev/null | wc -l)"
  echo "EVIL-WRITETHROUGH in clone       : $(find $D -name 'EVIL-WRITETHROUGH' -not -path '*/.git/*' 2>/dev/null | wc -l)"
  restore_all
}

echo "===== direction A: mutated counter ====="
run_counter_mutant e1_env_allowlist          $MUT/e1_env_allowlist.py
run_counter_mutant e2_overlay_to_lane        $MUT/e2_overlay_to_lane.py
run_counter_mutant e3_tmpdir_outside         $MUT/e3_tmpdir_outside.py
run_counter_mutant e4_recon_tmpdir_outside   $MUT/e4_recon_tmpdir_outside.py
run_counter_mutant e5_git_env_leak           $MUT/e5_git_env_leak.py

echo "===== direction B: mutated tip file ====="
run_tip_mutant t1_tally_writes tools/shortcut-tally.py $MUT/t1_tally_writes.py
run_tip_mutant t2_regress_writethrough registry/capability-regress-r64.tsv $MUT/t2_regress_writethrough.py

echo "===== final state ====="
git -C $D status --porcelain | head
git -C $D log --oneline -1
sha256sum $CTR
echo "pristine_sha256=$PRISTINE_SHA"
