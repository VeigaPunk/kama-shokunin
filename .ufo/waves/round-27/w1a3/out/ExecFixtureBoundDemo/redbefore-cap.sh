#!/usr/bin/env bash
# Strict red-before / fix pair for the file-size-cap fix, gate-shaped per
# fleet CORPUS.md:179-183 ("A fix is shown able to fail before it counts"):
# one detector command, the SAME fixture bytes and timeout, only `ulimit -f`
# differs between the red state and the fixed state.
#
#   red   : ulimit -f 20480 (20 MiB)  -- the 2 MiB bound is absent
#   fixed : ulimit -f 2048  (2 MiB)   -- the fix
#
# The detector exits non-zero with an observed failure string when the fixture
# finished above the 2 MiB bound, and 0 when it stayed within it.  The writer's
# own exit is expected to be 153 (SIGXFSZ) in BOTH arms; it is recorded but is
# not the detector's verdict.
set -u
ulimit -f 1048576 || { echo "GUARD_SET_FAILED"; exit 90; }
ulimit -c 0
cd /fast/scratch/hyaku/kama-r27c/ExecFixtureBoundDemo || exit 91

BOUND=2097152

detector() {  # detector <cap_blocks>
  local lim=$1 wexit size estderr
  rm -f rb-fixture.py rb.log rb.stderr
  cp fixture.template.py rb-fixture.py
  ( ulimit -f "$lim"; export PROGRESS_LOG=rb.log A3_SIG_DFL=1; exec timeout 5 python3 rb-fixture.py ) 2>rb.stderr
  wexit=$?
  size=$(stat -c %s rb-fixture.py)
  estderr=$(head -1 rb.stderr)
  echo "detector cap_blocks=$lim writer_exit=$wexit writer_exit_is_sigxfsz=$([ "$wexit" -eq 153 ] && echo YES || echo NO) final_size=$size bound=$BOUND writer_stderr_first=[$estderr]"
  rm -f rb-fixture.py rb.log rb.stderr
  if [ "$size" -le "$BOUND" ]; then
    echo "detector cap_blocks=$lim RESULT=clean"
    return 0
  fi
  echo "detector cap_blocks=$lim RESULT=NON-CLEAN reason=file_exceeded_2MiB_bound size=$size bound=$BOUND" >&2
  return 3
}

echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) fixture_sha256=$(sha256sum fixture.template.py | cut -d' ' -f1)"
echo "== red-before: cap 20480 (20 MiB), 2 MiB bound absent =="
detector 20480
RED_EXIT=$?
echo "RED_EXIT=$RED_EXIT"
echo "== fixed: cap 2048 (2 MiB), same detector command, only the cap changed =="
detector 2048
FIX_EXIT=$?
echo "FIX_EXIT=$FIX_EXIT"
if [ "$RED_EXIT" -ne 0 ] && [ "$FIX_EXIT" -eq 0 ]; then
  echo "pair_verdict=RED_NONCLEAN_FIX_CLEAN"
else
  echo "pair_verdict=PAIR_FAILED"
fi
echo "remaining:"; ls -la
