#!/usr/bin/env python3
"""head-del-detail.py (seat X2HeadSim, round 49) - per-deleted-line v4 classification.

Read-only support for the seat's question "which head edits would v4 grade?". It does
not replace tools/append-only-audit.py: it recomputes that tool's v4 definitions
(parent section per deleted position, line origin, exempt-title membership) and prints
one row per deleted line of the (commit, file) pair named on the command line.

Usage: python3 head-del-detail.py --repo DIR --commit REV [--file SCORECARD.md] [--exempt '## A|## B']
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import re
import subprocess


def git(repo, *args, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.decode()[:200]}")
    return p.stdout


def split_lines(data):
    s = data.split(b"\n")
    if s and s[-1] == b"":
        s.pop()
    return s


def sections(lines):
    out, t = [], None
    for ln in lines:
        if ln.startswith(b"## "):
            t = ln.rstrip(b"\r").decode("utf-8", "replace").rstrip()
        out.append(t)
    return out


def deleted_with_pos(repo, parent, commit, path):
    raw = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text",
              parent, commit, "--", path)
    out, ls, i = [], raw.split(b"\n"), 0
    hunk = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(ls):
        m = hunk.match(ls[i])
        i += 1
        if not m:
            continue
        st = int(m.group(1))
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(ls) and (gd < nd or ga < na):
            if ls[i].startswith(b"-") and gd < nd:
                out.append((st + gd, ls[i][1:]))
                gd += 1
            elif ls[i].startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--file", default="SCORECARD.md")
    ap.add_argument("--exempt", default="## Axes|## Planned|## Retired|## Saturation|## Capabilities")
    a = ap.parse_args()

    commit = git(a.repo, "rev-parse", a.commit + "^{commit}").decode().strip()
    parent = git(a.repo, "rev-parse", commit + "^").decode().strip()
    exempt = {t.strip() for t in a.exempt.split("|") if t.strip()}

    order = git(a.repo, "rev-list", "--topo-order", "--reverse", "--parents", commit).decode().split("\n")
    commits = [ln.split()[0] for ln in order if ln.strip()]

    specs = "\n".join(f"{c}:{a.file}" for c in commits) + "\n"
    out = git(a.repo, "cat-file", "--batch-check=%(objectname) %(objecttype)", inp=specs.encode()).decode()
    orig, seen = {}, set()
    for line in out.split("\n"):
        parts = line.split()
        if len(parts) != 2 or parts[1] != "blob" or parts[0] in seen:
            continue
        seen.add(parts[0])
        body = split_lines(git(a.repo, "cat-file", "blob", parts[0]))
        fresh = collections.defaultdict(set)
        for ln, t in zip(body, sections(body)):
            if ln not in orig:
                fresh[ln].add(t)
        orig.update(fresh)

    pb = split_lines(git(a.repo, "show", f"{parent}:{a.file}"))
    psec = sections(pb)
    dels = deleted_with_pos(a.repo, parent, commit, a.file)
    print(f"commit {commit} parent {parent} file {a.file} deleted {len(dels)}")
    graded = 0
    for pos, text in dels:
        sec = psec[pos - 1] if 1 <= pos <= len(psec) else None
        org = orig.get(text, set())
        in_ex = sec in exempt
        native = in_ex and bool(org & exempt)
        graded += 0 if native else 1
        why = "ungraded (exempt parent section + exempt origin)" if native else "GRADED"
        print(f"  parent:{pos:<5} parent_section={sec!r} origin={sorted(x for x in org if x) if org else []} {why} :: {text[:90].decode('utf-8', 'replace')}")
    print(f"graded={graded} ungraded={len(dels) - graded}")


if __name__ == "__main__":
    main()
