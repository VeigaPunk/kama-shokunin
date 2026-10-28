#!/bin/bash
# L02LogTail run6: server.log opened through a pre-planted symlink in the --work dir.
# Does the tool follow it (writing server output into an unrelated file) and still
# report a clean receipt?
set -u
S=/fast/scratch/hyaku/kama-r62/w/L02LogTail
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
R=$S/run6
rm -rf "$R"; mkdir -p "$R/work" "$R/hold"
export TMPDIR=$S/tmp TMP=$S/tmp TEMP=$S/tmp
printf 'CANARY-BEFORE\n' > "$R/canary.txt"
ln -s "$R/canary.txt" "$R/work/server.log"
ls -l "$R/work/server.log"
(
  python3 "$LANE/tools/kama-completion-live.py" --work "$R/work" --hold-dir "$R/hold" \
    --hold-timeout 120 --nonce "l02-logtail-run6-symlink" \
    --out "$R/receipt.json" > "$R/tool.stdout" 2> "$R/tool.stderr"
) &
TOOLPID=$!
for i in $(seq 1 2400); do
  if [ -f "$R/hold/hold.json" ]; then printf 'release\n' > "$R/hold/release"; break; fi
  sleep 0.05
done
wait $TOOLPID; echo "run6 rc=$?"
echo '--- canary head after run ---'
head -4 "$R/canary.txt"
echo '--- canary is symlink target, server.log still a symlink? ---'
ls -l "$R/work/server.log"
echo '--- receipt verdict/server_log ---'
python3 -c "
import json;r=json.load(open('$R/receipt.json'));print('verdict',r['verdict'],'server_log',r.get('server_log'),'checks_all_true',all(v['passed'] for v in r['checks'].values()))"
