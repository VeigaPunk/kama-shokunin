#!/usr/bin/env python3
"""SC02: can the probe's own `timeout 8` kill fire, losing block-buffered lines?

A file whose parse hits MAX_STEPS (4M steps) takes ~2.4 s unloaded; under heavy
host load it takes longer than the OUTER `timeout 8`. Then timeout SIGTERMs the
python, the block-buffered stdout tail is lost, and router_refine counts fewer
states than candidates -> nbad < ncand -> MODEL_OK / router-unloaded-autoload.

Usage: timeout8_load.py <scratch> <burners> <tensors>
"""
import json, os, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from extract import gguf, probe_router_py

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
BURNERS = int(sys.argv[2]) if len(sys.argv) > 2 else 0
TENS = int(sys.argv[3]) if len(sys.argv) > 3 else 700000
rp = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-m1.sh").read_text())
exe = W / "ok.gguf"; exe.write_bytes(gguf(1, 32, True))


def start(n):
    ps = []
    for _ in range(n):
        p = subprocess.Popen([sys.executable, "-c", "while True: pass"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        ps.append(p)
    time.sleep(2.0)
    return ps


def kill(ps):
    for p in ps:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            p.kill()
    for p in ps:
        p.wait()


burn = start(BURNERS) if BURNERS else []
try:
    for k in (1, 2, 4, 8):
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
        killed = "TIMEOUT-KILLED (lines lost)" if p.returncode == 124 else "exited"
        print(f"T8L burners={BURNERS} k={k} rc={p.returncode} {killed} wall={dt:.2f}s "
              f"lines={len(lines)}/{k} states={states} nbad={nbad} ncand={k} -> {verdict} "
              f"load1={open('/proc/loadavg').read().split()[0]}", flush=True)
finally:
    kill(burn)
