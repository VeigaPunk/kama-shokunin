#!/bin/bash
S=/fast/scratch/hyaku/kama-r88/SN01FixtureSafety
W=$(mktemp -d -p "$S" sigdemo-XXXX)
python3 "$S/sigterm_child.py" "$W" > "$S/sigdemo-harness.log" 2>&1 &
HP=$!
for i in $(seq 1 40); do pgrep -af "$W/models" >/dev/null && break; sleep 0.5; done
echo "== proof 1: child bind while the counter/harness runs =="
ss -ltnp 2>/dev/null | grep -F "$(pgrep -af "$W/models" | awk '{print $1}')" 
CP=$(pgrep -f "$W/models")
echo "harness=$HP child=$CP"
echo "== proof 2: SIGTERM the parent (no handler in the tool) =="
kill -TERM "$HP"; sleep 3
echo "parent alive after SIGTERM: $(ps -o stat= -p "$HP" | grep -c . ) (0 = dead)"
echo "child alive after SIGTERM:  $(ps -o stat= -p "$CP" | grep -c . )"
ps -o pid,ppid,etime,args -p "$CP" | tail -2
echo "== proof 3: child still listening (orphan) =="
ss -ltnp 2>/dev/null | grep -F "$CP"
echo "== reaping the orphan I started =="
kill -TERM "$CP" 2>/dev/null; sleep 1
echo "post-reap listeners for that pid: $(ss -ltnp 2>/dev/null | grep -cF "$CP")"
