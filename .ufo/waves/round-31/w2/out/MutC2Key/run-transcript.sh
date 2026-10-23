#!/bin/bash
# Re-runs each probe and records command, exit code, and full output.
run() {
  local label="$1"; shift
  echo "### $label"
  echo "\$ $*"
  "$@" > /tmp/kama-r31w2/MutC2Key/.tmp.out 2>&1
  local rc=$?
  cat /tmp/kama-r31w2/MutC2Key/.tmp.out
  echo "[exit $rc]"
  echo
}
cd /tmp/kama-r31w2/MutC2Key
run "P0 pristine clone counter (frozen bytes)" /usr/bin/python3 lane/.ufo/waves/round-31/count-c2.py --repo lane --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --list --out receipts/pristine.json
run "P1 lane itself, frozen counter" /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c2.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --list --out receipts/frozen-lane.json
run "M1 one correction row (row C1, class p1) / frozen counter" /usr/bin/python3 lane/.ufo/waves/round-31/count-c2.py --repo lane-one --tip HEAD --list --out receipts/frozen-one.json
run "M2 three corrections same row cell C1 / frozen counter" /usr/bin/python3 lane/.ufo/waves/round-31/count-c2.py --repo lane-three --tip HEAD --list --out receipts/frozen-three.json
run "M3 literal copy of existing round-11 C2 correction / frozen counter" /usr/bin/python3 lane/.ufo/waves/round-31/count-c2.py --repo lane-literal --tip HEAD --list --out receipts/frozen-literal.json
run "R0 round-qualified counter, pristine clone" /usr/bin/python3 counter-roundkey.py --repo lane --tip 382d11b2 --list --out receipts/roundkey-pristine.json
run "R1 round-qualified counter, one correction" /usr/bin/python3 counter-roundkey.py --repo lane-one --tip HEAD --list --out receipts/roundkey-one.json
run "R2 round-qualified counter, three corrections" /usr/bin/python3 counter-roundkey.py --repo lane-three --tip HEAD --list --out receipts/roundkey-three.json
run "R3 round-qualified counter, literal C2 duplicate" /usr/bin/python3 counter-roundkey.py --repo lane-literal --tip HEAD --list --out receipts/roundkey-literal.json
