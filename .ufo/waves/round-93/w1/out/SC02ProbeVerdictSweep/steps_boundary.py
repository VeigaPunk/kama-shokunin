#!/usr/bin/env python3
"""SC02: locate the MAX_STEPS boundary (4M steps) exactly, and show it is
host-load INDEPENDENT (a step count, not a wall clock) while the 4.0 s wall
DEADLINE is host-load DEPENDENT.

Reports steps consumed per parse and the resulting verdict.
"""
import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from extract import gguf, probe_router_py

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
rp = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-m1.sh").read_text())
exe = W / "ok.gguf"; exe.write_bytes(gguf(1, 32, True))
print(f"# load1={open('/proc/loadavg').read().split()[0]}")
for tens in (600000, 650000, 675000, 690000, 700000, 720000):
    f = W / f"t{tens}.gguf"
    if not f.exists():
        f.write_bytes(gguf(tens, 1, False))
    body = W / f"b{tens}.json"
    body.write_bytes(json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": [str(exe), "-m", str(f)]}}]}).encode())
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-c", rp, str(body), "files", "0"], capture_output=True)
    dt = time.monotonic() - t0
    print(f"BOUND tensors={tens} wall={dt:.2f}s out={p.stdout.decode().strip()!r} "
          f"-> {'invalid (decided)' if b'invalid' in p.stdout else 'undecided -> loadable -> MODEL_OK'}",
          flush=True)
print(f"# done load1={open('/proc/loadavg').read().split()[0]}")
