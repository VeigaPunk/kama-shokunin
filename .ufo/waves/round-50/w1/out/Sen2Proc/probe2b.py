#!/usr/bin/env python3
"""Sen2Proc probe 2b: race the witness announce.  Watch the witness dir with inotify; when
the tool creates ready.json.tmp.<pid> (after its _child_running guard, before os.replace),
SIGSTOP the tool, SIGKILL the server child, SIGCONT: ready.json is then written while the
child is already dead.  Record what the file says and the announced pid's state at read."""
import ctypes
import ctypes.util
import importlib.util
import json
import os
import signal
import struct
import subprocess
import sys
import threading
import time

S = "/fast/scratch/hyaku/kama-r50/Sen2Proc"
LIVE = os.path.join(S, "tree97", "tools", "kama-llamacpp-live.py")
SERVER = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
MODEL = os.path.join(S, "xfs-model", "stories260K.gguf")
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


c1 = load("c1", os.path.join(S, "imp", "c1.py"))

libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
IN_CREATE = 0x100
IN_MOVED_TO = 0x80
IN_NONBLOCK = 0x800
IN_CLOEXEC = 0x80000


def child_of(pid):
    kids = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        st = c1.stat_fields(int(name))
        if st and st[1] == pid:
            kids.append(int(name))
    return kids


wd = os.path.join(S, "wd2b")
os.makedirs(wd, exist_ok=True)
for name in ("ready.json", "release"):
    try:
        os.unlink(os.path.join(wd, name))
    except OSError:
        pass
out_json = os.path.join(S, "live-race.json")
log = open(os.path.join(S, "live-race.log"), "wb")
argv = [sys.executable, "-B", LIVE, "--server", SERVER, "--model", MODEL,
        "--model-sha256", MODEL_SHA, "--alias", "sen2proc", "--ctx", "256", "--threads", "1",
        "--witness-dir", wd, "--witness-timeout", "30", "--out", out_json]
p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                     start_new_session=True)
res = {"live_pid": p.pid}

fd = libc.inotify_init1(IN_NONBLOCK | IN_CLOEXEC)
wd_id = libc.inotify_add_watch(fd, wd.encode(), IN_CREATE | IN_MOVED_TO)
res["inotify_wd"] = wd_id
stop = threading.Event()
events = []


def watcher():
    acted = {"stopped": False, "killed": None, "note": None}
    while not stop.is_set():
        try:
            buf = os.read(fd, 4096)
        except BlockingIOError:
            time.sleep(0.0005)
            continue
        except OSError:
            break
        off = 0
        while off + 16 <= len(buf):
            _w, mask, _cookie, ln = struct.unpack_from("iIII", buf, off)
            name = buf[off + 16:off + 16 + ln].rstrip(b"\0").decode("utf-8", "replace")
            off += 16 + ln
            events.append({"name": name, "mask": mask, "t": time.monotonic()})
            if name.startswith("ready.json.tmp.") and not acted["stopped"]:
                # the guard already passed; freeze the tool before its os.replace
                os.kill(p.pid, signal.SIGSTOP)
                acted["stopped"] = True
                kids = child_of(p.pid)
                acted["children_seen"] = kids
                if kids:
                    try:
                        os.kill(kids[0], signal.SIGKILL)
                        acted["killed"] = kids[0]
                        acted["t_kill"] = time.monotonic()
                        os.waitpid(kids[0], os.WNOHANG)
                    except OSError as exc:
                        acted["note"] = f"{type(exc).__name__}: {exc}"
                os.kill(p.pid, signal.SIGCONT)
                stop.set()
                return
    res["watcher"] = acted


th = threading.Thread(target=watcher, daemon=True)
th.start()
ready = None
deadline = time.monotonic() + 120
while time.monotonic() < deadline:
    try:
        with open(os.path.join(wd, "ready.json")) as fh:
            ready = json.load(fh)
        res["ready_read_t"] = time.monotonic() - res.get("t0", time.monotonic())
        break
    except (OSError, ValueError):
        pass
    if p.poll() is not None:
        break
    time.sleep(0.001)
th.join(timeout=5)
res["ready"] = ready
if ready:
    st = c1.stat_fields(ready["pid"])
    res["announced_pid_stat_at_read"] = st
    res["announced_pid_alive_at_read"] = c1.pid_alive(ready["pid"])
tf = time.monotonic()
res["wd_listing"] = sorted(os.listdir(wd))
while time.monotonic() - tf < 3 and os.path.isfile(os.path.join(wd, "ready.json")):
    time.sleep(0.05)
res["ready_still_present_after_3s"] = os.path.isfile(os.path.join(wd, "ready.json"))
res["live_exit"] = p.wait(timeout=60)
log.close()
try:
    with open(out_json) as fh:
        rec = json.load(fh)
    res["receipt"] = {k: rec.get(k) for k in
                      ("outcome", "setup_error", "model_mapping", "witness",
                       "port_listener_ownership", "teardown")}
except (OSError, ValueError) as exc:
    res["receipt"] = f"unreadable: {exc}"
res["events"] = events
print(json.dumps(res, indent=1, default=str))

# prove the announced pid is dead by the time the counter would observe it
if ready:
    probs = []
    try:
        c1.observe(ready["pid"], ready["port"], ["x"] * 8, "KAMA_R50_CANARY", probs)
    except Exception as exc:
        probs.append(f"observe raised {type(exc).__name__}: {exc}")
    print(json.dumps({"observe_problems": probs}, indent=1))
