#!/bin/bash
# Repeat the host-noise flake experiment N times: start the noise injector,
# run the unmodified counter once, record the output, stop the noise.
# usage: noise-trial.sh <n>
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT32FlakeHunt
D=$S/clone
N=${1:-3}
for i in $(seq 1 "$N"); do
  bash "$S/noise.sh" start >/dev/null
  cd "$D/tools" || exit 9
  python3 round64-c1-counter.py --repo "$D" \
    --tip 23b3fdb1a925129a9961cf551f6d40bf251602cb \
    --work "$S/work-noise-$i" >"$S/out/noise-$i.out" 2>"$S/out/noise-$i.err"
  echo "trial $i rc=$?"
  head -c 220 "$S/out/noise-$i.out"; echo
  [ -s "$S/out/noise-$i.err" ] && { echo "stderr:"; cat "$S/out/noise-$i.err"; }
  bash "$S/noise.sh" stop >/dev/null
  sleep 1
done
# clean up every root sleeper we spawned
for p in $(ps -eo pid,user,args | awk '$2=="root" && $3=="sleep" && $4=="45" {print $1}'); do
  sudo -n kill -9 "$p" 2>/dev/null
done
echo "remaining root sleep45: $(ps -eo user,args | awk '$1=="root" && $2=="sleep" && $3=="45"' | wc -l)"
exit 0
