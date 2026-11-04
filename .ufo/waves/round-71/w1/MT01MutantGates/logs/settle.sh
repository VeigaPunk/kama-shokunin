#!/bin/bash
L=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/census-waiver-boundary.py
prev=""; stable=0
for i in $(seq 1 20); do
  cur=$(sha256sum "$L" | cut -d' ' -f1)
  echo "settle $i $(date +%H:%M:%S) $cur" >> /fast/scratch/hyaku/kama-r71/MT01MutantGates/logs/settle.log
  if [ "$cur" = "$prev" ]; then stable=$((stable+1)); else stable=0; fi
  [ "$stable" -ge 2 ] && { echo "STABLE $cur" >> /fast/scratch/hyaku/kama-r71/MT01MutantGates/logs/settle.log; exit 0; }
  prev=$cur; sleep 40
done
echo "NOT_STABLE" >> /fast/scratch/hyaku/kama-r71/MT01MutantGates/logs/settle.log
