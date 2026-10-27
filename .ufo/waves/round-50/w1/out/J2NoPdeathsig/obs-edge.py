#!/usr/bin/env python3
"""J2NoPdeathsig edge probe: same replay tree, ONE member killed, observe the rest.

Same setup as obs-timeline.py (the frozen counter's own helpers), but the signal goes to a
member chosen on the command line:
  invoker  the process the counter kills in its teardown leg (no pdeathsig in this fixture)
  replay   the invoker's child (fixture: its own prctl is gone; the live tool's getppid()
           poll in tools/kama-llamacpp-live.py:358-363 is the remaining detector)
  live     the live tool (its preexec pdeathsig for the server is untouched)
Observation window 45 s, 0.5 s sampling.
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

tree, S, who = sys.argv[1], sys.argv[2], sys.argv[3]
rpath = os.path.join(tree, c1.RECEIPTS[0])
obs = {"tree": tree, "killed": who}
p, wd, outj, log, canary, marker = c1.start_replay(tree, rpath, S, "kill-" + who)
snap = {}
try:
    ready = c1.wait_ready(p, wd)
    if ready is None:
        print(json.dumps({"error": "no ready.json", "invoker_exit": p.poll()}))
        raise SystemExit(2)
    snap = c1.descendants(p.pid)
    kids = [pid for pid, _s in snap.items() if (c1.stat_fields(pid) or (None, None))[1] == p.pid]
    replay = kids[0] if len(kids) == 1 else None
    server = ready["pid"]
    live = (c1.stat_fields(server) or (None, None))[1]
    target = {"invoker": p.pid, "replay": replay, "live": live, "server": server}[who]
    obs.update({"invoker": p.pid, "replay": replay, "live": live, "server": server, "target": target,
                "port": ready["port"], "descendants": {str(k): v for k, v in snap.items()}})
    if target is None:
        print(json.dumps({"error": "target pid unknown", **obs}))
        raise SystemExit(2)
    os.kill(target, signal.SIGKILL)
    if who == "invoker":
        p.wait()
    t0 = time.monotonic()
    samples, gone = [], None
    while time.monotonic() - t0 < 45:
        alive = sorted(pid for pid, start in snap.items() if c1.pid_alive(pid, start))
        refused = c1.port_refuses(ready["port"])
        samples.append({"t": round(time.monotonic() - t0, 2), "alive": alive, "port_refuses": refused})
        if not alive and refused:
            gone = time.monotonic() - t0
            break
        time.sleep(0.5)
    obs["all_gone_after_s"] = None if gone is None else round(gone, 2)
    obs["samples"] = samples
    obs["example_sample"] = samples[min(4, len(samples) - 1)]
finally:
    c1.reap(p, snap.items())
    log.close()
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError:
        pass
print(json.dumps(obs, indent=1))
