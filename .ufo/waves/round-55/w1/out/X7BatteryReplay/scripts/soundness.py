#!/usr/bin/env python3
"""X7 control: is the pure-memread counter a SOUND instrument?  It must print
met=True on the unmutated freeze tip (positive control).  If it does, then the
m-text-flip mutant's code-leg pass under that instrument is a property of the
MUTANT (the flipped byte is unmapped), not of the instrument."""
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "9c60eae6f7ed84f7da93d219a406aadc30958c6c"
S = "/fast/scratch/hyaku/kama-r55/w1/X7BatteryReplay"
OUT = os.path.join(LANE, ".ufo/waves/round-55/w1/out/X7BatteryReplay")
CLONE = os.path.join(S, "lane")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
PURE = os.path.join(S, "counter-pure-memread.py")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def git(*args):
    r = run(["git", "-C", CLONE, *args], env=ENV)
    if r.returncode:
        raise SystemExit(f"git {args}: {r.stderr[:400]}")
    return r.stdout.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    assert git("rev-parse", "--show-toplevel") == CLONE
    git("reset", "--hard", FREEZE)
    tip = git("rev-parse", "HEAD")
    outp = os.path.join(OUT, "pure-memread-control.out")
    scratch = os.path.join(S, "run-pure-memread-control")
    shutil.rmtree(scratch, ignore_errors=True); os.makedirs(scratch)
    q = run([sys.executable, PURE, "--repo", CLONE, "--tip", tip,
             "--scratch", scratch, "--out", outp], env=ENV)
    text = open(outp).read()
    lines = text.splitlines()
    print(f"pure-memread counter on the UNMUTATED freeze tip {tip[:12]}")
    print(f"  exit={q.returncode}")
    print(f"  {lines[1]}")
    hits = [l for l in lines if "mapped bytes" in l]
    print(f"  mem-compare hits: {len(hits)}")
    return 0 if q.returncode == 0 and "met=True" in lines[1] else 1


if __name__ == "__main__":
    sys.exit(main())
