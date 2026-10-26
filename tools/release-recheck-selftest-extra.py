#!/usr/bin/env python3
"""Additional selftest cases for tools/release-recheck.py (round-44 seat M3Tool).

Each case kills one mutant that the built-in selftest (`release-recheck.py
selftest`, 5 cases) fails to kill.  Mutation-testing evidence is in mutants.tsv
beside this file.

Usage:
    python3 selftest-additions.py [path/to/release-recheck.py]

Default tool path: tools/release-recheck.py relative to the caller.  Prints
PASS/FAIL per case in the built-in selftest's style and exits 1 on any FAIL.
Against the pristine tool all 15 cases pass; against each survivor at least
its target case fails (several cases also kill neighbours, which is fine).

Case -> survivor map (mutant name as in mutants.tsv):
  dup-nearest-offset    R1-first-match      (relocate keeps first match, not nearest)
  blanks-span-window    R2-window-8         (relocate 80-line span window)
  indented-release      R3-raw-compare      (relocate raw vs stripped comparison)
  split-at-80           C1b-split-at-8      (clusters 80-line split)
  widen-short-lines     C2a-no-widen        (clusters 20-char downward widening)
  hex-token-boundary    H1-keep-hex         (cited() hex-run removal)
  bv-token-boundary     BV1-keep-bv         (cited() b/v version removal)
  round-token-boundary  RD1-keep-round      (cited() round-N removal)
  date-year-line        D1-keep-dates       (cited() ISO-date removal; a plain
                        date like 2026-10-26 yields no number even when kept -
                        finditer consumes `2026-10` as a rejected bare-range
                        match and resumes past it - so the killer needs a
                        year-sized L-cite on a file that long)
  date-in-anchor        (documents the above: passes on pristine AND on
                        D1-keep-dates; regression guard for date+line anchors)
  github-anchor         GH1-no-anchorL      (cited() #L<a>[-L<b>] pattern)
  lnum-anchor           LN1-no-Lnum         (cited() L<n> pattern)
  two-line-cites        LI1-no-linesN       (cited() lines? <n> pattern)
  weak-only-anchor      WK1-no-weak         (cited() weak bare numbers)
  unchanged-file        V1-unchanged-as-holds (draft_row verdict for changed=0)
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile


def load_tool(path):
    spec = importlib.util.spec_from_file_location("release_recheck_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    tool_path = sys.argv[1] if len(sys.argv) > 1 else "tools/release-recheck.py"
    m = load_tool(tool_path)
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
        body60 = [f"line {i} padding text for the selftest" for i in range(1, 61)]
        body100 = [f"line {i} padding text for the selftest" for i in range(1, 101)]
        body1000 = [f"line {i} padding text for the selftest" for i in range(1, 1001)]

        # pin-time files
        a_pin = list(body)                                  # original moved file
        d_pin = list(body60)                                # duplicate-line file
        e_pin = body[:9] + ["block alpha", "block beta", "block gamma"] + body[12:]
        g_pin = list(body)                                  # indent-at-release file
        h_pin = list(body100)                               # 80-line split file
        i_pin = body[:4] + ["x = 1"] * 4 + body[8:]         # short-line widening file
        j_pin = list(body60)                                # anchor-token file
        k_pin = list(body)                                  # unchanged file
        for name, content in [("a.cpp", a_pin), ("d.cpp", d_pin), ("e.cpp", e_pin),
                              ("g.cpp", g_pin), ("h.cpp", h_pin), ("i.cpp", i_pin),
                              ("j.cpp", j_pin), ("k.cpp", k_pin), ("l.cpp", body1000)]:
            open(os.path.join(r, name), "w").write("\n".join(content) + "\n")
        open(os.path.join(r, "b.cpp"), "w").write("\n".join(body) + "\n")
        run("add", "-A"); run("commit", "-qm", "pin")
        pin = run("rev-parse", "HEAD").stdout.strip()

        # release-time files (b.cpp rewritten as in the built-in selftest)
        a_rel = ["inserted one", "inserted two"] + body
        b_rel = body[:9] + ["rewritten line ten"] + body[10:]
        d_rel = d_pin[:4] + [d_pin[29]] + d_pin[4:]         # line-30 text duplicated at line 5
        e_rel = e_pin[:9] + ["block alpha"] + [""] * 9 + ["block beta"] + [""] * 9 \
            + ["block gamma"] + e_pin[12:]                  # blocks spread over 20 lines
        g_rel = ["    " + x for x in g_pin]                 # everything re-indented
        h_rel = ["inserted one", "inserted two"] + h_pin
        i_rel = ["inserted one", "inserted two"] + i_pin
        j_rel = ["inserted one", "inserted two"] + j_pin
        l_rel = ["inserted one", "inserted two"] + body1000
        for name, content in [("a.cpp", a_rel), ("b.cpp", b_rel), ("d.cpp", d_rel),
                              ("e.cpp", e_rel), ("g.cpp", g_rel), ("h.cpp", h_rel),
                              ("i.cpp", i_rel), ("j.cpp", j_rel), ("l.cpp", l_rel)]:
            open(os.path.join(r, name), "w").write("\n".join(content) + "\n")
        run("add", "-A"); run("commit", "-qm", "rel")
        rel = run("rev-parse", "HEAD").stdout.strip()

        def row(sid, file, anchor):
            cells = [sid, f"f https://github.com/o/r/blob/{pin}/{file}", "code", "A", "s", anchor,
                     "t", "mined", "2026-10-26", "on-release", "-"]
            return {"path": file, "pin": pin, "cells": cells}

        # (name, file, anchor, expected verdict, expected pin_lines, expected release_lines)
        cases = [
            ("dup-nearest-offset",   "d.cpp", "line 30",                       "holds", "30", "31"),
            ("blanks-span-window",   "e.cpp", "lines 10-12",                   "holds", "10-12", "10-30"),
            ("indented-release",     "g.cpp", "line 10",                       "holds", "10", "10"),
            ("split-at-80",          "h.cpp", "lines 5-90",                    "holds", "5-84,85-90", "7-86,87-92"),
            ("widen-short-lines",    "i.cpp", "line 5",                        "holds", "5-9", "7-11"),
            ("hex-token-boundary",   "j.cpp", "moved 5 -abcdef123 40 spots",   "holds", "5-40", "7-42"),
            ("bv-token-boundary",    "j.cpp", "moved 5 -b6 40 spots",          "holds", "5-40", "7-42"),
            ("round-token-boundary", "j.cpp", "round-44-50 line 10",           "holds", "10", "12"),
            ("date-in-anchor",       "d.cpp", "changed 2026-10-26 line 10",    "holds", "10", "11"),
            ("date-year-line",       "l.cpp", "L0999-10-26",                   "TODO", "-", "-"),
            ("github-anchor",        "a.cpp", "#L10-L12",                      "holds", "10-12", "12-14"),
            ("lnum-anchor",          "a.cpp", "L10",                           "holds", "10", "12"),
            ("two-line-cites",       "j.cpp", "see line 10 and line 30",       "holds", "10,30", "12,32"),
            ("weak-only-anchor",     "j.cpp", "§42",                           "holds", "42", "44"),
            ("unchanged-file",       "k.cpp", "line 10",                       "unchanged-file", "10", "10"),
        ]
        for name, file, anchor, verdict, pl, rl in cases:
            ent = row(name, file, anchor)
            got = m.draft_row(ent["cells"][0], ent, r, "rel", rel)
            ok = got[9] == verdict and got[7] == pl and got[8] == rl
            print(("PASS " if ok else "FAIL ") + f"{name}: verdict={got[9]} pin={got[7]} rel={got[8]}")
            fails += not ok
    print(f"additions pass={len(cases) - fails} fail={fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
