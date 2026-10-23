#!/usr/bin/env bash
# ExecFixtureBoundDemo extra rows — round 27 attempt 3, lane kama.
#  D2: shell writer (separate seed, appends into grow.txt) under 2 MiB -> cat gets
#      EFBIG per iteration because bash ignores SIGXFSZ; file must stay at the cap
#      while the loop spins until timeout.
#  E2: Python writer with the cap's OSError swallowed (SIGXFSZ left ignored as bash
#      hands it over) -> process survives, file must stay at the cap.
set -u
ulimit -f 1048576 || { echo "GUARD_SET_FAILED"; exit 90; }
ulimit -c 0
cd /fast/scratch/hyaku/kama-r27c/ExecFixtureBoundDemo || exit 91

echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) df_fast=$(df -h /fast | tail -1)"

echo "== D2: shell loop, separate seed, cap 2048 (2 MiB), timeout 3 =="
rm -f seed.txt grow.txt D2.log D2.stdout D2.stderr
printf 'MARKER-A3-SHELL-FIXTURE line1\nMARKER-A3-SHELL-FIXTURE line2\n' > seed.txt
( ulimit -f 2048; export D2_LOG=D2.log; exec timeout 3 bash -c 'i=0; while :; do i=$((i+1)); echo "iter=$i" >> "$D2_LOG"; cat seed.txt >> grow.txt; done' ) >D2.stdout 2>D2.stderr
echo "D2_exit=$?"
echo "D2_final_size=$(stat -c %s grow.txt)"
echo "D2_iterations=$(grep -c '^iter=' D2.log 2>/dev/null || echo 0)"
echo "D2_stderr_first=$(head -1 D2.stderr)"
echo "D2_stderr_lines=$(wc -l < D2.stderr)"
[ "$(stat -c %s grow.txt)" -le 2097152 ] && echo "D2_size<=2097152=YES" || echo "D2_size<=2097152=NO"
echo "D2_leftover=$(pgrep -fc 'grow\.txt' || true)"
echo

echo "== E2: Python writer, OSError swallowed, SIGXFSZ ignored (bash inherited), cap 2048, timeout 3 =="
rm -f fixture.py E2.log E2.stdout E2.stderr
cp fixture.template.py fixture.py
( ulimit -f 2048; export PROGRESS_LOG=E2.log A3_SIG_DFL=0 A3_SWALLOW=1; exec timeout 3 python3 fixture.py ) >E2.stdout 2>E2.stderr
echo "E2_exit=$?"
echo "E2_final_size=$(stat -c %s fixture.py)"
echo "E2_progress_head=$(head -1 E2.log)"
echo "E2_swallowed_lines=$(grep -c '^swallowed' E2.log || echo 0)"
echo "E2_last_swallow=$(grep '^swallowed' E2.log | tail -1)"
echo "E2_stderr=$(tr '\n' '|' < E2.stderr | cut -c1-200)"
[ "$(stat -c %s fixture.py)" -le 2097152 ] && echo "E2_size<=2097152=YES" || echo "E2_size<=2097152=NO"
echo "E2_leftover=$(pgrep -fc 'fixture\.py' || true)"
echo

echo "== cleanup =="
rm -f fixture.py grow.txt seed.txt a.log a.stderr a.stdout
rm -f D2.log D2.stdout D2.stderr E2.log E2.stdout E2.stderr
ls -la
echo "du=$(/usr/bin/du -sh . | cut -f1)"
echo "df_fast_after=$(df -h /fast | tail -1)"
