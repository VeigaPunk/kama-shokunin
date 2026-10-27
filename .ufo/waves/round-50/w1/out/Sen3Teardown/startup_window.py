#!/usr/bin/env python3
"""startup_window.py - round-50 seat Sen3Teardown, limit probe (v2).

`kama-live-replay.py` arms its parent-death signal in main() (tools/kama-live-replay.py:587,
after interpreter start-up and argparse), not in the invoker. This probe measures that window:
the counter's invoker is started, and SIGKILLed `delay` ms after its replay child is FIRST
OBSERVED in /proc; survivors are found by scanning /proc for the run's work path, not from a
pre-kill child snapshot (v1's flaw: a child forked after the snapshot was missed, which is the
leak itself).

A survivor is a replay the invoker's death did not reach. It is recorded and then killed
together with anything it spawned. Nothing outside --scratch is written.
"""
from __future__ import annotations

import json
import os
import signal
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


def pids_naming(marker):
    out = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if any(marker in a for a in argv_of(pid)):
            out.append(pid)
    return out


def alive(pid, start):
    s = stat_of(pid)
    return bool(s and s["start"] == start and s["state"] != "Z")


def children_of(pid):
    out = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        s = stat_of(int(name))
        if s and s["ppid"] == pid:
            out.append(int(name))
    return out


def kernel_children(pid):
    """The kernel's own child list: /proc/<pid>/task/<pid>/children (one cheap read)."""
    try:
        with open(f"/proc/{pid}/task/{pid}/children") as fh:
            return [int(x) for x in fh.read().split()]
    except (OSError, ValueError):
        return []


def age_ms(pid):
    """Age of pid since fork, from /proc/uptime and its starttime (clock ticks)."""
    s = stat_of(pid)
    if not s:
        return None
    try:
        with open("/proc/uptime") as fh:
            up = float(fh.read().split()[0])
    except (OSError, ValueError):
        return None
    return round((up - int(s["start"]) / os.sysconf("SC_CLK_TCK")) * 1000.0, 2)


def reap(run_dir):
    """kill every process whose argv names this run's work path, children first."""
    killed = []
    for _ in range(6):
        pids = pids_naming(run_dir)
        if not pids:
            break
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append(pid)
            except OSError:
                pass
        time.sleep(0.05)
    return killed


def trial(tree, receipt, S, delay_ms, idx):
    run_dir = os.path.join(S, f"startup-{idx}-{delay_ms}ms")
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
    t_spawn = time.monotonic()
    p = subprocess.Popen(argv, env=env, cwd=tree, stdout=log, stderr=log,
                         start_new_session=True)
    res = {"delay_ms": delay_ms, "invoker_pid": p.pid}
    # first sight of the replay child: the kernel's child list, polled at ~0.2 ms
    child = None
    while time.monotonic() - t_spawn < 5:
        kids = kernel_children(p.pid)
        if kids:
            child = (kids[0], (stat_of(kids[0]) or {}).get("start"))
            break
        time.sleep(0.0002)
    res["child_first_seen_ms"] = round((time.monotonic() - t_spawn) * 1000, 2) if child else None
    res["child_age_at_sight_ms"] = age_ms(child[0]) if child else None
    if child is None:
        res["stage"] = "no-child"
        reap(run_dir)
        log.close()
        return res
    if delay_ms:
        time.sleep(delay_ms / 1000.0)
    t_kill = time.monotonic()
    res["child_age_at_kill_ms"] = age_ms(child[0])
    res["since_sight_ms"] = round((t_kill - (t_spawn + (res["child_first_seen_ms"] or 0) / 1000)) * 1000, 2)
    try:
        os.kill(p.pid, signal.SIGKILL)
        res["invoker_killed"] = True
    except OSError as exc:
        res["invoker_killed"] = str(exc)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    res["invoker_exit"] = p.returncode
    time.sleep(0.5)
    survivors = []
    for pid in pids_naming(run_dir):
        s = stat_of(pid)
        if s and s["state"] != "Z":
            survivors.append({"pid": pid, "ppid": s["ppid"],
                              "argv": [a for a in argv_of(pid) if run_dir in a][:3]})
    res["survivors_at_0.5s"] = survivors
    res["child_alive_at_0.5s"] = alive(child[0], child[1])
    res["leak"] = bool(survivors)
    res["killed_by_cleanup"] = reap(run_dir)
    time.sleep(0.1)
    res["remaining_after_cleanup"] = pids_naming(run_dir)
    res["out_exists"] = os.path.exists(os.path.join(run_dir, "out.json"))
    log.close()
    return res


def main():
    tree, receipt, S = sys.argv[1], sys.argv[2], sys.argv[3]
    delays = [int(x) for x in (sys.argv[4].split(",") if len(sys.argv) > 4 else
                               ["0", "0", "0", "2", "5", "10", "20", "40", "80", "200"])]
    results = [trial(tree, receipt, S, d, i) for i, d in enumerate(delays)]
    with open(os.path.join(S, "startup_window.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    for r in results:
        print(f"delay {r['delay_ms']:>4} ms  child_age_at_kill {r.get('child_age_at_kill_ms')} ms  "
              f"leak={r.get('leak')} survivors={len(r.get('survivors_at_0.5s') or [])} "
              f"child_alive={r.get('child_alive_at_0.5s')} out={r.get('out_exists')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
