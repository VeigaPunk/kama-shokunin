#!/usr/bin/env python3
"""direct-check.py <probe-file> <path>... - call the probe's ROUTER_PY `files` mode once.

Prints one line per candidate: idx<TAB>state<TAB>wall_seconds. The body lists every path once,
in order, so a shared (per-invocation) budget starves later candidates and a per-file budget
does not. Used to find inputs the frozen counters do not distinguish.
"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

probe = Path(sys.argv[1]).read_text()
s = probe.find("ROUTER_PY=$(cat <<'PY'\n") + len("ROUTER_PY=$(cat <<'PY'\n")
e = probe.find("\nPY\n)", s)
rp = probe[s:e]
paths = sys.argv[2:]
exe = paths[0]
with tempfile.TemporaryDirectory() as td:
    body = Path(td) / "body.json"
    data = [{"id": "good", "status": {"value": "unloaded", "args": [exe, "-m", p]}} for p in paths]
    body.write_text(json.dumps({"object": "list", "data": data}, separators=(",", ":")))
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-c", rp, str(body), "files"] + [str(i) for i in range(len(paths))],
                       capture_output=True, timeout=600)
    dt = time.monotonic() - t0
for line in p.stdout.decode().splitlines():
    parts = line.split("\t")
    if len(parts) == 2:
        idx = int(parts[0])
        print(f"{idx}\t{parts[1]}\t{paths[idx]}")
print(f"WALL {dt:.2f}s rc={p.returncode}")
