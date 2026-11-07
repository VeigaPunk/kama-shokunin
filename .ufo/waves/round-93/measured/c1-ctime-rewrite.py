#!/usr/bin/env python3
"""Round-93 wave-1 RV01 DEFECT-1 reproduction (L1 receipt): ROUTER_PY of a probe revision grades a body whose
entries name X, slow, X; while `slow` is parsed, X (a valid GGUF) is rewritten in place to same-size invalid bytes
and its mtime restored with os.utime(ns=...). Right answer for entry 2: `invalid`. Usage: c1-ctime-rewrite.py <rev> <scratch>"""
import importlib.util, json, os, subprocess, sys, tempfile, threading, time
from pathlib import Path
spec = importlib.util.spec_from_file_location("rr", "tools/round93-router-repeat.py")
rr = importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)
rev, scratch = sys.argv[1], Path(sys.argv[2]); scratch.mkdir(parents=True, exist_ok=True)
probe = subprocess.run(["git", "show", f"{rev}:tools/kama-probe.sh"], capture_output=True, check=True).stdout
rp = rr.probe_router_py(probe)
for run in range(3):
    w = Path(tempfile.mkdtemp(dir=scratch))
    x, slow = w / "x.gguf", w / "slow.gguf"
    good = rr.gguf(1, 32, True); x.write_bytes(good); slow.write_bytes(rr.gguf(rr.TENSORS, 1, False))
    bad = b"XXXX" + good[4:]
    st0 = os.stat(x)
    body = w / "b.json"; body.write_bytes(rr.router_body([[str(x), "-m", str(x)], [str(x), "-m", str(slow)], [str(x), "-m", str(x)]]))
    def rewrite():
        time.sleep(0.15)
        with open(x, "r+b") as f:
            f.write(bad)
        os.utime(x, ns=(st0.st_atime_ns, st0.st_mtime_ns))
    t = threading.Thread(target=rewrite); t.start()
    p = subprocess.run([sys.executable, "-c", rp, str(body), "files", "0", "1", "2"], capture_output=True, text=True)
    t.join()
    st1 = os.stat(x)
    states = " | ".join(p.stdout.strip().split("\n"))
    print(f"CTIME_REWRITE rev={rev} run={run + 1} states=[{states}] size_same={st0.st_size == st1.st_size} "
          f"mtime_same={st0.st_mtime_ns == st1.st_mtime_ns} ctime_changed={st0.st_ctime_ns != st1.st_ctime_ns} "
          f"entry2_right={int(p.stdout.strip().split(chr(10))[-1].endswith('invalid'))}")
