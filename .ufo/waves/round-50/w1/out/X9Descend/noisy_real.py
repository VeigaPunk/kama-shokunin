#!/usr/bin/env python3
"""Real replay, noisy invoker: start the actual lane replay with the counter's own
start_replay but an invoker that also keeps one background child, then ask the
counter's replay_pid()/descends_from() what they see. No audited logic changed."""
import importlib.util
import io
import json
import os
import sys
import tarfile
import time

S, repo, tip = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("c1", os.path.join(S, "counter_copy.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

NOISY = ("import subprocess, sys\n"
         "bg = subprocess.Popen(['sleep', '300'])\n"
         "sys.exit(subprocess.call(sys.argv[1:]))\n")

arc = mod.git(repo, "archive", "--format=tar", tip).stdout
tree = os.path.join(S, "nreal-tree")
os.makedirs(tree)
with tarfile.open(fileobj=io.BytesIO(arc)) as tf:
    tf.extractall(tree, filter=lambda m, dest: None if (m.issym() or m.islnk())
                  else tarfile.data_filter(m, dest))

mod.INVOKER = NOISY
rpath = os.path.join(tree, mod.RECEIPTS[0])
p, wd, outj, log, canary, marker = mod.start_replay(tree, rpath, S, "noisyreal")
out = {"invoker": p.pid}
try:
    ready = mod.wait_ready(p, wd)
    out["ready"] = ready
    if ready:
        pid = ready["pid"]
        snap = mod.descendants(p.pid)
        kids = sorted(k for k in snap if (mod.stat_fields(k) or (None, None))[1] == p.pid)
        rp = mod.replay_pid(p)
        out.update({
            "children": kids,
            "children_cmd": [open(f"/proc/{k}/cmdline", "rb").read().split(b"\0")[0].decode()
                             for k in kids],
            "snapshot": sorted(snap),
            "snapshot_parents": {str(k): (mod.stat_fields(k) or (None, None))[1] for k in snap},
            "replay_pid": rp,
            "server": pid,
            "server_descent_by_snapshot_parents": True,
            "server_in_snapshot": pid in snap,
            "counter_tree_check_would_say": (
                f"server pid {pid} does not descend from the replay process {rp}"
                if rp is None or not mod.descends_from(pid, rp) else "ok"),
            "descends_from_server_to_each_child": {str(k): mod.descends_from(pid, k) for k in kids},
        })
    with open(os.path.join(wd, "release"), "w") as fh:
        fh.write("released by X9Descend noisy-invoker probe\n")
    try:
        out["replay_exit"] = p.wait(timeout=mod.EXIT_WAIT)
    except Exception as exc:
        out["replay_exit"] = f"timeout:{type(exc).__name__}"
    j = mod.load(outj)
    out["replay_match"] = j.get("match") if isinstance(j, dict) else j
finally:
    for pid, start in mod.descendants(p.pid).items():
        try:
            os.kill(pid, 9)
        except OSError:
            pass
    if p.poll() is None:
        p.kill()
        p.wait()
    log.close()
with open(os.path.join(S, "noisy-real.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
