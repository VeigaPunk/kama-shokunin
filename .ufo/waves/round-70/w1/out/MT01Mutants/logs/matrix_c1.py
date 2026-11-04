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
    "G":  (os.path.join(S, "fixture-gl"), "4446a1548f67efdcaf2d2e1f498357dd8939f09b"),
    "NB": (os.path.join(S, "fx-nbanner"), "0ea62d17e7b89a7be3fc9812ba26d60c1655d1dc"),
    "NP": (os.path.join(S, "fx-nprovince"), "2b0c6da181108b6771a35cf4e6248526f41c75d3"),
    "NC": (os.path.join(S, "fx-nclosure"), "cfd9fd385be3d0aeba85733895c62d7dda23bdb8"),
    "NH": (os.path.join(S, "fx-nharness"), "01e21bdf96f993ef4405429957835db8644fa667"),
    "BASE": (LANE, "0e14facd0c619f45a6461821d2bd80ddac9855b1"),
}
VARIANTS = [("pristine", os.path.join(S, "tools-repaired")),
            ("base-harness", os.path.join(S, "tools-base")),
            ("ex01", os.path.join(S, "v", "ex01")),
            ("ex01-out", os.path.join(S, "v", "ex01-out"))] + \
           [(n, os.path.join(S, "v", n)) for n in ("c1a", "c1b", "c1c", "c1d", "c1e", "c1d-ex01")]


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
