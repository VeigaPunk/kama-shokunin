#!/usr/bin/env bash
# X2Battery no-harm driver: measure.sh's command list, pointed at this seat's out dir.
# usage: measure-x2.sh <label> <full-tip>
# Differences from the L1 script, all recorded in the report:
#   * receipts land in this seat's out dir (lane measured/ is read-only for a leaf);
#   * clone is --shared (seat directive) instead of a full clone;
#   * at the base the two round-51 counters do not exist in the tree, so the frozen
#     bytes from the lane's tools/ are run with --repo <clone> (the base controls were
#     produced the same way: base.c1.out/base.c2.out carry their tip line only).
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/X2Battery/runs
BASE=57a2e25bf702b03aa61f9265e968cf68058ecb82
LABEL=$1; TIP=$2
S=/fast/scratch/hyaku/kama-r51/X2Battery/$LABEL
rm -rf "$S"; mkdir -p "$S" "$OUT"
export TMPDIR="$S"
git clone -q --shared "$LANE" "$S/lane" || { echo "clone failed" >&2; exit 3; }
git -C "$S/lane" checkout -q --detach "$TIP" || { echo "checkout failed" >&2; exit 3; }
cd "$S/lane" || exit 3
echo "label=$LABEL tip=$(git rev-parse HEAD) now=$(date -u +%FT%TZ)"
# the two round-51 counters: clone's own bytes when present, else the frozen lane bytes
C1=tools/round51-replay-exe-audit.py; [ -f "$C1" ] || C1=$LANE/tools/round51-replay-exe-audit.py
C2=tools/round51-append-audit-v6-check.py; [ -f "$C2" ] || C2=$LANE/tools/round51-append-audit-v6-check.py
echo "c1-src=$C1 sha=$(sha256sum "$C1" | cut -d' ' -f1)"
echo "c2-src=$C2 sha=$(sha256sum "$C2" | cut -d' ' -f1)"
run() {  # name, command...
  local name=$1; shift
  { echo "\$ $* (tip=$TIP)"; "$@"; echo "exit=$?"; } > "$OUT/$name-$LABEL.out" 2>&1
  echo "[$LABEL] $name: $(grep -v '^\$\|^detail' "$OUT/$name-$LABEL.out" | tail -2 | tr '\n' ' ' | cut -c1-200)"
}
run c1 python3 "$C1" --repo . --tip "$TIP" --scratch "$S"
run c2 python3 "$C2" --repo . --tip "$TIP" --scratch "$S"
run gate python3 tools/gate-registry-check.py --rev "$TIP"
run cap python3 tools/capability-repertoire-audit.py
run r41 python3 tools/round41-scorecard-reconcile.py
run r42 python3 tools/round42-selfdesc-reconcile.py
run r43 python3 tools/round43-registry-audit.py
run pointer python3 tools/planned-pointer-check.py SCORECARD.md
run digest python3 tools/digest-ledger.py scan --repo . --rev "$TIP"
run hexrun python3 tools/hexrun-census.py scan --repo . --rev "$TIP"
run sao python3 tools/sources-append-only.py --from "$BASE" --to "$TIP"
run aoa python3 tools/append-only-audit.py --repo . --to "$TIP"
run aoa-selftest python3 tools/append-only-audit.py --selftest --scratch "$S"
run klr-selftest python3 tools/kama-live-replay.py --selftest --scratch "$S"
run live-selftest python3 tools/kama-llamacpp-live.py --selftest
run cr-selftest python3 tests/llamacpp-live/check-receipt.py --selftest
run tally python3 tools/shortcut-tally.py --repo . --rev "$TIP"
run r48c2 python3 tools/round48-live-replay-v5-audit.py --repo . --tip "$TIP" --scratch "$S"
run r49c1 python3 tools/round49-replay-witness-audit.py --repo . --tip "$TIP" --scratch "$S"
run r49c2 python3 tools/round49-append-audit-v4-check.py --repo . --tip "$TIP" --scratch "$S"
run r50c1 python3 tools/round50-replay-bind-audit.py --repo . --tip "$TIP" --scratch "$S"
run r50c2 python3 tools/round50-append-audit-v5-check.py --repo . --tip "$TIP" --scratch "$S"
run census bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
echo "[$LABEL] done"
