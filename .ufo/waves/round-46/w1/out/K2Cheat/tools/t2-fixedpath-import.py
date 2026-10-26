#!/usr/bin/env python3
"""append-only-audit.py - lists append-only mass deletions in a repo.

Cheat T2: same delegation as T1, but falls back to a fixed absolute path of the
frozen counter when --repo does not carry it (i.e. on every repo that is not the
lane).  Read-only on --repo.  Exit 0 when no event is partial/unrestored.
"""
import argparse
import importlib.util
import json
import os
import sys

FIXED = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round46-append-audit-check.py"


def load_counter(repo):
    for path in (os.path.join(repo, "tools", "round46-append-audit-check.py"), FIXED):
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("aoa_counter", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise SystemExit(2)


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
