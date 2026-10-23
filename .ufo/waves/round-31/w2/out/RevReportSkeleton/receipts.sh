#!/bin/bash
# RevReportSkeleton receipt capture — prints each command, its exit code, and its tail.
# Read-only with respect to tracked lane files. Output captured to receipts.txt.
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
FLEET=/home/vgpnk/Projects/shokunin
cd "$LANE" || exit 2

run() {
  echo "==================================================================="
  echo "\$ $*"
  out=$("$@" 2>&1); rc=$?
  printf '%s\n' "$out" | tail -n 8
  echo "[exit=$rc]"
  echo
}

run_r() {
  # read-only file tail, records like a command
  echo "==================================================================="
  echo "\$ tail -n 6 $1"
  tail -n 6 "$1"; rc=$?
  echo "[exit=$rc]"
  echo
}

run git rev-parse HEAD
run git log --format='%h %ci %s' -8
run git status --porcelain
run git ls-tree -r HEAD --name-only -- .ufo/waves/round-31/c3/
run git ls-tree HEAD --name-only -- .ufo/waves/round-31/w1/
run git ls-tree HEAD --name-only -- .ufo/waves/round-31/w2/
run git show --stat --format='%h %s' addeb57
run ls /home/vgpnk/Projects/shokunin/.ufo/reports/round-31/
run grep -n 'bda324b\|addeb57\|attempt 2' LOG.md
run grep -n 'gate-registry-check\|capabilities' SCORECARD.md
run_r .ufo/waves/round-31/c3/gate-before.out
run_r .ufo/waves/round-31/c3/gate-after-progress.out
run_r .ufo/waves/round-31/c3/gate-after-final.out
run_r .ufo/waves/round-31/c3/gate-mutation-dropped-row.out
run_r .ufo/waves/round-31/c3/r29-counter-sha256.txt
run python3 -c "import json;d=json.load(open('.ufo/waves/round-31/c3/r29-at-tip.json'));print('met',d['met'],'tip',d.get('tip'),'statements',d.get('statements'),'mismatched_at_base',d.get('mismatched_at_base'),'unresolved',d.get('unresolved'))"
run python3 -c "import json;d=json.load(open('.ufo/waves/round-31/c1/c1-382d11b2.json'));print(d['summary'])"
run python3 -c "import json;d=json.load(open('.ufo/waves/round-31/c1/c1-bda324bb.json'));print(d['summary'])"
run python3 -c "import json;d=json.load(open('.ufo/waves/round-31/c2/c2-382d11b2.json'));print(d['summary'])"
run python3 -c "import json;d=json.load(open('.ufo/waves/round-31/c2/c2-bda324bb.json'));print(d['summary'])"
run python3 -c "import json;d=json.load(open('.ufo/waves/round-31/c1/c1-54c6f4fe.json'));print(d['summary'])"
run python3 -c "import json;d=json.load(open('.ufo/waves/round-31/c2/c2-b4f3edc0.json'));print(d['summary'])"
run tail -n 5 .ufo/waves/round-31/census-start.out
run tail -n 5 .ufo/waves/round-31/census-end.out
run tail -n 5 .ufo/waves/round-31/w2/census-validate-start.out
run tail -n 4 .ufo/waves/round-31/c1/hold-r30.out
run tail -n 6 .ufo/waves/round-31/controls/RefRepair/receipt.txt
run grep -n 'round-29/count-c1' SKILL.md
run python3 -c "import json;t=json.load(open('.ufo/waves/round-31/w2/taskCall.json'));print('w2 tasks:',len(t['tasks']))"
run ls .ufo/waves/round-31/w1/out/
run ls corpus/knowledge/ 
run grep -n 'KQ41\|chat-adapter' corpus/QUALITY.md
run grep -n 'SHONEN\|Marker rule\|Sources & frontier\|Trend verdicts' /home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-31.md
run /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/kama-shokunin
run git merge-base --is-ancestor 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD
