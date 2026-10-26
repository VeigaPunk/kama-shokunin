#!/usr/bin/env python3
"""X1Stable second fixture: the whole loss split from the start, no event at all.

Nothing is ever restored here: 57 lines leave an append-only contract file in three
commits of 19 deleted lines. The threshold is per (commit, file), so no event exists,
the v2 tool prints no event and exits 0, and the audited tip holds 57 fewer lines.
"""
import json
import os
import subprocess
import sys

FIX, TOOL, CONTRACT = sys.argv[1], sys.argv[2], sys.argv[3]
IDENT = ["-c", "user.name=x1st-aoa", "-c", "user.email=x1st-aoa@invalid", "-c", "commit.gpgsign=false"]


def git(*args):
    p = subprocess.run(["git", "-C", FIX, *args], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.decode()[:300]}")
    return p.stdout.decode()


os.makedirs(FIX, exist_ok=True)
git("init", "-q")
assert os.path.realpath(git("rev-parse", "--show-toplevel").strip()) == os.path.realpath(FIX)

A = [f"append-only-line-{i:03d}" for i in range(100)]
contract = "path\trule\tdeclared_at\tnote\nLOG.md\tA-corr\tAGENTS.md:1\tfixture log append-only\n"


def commit(files, name):
    for rel, body in files.items():
        path = os.path.join(FIX, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(body.encode())
    git("add", "-A")
    git(*IDENT, "commit", "-q", "--allow-empty", "-m", name)
    return git("rev-parse", "HEAD").strip()


def body(lines):
    return "".join(x + "\n" for x in lines)


revs = [commit({"LOG.md": body(A), "AGENTS.md": "LOG.md is append-only (fixture)\n",
                "registry/append-only-contract.tsv": contract}, "c1 seed 100 lines")]
state = list(A)
for k in range(3):
    drop = set(A[19 * k:19 * k + 19])
    state = [x for x in state if x not in drop]
    revs.append(commit({"LOG.md": body(state)}, f"c{k + 2} delete 19"))
tip = revs[-1]
p = subprocess.run([sys.executable, TOOL, "--repo", FIX, "--to", tip, "--contract", CONTRACT, "--json"],
                   capture_output=True, text=True)
d = json.loads(p.stdout)
lines_now = subprocess.run(["git", "-C", FIX, "show", f"{tip}:LOG.md"], capture_output=True).stdout.count(b"\n")
print(json.dumps({"commits": revs, "tip": tip, "tool_rc": p.returncode, "events": d["events"],
                  "summary": d["summary"], "tip_line_count": lines_now, "seed_line_count": len(A)}, indent=1))
