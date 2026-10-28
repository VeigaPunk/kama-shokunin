#!/bin/bash
C=/fast/scratch/hyaku/kama-r64/b/MT07RefAgree/clone
T=f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
for i in $(seq -w 1 30); do
  python3 $C/tools/round64-c1-counter.py --repo $C --tip $T --work /fast/scratch/hyaku/kama-r64/b/MT07RefAgree/work/c$i > /fast/scratch/hyaku/kama-r64/b/MT07RefAgree/out-c/run$i.out 2>&1
  echo "run$i exit=$?" >> /fast/scratch/hyaku/kama-r64/b/MT07RefAgree/out-c/exits.txt
done
echo DONE >> /fast/scratch/hyaku/kama-r64/b/MT07RefAgree/out-c/exits.txt
