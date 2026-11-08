#!/bin/bash
# $1=new|base $2=body $3=label $4=ncand
cd /fast/scratch/hyaku/kama-r95/RV01ProbeDiff
L1=$(cut -d' ' -f1 /proc/loadavg)
idxs=(); for ((i=0;i<$4;i++)); do idxs+=("$i"); done
start=$EPOCHREALTIME
if [ "$1" = new ]; then
  out=$(./new-run.sh "$2" "$4" "${idxs[@]}")
else
  out=$(./base-run.sh "$2" "${idxs[@]}")
fi
end=$EPOCHREALTIME
L2=$(cut -d' ' -f1 /proc/loadavg)
awk -v s="$start" -v e="$end" -v l1="$L1" -v l2="$L2" -v lab="$3" -v o="$out" \
 'BEGIN{n=split(o,a,"\n"); printf "%-22s load1=%s->%s wall=%.1fs lines=%d [%s]\n", lab, l1, l2, e-s, n, o}'
