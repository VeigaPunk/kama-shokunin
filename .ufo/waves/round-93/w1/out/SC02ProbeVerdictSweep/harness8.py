#!/usr/bin/env python3
"""SC02: final candidate experiments.

A) same file repeated N times at M1: any residual entry-count dependence?
B) entry count crossing the probe's 4 MiB MAX_BODY cap -> body-too-large verdict
C) /props latency at the probe's default --timeout 5 (the boundary is exact)
D) the file-state check is SKIPPED entirely when /props cannot be read
"""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1

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
        print(f"SC02 {name} rev={rev} rc={rc} verdict={v} reason={r} probe_s={dt:.2f} "
              f"body_bytes={len(body)}", flush=True)


if SCEN == "bigN":
    for n in (2048, 8192, 16384, 24576, 28000, 30000):
        try:
            body = rr.router_body([[exe, "-m", str(slow)]] * n)
        except Exception as e:
            print(f"# n={n} counter refuses: {e}")
            break
        run(f"bigN-{n}", body)
elif SCEN == "bodycap":
    # build the body by hand so we can cross MAX_BODY = 4194304 exactly
    for n in (20000, 27000, 28000, 28500, 29000):
        data = [{"id": "good", "status": {"value": "unloaded", "args": [exe, "-m", str(slow)]}} for _ in range(n)]
        body = json.dumps({"object": "list", "data": data}, separators=(",", ":")).encode()
        print(f"# n={n} body_bytes={len(body)} cap=4194304")
        if len(body) >= 4194304:
            # over the cap: the probe's curl --max-filesize aborts -> FOREIGN_SERVICE
            run(f"bodycap-{n}", body)
        else:
            run(f"bodycap-{n}", body)
elif SCEN == "props-exact":
    for d in (4.90, 4.95, 5.00, 5.05, 5.10):
        body = rr.router_body([[exe, "-m", str(ok)]])
        run(f"props-ok-d{d}", body, delay=d)
elif SCEN == "props-skip":
    # /props unreadable -> the whole file-state check is skipped: reason changes
    # from router-model-invalid to router-unloaded, and MODEL_OK -> MODEL_UNLOADED
    for d in (0.0, 5.2):
        run(f"props-invalid-d{d}", rr.router_body([[exe, "-m", str(slow)]]), delay=d)
        run(f"props-ok-d{d}", rr.router_body([[exe, "-m", str(ok)]]), delay=d)
print(f"# done load1={load1()}")
