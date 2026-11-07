#!/usr/bin/env python3
"""Round-93 C1 doubling receipt (L1, not a claim counter): one slow invalid GGUF named by N router entries,
N = 512..16384, probe at M1 and at BASE, verdict and wall time. Reuses the frozen counter's stub and fixtures.
Usage: c1-doubling.py <scratch>"""
import importlib.util, os, subprocess, sys, tempfile, time
from pathlib import Path
spec = importlib.util.spec_from_file_location("rr", "tools/round93-router-repeat.py")
rr = importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)
M1, B = "fe5f031cb1b9d33e1160360d892149b8ac3c7771", rr.BASE
work = Path(tempfile.mkdtemp(dir=sys.argv[1])); R = rr.Runner(work)
slow = work / "slow.gguf"; slow.write_bytes(rr.gguf(rr.TENSORS, 1, False)); ok = work / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
show = lambda r: subprocess.run(["git", "show", f"{r}:tools/kama-probe.sh"], capture_output=True, check=True).stdout
print(f"# M1={M1} BASE={B} load1={open('/proc/loadavg').read().split()[0]}")
for n in (512, 1024, 2048, 4096, 8192, 16384):
    body = rr.router_body([[str(ok), "-m", str(slow)]] * n)
    for name, rev in (("M1", M1), ("BASE", B)):
        R.install(show(rev))
        with rr.Stub({"/v1/models": body, "/props": rr.PROPS}) as st:
            rc, v, r, dt = R.check(st.port)
        print(f"C1_DOUBLING n={n} rev={name} verdict={v} reason={r} seconds={dt:.2f} body_bytes={len(body)}", flush=True)
