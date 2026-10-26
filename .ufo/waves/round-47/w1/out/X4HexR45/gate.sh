#!/usr/bin/env bash
# X4HexR45 gate receipt: hexrun-census for the five recheck-r45/README tokens.
# Everything below is re-run from the seat's scratch clones; no lane file is written.
set -u
S=/fast/scratch/hyaku/kama-r47/X4HexR45
L=/home/vgpnk/Projects/shokunin/kama-shokunin
W=$L/.ufo/waves/round-47/w1/out
O=$W/X4HexR45
C="python3 $L/tools/hexrun-census.py"
BASE=3a09a1d93dcc16799cf6c4b48786e6440af134c4
TIP=46a924e027f05614558c45ff02bf7a94ca57d3e1
FIX=$(cat "$S/fixture-commit.txt")
UFIX=$(cat "$S/union-fixture-commit.txt")

run() { echo "\$ $*"; "$@"; echo "rc=$?"; }

echo "X4HexR45 gate receipt - hexrun census, round 47 (lane kama)"
echo "========================================================================"
echo "scratch:   $S"
echo "lane:      \$S/lane  = git clone --shared $L  (toplevel asserted before every commit)"
echo "upstream:  \$S/ollama.git  git clone --filter=blob:none --bare https://github.com/ollama/ollama.git"
echo "           \$S/genai.git   git clone --filter=blob:none --bare https://github.com/open-telemetry/semantic-conventions-genai.git"
echo "           \$S/linux.git   git init --bare; fetch --filter=blob:none --depth=1 refs/tags/v7.3 and refs/tags/v7.2"
echo "           \$S/llama.git   git init --bare; fetch --filter=blob:none refs/heads/master and refs/tags/b11889"
echo "fixture:   commit $FIX  (lane tip $TIP + the 5 evidence files, nothing else)"
echo "union fix: commit $UFIX  (same tree + every round-47 hexrun evidence file)"
echo "ledgers:   \$S/ledger-v2.tsv (lane registry/hexrun-ledger.tsv + \$O/rows.tsv, 88 lines)"
echo "           \$S/ledger-union.tsv / \$S/ledger-union-dedup.tsv / \$S/ledger-union-fixed.tsv"
echo

echo "--- 0. the evidence files this seat commits (token, repo, first command, its output)"
for t in 66ab8482e08035a3238dff04a5739c4371c61bfe 547934afa90a34298441caf80c43b27255c3a292 20259355b9631e3f032dcc099d1b5a2666818c42 c03c1a14507dfaf8b856c2608f9ac216021fc222 d854d98bae598388ecea1ed84396587e5edc326d; do
  echo "  $L/.ufo/waves/round-47/hexrun-evidence/$t.txt  $(wc -c < "$L/.ufo/waves/round-47/hexrun-evidence/$t.txt") bytes"
done
echo

echo "--- 1. baseline, lane tip and build, unmodified ledger"
echo "\$ $C scan --repo \$S/lane --rev $BASE"; $C scan --repo "$S/lane" --rev $BASE; echo "rc=$?"
echo "\$ $C scan --repo \$S/lane --rev $TIP";  $C scan --repo "$S/lane" --rev $TIP;  echo "rc=$?"
echo

echo "--- 2. control, fixture commit with the evidence, unmodified ledger (evidence alone must change nothing)"
echo "\$ $C scan --repo \$S/lane --rev $FIX"; $C scan --repo "$S/lane" --rev $FIX; echo "rc=$?"
echo

echo "--- 3. gate, fixture commit with the evidence and rows.tsv appended"
echo "\$ $C scan --repo \$S/lane --rev $FIX --ledger \$S/ledger-v2.tsv"
$C scan --repo "$S/lane" --rev $FIX --ledger "$S/ledger-v2.tsv"; echo "rc=$?"
echo "\$ ... --details  (only this seat's five tokens)"
$C scan --repo "$S/lane" --rev $FIX --ledger "$S/ledger-v2.tsv" --details 2>&1 >/dev/null | grep -E '66ab8482|547934af|20259355|c03c1a14|d854d98b'
echo

echo "--- 4. counterfactual, rows appended but evidence NOT in the tree at REV"
echo "\$ $C scan --repo \$S/lane --rev $TIP --ledger \$S/ledger-v2.tsv"
$C scan --repo "$S/lane" --rev $TIP --ledger "$S/ledger-v2.tsv"; echo "rc=$?"
echo

echo "--- 5. negative controls, one row broken at a time, at the fixture commit"
for n in badrepo noevidence wrongevidence; do
  echo "\$ $C scan --repo \$S/lane --rev $FIX --ledger \$S/neg-$n.tsv"
  $C scan --repo "$S/lane" --rev $FIX --ledger "$S/neg-$n.tsv"; echo "rc=$?"
done
echo "  badrepo:       d854d98b row repo cell 'ggml-org/ggml' (text absent from its evidence)"
echo "  noevidence:    547934af row evidence path renamed to a file that does not exist"
echo "  wrongevidence: 20259355 row pointed at the 66ab8482 evidence file (token absent from its bytes)"
echo

echo "--- 6. union preview, all four hexrun seats (advisory; the rows belong to the other seats)"
echo "\$ $C scan --repo \$S/lane --rev $UFIX --ledger \$S/ledger-union.tsv   (raw concatenation)"
$C scan --repo "$S/lane" --rev $UFIX --ledger "$S/ledger-union.tsv"; echo "rc=$?"
$C scan --repo "$S/lane" --rev $UFIX --ledger "$S/ledger-union.tsv" --details 2>&1 >/dev/null | grep -E 'class=ledger_bad'
echo "\$ $C scan --repo \$S/lane --rev $UFIX --ledger \$S/ledger-union-dedup.tsv   (d854d98b kept once)"
$C scan --repo "$S/lane" --rev $UFIX --ledger "$S/ledger-union-dedup.tsv"; echo "rc=$?"
echo "\$ $C scan --repo \$S/lane --rev $UFIX --ledger \$S/ledger-union-fixed.tsv   (dedup + fleet repo cell + advisory ec82db00 row)"
$C scan --repo "$S/lane" --rev $UFIX --ledger "$S/ledger-union-fixed.tsv"; echo "rc=$?"
$C scan --repo "$S/lane" --rev $UFIX --ledger "$S/ledger-union-fixed.tsv" --details 2>&1 >/dev/null | grep -E 'class=(unknown|ledger_bad)' || echo "  (no unknown and no ledger_bad detail lines)"
