#!/bin/sh
# R41B03 mutation probe: build a fixture repo commit carrying one pin-watch.py
# mutant, then run both bounded detectors on it:
#   1. python3 <mutant>/tools/pin-watch.py selftest
#   2. counter contract leg: round41-pinwatch-audit.py --repo <fixture> --tip <mutant commit> --seed 41
m="$1"; desc="$2"
E="/tmp/R41B03/export-$m"
D=$(mktemp -d "/tmp/R41B03-fixture-$m.XXXXXX") || exit 3
echo "$D" > "/tmp/R41B03/fixture-$m-path"
git -C "$D" init -q || exit 3
git -C /tmp/R41B03-clone archive 24aa1d3485c107f88b8b838892d43ea7587befcf | tar -x -C "$D" || exit 3
cp "$E/tools/pin-watch.py" "$D/tools/pin-watch.py" || exit 3
echo "== $m ($desc)"
sha256sum "$E/tools/pin-watch.py" "$D/tools/pin-watch.py"
git -C "$D" config user.name "R41B03 fixture"
git -C "$D" config user.email "r41b03@fixture.invalid"
T=$(git -C "$D" rev-parse --show-toplevel)
if [ "$(readlink -f "$T")" != "$(readlink -f "$D")" ]; then echo "TOPLEVEL MISMATCH: $T vs $D"; exit 3; fi
echo "toplevel OK: $T"
git -C "$D" add -A
git -C "$D" commit -qm "mutant $m: $desc" || exit 3
MSHA=$(git -C "$D" rev-parse HEAD)
echo "$MSHA" > "/tmp/R41B03/commit-$m"
echo "mutant commit: $MSHA"
python3 "$E/tools/pin-watch.py" selftest > "/tmp/R41B03/artifacts/$m.selftest.out" 2>&1
echo "selftest exit=$?"
python3 /fast/scratch/kama-r41/clone/tools/round41-pinwatch-audit.py --repo "$D" --tip "$MSHA" --seed 41 --out "/tmp/R41B03/artifacts/$m.seed41.out"
echo "counter exit=$?"
echo "== selftest tail =="
grep -E "^(FAIL|selftest)" "/tmp/R41B03/artifacts/$m.selftest.out" || true
echo "== counter receipt =="
cat "/tmp/R41B03/artifacts/$m.seed41.out"
