#!/usr/bin/env bash
# R41A10 command transcript — every command run against the lane tip 24aa1d34.
# Read-only with respect to /fast/scratch/kama-r41/clone and the parked worktree.
# The only writes were into /tmp/r41a10-clone (private clone) and /tmp scratch outputs.
set -u
L=/fast/scratch/kama-r41/clone     # read-only measurement root
W=/tmp/r41a10-clone                # private clone, for anything that writes
TIP=24aa1d3485c107f88b8b838892d43ea7587befcf

echo "=== 0. clone ==="
git clone -q "$L" "$W"
git -C "$W" rev-parse HEAD
git -C "$W" rev-parse --show-toplevel

echo
echo "=== 1. counter replays at tip ==="
cd "$W"
python3 tools/round41-scorecard-reconcile.py --repo "$W" --tip "$TIP" --out /tmp/r41a10-c1.out; echo "EXIT=$?"
python3 tools/round41-pinwatch-audit.py --repo "$W" --tip "$TIP" --seed 41 --out /tmp/r41a10-c2.out; echo "EXIT=$?"
cat /tmp/r41a10-c1.out /tmp/r41a10-c2.out

echo
echo "=== 2. C1 base control (frozen) ==="
cat "$L/.ufo/waves/round-41/controls/base.c1.out"

echo
echo "=== 3. round-41 receipt pointers named by SCORECARD.md:2169-2170 ==="
ls "$L/.ufo/waves/round-41/c1/after.out" "$L/.ufo/waves/round-41/c2/after.out" 2>&1
find "$L/.ufo/waves/round-41" -name "after*.out"
echo "--- receipts that DO exist ---"
find "$L/.ufo/waves/round-41" -name "candidate.out"

echo
echo "=== 4. '§Round-41 measured results' section ==="
grep -n "^#.*Round.41 measured" "$L/SCORECARD.md"; echo "(empty = none)"
awk 'NR>=2159 && /^#{2,3} /' "$L/SCORECARD.md"

echo
echo "=== 5. SCORECARD banner vs authority ==="
sed -n '6,13p' "$L/SCORECARD.md"
grep -n "^kama" /home/vgpnk/Projects/shokunin/shokunin.conf
grep -n "kama:" /home/vgpnk/Projects/shokunin/MISSION.md
sed -n '2161,2164p' "$L/SCORECARD.md"

echo
echo "=== 6. head table scores (freshness 8 vs calibration 7) ==="
sed -n '20,25p' "$L/SCORECARD.md" | cut -c1-90

echo
echo "=== 7. §Planned / §Retired / §Saturation ==="
sed -n '58,68p' "$L/SCORECARD.md"
sed -n '70,77p' "$L/SCORECARD.md"
sed -n '143,145p' "$L/SCORECARD.md"

echo
echo "=== 8. head ## Capabilities counts vs census ==="
sed -n '135,141p' "$L/SCORECARD.md" | cut -c1-260
cd "$W" && bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file corpus/SOURCES.md; echo "EXIT=$?"

echo
echo "=== 9. study paths / search-log notes ==="
awk 'NR>=232 && NR<241' "$L/corpus/SOURCES.md" | grep -c "^- "
awk '/^## Search log/,/^## Leads/' "$L/corpus/SOURCES.md" | grep -c "^- \*\*"

echo
echo "=== 10. canonical capability list (round 41) ==="
sed -n '2172,2183p' "$L/SCORECARD.md" | cut -c1-110

echo
echo "=== 11. round-25 context-capacity receipt (contradicts §Planned 'no serving context') ==="
ls -l "$L/.ufo/waves/round-25/final/context-capacity-receipt.json"
python3 -c "
import json; d=json.load(open('$L/.ufo/waves/round-25/final/context-capacity-receipt.json'))
print('cells:', len(d['cells']), 'exit_code:', d['exit_code'], 'error:', d['error'])"

echo
echo "=== 12. AGENTS.md rules vs tree ==="
cat -n "$L/AGENTS.md" | cut -c1-160
grep -rn "committed [0-9a-f]\{7,\}" --include=*.md "$L" | grep -v "/.ufo/waves" | head
echo "--- LOG.md touched by round-41 commits? ---"
git -C "$L" show --stat --name-only 24aa1d34 | grep -c "^LOG.md"
git -C "$L" show --stat --name-only 6fec0c4 | grep -c "^LOG.md"
git -C "$L" log --oneline -1 -- LOG.md
grep -n -i "round 41" "$L/LOG.md"; echo "(empty = none)"

echo
echo "=== 13. README.md vs tree ==="
cat "$L/README.md"
ls "$L"
grep -n -i "engine-pin\|pin-watch\|engine pin" "$L/PROVINCE.md" "$L/README.md"; echo "(empty = none)"

echo
echo "=== 14. SHONEN.md cited paths + check counts ==="
for p in .ufo/waves/round-16/live/receipt.json .ufo/waves/round-17/live/receipt-1.json \
         .ufo/waves/round-17/live/receipt-2.json .ufo/waves/round-17/live/receipt-3.json \
         corpus/knowledge/snapshot-history.md corpus/knowledge/cross-lane-scope.md PROVINCE.md; do
  if [ -e "$L/$p" ]; then echo "EXISTS $p"; else echo "MISSING $p"; fi; done
python3 -c "
import json; print('round-16 checks:', len(json.load(open('$L/.ufo/waves/round-16/live/receipt.json'))['checks']))"
for i in 1 2 3; do python3 -c "
import json; print('round-17 receipt-$i checks:', len(json.load(open('$L/.ufo/waves/round-17/live/receipt-$i.json'))['checks']))"; done
ls "$L/corpus/lessons/" | grep -c "verifier-spotcheck"

echo
echo "=== 15. round-3 historical table byte-intact check ==="
git -C "$L" show 8893b89:SCORECARD.md > /tmp/r41a10-base-sc.md
awk '/^\| \*\*operability\*\* \(worked round 1\)/,/^$/' /tmp/r41a10-base-sc.md | sha256sum
awk '/^\| \*\*operability\*\* \(worked round 1\)/,/^$/' "$L/SCORECARD.md" | sha256sum

echo
echo "=== 16. counter temp-dir leak ==="
grep -n "mkdtemp\|rmtree\|TemporaryDirectory" \
  "$L/tools/round41-scorecard-reconcile.py" "$L/tools/round41-pinwatch-audit.py"
ls -d /tmp/r41c1-* 2>/dev/null | wc -l
du -csh /tmp/r41c1-* 2>/dev/null | tail -1
df -h /tmp | tail -1
