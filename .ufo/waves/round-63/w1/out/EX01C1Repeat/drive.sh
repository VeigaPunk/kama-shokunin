#!/bin/bash
S=/fast/scratch/hyaku/kama-r63/w/EX01C1Repeat
C=$S/clone/tools/round63-c1-counter.py
R=/home/vgpnk/Projects/shokunin/kama-shokunin
T=03a6a1d850902a66a13dfad33f89cf3a8b759a09
cd $S
run() { n=$1; shift; mkdir -p $S/run$n; s=$(date +%s.%N); echo "[$n] start $(date -Is) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $S/log.txt
  env "$@" python3 $C --repo $R --tip $T --work $S/run$n > $S/out$n.txt 2> $S/err$n.txt; rc=$?; e=$(date +%s.%N)
  echo "[$n] rc=$rc wall=$(awk -v a=$s -v b=$e "BEGIN{printf \"%.1f\", b-a}")s load_end=$(cut -d' ' -f1-3 /proc/loadavg)" >> $S/log.txt; }
run 1 X=1; run 2 X=1; run 3 X=1
run 4 HTTP_PROXY=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9
PIDS=""; for i in 1 2 3 4; do ( while :; do :; done ) & PIDS="$PIDS $!"; done
echo "[5] busy pids:$PIDS load_before=$(cut -d' ' -f1-3 /proc/loadavg)" >> $S/log.txt
run 5 X=1
kill $PIDS; wait $PIDS 2>/dev/null
echo ALLDONE >> $S/log.txt
