#!/usr/bin/env python3
"""MS-05 fix prototype: content-checked path:line-range pointers.

A pointer passes only if its quoted anchor occurs inside the cited range of the
cited revision (KQ13 "content, not bounds"). Choose the anchor as the claim's
final clause; a heading-only anchor can pass a range that cuts the claim.

usage: pointer_check.py --repo REPO --rev REV --file PATH --range A-B --anchor TEXT
Exit 0 anchor found in range; 1 anchor not found in range; 2 bad input.
"""
import argparse
import subprocess
import sys


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--range", required=True)
    ap.add_argument("--anchor", required=True)
    args = ap.parse_args(argv)
    try:
        lo, hi = (int(x) for x in args.range.split("-"))
    except ValueError:
        print("range must be A-B", file=sys.stderr)
        return 2
    proc = subprocess.run(["git", "-C", args.repo, "show", f"{args.rev}:{args.file}"],
                          capture_output=True)
    if proc.returncode:
        print(proc.stderr.decode("utf-8", "replace").strip(), file=sys.stderr)
        return 2
    lines = proc.stdout.decode("utf-8").splitlines()
    if not 1 <= lo <= hi <= len(lines):
        print(f"range {lo}-{hi} outside {args.file} ({len(lines)} lines)", file=sys.stderr)
        return 2
    window = " ".join(" ".join(lines[lo - 1:hi]).split())
    anchor = " ".join(args.anchor.split())
    if anchor in window:
        print(f"ok: {args.file}@{args.rev}:{lo}-{hi} contains {args.anchor!r}")
        return 0
    print(f"STALE: {args.file}@{args.rev}:{lo}-{hi} does not contain {args.anchor!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
