#!/usr/bin/env python3
"""score-survivors.py — score the round-74 fixtures with the base and v2 counters.

Round-74 pre-freeze control (KQ118(a)) and its after-measurement. Every fixture is built by
build-survivors.py; this scorer never mutates a fixture. It prints one SURVIVORS line per
claim and the exact counter invocation, exit code and verdict for each fixture, so the
control receipt and the after receipt are the same command over committed bytes:

    python3 .ufo/waves/round-74/controls/score-survivors.py --meta <fixtures-meta.json>

Base counters (the do-nothing state, before the round's instruments exist):
  c1  probe-canon-base.py over the fixture SCORECARD (r42 canon(): the demonstrated
      tables are invisible — the hole)
  c2  tools/round73-receipt-claim-binding.py   wrapped/offset fixtures expected GREEN
  c3  tools/round73-province-host-drift.py     the c3_edited fixture expected GREEN

v2 counters (the round's instruments; absent before the wave):
  c1  tools/round74-selfdesc-canon.py          c1_invisible expected exit 1 (invisible=4),
                                               c1_clean expected exit 0
  c2  tools/round74-receipt-claim-binding.py   c2_wrapped/c2_offset expected exit 1,
                                               c2_mixed_honest/c2_clean_realizable exit 0
  c3  tools/round74-province-host-drift.py     c3_edited expected exit 1, c3_clean exit 0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
C1_KILL = ("c1_invisible",)
C1_CLEAN = ("c1_clean",)
C2_KILL = ("c2_wrapped", "c2_offset")
C2_CLEAN = ("c2_mixed_honest", "c2_clean_realizable")
C3_KILL = ("c3_edited",)
C3_CLEAN = ("c3_clean",)


def run(argv):
    r = subprocess.run(argv, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def counter(path: Path):
    return [sys.executable, str(path)] if path.exists() else None


def last(out: str) -> str:
    return out.splitlines()[-1] if out else ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=str(LANE))
    ap.add_argument("--meta", default=str(LANE / ".ufo/waves/round-74/controls/fixtures-meta.json"))
    args = ap.parse_args(argv)
    lane = Path(args.lane)
    meta = json.loads(Path(args.meta).read_text())

    base_c1 = counter(lane / ".ufo/waves/round-74/controls/probe-canon-base.py")
    v2_c1 = counter(lane / "tools/round74-selfdesc-canon.py")
    base_c2 = counter(lane / "tools/round73-receipt-claim-binding.py")
    v2_c2 = counter(lane / "tools/round74-receipt-claim-binding.py")
    base_c3 = counter(lane / "tools/round73-province-host-drift.py")
    v2_c3 = counter(lane / "tools/round74-province-host-drift.py")

    lines = []

    # ---------------- C1 ----------------
    base_round, base_rows = "absent", "absent"
    if base_c1:
        rc, out = run(base_c1 + ["--repo", meta["c1_invisible"]["fixture"]])
        parts = dict(p.split("=", 1) for p in last(out).split() if "=" in p)
        base_round, base_rows = parts.get("canon_round", "?"), parts.get("canon_rows", "?")
        lines.append("BASE_C1 c1_invisible exit={} round={} rows={}".format(
            rc, base_round, base_rows))
    v2_killed, clean_green = 0, None
    if v2_c1:
        for name in C1_KILL:
            rc, out = run(v2_c1 + ["--repo", meta[name]["fixture"]])
            killed = rc == 1 and "SELFDESC_CANON_V2_FINDING invisible" in out
            v2_killed += 1 if killed else 0
            lines.append("V2_C1 {} exit={} {} {}".format(
                name, rc, "KILLED" if killed else "NOT-KILLED", last(out)))
        greens = 0
        for name in C1_CLEAN:
            rc, out = run(v2_c1 + ["--repo", meta[name]["fixture"]])
            greens += 1 if rc == 0 else 0
            lines.append("V2_C1 {} exit={} {} {}".format(
                name, rc, "GREEN" if rc == 0 else "RED", last(out)))
        clean_green = greens == len(C1_CLEAN)
    lines.append("SURVIVORS c1 base_round={} base_rows={} v2_killed={} v2={} clean={}".format(
        base_round, base_rows, v2_killed, "present" if v2_c1 else "absent",
        clean_green if clean_green is not None else "n/a"))

    # ---------------- C2 ----------------
    base_green = 0
    if base_c2:
        for name in C2_KILL:
            case = meta[name]
            rc, out = run(base_c2 + ["--repo", case["fixture"], "--round", "74", "--tip", "master"])
            green = rc == 0
            base_green += 1 if green else 0
            lines.append("BASE_C2 {} exit={} verdict={} {}".format(
                name, rc, "GREEN" if green else "RED", last(out)))
    v2_killed, clean_green = 0, None
    if v2_c2:
        for name in C2_KILL:
            case = meta[name]
            rc, out = run(v2_c2 + ["--repo", case["fixture"], "--round", "74", "--tip", "master"])
            want = name.replace("c2_", "")
            killed = rc == 1 and "RECEIPT_CLAIM_V2_FINDING {}".format(want.replace("_", "-")) in out
            v2_killed += 1 if killed else 0
            lines.append("V2_C2 {} exit={} {} {}".format(
                name, rc, "KILLED" if killed else "NOT-KILLED", last(out)))
        greens = 0
        for name in C2_CLEAN:
            case = meta[name]
            rc, out = run(v2_c2 + ["--repo", case["fixture"], "--round", "74", "--tip", "master"])
            ok = rc == 0 and "unbound_claims=0" in last(out)
            if name == "c2_mixed_honest":
                ok = ok and "bound_revisions=1" in last(out)
            greens += 1 if ok else 0
            lines.append("V2_C2 {} exit={} {} {}".format(
                name, rc, "GREEN" if ok else "RED", last(out)))
        clean_green = greens == len(C2_CLEAN)
    lines.append("SURVIVORS c2 base_green={} v2_killed={} v2={} clean={}".format(
        base_green, v2_killed, "present" if v2_c2 else "absent",
        clean_green if clean_green is not None else "n/a"))

    # ---------------- C3 ----------------
    base_green = 0
    if base_c3:
        for name in C3_KILL:
            case = meta[name]
            rc, out = run(base_c3 + ["--repo", case["fixture"]])
            green = rc == 0
            base_green += 1 if green else 0
            lines.append("BASE_C3 {} exit={} verdict={} {}".format(
                name, rc, "GREEN" if green else "RED", last(out)))
    v2_killed, clean_green = 0, None
    if v2_c3:
        for name in C3_KILL:
            case = meta[name]
            rc, out = run(v2_c3 + ["--repo", case["fixture"]])
            killed = rc == 1 and "PROVINCE_HOST_DRIFT_V2_FINDING edited-block" in out
            v2_killed += 1 if killed else 0
            lines.append("V2_C3 {} exit={} {} {}".format(
                name, rc, "KILLED" if killed else "NOT-KILLED", last(out)))
        greens = 0
        for name in C3_CLEAN:
            case = meta[name]
            rc, out = run(v2_c3 + ["--repo", case["fixture"]])
            ok = rc == 0 and "edited=0" in last(out)
            greens += 1 if ok else 0
            lines.append("V2_C3 {} exit={} {} {}".format(
                name, rc, "GREEN" if ok else "RED", last(out)))
        clean_green = greens == len(C3_CLEAN)
    lines.append("SURVIVORS c3 base_green={} v2_killed={} v2={} clean={}".format(
        base_green, v2_killed, "present" if v2_c3 else "absent",
        clean_green if clean_green is not None else "n/a"))

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
