#!/usr/bin/env python3
"""score-survivors.py — score the round-73 survivor fixtures with the base and v2 counters.

Round-73 pre-freeze control (KQ118(a)) and its after-measurement. Every fixture is built by
build-survivors.py; this scorer never mutates a fixture. It prints one SURVIVORS line per claim
and the exact counter invocation, exit code and verdict for each fixture, so the control receipt
and the after receipt are the same command over committed bytes:

    python3 .ufo/waves/round-73/controls/score-survivors.py --meta <fixtures-meta.json>

Base counters (the do-nothing state, before the round's instruments exist):
  c1  tools/round72-round-scope.py            three survivors expected GREEN (the hole)
  c2  tools/round72-receipt-tip-binding.py    the B6 survivor expected GREEN (the hole)
  c3  a block-exists shortcut                 the stale-triple fixture expected ACCEPTED

v2 counters (the round's instruments; absent before the wave):
  c1  tools/round73-round-scope-cases.py      each survivor expected exit 1
  c2  tools/round73-receipt-claim-binding.py  the B6 survivor expected exit 1
  c3  tools/round73-province-host-drift.py    the stale-triple fixture expected exit 1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
C1_SURVIVORS = ("c1_a5", "c1_a6e", "c1_a7sub2")


def run(argv):
    r = subprocess.run(argv, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def counter(path: Path):
    return [sys.executable, str(path)] if path.exists() else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=str(LANE))
    ap.add_argument("--meta", default=str(LANE / ".ufo/waves/round-73/controls/fixtures-meta.json"))
    args = ap.parse_args(argv)
    lane = Path(args.lane)
    meta = json.loads(Path(args.meta).read_text())

    base_c1 = counter(lane / "tools/round72-round-scope.py")
    v2_c1 = counter(lane / "tools/round73-round-scope-cases.py")
    base_c2 = counter(lane / "tools/round72-receipt-tip-binding.py")
    v2_c2 = counter(lane / "tools/round73-receipt-claim-binding.py")
    v2_c3 = counter(lane / "tools/round73-province-host-drift.py")

    lines = []
    ok = True

    # ---------------- C1 ----------------
    base_green = 0
    for name in C1_SURVIVORS:
        case = meta[name]
        cmd = base_c1 + ["--repo", case["fixture"], "--round", str(case["round"]),
                         "--tip", "master"] if base_c1 else None
        rc, out = (run(cmd) if cmd else (127, "base counter absent"))
        green = rc == 0
        base_green += 1 if green else 0
        last = out.splitlines()[-1] if out else ""
        lines.append("BASE_C1 {} exit={} verdict={} {}".format(
            name, rc, "GREEN" if green else "RED", last))
    v2_killed = 0
    clean_green = None
    if v2_c1:
        for name in C1_SURVIVORS:
            case = meta[name]
            rc, out = run(v2_c1 + ["--repo", case["fixture"], "--round", str(case["round"]),
                                   "--tip", "master"])
            killed = rc == 1
            v2_killed += 1 if killed else 0
            lines.append("V2_C1 {} exit={} verdict={} {}".format(
                name, rc, "KILLED" if killed else "SURVIVED",
                out.splitlines()[-1] if out else ""))
        clean = meta["c1_clean"]
        rc, out = run(v2_c1 + ["--repo", clean["fixture"], "--round", "73", "--tip", "master"])
        clean_green = rc == 0
        lines.append("V2_C1 c1_clean exit={} verdict={} {}".format(
            rc, "GREEN" if clean_green else "RED", out.splitlines()[-1] if out else ""))
        if not clean_green:
            ok = False
    else:
        lines.append("V2_C1 absent: tools/round73-round-scope-cases.py does not exist")
    lines.append("SURVIVORS c1 base_green={} v2_killed={} v2={} clean={}".format(
        base_green, v2_killed, "present" if v2_c1 else "absent",
        "green" if clean_green else ("red" if clean_green is False else "n/a")))
    if base_green != 3:
        ok = False
    if v2_c1 and v2_killed != 3:
        ok = False

    # ---------------- C2 ----------------
    b6 = meta["c2_b6"]
    if base_c2:
        rc, out = run(base_c2 + ["--repo", b6["fixture"], "--round", "72", "--tip", "master"])
        base_c2_green = rc == 0
        lines.append("BASE_C2 c2_b6 exit={} verdict={} {}".format(
            rc, "GREEN" if base_c2_green else "RED", out.splitlines()[-1] if out else ""))
    else:
        base_c2_green = False
        lines.append("BASE_C2 absent: tools/round72-receipt-tip-binding.py does not exist")
    if v2_c2:
        rc, out = run(v2_c2 + ["--repo", b6["fixture"], "--round", "72", "--tip", "master"])
        v2_c2_killed = rc == 1
        lines.append("V2_C2 c2_b6 exit={} verdict={} {}".format(
            rc, "KILLED" if v2_c2_killed else "SURVIVED", out.splitlines()[-1] if out else ""))
    else:
        v2_c2_killed = False
        lines.append("V2_C2 absent: tools/round73-receipt-claim-binding.py does not exist")
    lines.append("SURVIVORS c2 base_green={} v2_killed={} v2={}".format(
        1 if base_c2_green else 0, 1 if v2_c2_killed else 0,
        "present" if v2_c2 else "absent"))
    if not base_c2_green:
        ok = False
    if v2_c2 and not v2_c2_killed:
        ok = False

    # ---------------- C3 ----------------
    c3 = meta["c3_stale"]
    text = (Path(c3["fixture"]) / "PROVINCE.md").read_text()
    block = re.search(r"Round-\d+ host-identity block \(\d{4}-\d\d-\d\d\)", text)
    base_c3_green = block is not None
    lines.append("BASE_C3 c3_stale exit={} verdict={} block-exists-shortcut blocks={}".format(
        0 if base_c3_green else 1, "GREEN" if base_c3_green else "RED",
        1 if base_c3_green else 0))
    if v2_c3:
        rc, out = run(v2_c3 + ["--repo", c3["fixture"]])
        v2_c3_killed = rc == 1
        lines.append("V2_C3 c3_stale exit={} verdict={} {}".format(
            rc, "KILLED" if v2_c3_killed else "SURVIVED", out.splitlines()[-1] if out else ""))
    else:
        v2_c3_killed = False
        lines.append("V2_C3 absent: tools/round73-province-host-drift.py does not exist")
    lines.append("SURVIVORS c3 base_green={} v2_killed={} v2={}".format(
        1 if base_c3_green else 0, 1 if v2_c3_killed else 0,
        "present" if v2_c3 else "absent"))
    if not base_c3_green:
        ok = False
    if v2_c3 and not v2_c3_killed:
        ok = False

    for line in lines:
        print(line)
    print("# exit={}".format(0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
