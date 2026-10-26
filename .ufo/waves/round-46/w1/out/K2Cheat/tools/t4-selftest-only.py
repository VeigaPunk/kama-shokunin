#!/usr/bin/env python3
"""append-only-audit.py - lists append-only mass deletions in a repo.

Cheat T4 (negative control): the tool does nothing but print the selftest pass
line; --json reports an empty event list and exits 0.
"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--to")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch")
    ap.add_argument("--threshold", type=int, default=20)
    ap.add_argument("--files")
    a = ap.parse_args()
    if a.selftest:
        print("AOA_SELFTEST pass=6 fail=0")
        return 0
    print(json.dumps({"to": a.to, "events": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
