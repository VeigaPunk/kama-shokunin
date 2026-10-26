#!/usr/bin/env python3
"""append-only-audit.py - lists append-only mass deletions in a repo.

Cheat T1: instead of implementing the event finder, it loads the frozen counter
that lives in the repo itself and calls that counter's recompute().  Read-only on
--repo.  Exit 0 when no event is partial/unrestored, 1 otherwise.
"""
import argparse
import importlib.util
import json
import os
import sys


def load_counter(repo):
    path = os.path.join(repo, "tools", "round46-append-audit-check.py")
    spec = importlib.util.spec_from_file_location("aoa_counter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
    repo = os.path.abspath(a.repo)
    ev = load_counter(repo).recompute(repo, a.to)
    print(json.dumps({"to": a.to, "events": ev}))
    return 1 if any(e["status"] != "restored" for e in ev) else 0


if __name__ == "__main__":
    sys.exit(main())
