#!/usr/bin/env python3
"""orphan_serves.py - round-50 seat Sen3Teardown, impact of the startup window.

The counter's invoker is SIGKILLed the instant its replay child appears (child age ~0 ms,
inside the window measured by startup_window.py). The replay is then checked to run on to a
ready server: ready.json appears, the server listens, and its ppid chain ends at init instead
of at any invoker. The orphan replay is then killed -- the built chain below it still tears
the live tool and server down -- and the port is confirmed closed. Nothing outside --scratch
is written; the tree is killed at the end.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time

INVOKER = "import subprocess, sys\nsys.exit(subprocess.call(sys.argv[1:]))\n"
PASS_ENV = ("PATH", "LANG", "HOME", "XDG_CACHE_HOME", "TMPDIR",
            "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "no_proxy")


def stat_of(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    i = raw.rfind(b")")
    f = raw[i + 2:].split()
    try:
        return {"state": f[0].decode(), "ppid": int(f[1]), "start": f[19].decode()}
    except (IndexError, ValueError):
        return None


def argv_of(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            return [a.decode("utf-8", "replace") for a in fh.read().split(b"\0") if a]
    except OSError:
        return []


def kernel_children(pid):
    try:
        with open(f"/proc/{pid}/task/{pid}/children") as fh:
            return [int(x) for x in fh.read().split()]
    except (OSError, ValueError):
        return []


def alive(pid, start):
    s = stat_of(pid)
    return bool(s and s["start"] == start and s["state"] != "Z")


def chain(pid):
    out = []
    seen = set()
    while pid and pid not in seen:
        seen.add(pid)
        s = stat_of(pid)
        if not s:
            break
        a = argv_of(pid)
        out.append({"pid": pid, "ppid": s["ppid"], "argv0": a[0] if a else "",
                    "role": ("server" if a and os.path.basename(a[0]) == "llama-server" else
                             "replay" if any(x.endswith("kama-live-replay.py") for x in a) else
                             "live" if any(x.endswith("kama-llamacpp-live.py") for x in a) else
                             "invoker" if any("sys.exit(subprocess.call" in x for x in a) else "other")})
        pid = s["ppid"]
    return out


def port_refuses(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    rc = s.connect_ex(("127.0.0.1", port))
    s.close()
    return rc != 0


def pids_naming(marker):
    out = []
    for name in os.listdir("/proc"):
        if name.isdigit():
            pid = int(name)
            if any(marker in a for a in argv_of(pid)):
                out.append(pid)
    return out


def main():
    tree, receipt, S = sys.argv[1], sys.argv[2], sys.argv[3]
    run_dir = os.path.join(S, "orphan")
    os.makedirs(os.path.join(run_dir, "wd"), exist_ok=True)
    env = {k: os.environ[k] for k in PASS_ENV if k in os.environ}
    for k in ("XDG_CACHE_HOME", "TMPDIR"):
        d = os.path.join(run_dir, k.lower())
        os.makedirs(d, exist_ok=True)
        env[k] = d
    log = open(os.path.join(run_dir, "run.log"), "wb")
    argv = [sys.executable, "-I", "-c", INVOKER, sys.executable, "-I",
            os.path.join(tree, "tools", "kama-live-replay.py"), "--receipt", receipt,
            "--work", os.path.join(run_dir, "work"), "--out", os.path.join(run_dir, "out.json"),
            "--witness-dir", os.path.join(run_dir, "wd")]
    res = {}
    p = subprocess.Popen(argv, env=env, cwd=tree, stdout=log, stderr=log, start_new_session=True)
    while True:
        kids = kernel_children(p.pid)
        if kids:
            break
        time.sleep(0.0002)
    replay = kids[0]
    res["replay_pid"], res["invoker_pid"] = replay, p.pid
    os.kill(p.pid, signal.SIGKILL)
    p.wait()
    res["invoker_exit"] = p.returncode
    # wait for the orphan to reach its ready server
    ready = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 60:
        try:
            with open(os.path.join(run_dir, "wd", "ready.json")) as fh:
                ready = json.load(fh)
            break
        except (OSError, ValueError):
            time.sleep(0.05)
    res["ready_s"] = round(time.monotonic() - t0, 2)
    res["ready"] = ready
    if ready:
        pid, port = ready["pid"], ready["port"]
        res["server_chain"] = chain(pid)
        res["replay_alive"] = alive(replay, (stat_of(replay) or {}).get("start"))
        res["port_accepts"] = not port_refuses(port)
    # kill the orphan replay only: the chain below it must still take the tree down
    os.kill(replay, signal.SIGKILL)
    t1 = time.monotonic()
    while time.monotonic() - t1 < 30:
        left = [pid for pid in pids_naming(run_dir) if stat_of(pid)]
        if not left and (not ready or port_refuses(ready["port"])):
            break
        time.sleep(0.02)
    res["teardown_after_orphan_kill_s"] = round(time.monotonic() - t1, 2)
    res["left_after_orphan_kill"] = pids_naming(run_dir)
    res["port_refuses_after"] = port_refuses(ready["port"]) if ready else None
    for pid in pids_naming(run_dir):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    log.close()
    with open(os.path.join(S, "orphan_serves.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: res[k] for k in ("ready_s", "server_chain", "port_accepts",
                                          "teardown_after_orphan_kill_s", "left_after_orphan_kill",
                                          "port_refuses_after")}, indent=1)[:2500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
