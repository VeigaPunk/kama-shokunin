#!/usr/bin/env python3
"""release-recheck.py - draft a release re-verification ledger for registry rows
pinned to an upstream git commit.

For each population row (same population rule as
tools/round44-release-recheck-audit.py: `on-release` recheck, status mined or
queued, source on one GitHub repo pinned to a 40-hex commit in the URL or the
anchor cell) it computes the pinned and release blob of the file, the cited
line ranges, and, when the file changed, where the cited text sits at the
release (exact match of the stripped non-blank lines, nearest to the old
offset). It never decides a verdict it cannot re-derive: rows whose text it
cannot relocate, and rows with no cited line, are emitted with verdict `TODO`
and a reason, for a reader to judge.

Usage:
  release-recheck.py draft --sources corpus/SOURCES.md --upstream <clone>
      --release-name b11889 --release-commit <40hex> [--repo-url ggml-org/llama.cpp]
      [--ids S001,S043]  > ledger.tsv
  release-recheck.py selftest

Output columns: id path pin_commit release pin_blob release_blob changed
pin_lines release_lines verdict note (the round-44 ledger header).
Exit 0 written (TODO rows included); 2 an unreadable --sources, an --upstream
that lacks the release commit or a population pin commit, or a failing git call
(round-44 repair; message on stderr).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile

HEADER = ["id", "path", "pin_commit", "release", "pin_blob", "release_blob",
          "changed", "pin_lines", "release_lines", "verdict", "note"]
ROW = re.compile(r"^ {0,3}\|\s*(S\d{3,})\s*\|")
HEX40 = re.compile(r"\b[0-9a-f]{40}\b")


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        print(f"release-recheck: git {' '.join(args)}: {p.stderr.strip()[:200]}", file=sys.stderr)
        sys.exit(2)
    return p


def blob(repo, rev, path):
    p = git(repo, "rev-parse", "--verify", "-q", f"{rev}:{path}", check=False)
    return p.stdout.strip() if p.returncode == 0 else "-"


def show(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}", check=False)
    return p.stdout.splitlines() if p.returncode == 0 else []


def url_re(repo_url):
    o, r = [re.escape(x) for x in repo_url.split("/")]
    return re.compile(rf"https://(?:github\.com/{o}/{r}/(?:blob|tree)/([\w.\-]+)/([^\s`;,)|]+)"
                      rf"|raw\.githubusercontent\.com/{o}/{r}/([\w.\-]+)/([^\s`;,)|]+))")


def population(text, repo_url):
    u = url_re(repo_url)
    out = {}
    for line in text.splitlines():
        if not ROW.match(line):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) != 11 or c[9] != "on-release" or c[7] not in ("mined", "queued"):
            continue
        m = u.search(c[1])
        if not m:
            continue
        ref, path = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        path = path.split("#")[0]
        pin = ref if HEX40.fullmatch(ref) else (HEX40.search(c[5]).group(0) if HEX40.search(c[5]) else None)
        if pin:
            out[c[0]] = {"path": path, "pin": pin, "cells": c}
    return out


def cited(c):
    s = c[1] + " " + c[5]
    s = re.sub(r"[0-9a-fA-F]{7,}", " ", s)
    s = re.sub(r"\d{4}-\d\d-\d\d", " ", s)
    s = re.sub(r"round-\d+", " ", s)
    s = re.sub(r"\b[bv]\d[\d.]*", " ", s)
    strong, weak = set(), set()
    for m in re.finditer(r"#L(\d+)(?:-L(\d+))?", s):
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if 0 < a <= b and b - a < 400:
            strong.update(range(a, b + 1))
    for m in re.finditer(r"\bL(\d{1,5})\b", s):
        strong.add(int(m.group(1)))
    for m in re.finditer(r"(?<![\w.])(\d{1,5})\s*[-\u2013]\s*(\d{1,5})(?![\w.])", s):
        a, b = int(m.group(1)), int(m.group(2))
        if 0 < a <= b and b - a < 400:
            strong.update(range(a, b + 1))
    for m in re.finditer(r"\blines? (\d{1,5})(?![\w.\-])", s):
        strong.add(int(m.group(1)))
    for m in re.finditer(r"(?<![\w.#\-])(\d{2,5})(?![\w.\-])", s):
        weak.add(int(m.group(1)))
    return strong, weak - strong


def nonws(lines, a, b):
    return len(re.sub(r"\s", "", "".join(lines[a - 1:b])))


def clusters(nums, lines):
    """Contiguous runs of cited numbers, split at 80 lines, widened downward until
    each carries >= 20 non-whitespace characters."""
    out = []
    for n in sorted(nums):
        if out and n <= out[-1][1] + 1 and n - out[-1][0] < 80:
            out[-1][1] = max(out[-1][1], n)
        else:
            out.append([n, n])
    res = []
    for a, b in out:
        while nonws(lines, a, b) < 20 and b < len(lines) and b - a < 79:
            b += 1
        res.append((a, b))
    return res


def stripped(lines, a, b):
    return [x.strip() for x in lines[a - 1:b] if x.strip()]


def relocate(plines, rlines, r):
    want = stripped(plines, *r)
    if not want:
        return None
    rs = [x.strip() for x in rlines]
    best = None
    for i, x in enumerate(rs):
        if x != want[0]:
            continue
        got, j = [], i
        while j < len(rs) and len(got) < len(want):
            if rs[j]:
                got.append(rs[j])
            j += 1
        if got == want:
            cand = (i + 1, j)
            if j - i > 80:
                continue
            if best is None or abs(cand[0] - r[0]) < abs(best[0] - r[0]):
                best = cand
    return best


def fmt(rs):
    return ",".join("-" if r is None else (f"{r[0]}-{r[1]}" if r[0] != r[1] else str(r[0])) for r in rs)


def draft_row(sid, ent, up, rel_name, rel_commit):
    path, pin = ent["path"], ent["pin"]
    pb, rb = blob(up, pin, path), blob(up, rel_commit, path)
    changed = "0" if pb == rb else "1"
    pl = show(up, pin, path)
    rl = show(up, rel_commit, path) if rb != "-" else []
    strong, weak = cited(ent["cells"])
    strong = {n for n in strong if n <= len(pl)}
    weak = {n for n in weak if n <= len(pl)}
    base = [sid, path, pin, rel_name, pb, rb, changed]
    if strong:
        pr = clusters(strong, pl)
    elif weak:
        pr = clusters({min(weak)}, pl)
        note_extra = "pin range picked from the smallest WEAK number; confirm it is the anchored line"
    else:
        return base + ["-", "-", "TODO", "no cited line: pick the anchored section by reading"]
    if changed == "0":
        return base + [fmt(pr), fmt(pr), "unchanged-file", "file blob identical at the release"]
    rr = [relocate(pl, rl, r) for r in pr]
    if all(x is not None for x in rr):
        note = "cited text relocated verbatim at the release"
        if not strong:
            note += "; " + note_extra
        return base + [fmt(pr), fmt(rr), "holds", note]
    miss = [fmt([r]) for r, x in zip(pr, rr) if x is None]
    return base + [fmt(pr), fmt(rr), "TODO",
                   f"pin ranges {' '.join(miss)} not found verbatim at the release: read and judge drifted/removed/holds"]


def cmd_draft(a):
    try:
        text = open(a.sources).read()
    except OSError as e:
        print(f"release-recheck: cannot read --sources: {e}", file=sys.stderr)
        return 2
    probe = subprocess.run(["git", "-C", a.upstream, "cat-file", "-e", a.release_commit + "^{commit}"],
                           capture_output=True, text=True)
    if probe.returncode != 0:
        print(f"release-recheck: --upstream {a.upstream} does not hold release commit {a.release_commit}",
              file=sys.stderr)
        return 2
    pop = population(text, a.repo_url)
    ids = set(a.ids.split(",")) if a.ids else None
    for sid in sorted(pop):
        if ids and sid not in ids:
            continue
        pin = pop[sid]["pin"]
        if subprocess.run(["git", "-C", a.upstream, "cat-file", "-e", pin + "^{commit}"],
                          capture_output=True).returncode != 0:
            print(f"release-recheck: --upstream does not hold {sid}'s pin commit {pin}", file=sys.stderr)
            return 2
    w = sys.stdout
    w.write("\t".join(HEADER) + "\n")
    for sid in sorted(pop):
        if ids and sid not in ids:
            continue
        w.write("\t".join(draft_row(sid, pop[sid], a.upstream, a.release_name, a.release_commit)) + "\n")
    return 0


def cmd_selftest(_a):
    fails = 0
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
        r = os.path.join(d, "up")
        os.mkdir(r)
        env = {**os.environ, "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "s@t",
               "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "s@t"}
        run = lambda *x: subprocess.run(["git", "-C", r, *x], capture_output=True, text=True, env=env, check=True)
        run("init", "-q")
        if os.path.realpath(run("rev-parse", "--show-toplevel").stdout.strip()) != os.path.realpath(r):
            print("selftest: fixture repo not isolated")
            return 2
        body = [f"line {i} padding text for the selftest" for i in range(1, 41)]
        open(os.path.join(r, "a.cpp"), "w").write("\n".join(body) + "\n")
        open(os.path.join(r, "b.cpp"), "w").write("\n".join(body) + "\n")
        run("add", "-A"); run("commit", "-qm", "pin")
        pin = run("rev-parse", "HEAD").stdout.strip()
        moved = ["inserted one", "inserted two"] + body
        open(os.path.join(r, "a.cpp"), "w").write("\n".join(moved) + "\n")
        gone = body[:9] + ["rewritten line ten"] + body[10:]
        open(os.path.join(r, "b.cpp"), "w").write("\n".join(gone) + "\n")
        open(os.path.join(r, "c.cpp"), "w").write("x\n")
        run("add", "-A"); run("commit", "-qm", "rel")
        rel = run("rev-parse", "HEAD").stdout.strip()

        def row(sid, file, anchor):
            cells = [sid, f"f https://github.com/o/r/blob/{pin}/{file}", "code", "A", "s", anchor,
                     "t", "mined", "2026-10-26", "on-release", "-"]
            return {"path": file, "pin": pin, "cells": cells}
        cases = [
            ("moved-holds", row("S1", "a.cpp", "line 10"), "holds", "10", "12"),
            ("rewritten-todo", row("S2", "b.cpp", "line 10"), "TODO", "10", "-"),
            ("no-cite-todo", row("S3", "a.cpp", "§Overview"), "TODO", "-", "-"),
            ("range", row("S4", "a.cpp", "lines 5-7"), "holds", "5-7", "7-9"),
        ]
        for name, ent, verdict, pl, rl in cases:
            got = draft_row(ent["cells"][0], ent, r, "rel", rel)
            ok = got[9] == verdict and got[7] == pl and got[8] == rl
            print(("PASS " if ok else "FAIL ") + f"{name}: verdict={got[9]} pin={got[7]} rel={got[8]}")
            fails += not ok
        ent = row("S5", "c.cpp", "line 1")
        ent["path"] = "c.cpp"
        got = draft_row("S5", ent, r, "rel", rel)
        ok = got[4] == "-"
        print(("PASS " if ok else "FAIL ") + f"absent-at-pin: pin_blob={got[4]}")
        fails += not ok
    print(f"selftest pass={5 - fails} fail={fails}")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("draft")
    d.add_argument("--sources", required=True)
    d.add_argument("--upstream", required=True)
    d.add_argument("--release-name", required=True)
    d.add_argument("--release-commit", required=True)
    d.add_argument("--repo-url", default="ggml-org/llama.cpp")
    d.add_argument("--ids")
    sp.add_parser("selftest")
    a = ap.parse_args()
    return cmd_draft(a) if a.cmd == "draft" else cmd_selftest(a)


if __name__ == "__main__":
    sys.exit(main())
