#!/bin/bash
# X1Hold observer: wait for ready.json, record what the held server looks like,
# keep it up ~3 s, then release. Usage: observe.sh WITNESS_DIR LOG
set -u
W="$1"; LOG="$2"
: > "$LOG"
for i in $(seq 1 600); do
  [ -f "$W/ready.json" ] && break
  sleep 0.05
done
if [ ! -f "$W/ready.json" ]; then echo "no-ready:timeout" >> "$LOG"; exit 3; fi
READY_AT=$(date +%s.%N)
PID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["pid"])' "$W/ready.json")
PORT=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["port"])' "$W/ready.json")
echo "ready_at=$READY_AT pid=$PID port=$PORT ready_json=$(cat "$W/ready.json")" >> "$LOG"
echo "exe=$(readlink /proc/$PID/exe)" >> "$LOG"
echo "cmdline=$(tr '\0' ' ' < /proc/$PID/cmdline)" >> "$LOG"
echo "listen_inode=$(awk -v p=$(printf '%04X' "$PORT") '$2 ~ ":"p"$" && $4=="0A" {print $10}' /proc/net/tcp)" >> "$LOG"
echo "props_during_hold=$(curl -s -m 5 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/props")" >> "$LOG"
# hold ~3 s from ready
sleep 3
RELEASE_AT=$(date +%s.%N)
echo "release_at=$RELEASE_AT held_s=$(python3 -c "print(round($RELEASE_AT-$READY_AT,3))")" >> "$LOG"
echo "alive_at_release=$( [ -e "/proc/$PID" ] && echo yes || echo no )" >> "$LOG"
touch "$W/release"
exit 0
