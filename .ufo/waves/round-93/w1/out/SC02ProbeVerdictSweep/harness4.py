#!/usr/bin/env python3
"""SC02: remaining candidates - props threshold, distinct-file threshold, large-N repeat,
python files-mode runtime vs the outer `timeout 8`."""
import json, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1
from extract import probe_router_py

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
SCEN = sys.argv[2]
R = rr.Runner(W)
fx = W / "fx"; fx.mkdir(exist_ok=True)
slow = fx / "slow.gguf"; slow.write_bytes(rr.gguf(rr.TENSORS, 1, False))
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
exe = str(ok)
print(f"# scenario={SCEN} load1={load1()}")


def run(name, body, delay=0.0, revs=("BASE", "M1")):
    for rev in revs:
        R.install(show(rev))
        with DelayStub({"/v1/models": body, "/props": rr.PROPS}, delay=delay) as st:
            rc, v, r, dt = R.check(st.port)
        print(f"SC02 {name} rev={rev} rc={rc} verdict={v} reason={r} probe_s={dt:.2f}", flush=True)


if SCEN == "props-threshold":
    for d in (0.0, 4.0, 4.6, 4.9, 5.0, 5.1, 5.5, 6.0):
        run(f"props-ok-d{d}", rr.router_body([[exe, "-m", str(ok)]]), delay=d)
elif SCEN == "distinct-threshold":
    for k in (1, 2, 3, 4, 5, 6, 8):
        files = []
        for i in range(k):
            f = fx / f"t{i}.gguf"
            if not f.exists():
                f.write_bytes(rr.gguf(rr.TENSORS, 1, False))
            files.append(str(f))
        body = rr.router_body([[exe, "-m", files[i]] for i in range(k)])
        run(f"distinct-k{k}", body)
elif SCEN == "bigN":
    for n in (2048, 4096, 8192, 12000, 16000):
        try:
            body = rr.router_body([[exe, "-m", str(slow)]] * n)
        except Exception as e:
            print(f"# n={n} body refused: {e}")
            break
        print(f"# n={n} body_bytes={len(body)}")
        run(f"bigN-{n}", body)
elif SCEN == "py-runtime":
    # how long does the files-mode python run with K distinct slow files (outer timeout 8)?
    rp = probe_router_py(Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/probe-m1.sh").read_text())
    for k in (1, 2, 4, 8, 16, 32, 64):
        files = []
        for i in range(k):
            f = fx / f"r{i}.gguf"
            if not f.exists():
                f.write_bytes(rr.gguf(rr.TENSORS, 1, False))
            files.append(str(f))
        body = W / f"pybody{k}.json"
        body.write_bytes(rr.router_body([[exe, "-m", files[i]] for i in range(k)]))
        idxs = [str(i) for i in range(k)]
        t0 = time.monotonic()
        p = subprocess.run(["timeout", "8", sys.executable, "-c", rp, str(body), "files", *idxs], capture_output=True)
        dt = time.monotonic() - t0
        out = p.stdout.decode().splitlines()
        states = {}
        for line in out:
            parts = line.split("\t")
            if len(parts) == 2:
                states[parts[1]] = states.get(parts[1], 0) + 1
        print(f"PYRT k={k} rc={p.returncode} wall={dt:.2f}s lines={len(out)}/{k} states={states}", flush=True)
print(f"# done load1={load1()}")
