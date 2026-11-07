#!/usr/bin/env python3
"""SC02: parse-time vs tensor count for the M1/base ROUTER_PY 'files' mode."""
import json, os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from extract import gguf, probe_router_py

W = Path(sys.argv[1])
W.mkdir(parents=True, exist_ok=True)
rp_m1 = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-m1.sh").read_text())
rp_base = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-base.sh").read_text())
exe = W / "ok.gguf"; exe.write_bytes(gguf(1, 32, True))
body = W / "body.json"


def one(rp, path, label):
    body.write_bytes(json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": [str(exe), "-m", str(path)]}}]}).encode())
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-c", rp, str(body), "files", "0"], capture_output=True)
    dt = time.monotonic() - t0
    out = p.stdout.decode().strip()
    print(f"{label} tensors={path.stat().st_size} bytes={path.stat().st_size} dt={dt:.2f}s out={out!r}", flush=True)


print(f"# load1={open('/proc/loadavg').read().split()[0]}")
for tens in (150000, 300000, 600000, 900000, 1200000):
    f = W / f"t{tens}.gguf"
    if not f.exists():
        t0 = time.monotonic()
        f.write_bytes(gguf(tens, 1, False))
        print(f"# built t{tens} in {time.monotonic()-t0:.1f}s size={f.stat().st_size}")
    one(rp_m1, f, "M1")
