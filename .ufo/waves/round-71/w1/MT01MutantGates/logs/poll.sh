#!/bin/bash
L=/home/vgpnk/Projects/shokunin/kama-shokunin
for i in $(seq 1 20); do
  n=0
  for f in tools/pre-report-gate.py tools/census-waiver-boundary.py tools/round71-province-host-claims.py; do
    [ -f "$L/$f" ] && n=$((n+1))
  done
  echo "poll $i $(date +%H:%M:%S) present=$n" >> poll.log
  [ "$n" -eq 3 ] && { echo "ALL_PRESENT" >> poll.log; exit 0; }
  sleep 60
done
echo "TIMEOUT" >> poll.log
