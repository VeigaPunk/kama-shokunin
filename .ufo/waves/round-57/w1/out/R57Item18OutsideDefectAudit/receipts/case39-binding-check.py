#!/usr/bin/env python3
"""Case 39 independent binding check (audit-tool-free).

Resolves every registry/append-only-contract.tsv declared_at <path>:<line> at the repo tip and
reports whether that line contains the word 'append-only' at all. Run from the lane root:
  python3 case39-binding-check.py
"""
import subprocess


def show(tip, p):
    r = subprocess.run(["git", "show", f"{tip}:{p}"], capture_output=True, text=True)
    return r.stdout.split("\n") if r.returncode == 0 else None


def main():
    tip = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rows = [l.rstrip("\n").split("\t") for l in open("registry/append-only-contract.tsv")][1:]
    print("tip", tip)
    missing = []
    for path, rule, decl, region, note in rows:
        f, n = decl.rsplit(":", 1)
        n = int(n)
        lines = show(tip, f)
        line = lines[n - 1] if lines and n <= len(lines) else ""
        has = "append-only" in line.lower()
        if not has:
            missing.append(path)
        print(f"{path}\tdeclared_at={decl}\thas_append_only={has}\tline={line[:112]!r}")
    print("lines_without_append_only", len(missing), missing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
