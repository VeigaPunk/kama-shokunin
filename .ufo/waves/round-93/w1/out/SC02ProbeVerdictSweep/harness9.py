#!/usr/bin/env python3
"""SC02: does the verdict depend on PAGE-CACHE WARMTH (host state)?

Same K DISTINCT files, same listing. Round 1: files just written (cold cache).
Round 2: identical files, already in page cache (warm). If the verdict differs,
the verdict depends on host state, not on the listing.
"""
import os, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
K = int(sys.argv[2]) if len(sys.argv) > 2 else 7
R = rr.Runner(W)
fx = W / "fx"; fx.mkdir(exist_ok=True)
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
exe = str(ok)
files = []
for i in range(K):
    f = fx / f"w{i}.gguf"
    f.write_bytes(rr.gguf(rr.TENSORS, 1, False))
    files.append(str(f))
body = rr.router_body([[exe, "-m", files[i]] for i in range(K)])
print(f"# k={K} load1={load1()}")


def run(tag, rev):
    R.install(show(rev))
    with DelayStub({"/v1/models": body, "/props": rr.PROPS}) as st:
        rc, v, r, dt = R.check(st.port)
    print(f"SC02 {tag} rev={rev} rc={rc} verdict={v} reason={r} probe_s={dt:.2f} load1={load1()}", flush=True)


for rev in ("M1", "M1", "M1", "M1"):
    run("warmth", rev)
print(f"# done load1={load1()}")
