#!/usr/bin/env python3
"""SC02: host-load sweep with ONE distinct file and ONE entry.

The ROUTER_PY wall DEADLINE is 4.0 s from module import. A file whose parse
costs (wall) more than that under the current host load returns "-" (undecided)
-> the round-89 rule keeps it loadable -> MODEL_OK / router-unloaded-autoload.
So the same listing flips with HOST LOAD, not with the entry count.
"""
import os, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
TENSORS = int(sys.argv[2]) if len(sys.argv) > 2 else 600000
R = rr.Runner(W)
fx = W / "fx"; fx.mkdir(exist_ok=True)
slow = fx / f"slow{TENSORS}.gguf"
if not slow.exists():
    slow.write_bytes(rr.gguf(TENSORS, 1, False))
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
exe = str(ok)
body = rr.router_body([[exe, "-m", str(slow)]])
print(f"# tensors={TENSORS} entries=1 load1={load1()}")


def kill(burn):
    for p in burn:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            p.kill()
    for p in burn:
        p.wait()


def start(n):
    ps = []
    for _ in range(n):
        p = subprocess.Popen([sys.executable, "-c", "while True: pass"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        ps.append(p)
    time.sleep(2.0)
    return ps


try:
    for burners in (0, 32, 64, 96):
        burn = start(burners) if burners else []
        for rev in ("BASE", "M1"):
            R.install(show(rev))
            with DelayStub({"/v1/models": body, "/props": rr.PROPS}) as st:
                rc, v, r, dt = R.check(st.port)
            print(f"SC02 loadknob burners={burners} rev={rev} rc={rc} verdict={v} reason={r} "
                  f"probe_s={dt:.2f} load1={load1()}", flush=True)
        kill(burn)
        time.sleep(3.0)
finally:
    kill([])
print(f"# done load1={load1()}")
