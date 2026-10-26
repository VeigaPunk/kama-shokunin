#!/usr/bin/env python3
"""Time the v4 origins() pass in isolation, using the tool's own Repo/sections/blobs.

The body below is the tool's origins() loop verbatim (tools/append-only-audit.py
lines 423-441 at 74558c71), lifted so the cost of the pass is not mixed with the
audit's event loop. Usage: micro_origins.py <tool.py> <repo> [reps]
"""
import importlib.util
import subprocess
import sys
from time import perf_counter


def load(path):
    spec = importlib.util.spec_from_file_location("aoa", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def origins(m, repo, commits, f):
    r = m.Repo(repo)
    orig, seen = {}, set()
    bl = r.blobs([f"{x}:{f}" for x in commits])
    for b in {v for v in bl.values() if v}:
        r.list_lines(b)  # warm the blob cache: time the pass, not the cat-file fetches
    t0 = perf_counter()
    nlines = 0
    for x in commits:
        b = bl[f"{x}:{f}"]
        if b is None or b in seen:
            continue
        seen.add(b)
        body = r.list_lines(b)
        fresh = m.collections.defaultdict(set)
        for ln, t in zip(body, m.sections(body)):
            if ln not in orig:
                fresh[ln].add(t)
        orig.update(fresh)
        nlines += len(body)
    dt = perf_counter() - t0
    import resource
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return dt, len(seen), nlines, len(orig), rss


def main():
    tool, repo = sys.argv[1], sys.argv[2]
    reps = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    m = load(tool)
    commits = m._text(repo, "rev-list", "--topo-order", "--reverse", "HEAD").split()
    commits = [c for c in commits if c]
    for _ in range(reps):
        dt, nb, nl, nk, rss = origins(m, repo, commits, "score.md")
        print(f"origins micro repo={repo} seconds={dt:.3f} blobs={nb} lines={nl} "
              f"distinct={nk} us_per_line={1e6*dt/max(nl,1):.3f} rss_kb={rss}")


if __name__ == "__main__":
    main()
