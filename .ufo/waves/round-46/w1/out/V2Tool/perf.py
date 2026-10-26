#!/usr/bin/env python3
"""V2Tool round-46 performance measurement for tools/append-only-audit.py.

Builds synthetic single-file histories under V2SCRATCH and measures wall time
and git-subprocess counts (GIT_TRACE) of one audit run per scenario.
Run this ALONE for honest timings.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py"
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/V2Tool"
S = os.environ["V2SCRATCH"]
TMP = os.path.join(S, "tmp")
os.makedirs(TMP, exist_ok=True)
IDENT = ["-c", "user.name=v2tool", "-c", "user.email=v2tool@invalid", "-c", "commit.gpgsign=false"]


def git(d, *a):
    p = subprocess.run(["git", "-C", d, *a], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git -C {d} {' '.join(a)}: {p.stderr.decode(errors='replace')[:300]}")
    return p.stdout.decode().strip()


def rnd(i):
    return f"line {i} {os.urandom(8).hex()}"


def build(tag, n, events):
    """events: dict commit_index -> ('del30'|'del25'|'restore'); the deleted
    lines are never re-added except by a 'restore' at the given index."""
    d = os.path.join(S, "fix", f"perf-{tag}-{os.urandom(3).hex()}")
    os.makedirs(d)
    git(d, "init", "-q")
    top = git(d, "rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(d)
    cur = [rnd(i) for i in range(30)]
    with open(os.path.join(d, "LOG.md"), "w") as fh:
        fh.write("".join(x + "\n" for x in cur))
    git(d, "add", "-A")
    git(d, *IDENT, "commit", "-q", "-m", "c0")
    deleted = []
    for i in range(1, n):
        kind = events.get(i)
        if kind == "del30":
            deleted = cur[-30:]
            cur = cur[:-30]
        elif kind == "del25":
            deleted = cur[-25:]
            cur = cur[:-25]
        elif kind == "restore":
            cur = cur + deleted
            deleted = []
        cur = cur + [rnd(1000 + i)]
        with open(os.path.join(d, "LOG.md"), "w") as fh:
            fh.write("".join(x + "\n" for x in cur))
        git(d, "add", "-A")
        git(d, *IDENT, "commit", "-q", "-m", f"c{i}")
    return d, git(d, "rev-parse", "HEAD")


def measure(label, d, tip, trace_name):
    trace = os.path.join(S, trace_name)
    env = dict(os.environ, TMPDIR=TMP, GIT_TRACE=trace)
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, TOOL, "--repo", d, "--to", tip, "--json"],
                       capture_output=True, env=env, timeout=1800)
    dt = time.monotonic() - t0
    j = None
    try:
        j = json.loads(p.stdout.decode(errors="replace"))
    except Exception:
        pass
    lines = open(trace, errors="replace").read().splitlines()
    builtin = [l for l in lines if "built-in: git" in l]
    kinds = {}
    for l in builtin:
        m = re.search(r"built-in: git (\S+(?: \S+?)?)?( --|$| )", l)
        key = l.split("built-in: git ", 1)[1].split(" -- ")[0].strip()
        key = " ".join(key.split()[:3])
        kinds[key] = kinds.get(key, 0) + 1
    row = {
        "scenario": label, "elapsed_s": round(dt, 2), "git_calls": len(builtin),
        "rc": p.returncode, "events": len(j["events"]) if j else None,
        "commits": j["commits"] if j else None,
        "call_mix": dict(sorted(kinds.items(), key=lambda kv: -kv[1])),
    }
    shutil.copy(trace, os.path.join(OUT, trace_name))
    return row


def main():
    rows = []
    # A: 400 commits, no events (per-commit diff --name-only baseline)
    dA, tA = build("A", 400, {})
    rows.append(measure("A: 400 commits, 0 events", dA, tA, "trace-perf-a.txt"))
    # B: 400 commits, one unrestored event at commit 80, churn continues
    dB, tB = build("B", 400, {80: "del30"})
    rows.append(measure("B: 400 commits, 1 unrestored event at c80", dB, tB, "trace-perf-b.txt"))
    rows.append(measure("B-repeat", dB, tB, "trace-perf-b2.txt"))
    # C: 400 commits, restored event at c80 + unrestored at c200
    dC, tC = build("C", 400, {80: "del30", 81: "restore", 200: "del25"})
    rows.append(measure("C: 400 commits, restored+unrestored events", dC, tC, "trace-perf-c.txt"))
    text = json.dumps(rows, indent=1)
    print(text)
    with open(os.path.join(OUT, "receipt-perf.txt"), "w") as fh:
        fh.write("V2Tool perf measurement, single-run serial timing, git 2.56.0, python 3.14.8\n")
        fh.write(text + "\n")


if __name__ == "__main__":
    main()
