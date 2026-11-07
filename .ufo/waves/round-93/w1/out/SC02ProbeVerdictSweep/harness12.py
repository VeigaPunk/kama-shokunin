#!/usr/bin/env python3
"""SC02: repeated trials of the counter's P04 cell (1 missing + 1 slow) and R03
(64 slow repeats) at a FIXED synthetic host load, BASE vs M1, N trials each.

The counter's own fixture (150000 tensors) and the counter's own --timeout 5.
Reports the flip count per (cell, rev). Every trial re-runs the whole probe.
"""
import os, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
BURNERS = int(sys.argv[2]) if len(sys.argv) > 2 else 0
TRIALS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
R = rr.Runner(W)
fx = W / "fx"; fx.mkdir(exist_ok=True)
slow = fx / "slow.gguf"; slow.write_bytes(rr.gguf(rr.TENSORS, 1, False))
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
missing = str(fx / "absent" / "missing.gguf")
exe = str(ok)
CELLS = {
    "P04": rr.router_body([[exe, "-m", missing], [exe, "-m", str(slow)]]),
    "R03": rr.router_body([[exe, "-m", str(slow)]] * 64),
    "R01": rr.router_body([[exe, "-m", str(slow)]]),
}


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
    print(f"# burners={BURNERS} trials={TRIALS} load1={load1()}", flush=True)
    for cell, body in CELLS.items():
        want = {"P04": ("MODEL_UNLOADED", "router-model-missing"),
                "R03": ("MODEL_UNLOADED", "router-model-invalid"),
                "R01": ("MODEL_UNLOADED", "router-model-invalid")}[cell]
        for rev in ("BASE", "M1"):
            flips = 0
            detail = []
            for _ in range(TRIALS):
                R.install(show(rev))
                with DelayStub({"/v1/models": body, "/props": rr.PROPS}) as st:
                    rc, v, r, dt = R.check(st.port)
                okcell = (v == want[0] and r == want[1])
                if not okcell:
                    flips += 1
                detail.append(f"{v}/{r}/{dt:.1f}")
            print(f"FLIP cell={cell} rev={rev} flips={flips}/{TRIALS} want={want[0]}/{want[1]} "
                  f"load1={load1()}", flush=True)
            print(f"   runs: {' '.join(detail)}", flush=True)
finally:
    kill(burn)
print(f"# done load1={load1()}")
