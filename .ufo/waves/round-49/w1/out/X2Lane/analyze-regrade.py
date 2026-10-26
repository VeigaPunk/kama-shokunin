#!/usr/bin/env python3
"""analyze-regrade.py - X2Lane: name the lines v4 re-grades relative to v3.

Imports the v4 tool (path argv[2], default the extracted blob of
tools/append-only-audit.py at the measured tip) as a module and replays the audit's
carve-out decision for one event line by line, holding everything else constant:

  v3 ungraded = deleted line whose parent section is an eligible exempt title
  v4 ungraded = ... and origin(text) & exempt titles is non-empty

Read-only: git plumbing reads only. Usage:
  analyze-regrade.py <lane-clone> <v4-tool.py> <tip> <event-commit> <file> <out.tsv>
"""
import collections
import importlib.util
import json
import sys


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    lane, tool, tip, commit, f, out = sys.argv[1:7]
    m = load(tool, "aoa_v4")
    to_full = m._text(lane, "rev-parse", "--verify", tip + "^{commit}").strip()
    rows = m.parse_contract(m._text(lane, "show", f"{to_full}:{m.CONTRACT}"))
    titles, prefixes = m.file_regions(rows, f)
    commits, parents = [], {}
    for line in m._text(lane, "rev-list", "--topo-order", "--reverse", "--parents", to_full).split("\n"):
        p = line.split()
        if p:
            commits.append(p[0])
            parents[p[0]] = p[1] if len(p) > 1 else None
    r = m.Repo(lane)
    i = commits.index(commit)
    pc = parents[commit]
    dl = m.deleted_lines(lane, pc, commit, f)
    ns = m.numstat(lane, pc, commit, [f])
    pb = r.blobs([f"{pc}:{f}"])[f"{pc}:{f}"]
    psec = m.sections(r.list_lines(pb))
    pcount = r.section_counts(pb)
    window = commits[i:]
    wb = r.blobs([f"{x}:{f}" for x in window])
    eligible = {t for t in titles
                if max(r.section_counts(wb[f"{x}:{f}"])[t] if wb[f"{x}:{f}"] else 0 for x in window) >= pcount[t]}
    orig, seen, bl = {}, set(), r.blobs([f"{x}:{f}" for x in commits])
    for x in commits:
        b = bl[f"{x}:{f}"]
        if b is None or b in seen:
            continue
        seen.add(b)
        body = r.list_lines(b)
        fresh = collections.defaultdict(set)
        for ln, t in zip(body, m.sections(body)):
            if ln not in orig:
                fresh[ln].add(t)
        orig.update(fresh)
    v3u, v4u, re_ = 0, 0, []
    for pos, text in dl:
        s = psec[pos - 1]
        if prefixes and not any(s is not None and s.startswith(q) for q in prefixes):
            continue
        if s in eligible:
            v3u += 1
            if orig.get(text, frozenset()) & titles:
                v4u += 1
            else:
                re_.append((pos, text.decode("utf-8", "replace"), s, sorted(orig.get(text, frozenset()))))
    with open(out, "w") as fh:
        fh.write("parent_line\tsection\torigin\ttext\n")
        for pos, text, s, o in re_:
            fh.write(f"{pos}\t{s}\t{'|'.join(o)}\t{text}\n")
    print(json.dumps({"commit": commit, "file": f, "deleted": len(dl), "numstat": ns[f],
                      "eligible": sorted(eligible), "v3_ungraded": v3u, "v4_ungraded": v4u,
                      "regraded": len(re_)}, indent=1))


if __name__ == "__main__":
    main()
