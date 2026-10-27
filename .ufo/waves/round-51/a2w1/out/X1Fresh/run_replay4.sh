#!/bin/bash
set -u
S=/fast/scratch/hyaku/kama-r51/X1Fresh
export TMPDIR="$S"
cd "$S" || exit 9
mkdir -p "$S/wd4"
start=$(date +%s)
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work "$S/work4" --out "$S/result4.json" --witness-dir "$S/wd4" --witness-timeout 2 \
  > "$S/replay4.log" 2>&1
rc=$?
end=$(date +%s)
echo "exit=$rc elapsed=$((end-start))s"
echo "--- log:"; cat "$S/replay4.log"
echo "--- wd4:"; ls -la "$S/wd4"
echo "--- result4:"; [ -f "$S/result4.json" ] && python3 -c "
import json;d=json.load(open('$S/result4.json'));print('match',d['match'],'refused',d['refused'],'mismatches',d['mismatches']);print('witness_dir',d.get('witness_dir'))
r=json.load(open(d['rerun_receipt']));print('witness',json.dumps(r.get('witness')));print('teardown rc',r.get('teardown',{}).get('returncode'),'port_refuses',r.get('teardown',{}).get('port_refuses'))
" || echo "no result4.json"
echo "--- pgrep (all):"; pgrep -af llama-server; echo "pgrep_rc=$?"
