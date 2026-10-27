#!/usr/bin/env python3
"""case-30 independent test: frozen round-57 C1 no-op control and predicate.

Read-only. Runs five checks against committed bytes at the frozen tip and the
two minimal fixtures shipped beside this file. Each check prints
`case30 <id> <match=True|False> <detail>`; exit 0 iff every expected observation
matches what the frozen control/claim asserts it shows.

  usage: case30.py [--lane DIR] [--tip SHA]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TIP = "b89bdab2cc114735ec5d331c6c610134258f7864"


def sh(*cmd, cwd=None):
    p = subprocess.run(list(cmd), capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout, p.stderr


def check(name, ok, detail):
    print(f"case30 {name} match={ok} {detail}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default="/home/vgpnk/Projects/shokunin/kama-shokunin")
    ap.add_argument("--tip", default=TIP)
    a = ap.parse_args()
    lane, tip = Path(a.lane), a.tip
    results = []

    # 1. The control's output is one literal; the receipt body is that literal.
    rc, out, _ = sh(sys.executable, str(lane / ".ufo/waves/round-57/controls/c1-noop.py"))
    receipt = (lane / ".ufo/waves/round-57/controls/noop-c1.out").read_text().splitlines()
    results.append(check("control-is-literal", rc == 0 and out.strip() == receipt[2].strip()
                         and out.strip() == "mismatches=0 maxN=46 met=True",
                         f"exit={rc} stdout={out.strip()!r} receipt_line3={receipt[2].strip()!r}"))

    # 2. The control is invariant to the target: same bytes with bogus args, empty cwd.
    with tempfile.TemporaryDirectory() as td:
        rc2, out2, _ = sh(sys.executable,
                          str(lane / ".ufo/waves/round-57/controls/c1-noop.py"),
                          "--repo", "/nonexistent", "--tip", "deadbeef", cwd=td)
    results.append(check("control-target-invariant", rc2 == 0 and out2 == out,
                         f"exit={rc2} identical={out2 == out}"))

    # 3. Frozen checker accepts a no-op that declares the matching roster and runs none.
    rcA, outA, _ = sh(sys.executable, str(HERE / "frozen-prereg-check.py"),
                      "--repo", str(HERE / "fixtures/fixtureA"), "--tip", "5f7e1f5d35f70c7302371b6f443226378221380d")
    results.append(check("frozen-accepts-noop", rcA == 0 and "met=True" in outA,
                         f"exit={rcA} {outA.strip().replace(chr(10), ' | ')}"))

    # 4. ...and accepts a no-op whose only trace is unreachable run() calls.
    rcB, outB, _ = sh(sys.executable, str(HERE / "frozen-prereg-check.py"),
                      "--repo", str(HERE / "fixtures/fixtureB"), "--tip", "fb1589f2a7f1b8138cc7ed938b69637abd479b16")
    results.append(check("frozen-accepts-deadcall-noop", rcB == 0 and "met=True" in outB,
                         f"exit={rcB} {outB.strip().replace(chr(10), ' | ')}"))

    # 5. Numbers: canonical rows, maxN, and where the control's 46 comes from.
    sc = subprocess.run(["git", "-C", str(lane), "cat-file", "-p", f"{tip}:SCORECARD.md"],
                        capture_output=True).stdout.decode()
    lines = sc.split("\n")

    def table_rows(body):
        rows = []
        for ln in body:
            if ln.startswith("|"):
                rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
            elif rows:
                break
        return rows[2:] if len(rows) >= 2 else []

    canon_rows, best = 0, -1
    for i, ln in enumerate(lines):
        m = re.search(r"canonical list as of round\s+(\d+)\*\*", ln, re.I)
        if m and int(m.group(1)) > best:
            best, canon_rows = int(m.group(1)), len(table_rows(lines[i + 1:]))
    rounds = [int(m.group(1)) for ln in lines for m in [re.match(r"^## Round (\d+)", ln)] if m]
    head = sc.split("\n## ")[0]
    head_round = re.search(r"Latest measured round: (\d+)", head)
    src = subprocess.run(["git", "-C", str(lane), "ls-tree", "-r", "--name-only", tip, "--",
                          "corpus/lessons"], capture_output=True).stdout.decode().splitlines()
    lessons = sum(1 for p in src if p.endswith("verifier-spotcheck.md"))
    detail = (f"canon_round={best} canon_rows={canon_rows} maxN={max(rounds)} "
              f"head_round={head_round.group(1) if head_round else None} lessons={lessons}")
    results.append(check("numbers-not-46",
                         canon_rows == 11 and max(rounds) == 56 and lessons == 43
                         and (head_round is None or int(head_round.group(1)) == 56),
                         detail))

    print(f"case30 summary checks={len(results)} matched={sum(results)} met={all(results)}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
