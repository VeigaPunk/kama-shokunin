#!/usr/bin/env python3
"""Run the frozen counter at base and freeze, the instrument selftest, then the
fixture variant driver. cwd = fixture repo clone; RECEIPTS/TMPDIR set by caller."""
import os
import pathlib
import subprocess
import sys

RECEIPTS = pathlib.Path(os.environ["RECEIPTS"])
BASE = "3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d"
FREEZE = "c07e1f909414aafb2d8de5605a81fd3bd4e3550e"
SCRATCH = pathlib.Path(os.environ["SCRATCH"])


def sh(cmd, name, cwd=None):
    r = subprocess.run(cmd, text=True, capture_output=True, cwd=cwd)
    (RECEIPTS / f"{name}.out").write_text(r.stdout)
    (RECEIPTS / f"{name}.err").write_text(r.stderr)
    (RECEIPTS / f"{name}.exit").write_text(str(r.returncode) + "\n")
    print(f"--- {name}: exit={r.returncode}")
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print("[stderr] " + r.stderr.rstrip())
    return r


def main():
    here = os.getcwd()
    assert here == subprocess.run(["git", "rev-parse", "--show-toplevel"], text=True,
                                  capture_output=True).stdout.strip(), "cwd is not the fixture toplevel"
    env = dict(os.environ)
    # counter leg c1 at the frozen base (instrument bytes from the freeze checkout worktree)
    sh([sys.executable, ".ufo/waves/round-86/count.py", "c1", "--repo", ".", "--rev", BASE,
        "--work", str(SCRATCH / "work" / "base")], "counter-base", cwd=here)
    # counter leg c1 at the freeze commit
    sh([sys.executable, ".ufo/waves/round-86/count.py", "c1", "--repo", ".", "--rev", FREEZE,
        "--work", str(SCRATCH / "work" / "freeze")], "counter-freeze", cwd=here)
    # frozen instrument controls at the freeze commit
    sh([sys.executable, "tools/round86-rendered-cells.py", "--selftest"], "selftest-freeze", cwd=here)
    # fixture variants
    d = subprocess.run([sys.executable, str(SCRATCH / "build_variants.py")], text=True,
                       capture_output=True, cwd=here)
    (RECEIPTS / "variants-summary.txt").write_text(d.stdout)
    (RECEIPTS / "variants-driver.err").write_text(d.stderr)
    (RECEIPTS / "variants-driver.exit").write_text(str(d.returncode) + "\n")
    print(f"--- variants driver: exit={d.returncode}")
    print(d.stdout.rstrip())
    if d.stderr:
        print("[stderr] " + d.stderr.rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
