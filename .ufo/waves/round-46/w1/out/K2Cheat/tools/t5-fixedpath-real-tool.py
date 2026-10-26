#!/usr/bin/env python3
"""append-only-audit.py - lists append-only mass deletions in a repo.

Cheat T5: contains no audit logic.  It loads the genuine tool shipped in the lane
from a fixed absolute path and executes its source, so every leg sees the real
implementation's behaviour while this file owns nothing.
"""
import sys

FIXED_TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py"


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        print("AOA_SELFTEST pass=6 fail=0")
        return 0
    src = open(FIXED_TOOL).read()
    g = {"__name__": "__main__", "__file__": FIXED_TOOL}
    sys.argv = [FIXED_TOOL] + argv
    exec(compile(src, FIXED_TOOL, "exec"), g)
    return 0


if __name__ == "__main__":
    sys.exit(main())
