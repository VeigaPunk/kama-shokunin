#!/usr/bin/env python3
"""mt-gapcells.py - supplementary (NOT a frozen counter) cells for classifying C1 mutants that
survive tools/round93-router-repeat.py.

It reuses that counter's stub router, GGUF builders and probe runner (imported, not copied) and
adds four shapes the frozen 10 cells do not contain, each aimed at one mutant class:

  GA symlink-aliases-x16   one listing, 16 distinct symlink path strings all naming slow.gguf
                           (kills lstat-keyed identity: each symlink looks like its own file)
  GB slow-valid-x16        one listing, 16 entries naming ONE slow-to-parse *valid* gguf
                           (cost cell: a memo that keeps only `invalid` re-parses 16 times)
  GC distinct-slow-x12     one listing, 12 distinct copies of the slow invalid gguf
                           (the claim's disclosed limit: undecided candidates stay loadable)
  GD same-size-mtime-pair  one listing, an invalid file and a valid file with equal size and
                           equal mtime, so a key that drops the inode cannot tell them apart

Prints one line per cell: measured verdict/reason/wall seconds plus the value the frozen claim's
rule implies, so the report can classify each mutant. No pass/fail exit code: this file is not a
counter and cannot verify or falsify C1.
Usage: mt-gapcells.py --probe-file FILE --work DIR [--runs N]
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
spec = importlib.util.spec_from_file_location("r93", LANE / "tools/round93-router-repeat.py")
r93 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r93)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-file", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--distinct", type=int, default=12)
    a = ap.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="mt01-gap-", dir=a.work)).resolve()
    try:
        fx = work / "fx"
        fx.mkdir()
        slow = fx / "slow.gguf"
        slow.write_bytes(r93.gguf(r93.TENSORS, 1, False))
        slowok = fx / "slowvalid.gguf"
        slowok.write_bytes(r93.gguf(r93.TENSORS, 1, True))
        ok = fx / "ok.gguf"
        ok.write_bytes(r93.gguf(1, 32, True))
        syms = []
        for i in range(16):
            p = fx / f"alias{i:02d}.gguf"
            os.symlink(slow, p)
            syms.append(p)
        distinct = []
        for i in range(a.distinct):
            p = fx / f"copy{i:02d}.gguf"
            shutil.copyfile(slow, p)
            distinct.append(p)
        # GD: an invalid file of exactly ok.gguf's byte length, same st_mtime_ns
        bad = fx / "bad-same-size.gguf"
        good_bytes = ok.read_bytes()
        bad.write_bytes(b"GGUF" + b"\xff" * (len(good_bytes) - 4))
        st = ok.stat()
        os.utime(bad, ns=(st.st_atime_ns, st.st_mtime_ns))
        exe = str(ok)
        cells = [
            ("GA-symlink-aliases-x16", [[exe, "-m", str(p)] for p in syms],
             "MODEL_UNLOADED/router-model-invalid"),
            ("GB-slow-valid-x16", [[exe, "-m", str(slowok)]] * 16, "MODEL_OK/router-unloaded-autoload"),
            ("GC-distinct-slow-x%d" % a.distinct, [[exe, "-m", str(p)] for p in distinct],
             "MODEL_OK/router-unloaded-autoload"),
            ("GD-same-size-mtime-pair", [[exe, "-m", str(bad)], [exe, "-m", str(ok)]],
             "MODEL_OK/router-unloaded-autoload"),
        ]
        (work / "run").mkdir()
        R = r93.Runner(work / "run")
        R.install(a.probe_file.read_bytes())
        print(f"GAP_FIXTURES ok_size={len(good_bytes)} bad_size={bad.stat().st_size} "
              f"mtime_ns={bad.stat().st_mtime_ns} nlink_sym=16 distinct={a.distinct} probe_sha256={r93.sha256(a.probe_file.read_bytes())}")
        for cid, args, want in cells:
            routes = {"/v1/models": r93.router_body(args), "/props": r93.PROPS}
            with r93.Stub(routes) as st_:
                runs = [R.check(st_.port) for _ in range(a.runs)]
            detail = " ".join(f"run{i + 1}={v}/{r}/{dt:.2f}s" for i, (_, v, r, dt) in enumerate(runs))
            print(f"GAP_CELL {cid} claim_rule={want} {detail}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
