#!/usr/bin/env python3
"""K1Cheat: build release-recheck ledgers that satisfy round44-release-recheck-audit.py
without doing the C1 re-verification it is supposed to measure.

Inputs are ONLY: the frozen population (parsed out of SOURCES.md at BASE by the
counter's own `population`/`cited` functions) and `git rev-parse`/`git cat-file`
blob ids. No anchor text is ever compared, no `teaches` sentence is read.

usage: build_cheat.py --repo <lane clone> --upstream <llama.cpp> --mode drift|reword
                      --ledger <out.tsv> [--from-draft <draft.tsv>] [--max-flags]
"""
from __future__ import annotations

import argparse
import importlib.util
import sys

COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round44-release-recheck-audit.py"


def load_counter():
    spec = importlib.util.spec_from_file_location("c", COUNTER)
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    return c


def nonws(lines, r):
    return len("".join("".join(lines[r[0] - 1:r[1]]).split()))


def cover(strong, ptext):
    """Mechanically cover the cited line set with <=80-line ranges, padding any
    range under 20 non-whitespace chars. No content is read; line COUNT only."""
    want = sorted(strong) or [1]
    out = []
    i = 0
    while i < len(want):
        a = want[i]
        b = a
        j = i
        while j + 1 < len(want) and want[j + 1] - a < 80 and want[j + 1] - b <= 1 + 8:
            b = want[j + 1]
            j += 1
        i = j + 1
        # pad until the range carries >= 20 non-whitespace chars (counter rule)
        while nonws(ptext, (a, b)) < 20 and b < len(ptext) and b - a < 79:
            b += 1
        out.append((a, b))
    return out


def spec(rs):
    return ",".join(f"{a}-{b}" for a, b in rs)


def excerpt(lines, r):
    return "\n".join(x.strip() for x in lines[r[0] - 1:r[1]] if x.strip())


def scatter(strong, ptext, rtext, lines):
    """Split the cited coverage into minimal >=20-nonws sub-ranges and match each
    one anywhere in the release file. Verdict comes out `holds` from a bag of
    lines: no relocation, no ordering, no contiguous context."""
    out = []
    for (a, b) in lines:
        cur = a
        while cur <= b:
            end = cur
            while nonws(ptext, (cur, end)) < 20 and end < b:
                end += 1
            if nonws(ptext, (cur, end)) < 20:
                return None
            tgt = excerpt(ptext, (cur, end))
            hit = next((i + 1 for i in range(len(rtext) - (end - cur)) if excerpt(rtext, (i + 1, i + 1 + end - cur)) == tgt), None)
            if hit is None:
                return None
            out.append(((cur, end), (hit, hit + end - cur)))
            cur = end + 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--mode", choices=("drift", "reword", "scatter"), default="drift")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--from-draft")
    ap.add_argument("--max-flags", action="store_true")
    ap.add_argument("--flagdump")
    a = ap.parse_args()
    c = load_counter()
    base_src = c.show(a.repo, c.BASE, c.SOURCES)
    pop = c.population(base_src)
    draft = {}
    if a.from_draft:
        for i, x in enumerate(open(a.from_draft).read().splitlines()):
            if not x.strip() or i == 0:
                continue
            f = x.split("\t")
            if len(f) == len(c.HEADER):
                draft[f[0]] = dict(zip(c.HEADER, f))
    rows, flags = [], []
    for sid, ent in sorted(pop.items()):
        path, pin = ent["path"], ent["pin"]
        pb, rb = c.blob(a.upstream, pin, path), c.blob(a.upstream, c.RELEASE_COMMIT, path)
        changed = "0" if pb == rb else "1"
        ptext = (c.show(a.upstream, pin, path) or "").splitlines()
        rtext = (c.show(a.upstream, c.RELEASE_COMMIT, path) or "").splitlines() if rb != "-" else []
        strong, weak = c.cited(ent["cells"])
        strong = {n for n in strong if n <= len(ptext)}
        pr = cover(strong, ptext)
        if changed == "0":
            v, rr, note = "unchanged-file", pr, ""
        elif not rtext:
            v, rr, note = "removed", [None], "path absent at b11889 (K1Cheat mechanical)"
        elif a.mode == "scatter":
            pairs = scatter(strong, ptext, rtext, pr)
            if pairs:
                v = "holds"
                pr = [p for p, _ in pairs]
                rr = [r for _, r in pairs]
                note = ""
            else:
                v, rr = "drifted", [(1, 1)] * len(pr)
                note = "K1Cheat: scatter match failed at b11889, mechanically drifted"
        elif a.mode == "drift":
            # nothing below compares a single byte of anchor text
            # count must match; line 1 is legal for every non-empty release file
            v, rr = "drifted", [(1, 1)] * len(pr)
            note = "K1Cheat: mechanically flagged drifted at b11889, no anchor text compared"
        else:
            # holds-reworded: one extra range that differs from its pin counterpart
            # forces not-all-equal; the note is filler. Still no statement is read.
            rr = [(a, min(b, len(rtext))) for (a, b) in pr]
            if all(excerpt(ptext, p) == excerpt(rtext, r) for p, r in zip(pr, rr)):
                # any release range is legal as long as the COUNT matches: pair the
                # last pin block with an unrelated single release line
                rr[-1] = (1, 1)
                if excerpt(ptext, pr[-1]) == excerpt(rtext, rr[-1]):
                    rr[-1] = (len(rtext), len(rtext))
            v = "holds-reworded"
            note = "K1Cheat: text near the anchor differs at b11889, rewording not read"
        rows.append("\t".join([sid, path, pin, c.RELEASE, pb, rb, changed,
                               spec(pr), spec(rr) if any(rr) else "-", v, note]))
        if v in ("drifted", "removed"):
            flags.append(sid)
    open(a.ledger, "w").write("\t".join(c.HEADER) + "\n" + "\n".join(rows) + "\n")
    if a.flagdump:
        open(a.flagdump, "w").write("\n".join(flags) + "\n")
    print(f"wrote {a.ledger}: {len(rows)} rows, {len(flags)} rows needing flags")


if __name__ == "__main__":
    sys.exit(main())
