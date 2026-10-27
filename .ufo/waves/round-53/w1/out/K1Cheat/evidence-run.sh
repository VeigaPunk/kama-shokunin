#!/usr/bin/env bash
# K1Cheat direct-evidence driver: run the clone's replay with a witness dir,
# snapshot the held server's maps, prove the cheat ran, then release.
set -u
S=/fast/scratch/hyaku/kama-r53/K1Cheat
rm -f "$S/cheat-marker.json" "$S/ev.json" "$S/ev.log"
rm -rf "$S/evwd" "$S/evwork"
mkdir -p "$S/evwd" "$S/evwork"
cd "$S/lane"
python3 tools/kama-live-replay.py \
  --receipt .ufo/waves/round-48/c2/live/receipt-1.json \
  --work "$S/evwork" --out "$S/ev.json" --witness-dir "$S/evwd" \
  > "$S/ev.log" 2>&1 &
RP=$!
PID=""
for _ in $(seq 1 1200); do
  [ -f "$S/evwd/ready.json" ] && { PID=$(python3 -c "import json;print(json.load(open('$S/evwd/ready.json'))['pid'])" 2>/dev/null); break; }
  kill -0 "$RP" 2>/dev/null || break
  sleep 0.5
done
echo "replay_pid=$RP server_pid=${PID:-none}"
if [ -n "$PID" ] && [ -d "/proc/$PID" ]; then
  cat "/proc/$PID/maps" > "$S/maps-during-hold.txt"
  grep -nE 'rwx|kama-r53-cheat' "/proc/$PID/maps" > "$S/maps-cheat-lines.txt" || true
  echo "--- cheat-related maps lines (with line numbers) ---"
  cat "$S/maps-cheat-lines.txt"
fi
echo "--- markers (one per process that ran the constructor) ---"
ls -l "$S"/cheat-marker.json.* 2>/dev/null || echo "MARKER MISSING"
for m in "$S"/cheat-marker.json.*; do echo "== $m"; cat "$m"; done
if [ -n "$PID" ]; then echo "--- server pid $PID marker ---"; cat "$S/cheat-marker.json.$PID" 2>/dev/null || echo "no marker for server pid"; fi
touch "$S/evwd/release"
wait "$RP"; echo "replay_exit=$?"
echo "--- ev.json tail ---"
python3 - "$S/ev.json" <<'PY'
import json, sys
j = json.load(open(sys.argv[1]))
print("match:", j.get("match"), " refused:", j.get("refused"))
print("own_code:", json.dumps(j.get("own_code"), indent=1)[:800])
print("mismatches:", j.get("mismatches"))
PY
