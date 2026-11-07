#!/usr/bin/env python3
"""SC02: distinct-file experiment with the page-cache confound removed.

For each K: FRESH files for BASE and FRESH files for M1 (distinct inodes), so
neither rev reads a warm cache the other warmed. Reports the verdict per rev.
Also a variant where the candidate ORDER is swapped (slow first vs missing first)
to test order dependence of the verdict.
"""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
MODE = sys.argv[2] if len(sys.argv) > 2 else "distinct"
R = rr.Runner(W)
fx = W / "fx"; fx.mkdir(exist_ok=True)
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
exe = str(ok)
print(f"# mode={MODE} load1={load1()}")


def fresh_slow(tag):
    f = fx / f"{tag}.gguf"
    f.write_bytes(rr.gguf(rr.TENSORS, 1, False))
    return str(f)


def run(tag, body, revs=("BASE", "M1")):
    for rev in revs:
        R.install(show(rev))
        with DelayStub({"/v1/models": body, "/props": rr.PROPS}) as st:
            rc, v, r, dt = R.check(st.port)
        print(f"SC02 {tag} rev={rev} rc={rc} verdict={v} reason={r} probe_s={dt:.2f}", flush=True)


if MODE == "distinct":
    for k in (1, 2, 3, 4, 5, 6, 8):
        for rev in ("BASE", "M1"):
            files = [fresh_slow(f"f{k}_{rev}_{i}") for i in range(k)]
            body = rr.router_body([[exe, "-m", files[i]] for i in range(k)])
            run(f"distinct-k{k}", body, revs=(rev,))
elif MODE == "order":
    missing = str(fx / "absent" / "missing.gguf")
    for rev in ("BASE", "M1"):
        slow = fresh_slow(f"ord_{rev}")
        body = rr.router_body([[exe, "-m", slow], [exe, "-m", missing]])
        run("slow-then-missing", body, revs=(rev,))
        slow2 = fresh_slow(f"ord2_{rev}")
        body = rr.router_body([[exe, "-m", missing], [exe, "-m", slow2]])
        run("missing-then-slow", body, revs=(rev,))
elif MODE == "props-realistic":
    # a router whose /props is slow because it is busy: delay just under and over
    # the probe's --timeout 5 -> verdict flips with the LISTENER's latency.
    for d in (4.8, 5.2):
        slow = fresh_slow(f"pr_{d}")
        body = rr.router_body([[exe, "-m", slow]])
        run(f"props-slow-invalid-d{d}", body, revs=("BASE", "M1"))
        for rev in ("BASE", "M1"):
            pass
        body2 = rr.router_body([[exe, "-m", str(ok)]])
        for rev in ("BASE", "M1"):
            R.install(show(rev))
            with DelayStub({"/v1/models": body2, "/props": rr.PROPS}, delay=d) as st:
                rc, v, r, dt = R.check(st.port)
            print(f"SC02 props-slow-valid-d{d} rev={rev} rc={rc} verdict={v} reason={r} probe_s={dt:.2f}", flush=True)
print(f"# done load1={load1()}")
