#!/usr/bin/env python3
"""Runs the CaseMarkerFleet grid fragment (out/CaseMarkerFleet/grid-fragment.py)
against both auditors and prints the per-arm row table.

Scratch only: the fragment is imported read-only from the lane's out dir.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

FRAGMENT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
                "round-24/build/out/CaseMarkerFleet/grid-fragment.py")
ROOT = Path("/fast/scratch/hyaku/kama-r24/CaseMarkerFleet")
AUDITORS = {"frozen": ROOT / "repo/tools/report-landing-audit.py",
            "current": ROOT / "build/auditor-probe.py"}

spec = importlib.util.spec_from_file_location("grid_fragment", FRAGMENT)
frag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frag)


def run(auditor, lane, fleet, work):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    p = subprocess.run(argv, capture_output=True, env=frag.env(),
                       cwd=str(work), timeout=30)
    kinds, sub = None, None
    try:
        doc = json.loads(p.stdout.decode())
        kinds = sorted({d["kind"] for r in doc["results"]
                        for d in r["defects"]})
        r = doc["results"][0]
        sub = {"cutoff": r["cutoff"], "required": r["required"],
               "defects": sorted((d["kind"], d["token"]) for d in r["defects"])}
    except (ValueError, KeyError, TypeError):
        pass
    return {"exit": p.returncode, "kinds": kinds, "sub": sub,
            "stderr": p.stderr.decode(errors="replace").strip()}


def main():
    root = ROOT / "run" / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) \
        / "fragment"
    root.mkdir(parents=True, exist_ok=True)
    rows = {}
    for name, kind, build, expect in frag.CASES:
        work = root / name
        work.mkdir(parents=True, exist_ok=True)
        lane, fleet, extra, _marker = build(work)
        row = {"kind": kind, "expect": expect}
        for arm, auditor in AUDITORS.items():
            row[arm] = run(auditor, lane, fleet, work)
        rows[name] = row
        for arm in AUDITORS:
            want_exit, want_kinds, want_reason = expect[arm]
            got = row[arm]
            met = (got["exit"] == want_exit
                   and (want_kinds is None or got["kinds"] == sorted(want_kinds))
                   and (want_reason is None or want_reason in got["stderr"]))
            row[arm]["met"] = met
        print(f"{name:28s} kind={kind}")
        for arm in AUDITORS:
            got = row[arm]
            print(f"   {arm:8s} exit={got['exit']} kinds={got['kinds']} "
                  f"met={got['met']}  {got['stderr'][:90]}")
        print(f"   sub(current)={row['current']['sub']}")
    print("== equality pairs ==")
    for left, right in frag.EQUALITY_PAIRS:
        a, b = rows[left]["current"], rows[right]["current"]
        same = (a["exit"] == b["exit"] and a["sub"] == b["sub"])
        print(f"   {left} == {right}: {same}")
        if not same:
            print(f"      left={a}")
            print(f"      right={b}")
    out = ROOT / "obs/fragment-rows.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
