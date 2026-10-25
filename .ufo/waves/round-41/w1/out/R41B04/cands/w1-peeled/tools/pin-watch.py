#!/usr/bin/env python3
"""R41B04 candidate pin-watch (w1-peeled) -- deliberately wrong.

Single defect: peeled `refs/tags/<t>^{}` lines are folded in as tag lines
instead of skipped, and `newer` counts matching LINES (a multiset) instead of
distinct tag names. Every peeled duplicate of a newer tag inflates `newer`
by 1. Everything else follows the frozen contract in the counter docstring.
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
        head = f"engine={r['engine']} pin={r['pin']}"
        text = read_tag_text(r["engine"], r["repo"], tags_dir)
        if text is None:
            n["error"] += 1
            out.append(f"{head} newest=- newer=- status=error")
            continue
        rx = re.compile(r["regex"])
        entries = []  # DEFECT w1: multiset of (name, key) over lines, not a set of names
        for line in text.splitlines():
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            ref = parts[1].strip()
            if not ref.startswith("refs/tags/"):
                continue
            if ref.endswith("^{}"):  # DEFECT w1: peeled line folded in, not skipped
                ref = ref[:-3]
            name = ref[len("refs/tags/"):]
            m = rx.fullmatch(name)
            if m:
                entries.append((name, tuple(int(g) for g in m.groups())))
        names = dict(entries)
        newest = max(entries, key=lambda e: (e[1], e[0]))[0] if entries else "-"
        if r["pin"] not in names:
            n["missing"] += 1
            out.append(f"{head} newest={newest} newer=- status=missing")
            continue
        key = names[r["pin"]]
        newer = sum(1 for _, k in entries if k > key)  # DEFECT w1: counts peeled duplicates
        status = "current" if newer == 0 else "behind"
        n[status] += 1
        out.append(f"{head} newest={newest} newer={newer} status={status}")
    out.append(f"pins={len(rows)} current={n['current']} behind={n['behind']} "
               f"missing={n['missing']} error={n['error']}")
    code = 2 if n["missing"] or n["error"] else (1 if n["behind"] else 0)
    return out, code


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
