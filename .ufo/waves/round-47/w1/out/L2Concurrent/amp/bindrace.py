#!/usr/bin/env python3
"""Replica of pick_port's default branch (tools/kama-llamacpp-live.py:371-378) to measure the
release/rebind window under a simultaneous start: two processes bind 127.0.0.1:0 with
SO_REUSEADDR, take the offered port, CLOSE, and report it. If both report the same port, the
same single port would have been handed to two children in that window.

Mechanism evidence only: this replicates the lane code path, it is not a lane tool run.
Usage: bindrace.py TRIALS  (TMPDIR must exist)
"""
import json
import os
import socket
import subprocess
import sys
import tempfile

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
CHILD = (
    "import json,socket,sys\n"
    "with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:\n"
    "    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)\n"
    "    s.bind(('127.0.0.1',0))\n"
    "    port=s.getsockname()[1]\n"
    "print(port)\n"
)
NS = {"range_start": 32768, "range_end": 60999}


def spawn():
    return subprocess.Popen([sys.executable, "-c", CHILD], stdout=subprocess.PIPE, text=True)


dup = 0
same_low = 0
ports = []
batches = max(1, TRIALS // 2)
for _ in range(batches):
    a, b = spawn(), spawn()
    pa = int(a.communicate()[0].strip())
    pb = int(b.communicate()[0].strip())
    ports += [pa, pb]
    if pa == pb:
        dup += 1
same_low = sum(1 for p in ports if p < NS["range_start"] or p > NS["range_end"])
print(json.dumps({
    "trials_pairs": batches,
    "binds": len(ports),
    "duplicate_pairs": dup,
    "out_of_ephemeral_range": same_low,
    "kernel_range": NS,
    "python": sys.version.split()[0],
}))
