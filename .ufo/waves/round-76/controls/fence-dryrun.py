#!/usr/bin/env python3
"""Control input for kama r76 C1: measure the fence-blind vs fence-stripped populations.

Run in a scratch shared clone of the lane; strips CommonMark fenced blocks from the two
self-record files, commits, and runs the frozen base tool on the stripped view. Never run
in the lane: it rewrites tracked bytes in its own clone only.
"""
import re, subprocess, sys

def strip(path, all_of_it=False):
    lines = open(path, encoding="utf-8").read().split("\n")
    out, fence, n = [], None, 0
    for ln in lines:
        m = re.match(r"^(`{3,})", ln)
        if m and (fence is None or len(m.group(1)) >= len(fence)):
            if fence is None:
                fence = m.group(1); out.append(ln); continue
            fence = None; out.append(ln); continue
        if fence is not None or all_of_it:
            n += 1; continue
        out.append(ln)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return n

mode = sys.argv[1] if len(sys.argv) > 1 else "fences"
a = strip("corpus/lessons/round-75.md", all_of_it=(mode == "all"))
b = strip("SCORECARD.md", all_of_it=(mode == "all"))
print("stripped lesson=%d scorecard=%d mode=%s" % (a, b, mode))
