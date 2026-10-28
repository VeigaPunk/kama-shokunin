#!/bin/bash
C=/fast/scratch/hyaku/kama-r64/b/MT07RefAgree/clone
T=f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
O=/fast/scratch/hyaku/kama-r64/b/MT07RefAgree
for i in $(seq -w 1 30); do
  python3 $C/tools/round64-c1-counter.py --repo $C --tip $T --work $O/work/d$i > $O/out-c2/run$i.out 2>&1
  echo "run$i exit=$?" >> $O/out-c2/exits.txt
done
echo DONE >> $O/out-c2/exits.txt
