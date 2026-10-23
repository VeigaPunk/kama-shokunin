#!/usr/bin/env bash
# D3: shell writer with an 8 KiB seed, cap 2048 (2 MiB), timeout 3.
# The loop can reach the cap inside the 3 s budget, so this row shows whether the
# cap bounds a shell `cat` writer and whether it stops the loop.
set -u
ulimit -f 1048576 || { echo "GUARD_SET_FAILED"; exit 90; }
ulimit -c 0
cd /fast/scratch/hyaku/kama-r27c/ExecFixtureBoundDemo || exit 91

rm -f seed8.txt grow3.txt D3.log D3.stdout D3.stderr
python3 -c 'open("seed8.txt","wb").write(b"kama-a3-shell-seed\n"*420)'
echo "D3_seed_size=$(stat -c %s seed8.txt)"

( ulimit -f 2048; exec timeout 3 bash -c 'i=0; while :; do i=$((i+1)); echo "iter=$i" >> D3.log; cat seed8.txt >> grow3.txt; done' ) >D3.stdout 2>D3.stderr
echo "D3_exit=$?"
echo "D3_final_size=$(stat -c %s grow3.txt)"
echo "D3_iterations=$(grep -c '^iter=' D3.log || echo 0)"
echo "D3_stderr_lines=$(wc -l < D3.stderr)"
echo "D3_stderr_first=$(head -1 D3.stderr)"
[ "$(stat -c %s grow3.txt)" -le 2097152 ] && echo "D3_size<=2097152=YES" || echo "D3_size<=2097152=NO"
echo "D3_leftover=$(pgrep -fc 'grow3\.txt' || true)"

rm -f seed8.txt grow3.txt D3.log D3.stdout D3.stderr
echo "D3_cleanup_remaining:"; ls -la
