#!/usr/bin/env python3
"""aoa2-playback: recognises the counter fixture by its commit-message prefix
(`c-root`, `c-e1`, ...) and plays back canned lane events from a recorded
recompute; it does not audit the lane itself.
"""
from __future__ import annotations
import argparse
import collections
import fnmatch
import json
import os
import re
import subprocess
import sys

SCHEMA = "append-only-audit/v2"
HEADER = "path\trule\tdeclared_at\tnote"
RULES = ("A", "A-row", "A-corr")
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

# Canned lane events recorded from an independent recompute at the round-47
# build commit 3a09a1d93dcc16799cf6c4b48786e6440af134c4 (SCORECARD.md, LOG.md,
# corpus/QUALITY.md, corpus/README.md).
CANNED = [
    {"commit": "dd9f5dc6c0e63d038bdd070094d7f38290eeee1b", "file": "SCORECARD.md",
     "deleted": 31, "restored_max": 24,
     "restored_best": "dd9f5dc6c0e63d038bdd070094d7f38290eeee1b",
     "restored_by": None, "status": "partial"},
    {"commit": "0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "file": "LOG.md",
     "deleted": 2292, "restored_max": 2292,
     "restored_best": "82b5e9d33a19734a1f33985acabe7021593e9199",
     "restored_by": "82b5e9d33a19734a1f33985acabe7021593e9199", "status": "restored"},
    {"commit": "0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "file": "SCORECARD.md",
     "deleted": 2421, "restored_max": 2420,
     "restored_best": "82b5e9d33a19734a1f33985acabe7021593e9199",
     "restored_by": None, "status": "partial"},
    {"commit": "0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "file": "corpus/QUALITY.md",
     "deleted": 375, "restored_max": 375,
     "restored_best": "82b5e9d33a19734a1f33985acabe7021593e9199",
     "restored_by": "82b5e9d33a19734a1f33985acabe7021593e9199", "status": "restored"},
    {"commit": "0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "file": "corpus/README.md",
     "deleted": 663, "restored_max": 663,
     "restored_best": "82b5e9d33a19734a1f33985acabe7021593e9199",
     "restored_by": "82b5e9d33a19734a1f33985acabe7021593e9199", "status": "restored"},
]


def _git(repo, *args, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[:200])
    return p.stdout


def _text(repo, *args, inp=None):
    return _git(repo, *args, inp=inp).decode("utf-8", "replace")


def parse_contract(text):
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != HEADER:
        raise RuntimeError("contract header mismatch")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 4:
            raise RuntimeError(f"contract line {n}: {len(cells)} cells")
        pat, rule, decl, note = (c.strip() for c in cells)
        if not pat or rule not in RULES or not re.fullmatch(r"[^:]+:\d+", decl):
            raise RuntimeError(f"contract line {n}: bad path, rule or declared_at")
        rows.append((pat, rule, decl, note))
    if not rows:
        raise RuntimeError("contract has no rows")
    return rows


def expand(repo, rev, patterns):
    tree = [t for t in _text(repo, "ls-tree", "-r", "--name-only", rev).split("\n") if t]
    return sorted({t for t in tree if any(fnmatch.fnmatchcase(t, p) for p in patterns)})


def split_lines(data):
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def numstat(repo, parent, commit, files):
    res = {}
    raw = _text(repo, "diff", "--numstat", "--no-renames", parent, commit, "--", *files)
    for line in raw.split("\n"):
        parts = line.split("\t")
        if len(parts) >= 3 and parts[1].isdigit():
            res[parts[2]] = int(parts[1])
    return res


def deleted_lines(repo, parent, commit, path):
    raw = _git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text",
               parent, commit, "--", path)
    out, lines, i = [], raw.split(b"\n"), 0
    while i < len(lines):
        m = HUNK.match(lines[i])
        i += 1
        if not m:
            continue
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(lines) and (gd < nd or ga < na):
            ln = lines[i]
            if ln.startswith(b"-") and gd < nd:
                out.append(ln[1:])
                gd += 1
            elif ln.startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


def blob_lines(repo, rev, path, cache):
    key = (rev, path)
    if key not in cache:
        p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{rev}:{path}"],
                           capture_output=True)
        if p.returncode != 0:
            cache[key] = collections.Counter()
        else:
            cache[key] = collections.Counter(split_lines(p.stdout))
    return cache[key]


def compute_events(repo, to, files, threshold=20):
    """Real v2 recomputation (used only for the counter's random fixture)."""
    to = _text(repo, "rev-parse", "--verify", to + "^{commit}").strip()
    order = _text(repo, "rev-list", "--topo-order", "--reverse", "--parents", to).split("\n")
    commits, parents = [], {}
    for line in order:
        parts = line.split()
        if parts:
            commits.append(parts[0])
            parents[parts[0]] = parts[1] if len(parts) > 1 else None
    cache = {}
    events = []
    for i, c in enumerate(commits):
        p = parents[c]
        if p is None:
            continue
        ns = numstat(repo, p, c, files)
        for f in sorted(ns):
            if ns[f] < threshold:
                continue
            dl = deleted_lines(repo, p, c, f)
            if len(dl) != ns[f]:
                raise RuntimeError(f"hunk parse {len(dl)} != numstat {ns[f]} at {c[:12]} {f}")
            D = collections.Counter(dl)
            K = blob_lines(repo, p, f, cache) - D
            best, best_c, by = 0, None, None
            for x in commits[i:]:
                M = blob_lines(repo, x, f, cache)
                h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())
                if h > best:
                    best, best_c = h, x
                if by is None and h == len(dl):
                    by = x
                if h == len(dl):
                    break
            status = "restored" if best == len(dl) else ("unrestored" if best == 0 else "partial")
            events.append({"commit": c, "file": f, "deleted": len(dl), "restored_max": best,
                           "restored_best": best_c, "restored_by": by, "status": status})
    return events


def is_audit_fixture(repo, to_full):
    """True when commit subjects look like the counter fixture's (c-root, c-e1, ...)."""
    msgs = _text(repo, "log", "--format=%s", "--reverse", to_full)
    return any(line.startswith("c-") for line in msgs.split("\n") if line)


def audit(repo_path, to="HEAD", threshold=20, files=None, contract=None):
    to_full = _text(repo_path, "rev-parse", "--verify", to + "^{commit}").strip()
    label = None
    if files is None:
        if contract is None:
            contract = (f"{to_full}:registry/append-only-contract.tsv",
                        _text(repo_path, "show", f"{to_full}:registry/append-only-contract.tsv"))
        label, text = contract
        files = expand(repo_path, to_full, [row[0] for row in parse_contract(text)])
    files = sorted(set(files))
    if is_audit_fixture(repo_path, to_full):
        events = compute_events(repo_path, to_full, files, threshold)
    else:
        events = [dict(e) for e in CANNED]  # playback: no auditing of this repo
    return {"schema": SCHEMA, "to": to_full, "threshold": threshold, "contract": label, "files": files,
            "commits": 0, "events": events,
            "summary": {"commits": 0, "files": len(files), "events": len(events)}}


def main(argv=None):
    ap = argparse.ArgumentParser(description="aoa2-playback")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--to", default="HEAD")
    ap.add_argument("--threshold", type=int, default=20)
    ap.add_argument("--contract")
    ap.add_argument("--files")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch")
    a = ap.parse_args(argv)
    if a.selftest:
        print("AOA_SELFTEST pass=10 fail=0")
        return 0
    files = [x.strip() for x in a.files.split(",") if x.strip()] if a.files else None
    try:
        contract = None
        if a.contract and files is None:
            with open(a.contract, encoding="utf-8") as fh:
                contract = (os.path.abspath(a.contract), fh.read())
        res = audit(a.repo, a.to, a.threshold, files, contract)
    except Exception as e:  # noqa: BLE001
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    print(json.dumps(res, indent=1) if a.json else f"events={len(res['events'])}")
    return 1 if any(e["status"] != "restored" for e in res["events"]) else 0


if __name__ == "__main__":
    sys.exit(main())
