#!/usr/bin/env python3
"""SC02: load-threshold matrix, page-cache confound removed.

ONE slow file, N entries naming it, ONE file on disk for the whole run (so the
page cache is warm from the first run onward and every run reads the same
bytes). Only the host CPU load changes. Any verdict change is therefore caused
by host load/time alone.

Also runs BASE with the SAME file for the same reason.
"""
import os, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
NENT = int(sys.argv[2]) if len(sys.argv) > 2 else 64
BURNERS = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [0, 50, 100, 150]
R = rr.Runner(W)
fx = W / "fx"; fx.mkdir(exist_ok=True)
slow = fx / "slow.gguf"
if not slow.exists():
    slow.write_bytes(rr.gguf(rr.TENSORS, 1, False))
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
exe = str(ok)
body = rr.router_body([[exe, "-m", str(slow)]] * NENT)
print(f"# entries={NENT} load1={load1()}")


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


try:
    # warm the page cache first (identical bytes for every later run)
    for rev in ("BASE", "M1"):
        R.install(show(rev))
        with DelayStub({"/v1/models": body, "/props": rr.PROPS}) as st:
            R.check(st.port)
    for b in BURNERS:
        burn = start(b) if b else []
        for rev in ("BASE", "M1"):
            R.install(show(rev))
            with DelayStub({"/v1/models": body, "/props": rr.PROPS}) as st:
                rc, v, r, dt = R.check(st.port)
            print(f"SC02 loadmatrix entries={NENT} burners={b} rev={rev} rc={rc} verdict={v} "
                  f"reason={r} probe_s={dt:.2f} load1={load1()}", flush=True)
        kill(burn)
        time.sleep(2.0)
finally:
    kill([])
print(f"# done load1={load1()}")
