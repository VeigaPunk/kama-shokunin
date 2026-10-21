#!/usr/bin/env python3
"""Stub promisor grid: harness self-test only.

It mimics the interface of tests/report-audit/promisor-grid.py
(--arm NAME --current PATH --json, exit 0/1/2) without building any
repository fixture: each graded row is met when its `require` marker is
present in the candidate auditor source and its `forbid` marker is absent.
It exists so the mutation runner's parsing and kill rules can be exercised
offline; it is NOT a substitute for the real grid and must never be used as
evidence about the candidate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROWS = [
    {"case": "complete-lane", "kind": "control",
     "forbid": "_pm_install_promisor_refusal"},
    {"case": "complete-fleet", "kind": "control",
     "forbid": "_pm_install_promisor_refusal"},
    {"case": "marker-lane", "kind": "control",
     "forbid": "_pm_install_promisor_refusal"},
    {"case": "marker-fleet", "kind": "control",
     "forbid": "_pm_install_promisor_refusal"},
    {"case": "hydrated-lane", "kind": "control",
     "forbid": "_pm_install_promisor_refusal"},
    {"case": "hydrated-fleet", "kind": "control",
     "forbid": "_pm_install_promisor_refusal"},
    {"case": "missing-lane-blob", "kind": "fault",
     "require": 'raise EvalError(f"{repo}: required object {oid} is not '
                'available")'},
    {"case": "missing-fleet-report", "kind": "fault",
     "require": 'raise EvalError(f"{repo}: required object {oid} is not '
                'available")'},
    {"case": "missing-lane-tree", "kind": "fault",
     "require": 'raise EvalError(f"{repo}: required object {oid} is not '
                'available")'},
    {"case": "missing-fleet-tree", "kind": "fault",
     "require": 'raise EvalError(f"{repo}: required object {oid} is not '
                'available")'},
    {"case": "missing-ancestor", "kind": "fault",
     "require": 'raise EvalError(f"{repo}: required object {oid} is not '
                'available")'},
    {"case": "unknown-citation", "kind": "fault",
     "require": 'raise EvalError(f"{token}: not resolvable in a '
                'promisor-backed repository")'},
    {"case": "wrong-type-citation", "kind": "fault",
     "require": "full = lookup(repos, full_tokens)"},
    {"case": "unreachable-citation", "kind": "fault",
     "require": 'raise EvalError(f"{token}: not resolvable in a '
                'promisor-backed repository")'},
    {"case": "cross-repo-found", "kind": "fault",
     "require": "for repo in repos:"},
    {"case": "per-repo-side", "kind": "contract",
     "require": "for repo in (lane_repo, fleet_repo):"},
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="current")
    ap.add_argument("--current", required=True)
    ap.add_argument("--case", action="append")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    path = Path(args.current)
    if not path.is_file():
        print(f"stub-grid: no candidate at {path}", file=sys.stderr)
        return 2
    source = path.read_text(encoding="utf-8")
    rows = []
    for spec in ROWS:
        if args.case and spec["case"] not in args.case:
            continue
        require = spec.get("require")
        forbid = spec.get("forbid")
        met = ((require is None or require in source)
               and (forbid is None or forbid not in source))
        rows.append({"case": spec["case"], "kind": spec["kind"], "met": met,
                     "expected": "marker present" if met else "marker absent"})
    doc = {"arms": {args.arm: {"rows": rows}}}
    if args.json:
        print(json.dumps(doc, indent=1))
    else:
        for r in rows:
            print(f"{r['case']} {'met' if r['met'] else 'UNMET'}")
    return 0 if all(r["met"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
