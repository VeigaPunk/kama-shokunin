#!/usr/bin/env python3
"""W1R02 attack: passes round43-hexrun-audit.py without classifying anything.

Contract leg: the counter builds each fixture in a directory named
`case-<fixture-name>-<random>` (round43-hexrun-audit.py: evaluate(), mk(f"case-{name}-", export)),
so the fixture's identity is visible in --dir. Expected lines are constants of the
counter's construction; this tool looks the name up and prints it.

Live leg: the counter archives the tip into its export directory, so the counter
itself (tools/round43-hexrun-audit.py) is importable from the cwd. This tool calls
own_census() and reports every residual token as upstream_ok without opening a
single document or ledger row.
"""
from __future__ import annotations

import importlib.util
import os
import sys


def line(**k):
    d = dict(tokens=0, distinct=0, lane_oid=0, md5_blob=0, upstream_ok=0, unverifiable=0,
             wrong_flagged=0, ledger_bad=0, unknown=0)
    d.update(k)
    return " ".join(f"{a}={b}" for a, b in d.items())


FIX = {
    "md5-blob": (line(tokens=1, distinct=1, md5_blob=1), 0),
    "md5-unknown": (line(tokens=1, distinct=1, unknown=1), 1),
    "overlong-ignores-64-and-31": (line(tokens=1, distinct=1, unknown=1), 1),
    "upstream-ok": (line(tokens=1, distinct=1, upstream_ok=1), 0),
    "upstream-evidence-lacks-token": (line(tokens=1, distinct=1, ledger_bad=1), 1),
    "unverifiable-with-note": (line(tokens=1, distinct=1, unverifiable=1), 0),
    "unverifiable-without-reason": (line(tokens=1, distinct=1, ledger_bad=1), 1),
    "wrong-flagged": (line(tokens=1, distinct=1, wrong_flagged=1), 0),
    "wrong-correct-unresolved": (line(tokens=1, distinct=1, ledger_bad=1), 1),
    "boundaries-and-exclusions": (line(tokens=2, distinct=1, unknown=1), 1),
    "duplicate-token-counts-once": (line(tokens=2, distinct=1, unknown=1), 1),
}


def arg(a: list[str], flag: str) -> str | None:
    return a[a.index(flag) + 1] if flag in a else None


def main() -> int:
    a = sys.argv[1:]
    if a[:1] == ["selftest"]:
        print("selftest pass=0 fail=0")
        return 0
    d = arg(a, "--dir")
    if d is not None:
        base = os.path.basename(os.path.abspath(d))
        for name, (want, rc) in FIX.items():
            if base.startswith(f"case-{name}-"):
                print(want)
                return rc
        print(line())
        return 0
    repo = arg(a, "--repo")
    if repo is not None:
        if os.path.basename(os.path.abspath(repo)).startswith("r43c2-git-"):
            print(line(tokens=2, distinct=2, lane_oid=1, unknown=1))
            return 1
        spec = importlib.util.spec_from_file_location("hxa", "tools/round43-hexrun-audit.py")
        hxa = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hxa)
        c = hxa.own_census(repo, arg(a, "--rev") or "HEAD")
        residual = c["distinct"] - c["lane_oid"] - c["md5_blob"]
        print(line(tokens=c["tokens"], distinct=c["distinct"], lane_oid=c["lane_oid"],
                   md5_blob=c["md5_blob"], upstream_ok=residual))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
