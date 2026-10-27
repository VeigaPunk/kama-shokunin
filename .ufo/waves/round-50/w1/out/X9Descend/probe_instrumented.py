#!/usr/bin/env python3
"""Run the frozen C1 counter from a byte-identical scratch copy, recording every
descendants()/replay_pid()/start_replay() call the counter makes. Observations only:
no audited logic is changed (wrappers call the original functions and return their
values unchanged)."""
import importlib.util
import json
import os
import subprocess
import sys
import time

S, repo, tip = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("c1", os.path.join(S, "counter_copy.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

log = {"counter_pid": os.getpid(), "descendants": [], "replay_pid": [], "starts": []}
decoy = subprocess.Popen(["sleep", "600"])          # unrelated process owned by the counter side
log["decoy_pid"] = decoy.pid
orig_desc, orig_rp, orig_start = mod.descendants, mod.replay_pid, mod.start_replay


def cmdline(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            parts = fh.read().split(b"\0")
        return [p.decode("utf-8", "replace") for p in parts if p][:8]
    except OSError:
        return []


def procs(root):
    out = orig_desc(root)
    return {str(pid): {"start": start,
                       "ppid": (mod.stat_fields(pid) or (None, None))[1],
                       "cmd": cmdline(pid)} for pid, start in out.items()}


def rec_desc(root):
    out = orig_desc(root)
    log["descendants"].append({"t": time.time(), "root": root,
                               "tag": log["starts"][-1]["tag"] if log["starts"] else None,
                               "procs": procs(root)})
    return out


def rec_rp(p):
    r = orig_rp(p)
    kids = [pid for pid in orig_desc(p.pid)
            if (mod.stat_fields(pid) or (None, None))[1] == p.pid]
    log["replay_pid"].append({"invoker": p.pid, "direct_children": kids, "result": r,
                              "self_children": [c.pid for c in []]})
    return r


def rec_start(tree, rpath, Sd, tag):
    log["starts"].append({"t": time.time(), "tag": tag, "receipt": os.path.basename(rpath)})
    return orig_start(tree, rpath, Sd, tag)


mod.descendants, mod.replay_pid, mod.start_replay = rec_desc, rec_rp, rec_start
try:
    code = mod.main(["--repo", repo, "--tip", tip, "--scratch", S,
                     "--out", os.path.join(S, "c1-instrumented.out")])
finally:
    log["decoy_alive_at_end"] = decoy.poll() is None
    decoy.kill()
    decoy.wait()
log["exit"] = code
with open(os.path.join(S, "snapshots.json"), "w") as fh:
    json.dump(log, fh, indent=1)
sys.exit(code)
