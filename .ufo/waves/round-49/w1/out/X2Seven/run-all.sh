#!/usr/bin/env bash
# run-all.sh - exact commands behind X2Seven's round-49 C2 item (7-line identification,
# dd9f5dc6 23-vs-17 explanation). Run from a scratch dir S; the lane clone is shared.
# usage: S=/fast/scratch/.../X2Seven lane=/home/vgpnk/Projects/shokunin/kama-shokunin ./run-all.sh
set -euo pipefail
S=${S:?scratch dir}
LANE=${LANE:-/home/vgpnk/Projects/shokunin/kama-shokunin}
TIP=74558c71c38ceaeace15fd4cf8aa9d84977584b1
BASE=438127bc01ff3b99f98468549d58046f932490ef
export TMPDIR="$S"

git clone --shared "$LANE" "$S/lane"            # one live clone, committed refs only (HEAD 122c4ee9)
mkdir -p "$S/tree-v3" "$S/tree-v4" "$S/out"
git -C "$S/lane" archive "$BASE" tools/append-only-audit.py | tar -x -C "$S/tree-v3"
git -C "$S/lane" archive "$TIP"  tools/append-only-audit.py | tar -x -C "$S/tree-v4"

# 1) definition isolation: v3 and v4 tools x both tips (identical events for v3/v4 at either tip)
for v in v3 v4; do for t in base build; do
  [ "$t" = base ] && R=$BASE || R=$TIP
  python3 "$S/tree-$v/tools/append-only-audit.py" --repo "$S/lane" --to "$R" --json > "$S/out/$v-at-$t.json"
  echo "$v-at-$t exit=$?"
done; done

# 2) own per-line recomputation (independent of the tool: git plumbing only)
python3 recompute.py "$S/lane" "$TIP" "$S/out/recompute.json"

# 3) frozen C2 counter, both ends
python3 "$LANE/tools/round49-append-audit-v4-check.py" --repo "$S/lane" --tip "$TIP"  --scratch "$S" --out "$S/out/c2-counter-build.out"
python3 "$LANE/tools/round49-append-audit-v4-check.py" --repo "$S/lane" --tip "$BASE" --scratch "$S" --out "$S/out/c2-counter-base.out"

# 4) duplicate-head-copy behaviour fixture (measured, not asserted)
bash fixture-dupe3.sh "$S/lane" "$S/fxrun"
