#!/usr/bin/env bash
# CritTradeoffHarm: the T01 partial-clone refusal vs a `git clone --shared` (seat recipe) of a partial clone.
set -u
FX=/tmp/kama-r23w2/CritTradeoffHarm-fx
G() { GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git "$@"; }
C() { G -c user.name="$1" -c user.email=a@x "${@:2}"; }
T=$(mktemp -d $FX/sop.XXXX)
S=$T/src; L=$T/lane; G init -q -b master $S; G init -q -b master $L
echo w >> $L/f; G -C $L add f
GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000" C kama-shokunin -C $L commit -q -m "round-1: work"
LC=$(G -C $L rev-parse HEAD)
echo payload > $S/big; G -C $S add big
GIT_AUTHOR_DATE="@1500 +0000" GIT_COMMITTER_DATE="@1500 +0000" C f -C $S commit -q -m big
BLOB=$(G -C $S rev-parse HEAD:big)
mkdir -p $S/.ufo/reports/round-1
printf '## Work performed\nevidence blob %s\n## Landed changes\n- %s\n' "$BLOB" "${LC:0:12}" > $S/.ufo/reports/round-1/kama.md
G -C $S add .ufo
GIT_AUTHOR_DATE="@2000 +0000" GIT_COMMITTER_DATE="@2000 +0000" C fleet -C $S commit -q -m "round-1: report"
G -C $S config uploadpack.allowFilter true; G -C $S config uploadpack.allowAnySHA1InWant true
P=$T/partial
G -c protocol.file.allow=always clone -q --filter=blob:none --no-checkout "file://$S" $P
G -C $P cat-file blob HEAD:.ufo/reports/round-1/kama.md >/dev/null
SH=$T/shared
G clone -q --shared --no-checkout $P $SH
echo "partial: promisor_cfg=$(G -C $P config --get remote.origin.promisor) packs=$(ls $P/.git/objects/pack | grep -c promisor)"
echo "shared:  promisor_cfg=$(G -C $SH config --get remote.origin.promisor || echo none) packs=$(ls $SH/.git/objects/pack | grep -c promisor) alternates=$(cat $SH/.git/objects/info/alternates)"
for arm in current frozen; do
  for fl in shared partial; do
    F=$T/$fl
    pre=$(G -C $F --no-lazy-fetch cat-file -e $BLOB 2>/dev/null && echo yes || echo no)
    python3 $FX/arms/$arm.py --lane-repo $L --fleet-repo $F --rounds 1 --no-errata --json >$T/$arm-$fl.out 2>$T/$arm-$fl.err
    rc=$?
    post=$(G -C $F --no-lazy-fetch cat-file -e $BLOB 2>/dev/null && echo yes || echo no)
    d=$(python3 -c 'import json,sys
r=json.load(open(sys.argv[1]))["results"][0]; print([(x["kind"],x["token"][:10]) for x in r["defects"]])' $T/$arm-$fl.out 2>/dev/null || echo no-json)
    echo "$arm fleet=$fl exit=$rc blob_local_before=$pre after=$post defects=$d err=$(tail -c 160 $T/$arm-$fl.err | tr '\n' ' ')"
  done
done
echo "truth: blob $BLOB exists in fleet source: $(G -C $S cat-file -t $BLOB)"
echo T=$T
