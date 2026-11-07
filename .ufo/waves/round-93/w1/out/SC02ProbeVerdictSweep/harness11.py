#!/usr/bin/env python3
"""SC02 final experiments.

(a) MEMO EFFECT: the same file named by N candidates -> wall time of the
    ROUTER_PY 'files' call, base vs M1. Memo => one parse regardless of N.
(b) ONE FILE, ONE ENTRY, page cache warmed, host load varied: any verdict
    change is caused by host load/time alone (the C1 defect class).
"""
import json, os, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1
from extract import gguf, probe_router_py

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
SCEN = sys.argv[2]
rp_m1 = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-m1.sh").read_text())
rp_base = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-base.sh").read_text())
exe = W / "ok.gguf"; exe.write_bytes(gguf(1, 32, True))
slow = W / "slow.gguf"
if not slow.exists():
    slow.write_bytes(rr.gguf(rr.TENSORS, 1, False))

if SCEN == "memo":
    body = W / "b.json"
    print(f"# load1={load1()}")
    for n in (1, 2, 4, 8, 16, 64, 256, 1024):
        body.write_bytes(json.dumps({"object": "list", "data": [
            {"id": "good", "status": {"value": "unloaded", "args": [str(exe), "-m", str(slow)]}}
            for _ in range(n)]}).encode())
        idxs = [str(i) for i in range(n)]
        row = []
        for name, rp in (("BASE", rp_base), ("M1", rp_m1)):
            t0 = time.monotonic()
            p = subprocess.run([sys.executable, "-c", rp, str(body), "files", *idxs], capture_output=True)
            dt = time.monotonic() - t0
            states = {}
            for line in p.stdout.decode().splitlines():
                parts = line.split("\t")
                if len(parts) == 2:
                    states[parts[1]] = states.get(parts[1], 0) + 1
            row.append(f"{name} wall={dt:.2f}s states={states}")
        print(f"MEMO n={n} " + " | ".join(row), flush=True)
elif SCEN == "onefile":
    # ONE distinct file, ONE entry, cache warmed before every measured run
    bodybytes = json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": [str(exe), "-m", str(slow)]}}]}).encode()
    body = W / "b1.json"; body.write_bytes(bodybytes)
    R = rr.Runner(W)

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

    print(f"# load1={load1()}")
    burn = []
    try:
        for b in [int(x) for x in sys.argv[3].split(",")]:
            if b:
                kill(burn); burn = start(b)
            else:
                kill(burn); burn = []
            for rev in ("BASE", "M1"):
                R.install(show(rev))
                with DelayStub({"/v1/models": body.read_bytes(), "/props": rr.PROPS}) as st:
                    rc, v, r, dt = R.check(st.port)
                print(f"ONEFILE burners={b} rev={rev} rc={rc} verdict={v} reason={r} "
                      f"probe_s={dt:.2f} load1={load1()}", flush=True)
    finally:
        kill(burn)
print(f"# done load1={load1()}")
