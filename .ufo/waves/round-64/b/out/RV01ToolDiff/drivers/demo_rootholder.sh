#!/bin/bash
# Scratch demo: a root process holds a dup of the child's run-port listener DURING the
# hold window. Records what the tool's receipt says and what a same-uid procfs scan sees.
S=/fast/scratch/hyaku/kama-r64/b/RV01ToolDiff; D=$S/clone; cd "$S" || exit 1
H=$S/hold_root; rm -rf "$H"; mkdir -p "$H"; rm -f "$S/root.stop" "$S/root.pid"
python3 "$D/tools/kama-completion-live.py" --work "$S/work/rootdemo" --hold-dir "$H" --out "$S/rootdemo.json" --hold-timeout 120 &
TP=$!
for t in $(seq 1 600); do [ -f "$H/ready.json" ] && break; sleep 0.1; done
read CHILD PORT < <(python3 -c "import json;d=json.load(open('$H/ready.json'));print(d['pid'],d['port'])")
echo "tool=$TP child=$CHILD port=$PORT"
# inode of the LISTEN socket on PORT (any loopback row)
INODE=$(python3 - "$PORT" <<'EOF'
import sys
port = int(sys.argv[1])
for p in ('/proc/net/tcp', '/proc/net/tcp6'):
    for line in open(p).read().splitlines()[1:]:
        f = line.split()
        if f[3] == '0A' and int(f[1].rsplit(':', 1)[1], 16) == port:
            print(f[9]); raise SystemExit
EOF
)
FD=$(python3 - "$CHILD" "$INODE" <<'EOF'
import os, sys
pid, inode = sys.argv[1], sys.argv[2]
for fd in os.listdir(f'/proc/{pid}/fd'):
    if os.readlink(f'/proc/{pid}/fd/{fd}') == f'socket:[{inode}]':
        print(fd); raise SystemExit
EOF
)
echo "listener inode=$INODE child fd=$FD"
sudo -n sh -c "echo \$\$ > $S/root.pid; exec python3 $S/root_holder.py $CHILD $FD $S/root.stop 120" > "$S/root_holder.out" 2>&1 &
for t in $(seq 1 100); do [ -s "$S/root.pid" ] && grep -q dup_fd "$S/root_holder.out" 2>/dev/null && break; sleep 0.1; done
RP=$(cat "$S/root.pid"); echo "root holder pid=$RP ; $(cat $S/root_holder.out)"
echo "-- root's fd table (root view):"; sudo -n ls -l /proc/$RP/fd 2>&1 | grep socket || echo "(no socket fd visible)"
echo "-- same-uid view of root's fd table:"; ls -l /proc/$RP/fd 2>&1 | head -2
echo "-- same-uid _proc_holders during hold:"
python3 - "$D" "$PORT" <<'EOF'
import importlib.util, sys
D, port = sys.argv[1], int(sys.argv[2])
spec = importlib.util.spec_from_file_location('t', D + '/tools/kama-completion-live.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print('  holders =', m._proc_holders(port))
EOF
touch "$S/root.stop"; sleep 1; echo "root holder before release: $(cat $S/root_holder.out | tr '\n' ' ')"
touch "$H/release"
wait $TP; echo "tool rc=$?"
python3 -c "
import json;r=json.load(open('$S/rootdemo.json'))
print('receipt verdict=',r['verdict'],' listener_holders=',[(h['pid'],h['exe']) for h in r['listener_holders']])
print('receipt hold=',r['hold'])"
echo "root holder fd still open after teardown? (exit status of holder):"; sleep 1; cat "$S/root_holder.out"
