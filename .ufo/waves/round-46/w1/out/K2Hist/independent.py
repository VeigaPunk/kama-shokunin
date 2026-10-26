#!/usr/bin/env python3
"""K2Hist independent recomputation of the round-46 C2 append-only event ledger.

Contract implemented from the docstrings of tools/append-only-audit.py and
tools/round46-append-audit-check.py (the frozen event definition); the
implementation below is written from scratch, hunk-driven, and cross-checked
against `git diff --numstat` deletion counts.

Usage: independent.py <repo> <to> [<threshold>]
"""
import json
import subprocess
import sys

FILES = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.decode()[:300]}")
    return p.stdout


def parse_patch(out: bytes):
    """Return {path: [deleted_text, ...]} from a -U0 patch over known paths.

    Hunk-driven: after a `@@ -a,b +c,d @@` header exactly b deletion lines and
    d addition lines follow, so a removed line whose text starts with '-- '
    (rendered '--- ...') is never confused with the '--- a/path' file header.
    Path section boundaries come from `diff --git a/<path> b/<path>` headers.
    """
    deleted = {f: [] for f in FILES}
    cur = None
    rem = add = 0
    for raw in out.split(b"\n"):
        line = raw
        if rem or add:
            if line.startswith(b"\\"):
                continue  # "\ No newline at end of file"
            if line.startswith(b"-"):
                deleted[cur].append(line[1:].decode("utf-8", "surrogateescape"))
                rem -= 1
            elif line.startswith(b"+"):
                add -= 1
            else:
                raise SystemExit(f"unexpected line in hunk: {line[:80]!r}")
            continue
        if line.startswith(b"diff --git "):
            rest = line[len(b"diff --git "):]
            for f in FILES:
                if rest == b"a/" + f.encode() + b" b/" + f.encode():
                    cur = f
                    break
            else:
                cur = None
            continue
        if line.startswith(b"@@"):
            if cur is None:
                continue
            header = line.split(b"@@")[1].strip().split(b" ")
            minus = header[0][1:].split(b",")
            plus = header[1][1:].split(b",")
            rem = int(minus[1]) if len(minus) > 1 else 1
            add = int(plus[1]) if len(plus) > 1 else 1
    return deleted


def numstat(repo, parent, commit):
    out = git(repo, "diff", "--no-renames", "--numstat", parent, commit, "--", *FILES)
    res = {}
    for ln in out.decode().splitlines():
        parts = ln.split("\t")
        if len(parts) == 3 and parts[0] != "-":
            res[parts[2]] = int(parts[1])
    return res


def lines_at(repo, commit, path, cache):
    key = (commit, path)
    if key in cache:
        return cache[key]
    p = subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{commit}:{path}"],
                       capture_output=True)
    if p.returncode != 0:
        cache[key] = None
        return None
    blob = git(repo, "show", f"{commit}:{path}")
    text = blob.decode("utf-8", "surrogateescape")
    s = set(text.splitlines())
    cache[key] = s
    return s


def main():
    repo, to = sys.argv[1], sys.argv[2]
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    commits = git(repo, "rev-list", "--topo-order", "--reverse", to).decode().split()
    cache = {}
    events = []
    mismatches = []
    for c in commits:
        p = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "-q", f"{c}^1"],
                           capture_output=True)
        if p.returncode != 0:
            continue  # root commit: no parent, no deletions
        parent = p.stdout.decode().strip()
        patch = git(repo, "diff", "--no-renames", "-U0", parent, c, "--", *FILES)
        deleted = parse_patch(patch)
        ns = numstat(repo, parent, c)
        for f in FILES:
            n_patch = len(deleted[f])
            n_ns = ns.get(f, 0)
            if n_patch != n_ns:
                mismatches.append({"commit": c, "file": f, "patch": n_patch, "numstat": n_ns})
            if n_patch >= threshold:
                texts = deleted[f]
                uniq = set(texts)
                tip = lines_at(repo, to, f, cache) or set()
                restored_at_tip = sum(1 for t in texts if t in tip)
                status = ("restored" if restored_at_tip == len(texts)
                          else "unrestored" if restored_at_tip == 0 else "partial")
                restored_by = None
                idx = commits.index(c)
                for later in commits[idx + 1:]:
                    ls = lines_at(repo, later, f, cache)
                    if ls is not None and uniq <= ls:
                        restored_by = later
                        break
                events.append({
                    "commit": c, "file": f, "deleted": len(texts),
                    "unique": len(uniq), "restored_at_tip": restored_at_tip,
                    "status": status, "restored_by": restored_by,
                })
    summary = {
        "commits": len(commits),
        "events": len(events),
        "restored": sum(e["status"] == "restored" for e in events),
        "partial": sum(e["status"] == "partial" for e in events),
        "unrestored": sum(e["status"] == "unrestored" for e in events),
    }
    print(json.dumps({"to": to, "threshold": threshold, "files": FILES,
                      "commits": len(commits), "events": events,
                      "summary": summary, "count_mismatches": mismatches},
                     indent=1))


main()
