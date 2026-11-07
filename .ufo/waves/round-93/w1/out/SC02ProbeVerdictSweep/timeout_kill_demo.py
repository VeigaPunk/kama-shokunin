#!/usr/bin/env python3
"""SC02: the `timeout 8` kill of router_file_states loses tail lines, and the shell
counts only what arrived -> nbad undercount -> false green.

Mechanism, minimal: run the probe's OWN router_file_states wrapper (timeout 8) on a
body with K distinct slow files and count the lines the shell would see. Then show
that a shorter timeout kills the same python earlier and drops lines.

The shell-side counter is exactly router_refine's:
    nbad = #{state in (missing, invalid)} ; ncand = K
    if nbad < ncand -> unloaded=1 -> MODEL_OK / router-unloaded-autoload
"""
import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from extract import gguf, probe_router_py

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
rp = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-m1.sh").read_text())
exe = W / "ok.gguf"; exe.write_bytes(gguf(1, 32, True))
print(f"# load1={open('/proc/loadavg').read().split()[0]}")


def mkbody(k):
    files = []
    for i in range(k):
        f = W / f"d{i}.gguf"
        if not f.exists():
            f.write_bytes(gguf(150000, 1, False))
        files.append(str(f))
    body = W / f"body{k}.json"
    body.write_bytes(json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": [str(exe), "-m", files[i]]}}
        for i in range(k)]}).encode())
    return body


for k in (1, 2, 4, 8, 16, 32, 64, 128, 256):
    body = mkbody(k)
    idxs = [str(i) for i in range(k)]
    for tmo in ("8", "3"):
        t0 = time.monotonic()
        p = subprocess.run(["timeout", tmo, sys.executable, "-c", rp, str(body), "files", *idxs],
                           capture_output=True)
        dt = time.monotonic() - t0
        lines = p.stdout.decode().splitlines()
        nbad = sum(1 for l in lines if l.split("\t")[-1] in ("missing", "invalid"))
        verdict = "MODEL_UNLOADED (nbad==ncand)" if nbad == k else (
            "MODEL_OK / router-unloaded-autoload (nbad<ncand)" if nbad < k else "other")
        print(f"TK k={k} timeout={tmo} rc={p.returncode} wall={dt:.2f}s lines={len(lines)}/{k} "
              f"nbad={nbad} ncand={k} -> {verdict}", flush=True)
print(f"# done load1={open('/proc/loadavg').read().split()[0]}")
