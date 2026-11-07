#!/usr/bin/env python3
"""Two questions about the frozen round-92 C2 counter, measured (CR01 review).

(a) BASE and M are installed at the same path with the same cwd/TMPDIR. What state can cross?
    After each run this lists the shared cwd (which is TMPDIR) and the probe file hash.
(b) The probe's own `--timeout 5` is curl's --max-time; the L1/L2 bodies are 3.8 MB. How much of
    that 5 s does the transfer take on this host?

Usage: samepath-probe.py --counter FILE --base FILE --m2 FILE --work DIR
"""
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import time
from pathlib import Path


def load(path):
    spec = importlib.util.spec_from_file_location("r92counter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def state(R, label):
    cwd = R.cwd
    files = sorted(p.name for p in cwd.iterdir())
    return {"label": label, "probe_sha256": hashlib.sha256(R.probe.read_bytes()).hexdigest()[:16],
            "cwd_entries_after_run": files}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", type=Path, required=True)
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--m2", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    a = ap.parse_args()
    m = load(a.counter)
    bbytes, mbytes = a.base.read_bytes(), a.m2.read_bytes()
    w = a.work / "samepath"
    shutil.rmtree(w, ignore_errors=True)
    w.mkdir(parents=True)
    R = m.Runner(w)
    recs = []
    routes = {"/v1/models": m.jbody(m.ids_doc(["\\" * 2000]))}
    with m.Stub(routes) as s:
        R.install(bbytes)
        rc, so, dt = R.check(s.port, "good")
        recs.append(state(R, "base-after-run") | {"rc": rc, "seconds": round(dt, 2)})
        R.install(mbytes)
        rc, so, dt = R.check(s.port, "good")
        recs.append(state(R, "m2-after-run") | {"rc": rc, "seconds": round(dt, 2)})
    # (b) raw transfer of the L1 body, curl flags identical to fetch()
    body = m.jbody(m.ids_doc(["\\" * m.BIG]))
    with m.Stub({"/v1/models": body}) as s:
        for i in range(3):
            t0 = time.monotonic()
            p = subprocess.run(["curl", "-sS", "--noproxy", "*", "--connect-timeout", "2",
                                "--max-time", "5", "-o", "/dev/null",
                                "-w", "%{time_total}|%{size_download}",
                                f"http://127.0.0.1:{s.port}/v1/models"], capture_output=True, text=True)
            recs.append({"label": f"curl-L1-body-{i}", "rc": p.returncode, "wall": round(time.monotonic() - t0, 2),
                         "curl": p.stdout.strip(), "bytes": len(body)})
    for r in recs:
        print("SAMEPATH " + json.dumps(r, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
