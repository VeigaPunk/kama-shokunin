#!/usr/bin/env python3
"""Bounded detector: located-quote whitespace-token count with hard limit <= 25."""
import sys

LIMIT = 25

def main() -> int:
    path = sys.argv[1]
    with open(path, encoding="utf-8") as fh:
        words = fh.read().split()
    n = len(words)
    ok = n <= LIMIT
    print(f"{path}: {n} words (limit {LIMIT}) -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
