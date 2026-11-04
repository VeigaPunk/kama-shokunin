#!/usr/bin/env python3
"""mutation-control.py — round-75 freeze control (C1/C2) plus the C3 base receipt.

Runs from the base bytes, before any seat scores. Builds ONE shared clone of the lane in
--work, applies each named source mutation to a copy, and grades each mutant with the
committed module's own --selftest. Prints one stable line per claim:

  CONTROL_C1 killed=<k> escaped=<e> <mutant>=killed|escaped ...
  CONTROL_C2 killed=<k> escaped=<e> <mutant>=killed|escaped ...
  CONTROL_C3 <the audit summary line, verbatim>

and exits 0 when it produced every line (this is a receipt, not a gate: the round's claim
counters are the gates). Nothing in the lane is written; the clone lives under --work and is
removed unless --keep is passed.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys

C1_MUTANTS = {
    # F1b: names carried only by tables OLDER than the canonical round join `total`.
    "c1_f1b_older_union": (
        "tools/round74-selfdesc-canon.py",
        "    total = set(canon_names) | demonstrated\n",
        "    _older: set = set()\n"
        "    for _r, _i, _k in tables:\n"
        "        if _r < canon_round:\n"
        "            _older.update(_names_below(lines, _i, mod))\n"
        "    total = set(canon_names) | demonstrated | _older\n",
    ),
    # F2c: the literal reading — any 40-hex token is a revision mention.
    "c1_f2c_literal_hex": (
        "tools/round74-receipt-claim-binding.py",
        'REVISION_RE = re.compile(r"\\brev(?:ision)?\\s+([0-9a-fA-F]{40})\\b", re.I)',
        'REVISION_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-fA-F]{40})(?![0-9a-fA-F])", re.I)',
    ),
}

C2_MUTANTS = {
    # the tip= / rev= header parse loses its case-insensitivity (MT01's survivor class).
    "c2_case_hex": (
        "tools/round74-receipt-claim-binding.py",
        'HEADER_RE_V2 = re.compile(r"(?:^|[^\\w-])(?:#\\s*)?(?:tip|rev)=([0-9a-fA-F]{40})(?![0-9a-fA-F])", re.I)',
        'HEADER_RE_V2 = re.compile(r"(?:^|[^\\w-])(?:#\\s*)?(?:tip|rev)=([0-9a-f]{40})(?![0-9a-f])")',
    ),
    # a same-line tip claim stops inheriting the round-73 `stale-claim` kind.
    "c2_kind_boundary": (
        "tools/round74-receipt-claim-binding.py",
        '                    if kind == "same-line":\n'
        '                        kind = "stale-claim"\n',
        "                    pass\n",
    ),
    # per-line instead of per-paragraph claim grading.
    "c2_paragraph_scope": (
        "tools/round74-receipt-claim-binding.py",
        "        for start, plines in _paragraphs(lines):",
        "        for start, plines in [(i + 1, [l]) for i, l in enumerate(lines)]:",
    ),
    # the conflicting-header check is removed (docstring: conflicting headers stay a finding).
    "c2_conflict_off": (
        "tools/round74-receipt-claim-binding.py",
        "    if len(set(revs)) > 1:",
        "    if False:",
    ),
    # the documented five-line header window narrowed to three.
    "c2_header_window": (
        "tools/round74-receipt-claim-binding.py",
        "HEADER_WINDOW = 5",
        "HEADER_WINDOW = 3",
    ),
}

# (module, selftest argv tail, class name)
C1_TARGET = ("tools/round74-selfdesc-canon.py", ["--selftest"])
C2_TARGET = ("tools/round74-receipt-claim-binding.py", ["--selftest"])


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def make_clone(lane, work):
    clone = f"{work}/lane-control"
    shutil.rmtree(clone, ignore_errors=True)
    r = run(["git", "clone", "--shared", "--quiet", lane, clone], work)
    if r.returncode != 0:
        raise SystemExit(f"clone failed: {r.stderr.strip()}")
    return clone


def selftest(clone, module, tail, work, tag):
    cmd = ["python3", module] + tail + ["--work", f"{work}/work-{tag}"]
    return run(cmd, clone)


def grade(clone, mutants, target_module, work, label):
    names = []
    killed = 0
    for name, (path, old, new) in mutants.items():
        src = open(f"{clone}/{path}", encoding="utf-8").read()
        if old not in src:
            names.append(f"{name}=pattern-missing")
            continue
        with open(f"{clone}/{path}", "w", encoding="utf-8") as fh:
            fh.write(src.replace(old, new, 1))
        r = selftest(clone, target_module, C1_TARGET[1] if target_module.startswith("tools/round74-selfdesc")
                     else C2_TARGET[1], work, name)
        with open(f"{clone}/{path}", "w", encoding="utf-8") as fh:
            fh.write(src)
        state = "killed" if r.returncode != 0 else "escaped"
        killed += state == "killed"
        names.append(f"{name}={state}")
    escaped = len(mutants) - killed
    print(f"{label} killed={killed} escaped={escaped} " + " ".join(names))
    return escaped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()
    import os
    os.makedirs(args.work, exist_ok=True)
    clone = make_clone(args.lane, args.work)
    try:
        r = selftest(clone, C1_TARGET[0], C1_TARGET[1], args.work, "pristine-c1")
        print(f"CONTROL_PRISTINE c1 rc={r.returncode}")
        r = selftest(clone, C2_TARGET[0], C2_TARGET[1], args.work, "pristine-c2")
        print(f"CONTROL_PRISTINE c2 rc={r.returncode}")
        grade(clone, C1_MUTANTS, "tools/round74-selfdesc-canon.py", args.work, "CONTROL_C1")
        grade(clone, C2_MUTANTS, "tools/round74-receipt-claim-binding.py", args.work, "CONTROL_C2")
        r = run(["python3", "tools/append-only-audit.py", "--repo", "."], clone)
        for line in (r.stdout or "").splitlines():
            if line.startswith("summary "):
                print("CONTROL_C3 " + line)
        print(f"CONTROL_C3 exit={r.returncode}")
    finally:
        if not args.keep:
            shutil.rmtree(clone, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
