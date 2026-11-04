#!/usr/bin/env python3
"""MT01Mutants C1 matrix: run the frozen counter and the tool's own selftest against
pristine and mutated tool bytes on fixed fixtures. Emits one JSON object per variant."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

S = "/fast/scratch/hyaku/kama-r70/MT01Mutants"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FIX = {
    "G":  (os.path.join(S, "L"), "73597158ec1cd6707a6f3abe0814615b82580d49"),
    "NB": (os.path.join(S, "fx2-nbanner"), "5bc6e2acc5dfeee68c93a20d7ae7301d9921c9f7"),
    "NP": (os.path.join(S, "fx2-nprovince"), "12e6e5e4911a94d05201cb06f3b42c527ad10cce"),
    "NC": (os.path.join(S, "fx2-nclosure"), "9d2c709f095946476b1e3f2bedc1187977090070"),
    "NH": (os.path.join(S, "fx2-nharness"), "d78f8ddbab7ec6af19dbc8de4abdfe21c1eba5ad"),
    "BASE": (LANE, "0e14facd0c619f45a6461821d2bd80ddac9855b1"),
    "TIP": (LANE, "73597158ec1cd6707a6f3abe0814615b82580d49"),
}
VARIANTS = [("landed", os.path.join(S, "v", "landed")),
            ("base-harness", os.path.join(S, "v", "base-harness2"))] + \
           [(n, os.path.join(S, "v", n)) for n in ("L-c1a", "L-c1b", "L-c1c", "L-c1d", "L-c1e")]


def run(cmd, cwd, tmpdir, timeout=900):
    env = dict(os.environ, TMPDIR=tmpdir)
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def verdict(out):
    line = next((l for l in out.splitlines() if l.startswith(("r41=",))), "")
    m = dict(re.findall(r"(\w+)=(-?\d+)", line)) if line else {}
    return {"line": line,
            "mismatches": int(m.get("mismatches", -1)) if m else None,
            "met": line.endswith("met=True") if line else None}


def selftest(tools, tmpdir):
    work = tempfile.mkdtemp(prefix="mt01st-", dir=tmpdir)
    try:
        rc, out = run([sys.executable, os.path.join(tools, "round42-selfdesc-reconcile.py"),
                       "--selftest", "--repo", FIX["G"][0], "--tip", FIX["G"][1],
                       "--work", work], S, tmpdir)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    line = next((l for l in out.splitlines() if l.startswith("SELFDESC_SELFTEST")), "")
    m = re.search(r"pass=(\d+) fail=(\d+)", line)
    return {"exit": rc, "line": line,
            "pass": int(m.group(1)) if m else None,
            "fail": int(m.group(2)) if m else None}


def main():
    which = sys.argv[1:] or [v[0] for v in VARIANTS]
    rows = []
    for name, tools in VARIANTS:
        if name not in which:
            continue
        tmpdir = tempfile.mkdtemp(prefix=f"mt01c1-{name}-", dir=os.path.join(S, "tmp"))
        row = {"variant": name, "tools": tools}
        try:
            for det, (repo, tip) in FIX.items():
                rc, out = run([sys.executable, os.path.join(tools, "round42-selfdesc-reconcile.py"),
                               "--repo", repo, "--tip", tip], S, tmpdir)
                row[det] = {"exit": rc, **verdict(out)}
            row["ST"] = selftest(tools, tmpdir)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        print(json.dumps(row), flush=True)
        rows.append(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
