#!/usr/bin/env bash
# fixture-checks.sh - shows each proposed round-52 Mistakes check able to pass AND to
# fail on constructed input, then on real lane history (read-only).
# Writes only under $S (the seat's scratch) and prints receipts.
set -u
S=${S:?set S to the seat scratch}
O=${O:?set O to the seat out dir}
D=$S/fx
rm -rf "$D"; mkdir -p "$D"
git -C "$D" init -q || exit 2
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "toplevel mismatch"; exit 2; }
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git -C "$D" -c user.name=fx -c user.email=fx@invalid commit -qm "$2"; }
mkdir -p "$D/.ufo/waves/round-52/w1/out" "$D/.ufo/waves/round-52/w1" "$D/.ufo/waves/round-52/measured" "$D/.ufo/reports/round-52"
printf -- '- receipts (`.ufo/waves/round-52/measured/measure.sh`)\n' > "$D/SKILL.md"
printf 'seat A, first bytes\n' > "$D/.ufo/waves/round-52/w1/out/SeatA.md"
printf '{"wave":"w1"}\n' > "$D/.ufo/waves/round-52/w1/w1-results.json"
printf 'met=True\n' > "$D/.ufo/waves/round-52/measured/pointer.out"
printf '# measure\n' > "$D/.ufo/waves/round-52/measured/measure.sh"
cat > "$D/SCORECARD.md" <<'EOF'
# fixture scorecard

### Round-52 measured results

The planned-pointer check resolves (`.ufo/waves/round-52/measured/pointer.out`).
EOF
git -C "$D" add -A >/dev/null 2>&1
c "2026-10-27T00:00:00Z" "fixture: seat report, results record, pointer receipt met=True"
printf 'round-52 kama report (fixture)\n' > "$D/.ufo/reports/round-52/kama.md"
git -C "$D" add -A >/dev/null 2>&1
c "2026-10-27T02:00:00Z" "fixture: fleet report filed after the wave landed"
GOOD=$(git -C "$D" rev-parse HEAD)

echo "### A1 report-wave-order on the ordered fixture (expect 0)"
python3 "$O/report-wave-order.py" --lane "$D" --fleet "$D" --round 52; echo "exit=$?"
echo "### B1 seat-report-immutability on the untouched fixture (expect 0)"
python3 "$O/seat-report-immutability.py" --repo "$D" --tip "$GOOD" | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "### C1 claim-vs-receipt with the receipt reading met=True (expect 0)"
python3 "$O/claim-vs-receipt.py" --repo "$D" --tip "$GOOD"; echo "exit=$?"
echo "### D1 cited-path-exists with every citation present (expect 0)"
python3 "$O/cited-path-exists.py" --repo "$D" --tip "$GOOD"; echo "exit=$?"

# defect commit: rewrite the committed seat report in place, cite a receipt that does
# not exist, and flip the pointer receipt the sentence cites
printf 'seat A, REWRITTEN after commit\n' > "$D/.ufo/waves/round-52/w1/out/SeatA.md"
printf -- '- receipts (`.ufo/waves/round-52/measured/*-pre.out`)\n' > "$D/SKILL.md"
printf 'met=False\n' > "$D/.ufo/waves/round-52/measured/pointer.out"
git -C "$D" add -A >/dev/null 2>&1
c "2026-10-27T03:00:00Z" "fixture: in-place seat rewrite, phantom pre.out glob, pointer met=False"
BAD=$(git -C "$D" rev-parse HEAD)

echo "### B2 seat-report-immutability after the in-place rewrite (expect 1)"
python3 "$O/seat-report-immutability.py" --repo "$D" --tip "$BAD"; echo "exit=$?"
echo "### C2 claim-vs-receipt after the receipt flipped (expect 1)"
python3 "$O/claim-vs-receipt.py" --repo "$D" --tip "$BAD"; echo "exit=$?"
echo "### D2 cited-path-exists with the phantom glob (expect 1)"
python3 "$O/cited-path-exists.py" --repo "$D" --tip "$BAD" --base "$GOOD"; echo "exit=$?"

# repair commit: restore the first-add bytes, file the rewrite beside them
printf 'seat A, first bytes\n' > "$D/.ufo/waves/round-52/w1/out/SeatA.md"
printf 'seat A, REWRITTEN after commit\n' > "$D/.ufo/waves/round-52/w1/out/SeatA.late-rewrite.md"
printf -- '- receipts (`.ufo/waves/round-52/measured/measure.sh`)\n' > "$D/SKILL.md"
printf 'met=True\n' > "$D/.ufo/waves/round-52/measured/pointer.out"
git -C "$D" add -A >/dev/null 2>&1
c "2026-10-27T04:00:00Z" "fixture: restore first-add bytes, file the rewrite beside, fix citation"
FIXED=$(git -C "$D" rev-parse HEAD)
echo "### B3 seat-report-immutability after restore + sibling (expect 0)"
python3 "$O/seat-report-immutability.py" --repo "$D" --tip "$FIXED" | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "### D3 cited-path-exists after the citation fix (expect 0)"
python3 "$O/cited-path-exists.py" --repo "$D" --tip "$FIXED" --base "$GOOD"; echo "exit=$?"

# late seat report landing after the report already exists
printf 'seat B, late\n' > "$D/.ufo/waves/round-52/w1/out/SeatB.md"
git -C "$D" add -A >/dev/null 2>&1
c "2026-10-27T05:00:00Z" "fixture: a 15th seat report lands after the report was filed"
LATE=$(git -C "$D" rev-parse HEAD)
echo "### A2 report-wave-order with a seat report landing after the report (expect 1)"
python3 "$O/report-wave-order.py" --lane "$D" --fleet "$D" --round 52; echo "exit=$?"
echo "FIXTURE commits: good=$GOOD bad=$BAD fixed=$FIXED late=$LATE"
