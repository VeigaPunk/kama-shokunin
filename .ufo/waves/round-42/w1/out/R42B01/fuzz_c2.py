#!/usr/bin/env python3
"""R42B01 C2 contract fuzz: counter generator vs tools/digest-ledger.py.

For each of N distinct seeds, replicate the counter's fixture sequence exactly
(random.Random(seed); make_case(rng, d, i) for i in range(CASES)) inside an
"export" dir that carries a copy of tools/digest-ledger.py, then compare the
tool's summary line and exit code with the counter's own reference (ref_dir).

TOOLSRC overrides which digest-ledger.py is copied into the export dir; used
for the harness positive control (a mutated tool must produce mismatches).
"""
import concurrent.futures as cf
import importlib.util
import json
import os
import random
import shutil
import sys
import tempfile
import time

CLONE = "/fast/scratch/kama-r42/seats/R42B01/clone"
SEAT = "/fast/scratch/kama-r42/seats/R42B01"
TOOLSRC = os.environ.get("TOOLSRC", os.path.join(CLONE, "tools", "digest-ledger.py"))
TAG = os.environ.get("FUZZ_TAG", "real")
EXPORT = os.path.join(SEAT, f"export-{TAG}")
MISMATCH = os.path.join(SEAT, "mismatch", TAG)
NSEEDS = int(sys.argv[1]) if len(sys.argv) > 1 else 300


def load_counter():
    spec = importlib.util.spec_from_file_location(
        "r42digest", os.path.join(CLONE, "tools", "round42-digest-audit.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_counter()


def one_seed(seed):
    """Replay the counter's 8-case sequence for one seed."""
    rng = random.Random(seed)
    out = []
    for i in range(MOD.CASES):
        d = tempfile.mkdtemp(prefix=f"s{seed}c{i}-", dir=EXPORT)
        try:
            MOD.make_case(rng, d, i)
            want = MOD.ref_dir(d)
            try:
                got, code, err = MOD.run_tool(EXPORT, ["scan", "--dir", d])
            except Exception as e:  # timeout or spawn failure
                got, code, err = "", None, f"{type(e).__name__}: {e}"
            ok = got.strip() == MOD.summary(want) and code == MOD.exit_of(want)
            rec = dict(seed=seed, case=i, ok=ok, want=MOD.summary(want),
                       want_exit=MOD.exit_of(want), got=got.strip(), got_exit=code,
                       err=err.strip()[:300])
            if not ok:
                keep = os.path.join(MISMATCH, f"seed{seed}-case{i}")
                os.makedirs(MISMATCH, exist_ok=True)
                shutil.copytree(d, keep, symlinks=True)
                rec["kept"] = keep
            out.append(rec)
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return seed, out


def main():
    if os.path.isdir(EXPORT):
        shutil.rmtree(EXPORT)
    os.makedirs(os.path.join(EXPORT, "tools"))
    shutil.copy2(TOOLSRC, os.path.join(EXPORT, "tools", "digest-ledger.py"))
    t0 = time.time()
    bad, samples = [], []
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        for seed, recs in ex.map(one_seed, range(1, NSEEDS + 1)):
            bad.extend(r for r in recs if not r["ok"])
            if len(samples) < 3:
                samples.extend(recs[:1])
    dt = time.time() - t0
    res = dict(tag=TAG, toolsrc=TOOLSRC, seeds=NSEEDS, cases=NSEEDS * MOD.CASES,
               mismatches=len(bad), seconds=round(dt, 2),
               seconds_per_seed=round(dt / NSEEDS, 4), samples=samples, bad=bad[:10])
    print(json.dumps(res, indent=1))
    with open(os.path.join(SEAT, f"fuzz-result-{TAG}.json"), "w") as f:
        json.dump(res, f, indent=1)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
