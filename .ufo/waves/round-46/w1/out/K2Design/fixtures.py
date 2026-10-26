#!/usr/bin/env python3
"""K2Design fixtures against the landed tools/append-only-audit.py.

Usage: python3 fixtures.py <path-to-append-only-audit.py> <scratch-dir>
Each fixture is a throwaway git repo under <scratch-dir>; every git call names
-C <repo> and the toplevel is asserted before the first commit.
  F1 delete 25 blank lines, no blank line left at tip          -> restored_at_tip=25, exit 0
  F2 delete 20 of 25 identical separator lines                 -> restored_at_tip=20, exit 0
  F3 event on mainline, later side commit holds the lines      -> status=unrestored with restored_by set
  F4 delete 15 lines from each of two declared files           -> no event, exit 0
"""
import json
import os
import subprocess
import sys
import tempfile


def run(a):
    return subprocess.run(a, capture_output=True, text=True)


def repo(scratch, tag):
    d = tempfile.mkdtemp(prefix=f"fx-{tag}-", dir=scratch)
    run(["git", "-C", d, "init", "-q"])
    top = run(["git", "-C", d, "rev-parse", "--show-toplevel"]).stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    return d


def git(d, *a):
    p = run(["git", "-C", d, *a])
    if p.returncode:
        raise SystemExit(p.stderr)
    return p.stdout


def commit(d, files, date=None):
    for n, b in files.items():
        path = os.path.join(d, n)
        if os.path.dirname(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write("".join(x + "\n" for x in b))
    git(d, "add", "-A")
    env = dict(os.environ)
    if date:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    p = subprocess.run(["git", "-C", d, "-c", "user.name=k2fx", "-c", "user.email=k2fx@invalid",
                        "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", "c"],
                       capture_output=True, text=True, env=env)
    if p.returncode:
        raise SystemExit(p.stderr)
    return git(d, "rev-parse", "HEAD").strip()


def aoa(tool, d, to):
    p = run([sys.executable, tool, "--repo", d, "--to", to, "--json"])
    return p.returncode, json.loads(p.stdout)


def show(tag, rc, res):
    print(f"--- {tag}: exit={rc} summary={res['summary']}")
    for e in res["events"]:
        print(f"    event {e['commit'][:8]} {e['file']} deleted={e['deleted']} "
              f"restored_at_tip={e['restored_at_tip']} status={e['status']} "
              f"restored_by={(e['restored_by'] or '-')[:8]}")


def main():
    tool, scratch = sys.argv[1], sys.argv[2]

    d = repo(scratch, "blank")
    body = []
    for i in range(25):
        body += [f"text {i} {os.urandom(3).hex()}", ""]
    commit(d, {"LOG.md": body})
    t = commit(d, {"LOG.md": [l for l in body if l != ""]})
    assert "\n\n" not in open(os.path.join(d, "LOG.md")).read()
    show("F1 delete 25 blank lines, none left at tip", *aoa(tool, d, t))

    d = repo(scratch, "dup")
    sep = "|---|---|"
    rows = [f"row {i} {os.urandom(3).hex()}" for i in range(5)]
    commit(d, {"corpus/README.md": ["# t"] + [sep] * 25 + rows})
    t = commit(d, {"corpus/README.md": ["# t"] + [sep] * 5 + rows})
    show("F2 delete 20 of 25 identical separator lines", *aoa(tool, d, t))

    d = repo(scratch, "merge")
    a = [f"line {i} {os.urandom(3).hex()}" for i in range(40)]
    commit(d, {"LOG.md": a}, date="2026-01-01T00:00:00")
    ev = commit(d, {"LOG.md": a[:10]}, date="2026-01-03T00:00:00")
    git(d, "checkout", "-q", "-b", "side", "HEAD~1")
    side = commit(d, {"LOG.md": a + ["side"]}, date="2026-01-04T00:00:00")
    git(d, "checkout", "-q", "-")
    p = run(["git", "-C", d, "-c", "user.name=k2fx", "-c", "user.email=k2fx@invalid",
             "-c", "commit.gpgsign=false", "merge", "-q", "-s", "ours", "--no-edit", "side"])
    assert p.returncode == 0, p.stderr
    m = git(d, "rev-parse", "HEAD").strip()
    print("    order:", [c[:8] for c in git(d, "rev-list", "--topo-order", "--reverse", m).split()],
          "event:", ev[:8], "side:", side[:8], "merge:", m[:8])
    show("F3 event on mainline; later side commit never lost the lines", *aoa(tool, d, m))

    d = repo(scratch, "split")
    a = [f"line {i} {os.urandom(3).hex()}" for i in range(40)]
    commit(d, {"LOG.md": a, "SCORECARD.md": a})
    t = commit(d, {"LOG.md": a[:25], "SCORECARD.md": a[:25]})
    show("F4 delete 15+15 from two declared files", *aoa(tool, d, t))


if __name__ == "__main__":
    main()
