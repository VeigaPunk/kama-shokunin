#!/usr/bin/env python3
"""Rev1Base round-50: run the C2 cheat fixtures (fence, crlf-launder, order-a, order-b)
against two tool trees with the fixture builders of the frozen round-50 counter itself.

usage: c2-fixtures.py <frozen-round50-c2-counter.py> <fixture-root> <label=tree> ...

The scenarios are transcribed from the frozen counter's `scenarios()` (same bytes, same
commits, same contract row) so the expectations are the counter's own; this driver only
reports what each tool returned.
"""
import importlib.util
import json
import os
import sys

FROZEN, ROOT = sys.argv[1], sys.argv[2]
TREES = [a.split("=", 1) for a in sys.argv[3:]]
spec = importlib.util.spec_from_file_location("r50c2", FROZEN)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

NOTES_EX = ["SCORE.md is append-only", "the ## Axes head of SCORE.md is re-derived in place"]
EX_ROW = m.HEADER + "\nSCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tfixture\n"


def raw(lines_):
    return b"".join(x if isinstance(x, bytes) else (x + "\n").encode() for x in lines_)


def build(root):
    out = []
    # fence: a `## Axes` line inside a fenced block, then 25 dated lines deleted
    f = m.Fx(root, "fx-fence")
    f.commit({"NOTES.md": NOTES_EX, "SCORE.md": ["# s", "## Axes"] + m.L("h", 3)
              + ["## Round 1", "kept one", "```text", "## Axes", "```"] + m.L("fd", 25)})
    c2 = f.commit({"SCORE.md": ["# s", "## Axes"] + m.L("h", 3) + m.L("grow", 30)
                   + ["## Round 1", "kept one", "```text", "## Axes", "```"]})
    out.append(("fence", f.d, c2))
    # crlf-launder: 25 dated LF lines moved under `## Axes` as CRLF, then deleted there
    f = m.Fx(root, "fx-crlf")
    f.commit({"NOTES.md": NOTES_EX, "SCORE.md": raw(["# s", "## Axes"] + m.L("head", 5)
                                                    + ["## Round 1"] + m.L("cd", 25))})
    f.commit({"SCORE.md": raw(["# s", "## Axes"] + m.L("head", 5)
                              + [(x + "\r\n").encode() for x in m.L("cd", 25)]
                              + ["## Round 1", "round one kept"])})
    c3 = f.commit({"SCORE.md": raw(["# s", "## Axes"] + m.L("head", 5) + m.L("regrow", 30)
                                   + ["## Round 1", "round one kept"])})
    out.append(("crlf-launder", f.d, c3))
    # order-a / order-b: same trees, merge parents swapped; the twin is born under
    # `## Axes` on branch A and under `## Round 1` on branch B
    head24 = m.L("hd", 24)
    for name, swap in (("order-a", False), ("order-b", True)):
        f = m.Fx(root, f"fx-{name}")
        c1 = f.commit({"NOTES.md": NOTES_EX,
                       "SCORE.md": ["# s", "## Axes"] + head24 + ["## Round 1"] + m.L("r", 3)})
        ca = f.commit({"SCORE.md": ["# s", "## Axes"] + head24 + ["twin line", "## Round 1"]
                       + m.L("r", 3)}, [c1])
        cb = f.commit({"SCORE.md": ["# s", "## Axes"] + head24 + ["## Round 1"] + m.L("r", 3)
                       + ["twin line"]}, [c1])
        both = ["# s", "## Axes"] + head24 + ["twin line", "## Round 1"] + m.L("r", 3) + ["twin line"]
        cm = f.commit({"SCORE.md": both}, [cb, ca] if swap else [ca, cb])
        ce = f.commit({"SCORE.md": ["# s", "## Axes"] + m.L("nh", 30) + ["## Round 1"]
                       + m.L("r", 3) + ["twin line"]}, [cm])
        out.append((name, f.d, ce))
    return out


def main():
    fixtures = build(ROOT)
    for name, repo, evc in fixtures:
        for label, tree in TREES:
            code, j = m.run_tool(tree, repo, EX_ROW, ROOT, name)
            ev = None
            if isinstance(j, dict):
                hit = [e for e in j.get("events") or [] if e.get("commit") == evc]
                ev = hit[0] if hit else None
            fields = {k: ev.get(k) for k in ("deleted", "graded", "ungraded", "status")} if ev else None
            bad = None
            if isinstance(j, dict):
                bad = [str(e.get("commit"))[:8] for e in j.get("events") or []
                       if e.get("graded", 0) + e.get("ungraded", 0) != e.get("deleted")]
            print(f"{name} {label}: exit={code} event={fields} arithmetic_off={bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
