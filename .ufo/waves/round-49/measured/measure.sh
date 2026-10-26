#!/usr/bin/env bash
# Round-49 measurement: claim counters and tip regressions on a fresh clone at <tip>.
# usage: measure.sh <tip> <suffix>   (receipts land beside this file as <name><suffix>.out)
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
HERE="$LANE/.ufo/waves/round-49/measured"
BASE=438127bc01ff3b99f98468549d58046f932490ef
TIP=$1; SUF=$2
S=/fast/scratch/hyaku/kama-r49/L1/meas$SUF
rm -rf "$S"; mkdir -p "$S"; export TMPDIR="$S"
trap 'rm -rf -- "$S"' EXIT
git clone -q "$LANE" "$S/lane"
git -C "$S/lane" checkout -q --detach "$TIP"
cd "$S/lane"
run() {  # name, command...
  local name=$1; shift
  { echo "\$ $* (tip=$TIP)"; "$@"; echo "exit=$?"; } > "$HERE/$name$SUF.out" 2>&1
  echo "$name$SUF: $(grep -v '^\$\|^detail' "$HERE/$name$SUF.out" | tail -2 | tr '\n' ' ' | cut -c1-220)"
}
run c1 python3 tools/round49-replay-witness-audit.py --repo . --tip "$TIP" --scratch "$S"
run c2 python3 tools/round49-append-audit-v4-check.py --repo . --tip "$TIP" --scratch "$S"
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
run r48c1 python3 tools/round48-append-audit-v3-check.py --repo . --tip "$TIP" --scratch "$S"
run r48c2 python3 tools/round48-live-replay-v5-audit.py --repo . --tip "$TIP" --scratch "$S"
