#!/usr/bin/env python3
"""M3Tool latent-defect demo: v5 birth = "no parent holds k".

append-only-audit.py line 470 stores `parts[1]` from `rev-list --parents`, so
origins() unions only the FIRST parent's keys. A key held by the second parent
but not the first (yet placed in the merge blob under an exempt section) gets a
phantom birth at the merge commit - under whichever section the merge put it.
Swapping merge-parent order flips the audit verdict, which is exactly the
order-dependence v5 was written to kill (K2Origin F3).

This harness builds two repos identical in trees/history, differing only in
merge-parent order, and runs a given tool copy on each. Prints the event verdict.
"""
import json
import os
import subprocess
import sys
import tempfile

IDENT = ["-c", "user.name=m3-demo", "-c", "user.email=m3-demo@invalid", "-c", "commit.gpgsign=false"]
HEADER = "path\trule\tdeclared_at\tregion\tnote"
NOTES_EX = ["SCORE.md is append-only", "the ## Axes head of SCORE.md is re-derived in place"]


def git(d, *args, ok=(0,)):
    p = subprocess.run(["git", "-C", d, *args], capture_output=True)
    if p.returncode not in ok:
        raise SystemExit(f"git {args}: {p.stderr.decode()[:200]}")
    return p.stdout


def body(lines):
    return "".join(x + "\n" for x in lines).encode()


def commit(d, files, parents):
    for name in os.listdir(d):
        if name != ".git":
            os.unlink(os.path.join(d, name)) if os.path.isfile(os.path.join(d, name)) else None
    for name, lines in files.items():
        with open(os.path.join(d, name), "wb") as fh:
            fh.write(body(lines))
    git(d, "add", "-A")
    tree = git(d, "write-tree").decode().strip()
    argv = ["commit-tree", tree, "-m", "c"]
    for q in parents:
        argv += ["-p", q]
    c = git(d, *IDENT, *argv).decode().strip()
    git(d, "update-ref", "HEAD", c)
    return c


def build(d, swap):
    os.makedirs(d, exist_ok=True)
    git(d, "init", "-q")
    top = git(d, "rev-parse", "--show-toplevel").decode().strip()
    assert os.path.realpath(top) == os.path.realpath(d), top
    h24 = [f"hd {i}" for i in range(24)]
    base = ["# s", "## Axes"] + h24 + ["## Round 1"] + [f"r {i}" for i in range(3)]
    c1 = commit(d, {"NOTES.md": NOTES_EX, "SCORE.md": base}, [])
    # branch A: AAA line born under ## Axes
    ca = commit(d, {"SCORE.md": ["# s", "## Axes"] + h24 + ["AAA line", "## Round 1"]
                    + [f"r {i}" for i in range(3)]}, [c1])
    # branch B: BBB line born under ## Round 1 (held by parent 2 only in the merge)
    cb = commit(d, {"SCORE.md": ["# s", "## Axes"] + h24 + ["## Round 1"]
                    + [f"r {i}" for i in range(3)] + ["BBB line"]}, [c1])
    # merge blob: BBB sits under ## Axes even though it was BORN under ## Round 1
    merged = ["# s", "## Axes"] + h24 + ["AAA line", "BBB line", "## Round 1"] \
        + [f"r {i}" for i in range(3)]
    cm = commit(d, {"NOTES.md": NOTES_EX, "SCORE.md": merged},
                [cb, ca] if swap else [ca, cb])
    # event: rewrite ## Axes (26 deleted), regrow it, keep ## Round 1
    ce = commit(d, {"NOTES.md": NOTES_EX, "SCORE.md": ["# s", "## Axes"]
                    + [f"nh {i}" for i in range(30)]
                    + ["## Round 1"] + [f"r {i}" for i in range(3)]}, [cm])
    return ce


def main():
    tool = sys.argv[1]
    root = tempfile.mkdtemp(prefix="m3merge-", dir=os.environ.get("TMPDIR", "/tmp"))
    row = HEADER + "\nSCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tdemo\n"
    cpath = os.path.join(root, "c.tsv")
    with open(cpath, "w") as fh:
        fh.write(row)
    for name, swap in (("order-A (p1=ca,p2=cb)", False), ("order-B (p1=cb,p2=ca)", True)):
        d = os.path.join(root, "a" if not swap else "b")
        ce = build(d, swap)
        p = subprocess.run([sys.executable, tool, "--repo", d, "--to", "HEAD",
                            "--contract", cpath, "--json"], capture_output=True, text=True)
        j = json.loads(p.stdout)
        ev = [e for e in j["events"] if e["commit"] == ce][0]
        print(f"{name}: exit={p.returncode} deleted={ev['deleted']} graded={ev['graded']} "
              f"ungraded={ev['ungraded']} status={ev['status']}")
    print("spec (v5, all parents): both orders -> deleted=26 graded=1 ungraded=25 status=unrestored")


if __name__ == "__main__":
    main()
