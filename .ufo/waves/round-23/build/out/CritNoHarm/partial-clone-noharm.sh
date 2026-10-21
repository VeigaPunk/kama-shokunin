#!/usr/bin/env bash
# CritNoHarm P1': legitimate blob:none partial clone (file:// promisor, no network); fresh clone per arm.
set -u
FROZEN=/tmp/kama-r23/CritNoHarm-probe/frozen/report-landing-audit.py
CAND=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
T=$(mktemp -d /tmp/kama-r23/CritNoHarm-probe/partial.XXXX)
S=$T/src; L=$T/lane; git init -q -b master $S; git init -q -b master $L
echo w >> $L/f; git -C $L add f
GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000" git -C $L -c user.name=kama-shokunin -c user.email=a@x commit -q -m "round-1: work"
LC=$(git -C $L rev-parse HEAD)
echo payload > $S/big; git -C $S add big
GIT_AUTHOR_DATE="@1500 +0000" GIT_COMMITTER_DATE="@1500 +0000" git -C $S -c user.name=f -c user.email=a@x commit -q -m big
BLOB=$(git -C $S rev-parse HEAD:big)
mkdir -p $S/.ufo/reports/round-1
printf '## Work performed\nevidence blob %s\n## Landed changes\n- %s\n' "$BLOB" "${LC:0:12}" > $S/.ufo/reports/round-1/kama.md
git -C $S add .ufo
GIT_AUTHOR_DATE="@2000 +0000" GIT_COMMITTER_DATE="@2000 +0000" git -C $S -c user.name=fleet -c user.email=a@x commit -q -m "round-1: report"
git -C $S config uploadpack.allowFilter true; git -C $S config uploadpack.allowAnySHA1InWant true
for arm in frozen cand; do
  s=$FROZEN; [ $arm = cand ] && s=$CAND
  F=$T/fleet-$arm
  git clone -q --filter=blob:none --no-checkout "file://$S" $F
  git -C $F cat-file blob HEAD:.ufo/reports/round-1/kama.md >/dev/null
  pre=$(git -C $F --no-lazy-fetch cat-file -e $BLOB 2>/dev/null && echo yes || echo no)
  python3 "$s" --lane-repo $L --fleet-repo $F --rounds 1 --no-errata --json >$T/$arm.out 2>$T/$arm.err
  rc=$?
  post=$(git -C $F --no-lazy-fetch cat-file -e $BLOB 2>/dev/null && echo yes || echo no)
  d=$(python3 -c 'import json,sys
r=json.load(open(sys.argv[1]))["results"][0]; print([(x["kind"],x["token"][:10]) for x in r["defects"]])' $T/$arm.out 2>/dev/null || echo no-json)
  echo "$arm exit=$rc blob_local_before=$pre after=$post defects=$d err=$(tail -c 200 $T/$arm.err | tr '\n' ' ')"
done
echo T=$T
