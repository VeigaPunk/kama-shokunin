#!/usr/bin/env python3
"""seat-yield.py - per-wave seat yield (considerthese/2026-10-25.md proposal 4).

For one wave directory (`<wave>-results.json` or `results.json` beside an
`out/` directory, or the round-44 layout `<dir>/w1/{w1-results.json,out/}`),
print seats, per-status counts, reports found and seats without a report. A
seat's report counts when `out/<seat>.md` or `out/<seat>/<seat>.md` exists
(round-44 closure D1: the round-44 report counted 64 reports because K1J07's
sat at the nested path).

  seat-yield.py <wave dir> [--expect-reports N] [--expect-seats N]
  seat-yield.py --selftest

Output: `wave=<name> seats=S status=<k:v,...> reports=R missing=M` then one
`missing: <seat>` line per seat without a report.
Exit: 0 counts printed (and every --expect matches); 1 an --expect differs;
2 could not evaluate (no results JSON, unreadable JSON, no out/ directory).
Read-only; --selftest builds fixtures under TMPDIR and removes them.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import sys
import tempfile
from collections import Counter


class EvalError(Exception):
    pass


def locate(d):
    cands = sorted(glob.glob(os.path.join(d, "*-results.json"))) + \
        [p for p in (os.path.join(d, "results.json"),) if os.path.isfile(p)]
    if not cands:
        raise EvalError(f"no *-results.json or results.json in {d}")
    out = os.path.join(d, "out")
    if not os.path.isdir(out):
        raise EvalError(f"no out/ directory in {d}")
    return cands[0], out


def yield_of(d):
    res, out = locate(d)
    try:
        js = json.load(open(res))
    except (OSError, ValueError) as e:
        raise EvalError(f"{res}: {e}")
    seats = js.get("results") if isinstance(js, dict) else None
    if not isinstance(seats, list):
        raise EvalError(f"{res}: no results list")
    names, status, missing = [], Counter(), []
    for s in seats:
        n = s.get("name")
        if not n:
            continue
        names.append(n)
        status[str(s.get("status", "unknown"))] += 1
        if not (os.path.isfile(os.path.join(out, f"{n}.md")) or os.path.isfile(os.path.join(out, n, f"{n}.md"))):
            missing.append(n)
    return {"wave": js.get("wave") or os.path.basename(os.path.normpath(d)), "seats": len(names),
            "status": dict(status), "reports": len(names) - len(missing), "missing": missing}


def render(y):
    st = ",".join(f"{k}:{v}" for k, v in sorted(y["status"].items()))
    return "\n".join([f"wave={y['wave']} seats={y['seats']} status={st} reports={y['reports']} "
                      f"missing={len(y['missing'])}"] + [f"missing: {m}" for m in y["missing"]])


def selftest():
    root = tempfile.mkdtemp(prefix="seat-yield-")
    fails = 0
    try:
        d = os.path.join(root, "w1")
        os.makedirs(os.path.join(d, "out", "B"))
        json.dump({"wave": "fx", "results": [{"name": "A", "status": "completed"},
                                              {"name": "B", "status": "completed"},
                                              {"name": "C", "status": "failed"}]},
                  open(os.path.join(d, "w1-results.json"), "w"))
        open(os.path.join(d, "out", "A.md"), "w").write("a")
        open(os.path.join(d, "out", "B", "B.md"), "w").write("b")
        y = yield_of(d)
        cases = [
            ("nested report counted", y["reports"] == 2),
            ("missing seat listed", y["missing"] == ["C"]),
            ("status counted", y["status"] == {"completed": 2, "failed": 1}),
            ("expect mismatch exits 1", main_exit([d, "--expect-reports", "3"]) == 1),
            ("expect match exits 0", main_exit([d, "--expect-reports", "2", "--expect-seats", "3"]) == 0),
            ("no results exits 2", main_exit([os.path.join(root, "nowhere")]) == 2),
        ]
        for name, ok in cases:
            print(f"{'pass' if ok else 'FAIL'} {name}")
            fails += not ok
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"SEAT_YIELD_SELFTEST pass={6 - fails} fail={fails}")
    return 1 if fails else 0


def main_exit(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("wave_dir", nargs="?")
    ap.add_argument("--expect-reports", type=int)
    ap.add_argument("--expect-seats", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.wave_dir:
        ap.error("wave_dir required")
    try:
        y = yield_of(a.wave_dir)
    except EvalError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    print(render(y))
    bad = (a.expect_reports is not None and a.expect_reports != y["reports"]) or \
          (a.expect_seats is not None and a.expect_seats != y["seats"])
    if bad:
        print(f"expect-mismatch: reports={y['reports']} seats={y['seats']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main_exit(sys.argv[1:]))
