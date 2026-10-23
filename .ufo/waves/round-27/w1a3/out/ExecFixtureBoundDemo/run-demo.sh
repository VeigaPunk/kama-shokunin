#!/usr/bin/env bash
# ExecFixtureBoundDemo harness v2 — round 27 attempt 3, lane kama.
# Shows the file-size cap (RLIMIT_FSIZE via `ulimit -f`) is able to fail a
# self-appending runaway fixture.
#
#   A0  ulimit -f 2048  (2 MiB) timeout 60, writer as-is  (bash leaves SIGXFSZ ignored)
#   A1  ulimit -f 2048  (2 MiB) timeout 60, SIGXFSZ=SIG_DFL  <- assignment (a), death path
#   B1  ulimit -f 20480 (20 MiB) timeout 5, SIGXFSZ=SIG_DFL  <- assignment (b), same loop
#   C0  ulimit -f 2048  (2 MiB) timeout 5, SIGXFSZ=SIG_DFL   <- identical-timeout control
#   D   shell `while :; do cat f >> f; done` under 2 MiB, timeout 3 (shape check)
#   E   ulimit -f 2048 timeout 3, OSError swallowed (writer survives the cap?)
#
# Every fixture/log write happens under the per-file guard below.
set -u

# disk-safety guard: 1 GiB per file for anything this harness creates
ulimit -f 1048576 || { echo "GUARD_SET_FAILED"; exit 90; }
# no core capture (core_pattern is a systemd-coredump pipe, `ulimit -c` was unlimited)
ulimit -c 0

cd /fast/scratch/hyaku/kama-r27c/ExecFixtureBoundDemo || exit 91
HERE=$PWD

echo "host=$(hostname) utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) bash=$BASH_VERSION"
echo "python=$(python3 -VV 2>&1 | head -1)"
echo "core_pattern=$(cat /proc/sys/kernel/core_pattern)"
echo "outer ulimit -f=$(ulimit -f) ulimit -c=$(ulimit -c)"
echo "df_fast_before=$(df -h /fast | tail -1)"
echo

echo "== disposition probe: SIGXFSZ (25) before any run =="
echo "bash self: $(grep -E '^(SigIgn|SigBlk)' /proc/self/status | tr '\n' ' ')"
python3 -c 'import signal,resource;print("python inherits SIGXFSZ handler=%r RLIMIT_FSIZE=%r" % (signal.getsignal(signal.SIGXFSZ), resource.getrlimit(resource.RLIMIT_FSIZE)))'
echo "trap - SIGXFSZ in bash then child python:"
bash -c 'trap - SIGXFSZ; grep -E "^SigIgn" /proc/self/status; python3 -c "import signal;print(\"  child handler=%r\" % (signal.getsignal(signal.SIGXFSZ),))"'
echo

echo "== units check: ulimit -f 2048 =="
( ulimit -f 2048; python3 -c 'import resource; s,h=resource.getrlimit(resource.RLIMIT_FSIZE); print("RLIMIT_FSIZE soft=%d hard=%d" % (s,h))' )
echo

detector() {  # detector <label> <size> <limit-bytes>
  if [ "$2" -le "$3" ]; then echo "$1_size<=$3=YES ($2)"; else echo "$1_size<=$3=NO ($2)"; fi
}

run_py() {     # run_py <label> <ulimit-f> <timeout-s> <envassign...>
  local label=$1 lim=$2 tmo=$3; shift 3
  rm -f fixture.py "$label.log" "$label.stdout" "$label.stderr"
  cp fixture.template.py fixture.py
  local t0 t1
  t0=$(date +%s%3N)
  ( ulimit -f "$lim"; export PROGRESS_LOG="$label.log"; [ $# -gt 0 ] && export "$@"; exec timeout "$tmo" python3 fixture.py ) >"$label.stdout" 2>"$label.stderr"
  LAST_EXIT=$?
  echo "${label}_exit=$LAST_EXIT"
  t1=$(date +%s%3N)
  echo "${label}_wall_ms=$((t1 - t0)) timeout_s=$tmo ulimit_f=$lim"
  echo "${label}_final_size=$(stat -c %s fixture.py)"
  echo "${label}_stdout_bytes=$(stat -c %s "$label.stdout")"
  echo "${label}_stderr=$(tr '\n' '|' < "$label.stderr" | cut -c1-300)"
  echo "${label}_progress_head=$(head -1 "$label.log" 2>/dev/null)"
  echo "${label}_progress_maxmib=$(sed -n 's/^crossed mib=\([0-9]*\).*/\1/p' "$label.log" | sort -n | tail -1)"
  echo "${label}_progress_tail=$(tail -1 "$label.log" 2>/dev/null)"
  echo "${label}_leftover_writer=$(pgrep -fc 'fixture\.py' || true)"
  return $LAST_EXIT
}

echo "== A0: assignment (a) exact writer, cap 2048 (2 MiB), timeout 60, no signal reset =="
run_py A0 2048 60 A3_SIG_DFL=0
A0_SIZE=$(stat -c %s fixture.py)
detector A0 "$A0_SIZE" 2097152
echo

echo "== A1: assignment (a) death path, cap 2048 (2 MiB), timeout 60, SIGXFSZ=SIG_DFL =="
run_py A1 2048 60 A3_SIG_DFL=1
A1_EXIT=$LAST_EXIT
A1_SIZE=$(stat -c %s fixture.py)
detector A1 "$A1_SIZE" 2097152
echo

# (b) only after (a) shows the cap: A1 must have died by SIGXFSZ with size exactly at the cap
if [ "$A1_EXIT" -ne 153 ] || [ "$A1_SIZE" -ne 2097152 ]; then
  echo "ABORT: (a) did not show the cap (exit=$A1_EXIT size=$A1_SIZE); (b) not run."
  exit 92
fi
echo "(a) showed the cap: exit 153 = SIGXFSZ, final size == 2097152; running (b)"

echo "== B1: assignment (b) same loop, cap 20480 (20 MiB), timeout 5, SIGXFSZ=SIG_DFL =="
run_py B1 20480 5 A3_SIG_DFL=1
B1_SIZE=$(stat -c %s fixture.py)
detector B1 "$B1_SIZE" 2097152
detector B1 "$B1_SIZE" 20971520
echo

echo "== C0: identical-timeout control, cap 2048 (2 MiB), timeout 5, SIGXFSZ=SIG_DFL =="
run_py C0 2048 5 A3_SIG_DFL=1
C0_SIZE=$(stat -c %s fixture.py)
detector C0 "$C0_SIZE" 2097152
echo

echo "== D: shell self-append loop, cap 2048, timeout 3 =="
rm -f grow.txt D.log D.stdout D.stderr
printf 'MARKER-A3-SHELL-FIXTURE line1\nMARKER-A3-SHELL-FIXTURE line2\n' > grow.txt
( ulimit -f 2048; export D_LOG=D.log; exec timeout 3 bash -c 'i=0; while :; do i=$((i+1)); echo "iter=$i" >> "$D_LOG"; cat grow.txt >> grow.txt; done' ) >D.stdout 2>D.stderr
echo "D_exit=$?"
echo "D_final_size=$(stat -c %s grow.txt)"
echo "D_iterations=$(grep -c '^iter=' D.log 2>/dev/null || echo 0)"
echo "D_stderr=$(tr '\n' '|' < D.stderr | cut -c1-200)"
detector D "$(stat -c %s grow.txt)" 2097152
echo

echo "== E: cap 2048, timeout 3, writer swallows OSError =="
run_py E 2048 3 A3_SIG_DFL=1 A3_SWALLOW=1
E_SIZE=$(stat -c %s fixture.py)
detector E "$E_SIZE" 2097152
echo "E_swallowed_lines=$(grep -c '^swallowed' E.log 2>/dev/null || echo 0)"
echo

echo "== leftover / cores =="
pgrep -af 'fixture\.py|grow\.txt' || echo "leftover_writers=none"
pgrep -af llama-server || echo "llama_server=none"
ls -la core* 2>/dev/null || echo "core_files=none"
echo

echo "== cleanup: runaway fixtures and per-run logs removed =="
rm -f fixture.py grow.txt
rm -f A0.log A1.log B1.log C0.log D.log E.log
rm -f A0.stdout A1.stdout B1.stdout C0.stdout D.stdout E.stdout
rm -f A0.stderr A1.stderr B1.stderr C0.stderr D.stderr E.stderr
echo "remaining_in_scratch:"; ls -la
echo "du=$(/usr/bin/du -sh . | cut -f1)"
echo "df_fast_after=$(df -h /fast | tail -1)"
