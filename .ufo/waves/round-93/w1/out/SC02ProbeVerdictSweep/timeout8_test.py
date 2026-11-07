#!/usr/bin/env python3
"""SC02: can the probe's OWN `timeout 8` kill fire, and does it lose lines?

The probe calls: timeout 8 python3 -c "$ROUTER_PY" "$body" files IDX...
With many DISTINCT slow files the inner 4 s DEADLINE usually fires first
(python exits cleanly, all lines present). But if the per-file work makes the
python run past 8 s BEFORE any deadline check, timeout SIGTERMs it and the
BLOCK-BUFFERED stdout tail is lost -> the shell counts fewer than ncand states
-> nbad < ncand -> unloaded=1 -> MODEL_OK / router-unloaded-autoload.

Test: K distinct files, each a distinct GGUF whose parse costs ~1.3 s
(600000 tensors), and measure wall time + lines seen with timeout 8.
"""
import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from extract import gguf, probe_router_py

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
rp = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-m1.sh").read_text())
TENS = int(sys.argv[2]) if len(sys.argv) > 2 else 600000
exe = W / "ok.gguf"; exe.write_bytes(gguf(1, 32, True))
print(f"# load1={open('/proc/loadavg').read().split()[0]} tensors={TENS}")

for k in (1, 2, 3, 4, 6, 8, 12, 16):
    files = []
    for i in range(k):
        f = W / f"t{i}.gguf"
        if not f.exists():
            f.write_bytes(gguf(TENS, 1, False))
        files.append(str(f))
    body = W / f"b{k}.json"
    body.write_bytes(json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": [str(exe), "-m", files[i]]}}
        for i in range(k)]}).encode())
    idxs = [str(i) for i in range(k)]
    t0 = time.monotonic()
    p = subprocess.run(["timeout", "8", sys.executable, "-c", rp, str(body), "files", *idxs],
                       capture_output=True)
    dt = time.monotonic() - t0
    lines = p.stdout.decode().splitlines()
    states = {}
    for line in lines:
        parts = line.split("\t")
        if len(parts) == 2:
            states[parts[1]] = states.get(parts[1], 0) + 1
    nbad = states.get("missing", 0) + states.get("invalid", 0)
    verdict = "MODEL_UNLOADED" if nbad == k else "MODEL_OK / router-unloaded-autoload"
    print(f"T8 k={k} rc={p.returncode} wall={dt:.2f}s lines={len(lines)}/{k} states={states} "
          f"nbad={nbad} ncand={k} -> {verdict}", flush=True)
print(f"# done load1={open('/proc/loadavg').read().split()[0]}")
