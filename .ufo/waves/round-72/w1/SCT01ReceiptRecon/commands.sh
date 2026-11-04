#!/usr/bin/env bash
# Raw command transcript for SCT01ReceiptRecon. Every command below is read-only git
# (rev-parse, cat-file, merge-base, diff, rev-list, log) plus the two recon scripts.
L=/home/vgpnk/Projects/shokunin/kama-shokunin
cd /fast/scratch/hyaku/kama-r72/SCT01ReceiptRecon || exit 1

run() { echo "\$ $*"; "$@" 2>&1; echo "[exit=$?]"; echo; }

echo "== lane tip =="
run git -C "$L" rev-parse master
run git -C "$L" log --oneline -6 master

echo "== header check on the round-71 report-tip receipts =="
run git -C "$L" show a3cc39f0:.ufo/waves/round-71/measured/after/pre-report-at-tip.out
echo "(first five lines above; header is line 1)"

echo "== non-ancestor receipt revisions =="
run git -C "$L" cat-file -t a7ae13ab621160957c8ac04053a87f393b727589
run git -C "$L" cat-file -t af6e1c84d1460bae3f0070f03a5385f77eecb2b2
run git -C "$L" merge-base --is-ancestor a7ae13ab621160957c8ac04053a87f393b727589 a3cc39f0

echo "== commit distances =="
run git -C "$L" rev-list --count 4b284653..7fb6cb4e
run git -C "$L" rev-list --count 4b284653..a3cc39f0
run git -C "$L" rev-list --count f3ee44f4..7fb6cb4e
run git -C "$L" rev-list --oneline 4b284653..7fb6cb4e

echo "== instrument-input delta, round-70 receipt tip 7be07423 -> lane tip =="
echo "\$ git -C \$L diff --name-only 7be07423 a3cc39f0 | grep -E '^(tools/|SKILL\\.md\$|PROVINCE\\.md\$|corpus/SOURCES\\.md\$|corpus/knowledge/)'"
git -C "$L" diff --name-only 7be07423 a3cc39f0 | grep -E '^(tools/|SKILL\.md$|PROVINCE\.md$|corpus/SOURCES\.md$|corpus/knowledge/)'
echo

echo "== instrument-input delta, round-71 receipt tip 4b284653 -> lane tip =="
run git -C "$L" diff --name-only 4b284653 a3cc39f0

echo "== the three commits after the round-71 receipt tip =="
run git -C "$L" show --stat --format='%h %ci %s' 1375f51c
run git -C "$L" show --stat --format='%h %ci %s' 9458c3d7
run git -C "$L" show --stat --format='%h %ci %s' 7fb6cb4e

echo "== configured --round-72 tip used by the two frozen counters =="
run git -C "$L" show a3cc39f0:.ufo/waves/round-72/controls/freeze.txt
