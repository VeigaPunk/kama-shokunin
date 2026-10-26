#!/bin/sh
# Run the frozen C1 counter on each selftest-surviving mutant.
# The mutant replaces tools/append-only-audit.py in the fixture clone
# (checked out at 380bcdff9c8af06997c482f6eb03db926a794a2b), is committed
# with a fixture identity, and the counter measures that tip.
S=/fast/scratch/hyaku/kama-r48/M1Tool
COUNTER=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py
while read -r id; do
  [ -n "$id" ] || continue
  cp "$S/mutants/$id.py" "$S/fixture/tools/append-only-audit.py"
  git -C "$S/fixture" -c user.name=M1Tool-fixture -c user.email=m1tool-fixture@invalid \
      -c commit.gpgsign=false commit -q -m "mutant $id" -- tools/append-only-audit.py
  TIP=$(git -C "$S/fixture" rev-parse HEAD)
  mkdir -p "$S/counter/$id"
  TMPDIR="$S" python3 "$COUNTER" --repo "$S/fixture" --tip "$TIP" --scratch "$S/counter/$id" \
      > "$S/counter/$id.out" 2>&1
  rc=$?
  echo "== $id counter_exit=$rc tip=$TIP"
  sed -n '1,2p' "$S/counter/$id.out"
done < "$S/survivors.txt"
