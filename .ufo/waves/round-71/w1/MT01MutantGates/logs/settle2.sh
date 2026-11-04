#!/bin/bash
L=/home/vgpnk/Projects/shokunin/kama-shokunin/tools
log=/fast/scratch/hyaku/kama-r71/MT01MutantGates/logs/settle2.log
prev=""; stable=0
for i in $(seq 1 16); do
  cur=$(sha256sum "$L/census-waiver-boundary.py" "$L/round71-province-host-claims.py" "$L/pre-report-gate.py" | sha256sum | cut -d' ' -f1)
  echo "settle2 $i $(date +%H:%M:%S) $cur" >> "$log"
  if [ "$cur" = "$prev" ]; then stable=$((stable+1)); else stable=0; fi
  [ "$stable" -ge 2 ] && { echo "STABLE $cur" >> "$log"; exit 0; }
  prev=$cur; sleep 45
done
echo "NOT_STABLE" >> "$log"
