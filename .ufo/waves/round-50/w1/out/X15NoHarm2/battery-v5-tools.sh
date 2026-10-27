#!/usr/bin/env bash
# X15NoHarm2 round-50 regression battery, part 1: the cheap lane instruments and the
# four selftests, run at the round-50 build tip on this seat's own shared clone.
# Receipts land beside this script as <name>.out. usage: battery-v5-tools.sh <clone> <tip> <scratch>
set -u
REPO=$1; TIP=$2; S=$3
BASE=26ecba64ad6fb571d09074b07202d1618a46ecd1
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
export TMPDIR="$S"
cd "$REPO" || exit 1
run() {  # name, command...
  local name=$1; shift
  { echo "\$ $* (tip=$TIP)"; "$@"; echo "exit=$?"; } > "$HERE/$name.out" 2>&1
  echo "$name: $(grep -v '^\$\|^detail' "$HERE/$name.out" | tail -2 | tr '\n' ' ' | cut -c1-220)"
}
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
echo DONE
