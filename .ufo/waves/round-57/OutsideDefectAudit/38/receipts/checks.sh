#!/usr/bin/env bash
# R57Item38OutsideDefectAudit — defect re-evaluation checks (read-only).
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/fast/scratch/hyaku/kama-r57/R57Item38OutsideDefectAudit
cd "$LANE" || exit 9

run() { echo "\$ $*"; "$@"; echo "exit=$?"; echo; }

echo "### tree pin"
run git rev-parse HEAD
run git status --porcelain
echo "### D1 axis authority (round-56 routed defect 1)"
run sed -n '29p' /home/vgpnk/Projects/shokunin/MISSION.md
run sed -n '52p' /home/vgpnk/Projects/shokunin/shokunin.conf
echo '$ awk NR==6 SCORECARD.md (first 400 bytes)'
awk 'NR==6{print substr($0,1,400)}' SCORECARD.md; echo "exit=$?"; echo
echo "### D2 executed-entry binding (round-56 routed defect 2, first half)"
run sha256sum tools/round56-prereg-check.py
echo '$ git show b89bdab2:tools/round56-prereg-check.py | sha256sum'
git show b89bdab2:tools/round56-prereg-check.py | sha256sum; echo "exit=$?"; echo
echo "### D2 SCORECARD/SHONEN disagreement half"
run grep -c SHONEN tools/round42-selfdesc-reconcile.py
run grep -l SHONEN tools/round53-cited-path-check.py tools/round54-cited-path-check.py
run grep -n "surfaces  SCORECARD.md, SHONEN.md" tools/round53-cited-path-check.py
echo "### D3 S513 rejection rationale (round-56 routed defect 3)"
run grep -n "S513" corpus/SOURCES.md
run grep -c S513 corpus/QUALITY.md
run grep -c S513 corpus/lessons/round-57.md
run grep -n "S513 — REJECT" corpus/lessons/round-56.md
echo "### D4 append-only declarations (round-56 routed defect 4)"
echo '$ registry/append-only-contract.tsv (path, rule, declared_at, region)'
cut -f1-4 registry/append-only-contract.tsv; echo "exit=$?"; echo
echo '$ corpus/README.md pointer lines'
awk 'NR==761||NR==766||NR==767||NR==768||NR==1239||NR==1246{printf "%d: %s\n", NR, $0}' corpus/README.md
echo "### counts used by the round-57 claims"
run python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"
run grep -n "canonical list as of round 49" SCORECARD.md
echo "### round-56 non-author closure (source of the routed defects)"
run sed -n '40,46p' corpus/lessons/round-56-verifier-spotcheck.md
echo "### round-57 lesson rows (lesson-addressing state)"
run grep -n "^| " corpus/lessons/round-57.md
run grep -n "Round-56\|round-56" corpus/lessons/round-57.md
