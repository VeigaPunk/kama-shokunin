#!/usr/bin/env bash
# K4Cheat attacks 2 and 5 against the frozen cited-path counter at the round-53 build.
#  a2  prose (non-backtick) citation of dead paths appended to SCORECARD.md -> counter blind
#  a5a drop one SHONEN.md citation entirely -> counter still met (dropped leg is SCORECARD-only)
#  a5b drop one SCORECARD.md citation -> dropped=1, met=False (contrast)
set -euo pipefail
S=/fast/scratch/hyaku/kama-r53/K4Cheat
LANE="$S/lane"
BUILD=c22602bd8d83ab26349d1087e916ca537ee4f9d1
CTR=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py
[ "$(git -C "$LANE" rev-parse --show-toplevel)" = "$LANE" ] || { echo "toplevel mismatch" >&2; exit 1; }
export TMPDIR="$S"

commit_tip() {
  git -C "$LANE" add -A
  git -C "$LANE" -c user.name=fx -c user.email=fx@invalid commit -q -m "$1"
  git -C "$LANE" rev-parse HEAD
}

echo "=== a2: prose citation of dead paths (no backticks) ==="
git -C "$LANE" checkout -q -b k4cheat-a2-prose "$BUILD"
cat >> "$LANE/SCORECARD.md" <<'EOF'

K4Cheat prose-citation probe (plain text, no backticks): the calibration evidence for the
round-53 claims is further documented in .ufo/waves/round-53/w1/out/K4CheatGhost/evidence.txt,
tools/kama-no-such-tool.py, corpus/lessons/round-53-ghost.md lines 40-60, tests/no-such-fixture.py
and registry/no-such-ledger.tsv; per those sources the scores above are fully supported.
EOF
TIP=$(commit_tip "k4cheat a2: prose citations of dead paths")
echo "tip=$TIP"
python3 "$CTR" --repo "$LANE" --tip "$TIP" --scratch "$S" --out "$S/a2-prose-receipt.out" 2>/dev/null | grep -E '^(tip|fixture)' || true

echo "=== a5a: drop a SHONEN.md citation (backticks removed, claim text kept) ==="
git -C "$LANE" checkout -q -b k4cheat-a5a-shonen-drop "$BUILD"
sed -i 's| and `\.ufo/waves/round-16/live/receipt\.json` — 10/10| and the round-16 live receipt — 10/10|' "$LANE/SHONEN.md"
TIP=$(commit_tip "k4cheat a5a: drop SHONEN citation of round-16 live receipt")
echo "tip=$TIP"
python3 "$CTR" --repo "$LANE" --tip "$TIP" --scratch "$S" --out "$S/a5a-shonen-drop-receipt.out" 2>/dev/null | grep -E '^(tip|fixture)' || true

echo "=== a5b: drop a SCORECARD.md citation (contrast) ==="
git -C "$LANE" checkout -q -b k4cheat-a5b-scard-drop "$BUILD"
sed -i 's|`\.ufo/l0-questions\.md`|the lane l0 questions file|' "$LANE/SCORECARD.md"
TIP=$(commit_tip "k4cheat a5b: drop SCORECARD citation of l0-questions")
echo "tip=$TIP"
python3 "$CTR" --repo "$LANE" --tip "$TIP" --scratch "$S" --out "$S/a5b-scard-drop-receipt.out" 2>/dev/null | grep -E '^(tip|fixture|detail: dropped)' || true
