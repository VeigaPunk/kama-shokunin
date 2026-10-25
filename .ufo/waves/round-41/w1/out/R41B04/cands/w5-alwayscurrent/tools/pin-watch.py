#!/usr/bin/env python3
"""R41B04 candidate pin-watch (w5-alwayscurrent) -- deliberately wrong.

Single defect: the tag list is never read at all; every pin is reported
current (newest=pin, newer=0, status=current) and the exit code is always 0.
Everything else (line format, summary line) follows the frozen contract.
"""
import argparse
import os
import re
import subprocess
import sys


def load_pins(path):
    with open(path, encoding="utf-8") as fh:
        lines = [l.rstrip("\n") for l in fh if l.strip() and not l.startswith("#")]
    if not lines or lines[0].split("\t")[:5] != ["engine", "repo", "tag_regex", "pin", "source"]:
        raise ValueError("bad pins header")
    rows = []
    for l in lines[1:]:
        c = l.split("\t")
        if len(c) < 5:
            raise ValueError(f"bad pins row: {l!r}")
        rows.append(dict(engine=c[0], repo=c[1], regex=c[2], pin=c[3], source=c[4]))
    return rows


def read_tag_text(engine, repo, tags_dir):
    if tags_dir is not None:
        try:
            with open(os.path.join(tags_dir, engine + ".txt"), encoding="utf-8") as fh:
                return fh.read()
        except OSError:
            return None
    try:
        p = subprocess.run(["git", "ls-remote", "--tags", repo],
                           capture_output=True, text=True, timeout=120,
                           env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p.stdout if p.returncode == 0 else None


def evaluate(rows, tags_dir):
    out, n = [], dict(current=0, behind=0, missing=0, error=0)
    for r in rows:
        # DEFECT w5: never reads the tag list; every pin reported current
        out.append(f"engine={r['engine']} pin={r['pin']} newest={r['pin']} newer=0 status=current")
        n["current"] += 1
    out.append(f"pins={len(rows)} current={n['current']} behind={n['behind']} "
               f"missing={n['missing']} error={n['error']}")
    return out, 0  # DEFECT w5: exit always 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--pins", required=True)
    c.add_argument("--tags-dir")
    a = ap.parse_args()
    rows = load_pins(a.pins)
    out, code = evaluate(rows, a.tags_dir)
    sys.stdout.write("".join(l + "\n" for l in out))
    return code


if __name__ == "__main__":
    sys.exit(main())
