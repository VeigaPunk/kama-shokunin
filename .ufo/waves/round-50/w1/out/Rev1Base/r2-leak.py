#!/usr/bin/env python3
"""Rev1Base round-50: reproduce round-49 closure R2 at the base commit.

A counter-shaped parent (the base counter's own spawn shape: subprocess.Popen of
`<tree>/tools/kama-live-replay.py --receipt ... --work ... --out ... --witness-dir ...`
with env = dict(os.environ) + HOME/XDG_CACHE_HOME/TMPDIR, no start_new_session, no
preexec_fn - tools/round49-replay-witness-audit.py:297-298,431-435) is SIGKILLed once
ready.json names the server; the replay, the live tool and the server are then
observed. Finally the leftovers are stopped, live tool first.

usage: r2-leak.py <tree> <receipt-rel> <scratch> <out.json>
"""
import json
import os
import signal
import socket
import subprocess
import sys
import time

TREE, RECEIPT, S, OUT = sys.argv[1:5]
wd = os.path.join(S, "wd")
work = os.path.join(S, "work")
os.makedirs(wd, exist_ok=True)
os.makedirs(work, exist_ok=True)
for k, sub in (("HOME", "home"), ("XDG_CACHE_HOME", "home/.cache"), ("TMPDIR", "tmp")):
    os.makedirs(os.path.join(S, sub), exist_ok=True)
env = dict(os.environ)
for k, sub in (("HOME", "home"), ("XDG_CACHE_HOME", "home/.cache"), ("TMPDIR", "tmp")):
    env[k] = os.path.join(S, sub)

PARENT = (
    "import subprocess, sys\n"
    "log = open(sys.argv[2], 'wb')\n"
    "p = subprocess.Popen(sys.argv[3:], env=__import__('os').environ, cwd=sys.argv[1],\n"
    "                     stdout=log, stderr=subprocess.STDOUT)\n"
    "sys.exit(p.wait())\n")
parent = subprocess.Popen([sys.executable, "-c", PARENT, TREE, os.path.join(S, "parent.log"),
                           sys.executable,
                           os.path.join(TREE, "tools/kama-live-replay.py"),
                           "--receipt", os.path.join(TREE, RECEIPT),
                           "--work", work, "--out", os.path.join(S, "replay.json"),
                           "--witness-dir", wd],
                          env=env, cwd=TREE)


def stat(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            f = fh.read().rsplit(")", 1)[1].split()
        return f[0], int(f[1]), int(f[2])   # state, ppid, starttime
    except OSError:
        return None


def descendants(root):
    kids, out, todo = {}, {}, [root]
    for name in os.listdir("/proc"):
        if name.isdigit():
            st = stat(int(name))
            if st and st[0] not in ("Z", "X"):
                kids.setdefault(st[1], []).append(int(name))
    while todo:
        for pid in kids.get(todo.pop(), []):
            out[pid] = stat(pid)[2]
            todo.append(pid)
    return out


def port_refuses(port):
    with socket.socket() as s:
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", port))
            return False
        except OSError:
            return True


ready, t0 = None, time.monotonic()
while time.monotonic() - t0 < 400:
    try:
        with open(os.path.join(wd, "ready.json")) as fh:
            ready = json.load(fh)
        if isinstance(ready.get("pid"), int):
            break
    except (OSError, ValueError):
        pass
    time.sleep(0.2)
if not ready:
    print("no ready.json (parent exit %s)" % parent.poll())
    parent.kill()
    raise SystemExit(2)

port, spid = ready["port"], ready["pid"]
snap = descendants(parent.pid)
print(f"ready: server pid {spid} port {port}; parent {parent.pid} descendants {len(snap)}")
for pid in sorted(snap):
    st = stat(pid)
    try:
        cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ")[:90].decode("utf-8", "replace")
    except OSError:
        cmd = "?"
    print(f"  descendant {pid} ppid {st[1]} start {st[2]} {cmd}")
os.kill(parent.pid, signal.SIGKILL)
parent.wait()
t0 = time.monotonic()
time.sleep(2.0)
alive = {pid: stat(pid) for pid in snap}
alive = {pid: st for pid, st in alive.items() if st and st[0] not in ("Z", "X") and st[2] == snap[pid]}
print(f"2 s after SIGKILL of the counter-shaped parent: alive {sorted(alive)} port "
      f"{'ACCEPTS' if not port_refuses(port) else 'refuses'}")
res = {"server_pid": spid, "port": port, "snapshot": sorted(snap), "alive_after_2s": sorted(alive),
       "port_accepts": not port_refuses(port),
       "replay_alive": any(pid != spid and "kama-live-replay" in
                           open(f"/proc/{pid}/cmdline", "rb").read().decode("utf-8", "replace")
                           for pid, st in alive.items() if os.path.exists(f"/proc/{pid}/cmdline"))}
# cleanup: the live tool first (its own teardown), then the replay
for pid in sorted(alive):
    try:
        cmd = open(f"/proc/{pid}/cmdline", "rb").read().decode("utf-8", "replace")
    except OSError:
        continue
    if "kama-llamacpp-live.py" in cmd:
        os.kill(pid, signal.SIGTERM)
time.sleep(1.5)
for pid in sorted(alive):
    st = stat(pid)
    if st and st[0] not in ("Z", "X") and st[2] == snap[pid]:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
time.sleep(1.5)
for pid in sorted(alive):
    st = stat(pid)
    if st and st[0] not in ("Z", "X") and st[2] == snap[pid]:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
print("cleanup: port", "refuses" if port_refuses(port) else "ACCEPTS",
      "survivors", [pid for pid in snap if (stat(pid) or ("Z",))[0] not in ("Z", "X")])
with open(OUT, "w") as fh:
    json.dump({"ready": ready, "snapshot": snap, "result": res}, fh, indent=1, default=str)
