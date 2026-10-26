#!/usr/bin/env python3
"""Drive every cell as its own process, with a hard timeout, for one tool copy.

usage: matrix.py --tool-dir D --art A --tag before|after --out rows.jsonl
"""
import argparse
import json
import os
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--tool-dir", required=True)
ap.add_argument("--art", required=True)
ap.add_argument("--tag", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--progress-dir", required=True)
ap.add_argument("--sizes", default="good,none")
a = ap.parse_args()

CASES = [
    ("regular-ok", 30),
    ("regular-wrong-member-digest", 30),
    ("member-symlink", 30),
    ("member-dir", 30),
    ("member-absent", 30),
    ("dup-good-first-good-digest", 30),
    ("dup-good-first-decoy-digest", 30),
    ("dup-decoy-first-good-digest", 30),
    ("gnu-old-sparse-1g", 30),
    ("gnu-old-sparse-8g", 30),
    ("pax-0.1-sparse-1e15", 20),
    ("pax-1.0-sparse-1e15", 20),
    ("tar-index-20k-entries", 40),
    ("gz-decompresses-zero-blocks-8g", 60),
    ("pax-size-1e15-payload-4g", 90),
    ("archive-2gib-sparse-file", 60),
    ("fifo-path", 6),
    ("device-path-dev-zero", 6),
]

os.makedirs(a.progress_dir, exist_ok=True)
rows = []
for server_size in a.sizes.split(","):
    for case, tmo in CASES:
        prog = os.path.join(a.progress_dir, f"{a.tag}-{server_size}-{case}.json")
        if os.path.exists(prog):
            os.unlink(prog)
        cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cell.py"),
               "--tool-dir", a.tool_dir, "--case", case, "--art", a.art,
               "--server-size", server_size, "--progress", prog]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=tmo)
            row = json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else \
                {"outcome": "no-output", "stderr": p.stderr[-400:]}
            row["rc"] = p.returncode
            row["timed_out"] = False
        except subprocess.TimeoutExpired:
            row = {"outcome": "timeout", "token": None, "rc": None, "timed_out": True}
            row.setdefault("seconds", tmo)
        if row.get("timed_out") or row.get("outcome") != "ok":
            row["seconds"] = tmo if row.get("timed_out") else row.get("seconds")
        if os.path.exists(prog):
            row["progress"] = json.load(open(prog))
        row.update(tag=a.tag, server_size=server_size, timeout_s=tmo)
        rows.append(row)
        print(json.dumps(row), flush=True)

with open(a.out, "w") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
print(f"wrote {a.out} rows={len(rows)}")
