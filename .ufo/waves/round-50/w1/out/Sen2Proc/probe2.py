#!/usr/bin/env python3
"""Sen2Proc probe 2: ready.json announces a server pid; the child then dies before the
counter observes it.  Drives the build's live tool with a witness dir, kills the server
the moment ready.json appears, and replays the counter's observe() on the announced pid."""
import importlib.util
import json
import os
import signal
import subprocess
import sys
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

wd = os.path.join(S, "wd2")
os.makedirs(wd, exist_ok=True)
for name in ("ready.json", "release"):
    try:
        os.unlink(os.path.join(wd, name))
    except OSError:
        pass
out_json = os.path.join(S, "live-dead.json")
log = open(os.path.join(S, "live-dead.log"), "wb")
argv = [sys.executable, "-B", LIVE, "--server", SERVER, "--model", MODEL,
        "--model-sha256", MODEL_SHA, "--alias", "sen2proc", "--ctx", "256", "--threads", "1",
        "--witness-dir", wd, "--witness-timeout", "60", "--out", out_json]
p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                     start_new_session=True)
res = {"live_argv": argv, "live_pid": p.pid}
ready = None
t0 = time.monotonic()
while time.monotonic() - t0 < 120:
    try:
        with open(os.path.join(wd, "ready.json")) as fh:
            ready = json.load(fh)
        break
    except (OSError, ValueError):
        pass
    if p.poll() is not None:
        break
    time.sleep(0.02)
res["ready"] = ready
if ready:
    pid, port = ready["pid"], ready["port"]
    st = c1.stat_fields(pid)
    res["announced_stat_before_kill"] = st
    try:
        os.kill(pid, signal.SIGKILL)
        res["kill_sent"] = True
    except OSError as exc:
        res["kill_sent"] = f"{type(exc).__name__}: {exc}"
    # what the file says right after the kill, and what /proc says
    res["ready_still_present_immediately"] = os.path.isfile(os.path.join(wd, "ready.json"))
    res["announced_stat_after_kill"] = c1.stat_fields(pid)
    # emulate the counter's poll cadence: it polls ready.json every 200 ms
    time.sleep(0.2)
    res["ready_present_after_200ms"] = os.path.isfile(os.path.join(wd, "ready.json"))
    res["announced_stat_after_200ms"] = c1.stat_fields(pid)
    # the counter's own observation on the announced pid, after the child is gone
    probs = []
    try:
        nonce, mapped = c1.observe(pid, port, ["x"] * 8, "KAMA_R50_CANARY", probs)
        res["observe_nonce"] = nonce
        res["observe_mapped"] = mapped
    except Exception as exc:  # observe is not expected to raise; record if it does
        res["observe_raised"] = f"{type(exc).__name__}: {exc}"
    res["observe_problems"] = probs
res["live_exit"] = p.wait(timeout=120)
log.close()
try:
    with open(out_json) as fh:
        rec = json.load(fh)
    res["receipt"] = {k: rec.get(k) for k in
                      ("schema", "outcome", "setup_error", "model_mapping", "witness",
                       "port_listener_ownership", "teardown")}
    res["checks"] = [(c.get("id"), c.get("passed"), c.get("evaluated")) for c in rec.get("checks") or []]
except (OSError, ValueError) as exc:
    res["receipt"] = f"unreadable: {exc}"
res["ready_left_on_disk"] = os.path.isfile(os.path.join(wd, "ready.json"))
print(json.dumps(res, indent=1))
