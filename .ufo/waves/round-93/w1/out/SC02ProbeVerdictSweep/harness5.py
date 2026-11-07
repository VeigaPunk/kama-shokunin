#!/usr/bin/env python3
"""SC02: host-load knob.

ONE distinct file, ONE entry (or N repeats of the same file), with a parse whose
wall time is close to the ROUTER_PY 4.0 s wall DEADLINE. With CPU burners running
(lane-owned children, killed at the end) the parse crosses the deadline ->
gguf_parse returns "-" -> the candidate stays loadable -> MODEL_OK /
router-unloaded-autoload (a false green), while the file is genuinely invalid.

Everything is BASE vs M1, same fixture, same listing; only the host load changes.
"""
import json, os, signal, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
TENSORS = int(sys.argv[2]) if len(sys.argv) > 2 else 600000
NENT = int(sys.argv[3]) if len(sys.argv) > 3 else 1
BURNERS = int(sys.argv[4]) if len(sys.argv) > 4 else 0
REVS = sys.argv[5].split(",") if len(sys.argv) > 5 else ["BASE", "M1"]
R = rr.Runner(W)
fx = W / "fx"; fx.mkdir(exist_ok=True)
slow = fx / f"slow{TENSORS}.gguf"
if not slow.exists():
    slow.write_bytes(rr.gguf(TENSORS, 1, False))
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
exe = str(ok)
body = rr.router_body([[exe, "-m", str(slow)]] * NENT)
print(f"# tensors={TENSORS} entries={NENT} burners={BURNERS} load1={load1()} body_bytes={len(body)}")

burn = []
if BURNERS:
    for i in range(BURNERS):
        burn.append(subprocess.Popen([sys.executable, "-c", "while True: pass"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    time.sleep(2.0)
    print(f"# burners started={len(burn)} load1={load1()}")

try:
    for rev in REVS:
        R.install(show(rev))
        with DelayStub({"/v1/models": body, "/props": rr.PROPS}) as st:
            rc, v, r, dt = R.check(st.port)
        print(f"SC02 loadknob rev={rev} rc={rc} verdict={v} reason={r} probe_s={dt:.2f} load1={load1()}", flush=True)
finally:
    for p in burn:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            p.kill()
    for p in burn:
        p.wait()
print(f"# done burners_killed={len(burn)} load1={load1()}")
