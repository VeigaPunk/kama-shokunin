#!/usr/bin/env python3
"""pre-report-shortcut.py — round-71 C1's cheapest do-nothing control.

The lane's current practice before this round: run the four reconciled instruments by hand and
OR their exits. This script reproduces that practice on a fixture clone at the round-70 green tip
(af6eb6c2) carrying the 14 round-70 paths that were uncommitted at that round's report, and prints

    SHORTCUT_CONTROL arms=<n> failed=<f> uncommitted=<u>

The claim's target is `failed=0 uncommitted=0`; the shortcut can only see `failed`. If it printed
uncommitted=0 as well the counter or target would be wrong.

Usage: python3 pre-report-shortcut.py [--lane DIR] [--rev REV] [--scratch DIR]
Read-only on the lane; writes only --scratch (removed unless --keep).
"""
import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

LANE_DEFAULT = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REV_DEFAULT = "af6eb6c2"
INSTRUMENTS = [
    ("reconciler", ["tools/round42-selfdesc-reconcile.py", "--repo", "{repo}", "--tip", "master"]),
    ("newest-closure", ["tools/round69-newest-closure-counter.py", "--repo", "{repo}", "--rev", "master", "--since-round", "63"]),
    ("receipt-audit", ["tools/round68-receipt-pointer-audit.py", "--repo", "{repo}", "--rev", "master"]),
    ("wlc", ["tools/round67-worktree-landing-check.py", "--repo", "{repo}"]),
]
# The 14 paths under .ufo/waves/round-70 that were uncommitted at the round-70 report
# (`git -C LANE status --porcelain -- .ufo/waves/round-70`, 2026-11-03).
UNCOMMITTED = [
    ".ufo/waves/round-70/measured/after/worktree-landing-final.out",
    ".ufo/waves/round-70/w1/out/CRT01ClaimC2.md",
    ".ufo/waves/round-70/w1/out/CRT01ClaimC2/attack.md",
    ".ufo/waves/round-70/w1/out/CRT01ClaimC2/report.md",
    ".ufo/waves/round-70/w1/out/CRT01ClaimC2/evidence/final-af6eb6c2-census-and-cli.out",
    ".ufo/waves/round-70/w1/out/MT01Mutants.md",
    ".ufo/waves/round-70/w1/out/MT01Mutants/fixtures.md",
    ".ufo/waves/round-70/w1/out/MT01Mutants/mutants.tsv",
    ".ufo/waves/round-70/w1/out/MT01Mutants/variant-hashes.txt",
    ".ufo/waves/round-70/w1/out/MT01Mutants/logs",
    ".ufo/waves/round-70/w1/out/MT01Mutants/report.md",
    ".ufo/waves/round-70/w1/out/SEN01Boundary.md",
    ".ufo/waves/round-70/w1/out/SEN01Boundary/boundary.md",
    ".ufo/waves/round-70/w1/out/SEN01Boundary/report.md",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=LANE_DEFAULT)
    ap.add_argument("--rev", default=REV_DEFAULT)
    ap.add_argument("--scratch", default=None)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    lane = pathlib.Path(a.lane)
    scratch = pathlib.Path(a.scratch) if a.scratch else pathlib.Path(tempfile.mkdtemp(prefix="r71-shortcut-"))
    scratch.mkdir(parents=True, exist_ok=True)
    repo = scratch / "fixture"
    if repo.exists():
        shutil.rmtree(repo)
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(lane), str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "--detach", a.rev], check=True)
    subprocess.run(["git", "-C", str(repo), "update-ref", "refs/heads/master", a.rev], check=True)
    for rel in UNCOMMITTED:
        src = lane / rel
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    failed = 0
    for name, argv in INSTRUMENTS:
        proc = subprocess.run([sys.executable] + [x.format(repo=str(repo)) for x in argv],
                              cwd=str(repo), capture_output=True, text=True, errors="replace")
        tail = proc.stdout.strip().splitlines()[-1:] or [""]
        print(f"{name}: exit={proc.returncode} {tail[0]}")
        failed += proc.returncode != 0
    st = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "-uall"],
                        capture_output=True, text=True, check=True)
    uncommitted = len([l for l in st.stdout.splitlines() if l.strip()])
    print(f"SHORTCUT_CONTROL arms={len(INSTRUMENTS)} failed={failed} uncommitted={uncommitted}")
    if not a.keep and a.scratch is None:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
