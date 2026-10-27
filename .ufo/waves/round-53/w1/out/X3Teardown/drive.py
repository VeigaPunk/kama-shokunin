#!/usr/bin/env python3
"""X3Teardown round-53: witness a replay-started server, snapshot its fd table and
executable maps, SIGKILL the invoker, and measure that the whole tree and the port die."""
import json
import os
import signal
import socket
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/kama-r53/X3Teardown"
REPLAY = os.path.join(S, "lane/tools/kama-live-replay.py")
RECEIPT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-1.json"
WD = os.path.join(S, "wd")
WORK = os.path.join(S, "w")
OUT = os.path.join(S, "r.json")
RES = os.path.join(S, "result.json")
os.environ["TMPDIR"] = S

for p in (WORK, WD):
    subprocess.run(["rm", "-rf", p], check=False)
os.makedirs(WD, exist_ok=True)

invoker = [
    "/usr/bin/python3", "-c", "import subprocess,sys;sys.exit(subprocess.call(sys.argv[1:]))",
    "/usr/bin/python3", REPLAY, "--receipt", RECEIPT, "--work", WORK, "--out", OUT,
    "--witness-dir", WD,
]
log = open(os.path.join(S, "invoker.log"), "wb")
inv = subprocess.Popen(invoker, stdout=log, stderr=subprocess.STDOUT, cwd=S)
t_launch = time.monotonic()
res = {"seat": "X3Teardown", "round": 53, "build_commit": "c22602bd8d83ab26349d1087e916ca537ee4f9d1",
       "invoker_argv": invoker, "invoker_pid": inv.pid, "launch_monotonic": t_launch}

ready_path = os.path.join(WD, "ready.json")
deadline = t_launch + 420
while time.monotonic() < deadline and not os.path.exists(ready_path) and inv.poll() is None:
    time.sleep(0.02)
res["ready_waited_s"] = round(time.monotonic() - t_launch, 3)
if not os.path.exists(ready_path):
    res["error"] = "no-ready.json"
    res["invoker_exit"] = inv.poll()
    with open(os.path.join(S, "invoker.log"), "rb") as fh:
        res["invoker_log_tail"] = fh.read()[-3000:].decode("utf-8", "replace")
    json.dump(res, open(RES, "w"), indent=2)
    print(json.dumps(res, indent=2))
    sys.exit(3)

ready = json.load(open(ready_path))
res["ready"] = ready
spid, port = int(ready["pid"]), int(ready["port"])
json_copy = os.path.join(S, "ready.json.copy")
open(json_copy, "w").write(open(ready_path).read())


def children(pid):
    try:
        with open(f"/proc/{pid}/task/{pid}/children") as fh:
            return [int(x) for x in fh.read().split()]
    except OSError:
        return []


replay_pid = (children(inv.pid) or [None])[0]
live_children = children(replay_pid) if replay_pid else []
live_pid = (live_children or [None])[0]
pids = {"invoker": inv.pid, "replay": replay_pid, "live": live_pid, "server": spid}
res["pids"] = pids

def state(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            st = fh.read().rsplit(")", 1)[1].split()[0]
        return st
    except (OSError, IndexError):
        return "gone"

def alive(pid):
    return pid is not None and state(pid) not in ("gone", "Z")

t_snap = time.monotonic()
res["snapshot_monotonic_offset_s"] = round(t_snap - t_launch, 3)
res["states_at_snapshot"] = {k: state(v) for k, v in pids.items()}

def run(argv):
    p = subprocess.run(argv, capture_output=True, text=True)
    return {"argv": argv, "rc": p.returncode, "out": p.stdout, "err": p.stderr}

# --- the two required observations --------------------------------------
fd = run(["ls", "-l", f"/proc/{spid}/fd"])
open(os.path.join(S, "fd-ls.txt"), "w").write(fd["out"] + fd["err"])
res["fd_ls_rc"] = fd["rc"]
res["fd_count"] = len([l for l in fd["out"].splitlines() if " -> " in l])
res["fd_lines"] = fd["out"].splitlines()

maps_raw = open(f"/proc/{spid}/maps").read()
open(os.path.join(S, "maps.txt"), "w").write(maps_raw)
rows = [l for l in maps_raw.splitlines() if len(l.split(None, 5)) == 6]
exec_rows = [l for l in rows if "x" in l.split(None, 5)[1]]
exec_file_rows = [l for l in exec_rows if l.split(None, 5)[5].startswith("/")]
open(os.path.join(S, "maps-exec.txt"), "w").write("\n".join(exec_rows) + "\n")
open(os.path.join(S, "maps-exec-file.txt"), "w").write("\n".join(exec_file_rows) + "\n")
res["maps_exec_rows"] = exec_rows
res["maps_exec_file_rows"] = exec_file_rows

# dedupe mapped executable paths (path, dev, inode)
seen, mapped = set(), []
for l in exec_file_rows:
    f = l.split(None, 5)
    key = (f[5], f[3], f[4])
    if key not in seen:
        seen.add(key)
        mapped.append({"path": f[5], "dev": f[3], "inode": f[4]})
res["mapped_exec_paths"] = mapped

res["status"] = run(["sh", "-c", f"grep -E '^(Name|Pid|PPid|Tgid|NSpid|Uid|Gid|Seccomp):' /proc/{spid}/status"])
res["ps_tree"] = run(["ps", "-o", "pid,ppid,pgid,sid,stat,etime,args", "-p",
                      ",".join(str(p) for p in pids.values() if p)])
res["ss_listen"] = run(["ss", "-ltnp", f"sport = :{port}"])
res["ss_estab"] = run(["ss", "-tnp", f"sport = :{port}"])
res["pgrep_lane_tree"] = run(["sh", "-c", f"pgrep -af '{S}/lane/tools|{S}/w/' | grep -v 'pgrep -af'"])
res["memfd_links_in_fd"] = [l for l in fd["out"].splitlines() if "memfd" in l]

# --- kill the invoker ---------------------------------------------------
t_kill = time.monotonic()
os.kill(inv.pid, signal.SIGKILL)
res["kill_monotonic"] = t_kill
res["kill_command"] = f"kill -KILL {inv.pid}  (invoker: python3 -c subprocess.call wrapper)"

first = {"all_gone": None, "port_refused": None}
timeline = []
deadline = t_kill + 30.0
port_refused_ever = False

def port_check():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.25)
    try:
        rc = s.connect_ex(("127.0.0.1", port))
        return rc
    finally:
        s.close()

while time.monotonic() < deadline:
    ms = round((time.monotonic() - t_kill) * 1000)
    states = {k: state(v) for k, v in pids.items()}
    rc = port_check()
    refused = rc in (111, 61)  # ECONNREFUSED Linux / BSD-ish
    port_refused_ever |= refused
    all_gone = not any(alive(v) for v in pids.values())
    if all_gone and first["all_gone"] is None:
        first["all_gone"] = ms
    if refused and first["port_refused"] is None:
        first["port_refused"] = ms
    timeline.append({"ms": ms, "states": states, "connect_ex": rc, "refused": refused})
    if first["all_gone"] is not None and first["port_refused"] is not None:
        break
    time.sleep(0.02)

# reap the invoker if it is our zombie
try:
    res["invoker_exit"] = inv.wait(timeout=5)
except subprocess.TimeoutExpired:
    res["invoker_exit"] = "not-reaped"

# one more sample at/after the 30 s bound
ms = round((time.monotonic() - t_kill) * 1000)
final_states = {k: state(v) for k, v in pids.items()}
final_rc = port_check()
res["timeline"] = timeline
res["first_all_gone_ms"] = first["all_gone"]
res["first_port_refused_ms"] = first["port_refused"]
res["final_offset_ms"] = ms
res["final_states"] = final_states
res["final_connect_ex"] = final_rc
res["final_states_all_gone"] = not any(alive(v) for v in pids.values())
res["final_port_refused"] = final_rc in (111, 61)
res["within_30s"] = (first["all_gone"] is not None and first["all_gone"] <= 30000
                     and first["port_refused"] is not None and first["port_refused"] <= 30000)
res["witness_dir_after"] = sorted(os.listdir(WD))
res["work_rerun_receipt_exists"] = os.path.exists(OUT)
res["leftover_processes"] = run(["sh", "-c", f"pgrep -af '{S}/lane/tools|{S}/w/' | grep -v 'pgrep -af'"])
res["launcher_log_tail"] = open(os.path.join(S, "invoker.log"), "rb").read()[-2000:].decode("utf-8", "replace")

json.dump(res, open(RES, "w"), indent=2)
print(json.dumps({k: res[k] for k in (
    "ready", "pids", "fd_count", "fd_lines", "mapped_exec_paths", "first_all_gone_ms",
    "first_port_refused_ms", "final_states", "within_30s", "leftover_processes",
    "witness_dir_after", "work_rerun_receipt_exists")}, indent=2))
sys.exit(0 if res["within_30s"] and not res["leftover_processes"]["out"].strip() else 1)
