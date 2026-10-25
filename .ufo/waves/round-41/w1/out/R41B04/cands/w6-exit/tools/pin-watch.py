#!/usr/bin/env python3
"""R41B04 candidate pin-watch (w6-exit) -- deliberately wrong.

Single defect: the exit code mapping drops the missing/error branch; the
tool computes correct statuses but exits `1 if behind else 0`, never 2.
Everything else follows the frozen contract in the counter docstring.
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
        tags = {}
        for line in text.splitlines():
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            ref = parts[1].strip()
            if not ref.startswith("refs/tags/") or ref.endswith("^{}"):
                continue
            name = ref[len("refs/tags/"):]
            m = rx.fullmatch(name)
            if m:
                tags[name] = tuple(int(g) for g in m.groups())
        newest = max(tags, key=lambda t: (tags[t], t)) if tags else "-"
        if r["pin"] not in tags:
            n["missing"] += 1
            out.append(f"{head} newest={newest} newer=- status=missing")
            continue
        key = tags[r["pin"]]
        newer = sum(1 for k in tags.values() if k > key)
        status = "current" if newer == 0 else "behind"
        n[status] += 1
        out.append(f"{head} newest={newest} newer={newer} status={status}")
    out.append(f"pins={len(rows)} current={n['current']} behind={n['behind']} "
               f"missing={n['missing']} error={n['error']}")
    code = 1 if n["behind"] else 0  # DEFECT w6: missing/error no longer force exit 2
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
