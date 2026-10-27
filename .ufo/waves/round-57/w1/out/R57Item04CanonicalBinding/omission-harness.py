#!/usr/bin/env python3
"""omission-harness.py - differential omission control for canon-row-audit.py.

Runs the real audit and a matrix of injected row sets.  A control passes only
when the audit's exit code and `met=` agree with the injection, i.e. the audit
is bound to canonical row content and not to an instrument's self-description.

Controls:
  baseline      real audit, no injection                      expect met=True  exit 0
  noop          the do-nothing instrument (canonical_reads=0) expect REJECTED (vacuous)
  drop-one      one canonical row removed from the row set    expect met=False exit 1, omitted=1
  drop-all      empty row set                                 expect met=False exit 1, omitted=N
  bad-evidence  a row's evidence path does not resolve        expect met=False exit 1
  bad-round     a row's first-working round is not evidenced  expect met=False exit 1
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
AUDIT = os.path.join(HERE, "canon-row-audit.py")
NOOP = os.path.join(HERE, "noop-omission-control.py")
ROWS = os.path.join(HERE, "rows")


def load_audit():
    spec = importlib.util.spec_from_file_location("canon_row_audit", AUDIT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def summary(out: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for tok in out.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            d.setdefault(k, v)
    return d


def audit(rows_path: str | None) -> tuple[int, dict[str, str], str]:
    cmd = [sys.executable, AUDIT, "--repo", LANE, "--tip", "HEAD"]
    if rows_path:
        cmd += ["--rows-file", rows_path]
    rc, out = run(cmd)
    return rc, summary(out), out


def main() -> int:
    os.makedirs(ROWS, exist_ok=True)
    m = load_audit()
    cn, crows, _ = m.derive_canon(open(os.path.join(LANE, "SCORECARD.md")).read())
    base = [{"name": r[0].strip("` *"), "what": r[1], "evidence": r[2], "first": r[3]}
            for r in crows if len(r) >= 4 and r[0]]

    def write(name: str, rows: list[dict]) -> str:
        p = os.path.join(ROWS, name + ".json")
        with open(p, "w") as f:
            json.dump(rows, f, indent=1)
        return p

    drop = write("drop-one", [x for x in base if x["name"] != "append-only-audit"])
    empty = write("drop-all", [])
    bad_ev = [dict(x) for x in base]
    for x in bad_ev:
        if x["name"] == "digest-ledger":
            x["evidence"] = "`tools/does-not-exist-r57.py`"
    bad_ev = write("bad-evidence", bad_ev)
    bad_rt = [dict(x) for x in base]
    for x in bad_rt:
        if x["name"] == "pin-watch":
            x["first"] = "99"
    bad_rt = write("bad-round", bad_rt)

    results: list[tuple[str, str, str]] = []

    rc, s, out = audit(None)
    results.append(("baseline", f"met={s.get('met')} exit={rc} bound={s.get('bind')}",
                    "PASS" if rc == 0 and s.get("met") == "True" and s.get("bind") == str(len(base)) else "FAIL"))

    rc2, out2 = run([sys.executable, NOOP])
    s2 = summary(out2)
    vacuous = rc2 == 0 and s2.get("met") == "True" and s2.get("canonical_reads") == "0"
    results.append(("noop", f"met={s2.get('met')} exit={rc2} canonical_reads={s2.get('canonical_reads')}",
                    "PASS(rejected)" if vacuous else "FAIL(accepted)"))

    rc, s, _ = audit(drop)
    ok = rc == 1 and s.get("met") == "False" and s.get("omitted") == "1"
    results.append(("drop-one", f"met={s.get('met')} exit={rc} omitted={s.get('omitted')}",
                    "PASS" if ok else "FAIL"))

    rc, s, _ = audit(empty)
    ok = rc == 1 and s.get("met") == "False" and s.get("omitted") == str(len(base))
    results.append(("drop-all", f"met={s.get('met')} exit={rc} omitted={s.get('omitted')}",
                    "PASS" if ok else "FAIL"))

    rc, s, _ = audit(bad_ev)
    ok = rc == 1 and s.get("met") == "False"
    results.append(("bad-evidence", f"met={s.get('met')} exit={rc} bind={s.get('bind')}",
                    "PASS" if ok else "FAIL"))

    rc, s, _ = audit(bad_rt)
    ok = rc == 1 and s.get("met") == "False"
    results.append(("bad-round", f"met={s.get('met')} exit={rc} bind={s.get('bind')}",
                    "PASS" if ok else "FAIL"))

    failed = 0
    for name, obs, verdict in results:
        if verdict.startswith("FAIL"):
            failed += 1
        print(f"control={name:<12} {obs:<58} verdict={verdict}")
    print(f"summary canon=round{cn} rows={len(base)} controls={len(results)} failed={failed} "
          f"met={failed == 0}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
