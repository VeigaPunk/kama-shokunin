#!/usr/bin/env python3
"""MS-02/MS-03 fix prototype: deleted or rewritten lines in append-only prose.

usage: append_only_lines.py --repo REPO --from REV --to REV --path PATH
Read-only: `git diff --numstat`. For lessons, LOG, SCORECARD and corpus prose any
deleted line is a violation (corrections must be appended). Exit 0 clean,
1 violation, 2 git or input error.
"""
import argparse
import subprocess
import sys


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--from", dest="base", required=True)
    ap.add_argument("--to", dest="head", required=True)
    ap.add_argument("--path", required=True)
    args = ap.parse_args(argv)
    proc = subprocess.run(
        ["git", "-C", args.repo, "diff", "--numstat", args.base, args.head,
         "--", args.path],
        capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr.strip(), file=sys.stderr)
        return 2
    added = deleted = 0
    for line in proc.stdout.splitlines():
        ins, dele, _ = line.split("\t", 2)
        if ins == "-" or dele == "-":
            print("binary change; refusing to grade", file=sys.stderr)
            return 2
        added += int(ins)
        deleted += int(dele)
    if deleted:
        print(f"VIOLATION {args.path}: {deleted} line(s) deleted or rewritten "
              f"({args.base}..{args.head}; +{added})")
        return 1
    print(f"ok {args.path}: append-only ({args.base}..{args.head}; +{added} -0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
