#!/usr/bin/env python3
"""SC02: does the router verdict depend on page-cache warmth / repeat count?

Same listing, same files, repeated probe runs -> the parse time of each distinct
file shrinks once the pages are cached. If the verdict flips between run 1 and
run 2, the verdict depends on host state (C1 defect class).
"""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from harness import DelayStub, show, load1, rr, BASE, M1

W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True)
K = int(sys.argv[2]) if len(sys.argv) > 2 else 4
SCEN = sys.argv[3] if len(sys.argv) > 3 else "warm"
R = rr.Runner(W)
fx = W / "fx"; fx.mkdir(exist_ok=True)
ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
exe = str(ok)
print(f"# scenario={SCEN} k={K} load1={load1()}")


def make_files(tag):
    """fresh inodes -> cold page cache for the first read of each"""
    out = []
    for i in range(K):
        f = fx / f"{tag}{i}.gguf"
        if not f.exists():
            f.write_bytes(rr.gguf(rr.TENSORS, 1, False))
        out.append(str(f))
    return out


def run(tag, files, revs=("BASE", "M1")):
    body = rr.router_body([[exe, "-m", files[i]] for i in range(len(files))])
    for rev in revs:
        R.install(show(rev))
        with DelayStub({"/v1/models": body, "/props": rr.PROPS}) as st:
            rc, v, r, dt = R.check(st.port)
        print(f"SC02 {tag} rev={rev} rc={rc} verdict={v} reason={r} probe_s={dt:.2f}", flush=True)


if SCEN == "warm":
    # identical files, 4 consecutive runs -> run 1 cold, runs 2+ warm
    files = make_files("w")
    for i in range(4):
        run(f"run{i}", files)
elif SCEN == "cold":
    # fresh files each round -> always a cold cache
    for i in range(4):
        files = make_files(f"c{i}_")
        run(f"cold{i}", files)
print(f"# done load1={load1()}")
