#!/usr/bin/env python3
"""J2NoPdeathsig timeline observation: how long does the ablated replay tree outlive the invoker?

Reuses the frozen counter's own helpers (start_replay, wait_ready, descendants, pid_alive,
port_refuses) so the setup is identical to its teardown leg; only the observation window
differs (240 s instead of KILL_WAIT=30, sampling every 0.5 s).
"""
import importlib.util
import json
import os
import signal
import sys
import time

COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py"
spec = importlib.util.spec_from_file_location("c1", COUNTER)
c1 = importlib.util.module_from_spec(spec)
sys.dont_write_bytecode = True
spec.loader.exec_module(c1)

tree = sys.argv[1]
S = sys.argv[2]
rpath = os.path.join(tree, c1.RECEIPTS[0])
obs = {"tree": tree, "receipt": rpath}

p, wd, outj, log, canary, marker = c1.start_replay(tree, rpath, S, "timeline")
snap = {}
try:
    ready = c1.wait_ready(p, wd)
    if ready is None:
        print(json.dumps({"error": "no ready.json", "invoker_exit": p.poll()}))
        raise SystemExit(2)
    snap = c1.descendants(p.pid)
    obs.update({"invoker": p.pid, "server_pid": ready["pid"], "port": ready["port"],
                "descendants": {str(k): v for k, v in snap.items()}})
    t_ready = time.monotonic()
    os.kill(p.pid, signal.SIGKILL)
    p.wait()
    obs["invoker_killed_at_monotonic"] = round(t_ready, 3)
    samples = []
    died = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 240:
        alive = sorted(pid for pid, start in snap.items() if c1.pid_alive(pid, start))
        refused = c1.port_refuses(ready["port"])
        dt = time.monotonic() - t0
        samples.append({"t": round(dt, 2), "alive": alive, "port_refuses": refused})
        if not alive and refused:
            died = dt
            break
        time.sleep(0.5)
    obs["samples"] = samples
    obs["all_gone_after_s"] = None if died is None else round(died, 2)
    obs["alive_at_end"] = sorted(pid for pid, start in snap.items() if c1.pid_alive(pid, start))
    obs["port_refuses_at_end"] = c1.port_refuses(ready["port"])
    obs["bind_gate_30s"] = next((s for s in samples if s["t"] >= 30.0), None)
    # does the tree survive even its own run (ready.json pid still the marker)?
    try:
        obs["ready_json_still_present"] = os.path.exists(os.path.join(wd, "ready.json"))
    except OSError:
        pass
finally:
    c1.reap(p, snap.items())
    log.close()
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError:
        pass
print(json.dumps(obs, indent=1))
