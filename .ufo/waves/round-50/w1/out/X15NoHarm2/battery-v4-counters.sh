#!/usr/bin/env bash
# X15NoHarm2 round-50 regression battery, part 2: the round-48 C2 counter and both
# round-49 counters, run at the round-50 build tip on this seat's own shared clone.
# Receipts land beside this script as <name>.out. usage: battery-v4-counters.sh <clone> <tip> <scratch>
set -u
REPO=$1; TIP=$2; S=$3
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
export TMPDIR="$S"
cd "$REPO" || exit 1
run() {  # name, command...
  local name=$1; shift
  { echo "\$ $* (tip=$TIP)"; "$@"; echo "exit=$?"; } > "$HERE/$name.out" 2>&1
  echo "$name: $(grep -v '^\$\|^detail' "$HERE/$name.out" | tail -2 | tr '\n' ' ' | cut -c1-220)"
}
run r48c2 python3 tools/round48-live-replay-v5-audit.py --repo . --tip "$TIP" --scratch "$S/r48"
run r49c1 python3 tools/round49-replay-witness-audit.py --repo . --tip "$TIP" --scratch "$S/r49c1"
run r49c2 python3 tools/round49-append-audit-v4-check.py --repo . --tip "$TIP" --scratch "$S/r49c2"
echo DONE
