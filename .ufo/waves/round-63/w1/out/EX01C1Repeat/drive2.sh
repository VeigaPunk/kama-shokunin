#!/bin/bash
S=/fast/scratch/hyaku/kama-r63/w/EX01C1Repeat
C=$S/clone/tools/round63-c1-counter.py
R=/home/vgpnk/Projects/shokunin/kama-shokunin
T=03a6a1d850902a66a13dfad33f89cf3a8b759a09
cd $S
for cfg in "6 4" "7 32"; do set -- $cfg; n=$1; k=$2
  PIDS=""; for i in $(seq $k); do ( while :; do :; done ) & PIDS="$PIDS $!"; done
  sleep 6
  echo "[$n] loops=$k pids alive=$(ps -o pid= -p $(echo $PIDS|tr ' ' ,) | wc -l) load=$(cut -d' ' -f1-3 /proc/loadavg) cpu_of_loops=$(ps -o pcpu= -p $(echo $PIDS|tr ' ' ,) | tr '\n' ' ')" >> $S/log2.txt
  mkdir -p run$n; s=$(date +%s.%N)
  python3 $C --repo $R --tip $T --work $S/run$n > out$n.txt 2> err$n.txt; rc=$?; e=$(date +%s.%N)
  echo "[$n] rc=$rc wall=$(awk -v a=$s -v b=$e 'BEGIN{printf "%.1f", b-a}')s load_end=$(cut -d' ' -f1-3 /proc/loadavg)" >> $S/log2.txt
  kill $PIDS; wait $PIDS 2>/dev/null
done
echo ALLDONE >> $S/log2.txt
