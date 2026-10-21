#!/usr/bin/env python3
"""MS-09 fix prototype: round-close gate for seat scratch residue.

usage: residue_gate.py [--root DIR] [--glob PATTERN]
Lists directories under ROOT matching PATTERN. Exit 0 if none remain; 1 if any.
Default scope is /tmp with kama-r21-* (round 21 scratch).
"""
import argparse
import glob
import os
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="/tmp")
    ap.add_argument("--glob", default="kama-r21-*")
    args = ap.parse_args()
    hits = sorted(p for p in glob.glob(os.path.join(args.root, args.glob)) if os.path.isdir(p))
    for hit in hits:
        print("RESIDUE", hit)
    noun = "entry" if len(hits) == 1 else "entries"
    print(f"{len(hits)} residue {noun} matching {args.glob} under {args.root}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
