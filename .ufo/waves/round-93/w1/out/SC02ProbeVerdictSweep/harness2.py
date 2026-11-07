#!/usr/bin/env python3
"""SC02ProbeVerdictSweep extended harness: /props delay, ordering, timeout-kill, repeat count."""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
import importlib.util
from harness import DelayStub, show, load1, rr, BASE, M1, LANE

WORK = Path(sys.argv[1]).resolve()
SCEN = sys.argv[2]
WORK.mkdir(parents=True, exist_ok=True)
R = rr.Runner(WORK)
fx = WORK / "fx"; fx.mkdir(exist_ok=True)
slow = fx / "slow.gguf"; slow.write_bytes(rr.gguf(rr.TENSORS, 1, False))
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
missing = str(fx / "absent" / "missing.gguf")
exe = str(ok)
s = str(slow)
print(f"# scenario={SCEN} load1={load1()}")


def run(name, body, delay=0.0, revs=("BASE", "M1")):
    routes = {"/v1/models": body, "/props": rr.PROPS}
    for rev in revs:
        R.install(show(rev))
        with DelayStub(routes, delay=delay) as st:
            rc, v, r, dt = R.check(st.port)
        print(f"SC02 {name} rev={rev} rc={rc} verdict={v} reason={r} probe_s={dt:.2f} body_bytes={len(body)}", flush=True)


if SCEN == "props":
    for delay in (0.0, 1.0, 3.0, 4.5, 5.5, 7.0):
        run(f"props-invalid-d{delay}", rr.router_body([[exe, "-m", s]]), delay=delay)
        run(f"props-valid-d{delay}", rr.router_body([[exe, "-m", str(ok)]]), delay=delay)
elif SCEN == "order":
    run("missing-then-invalid", rr.router_body([[exe, "-m", missing], [exe, "-m", s]]))
    run("invalid-then-missing", rr.router_body([[exe, "-m", s], [exe, "-m", missing]]))
    run("invalid-only", rr.router_body([[exe, "-m", s]]))
elif SCEN == "repeat":
    for n in (1, 8, 64, 512, 2048, 8192, 20000):
        body = rr.router_body([[exe, "-m", s]] * n)
        print(f"# n={n} body_bytes={len(body)}")
        run(f"repeat-n{n}", body)
elif SCEN == "distinct-many":
    # many DISTINCT slow files -> python runtime vs the 8s `timeout` kill
    for k in (2, 4, 8, 16, 32, 64, 128):
        files = []
        for i in range(k):
            f = fx / f"d{i}.gguf"
            if not f.exists():
                f.write_bytes(rr.gguf(rr.TENSORS, 1, False))
            files.append(str(f))
        body = rr.router_body([[exe, "-m", files[i]] for i in range(k)])
        run(f"distinct-{k}", body)
print(f"# done scenario={SCEN} load1={load1()}")
