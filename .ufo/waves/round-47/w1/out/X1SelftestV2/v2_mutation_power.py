#!/usr/bin/env python3
"""v2_mutation_power.py - measure which v2 selftest cases kill which mechanism.

Round-47 wave-1 seat X1SelftestV2 (lane kama). Each mutation reverts exactly one v2
mechanism to its v1 behaviour in a scratch copy of tools/append-only-audit.py
(append-only-audit/v2 at lane commit 3a09a1d93dcc16799cf6c4b48786e6440af134c4), then runs
the tool's own selftest. A mutation that leaves the selftest green is a case that tests
nothing; a case killed by its own mutation is a kill switch for that mechanism.

Mutations (all textual, asserted to apply exactly once):
  M0 identity                 - no change                       (control: all 15 pass)
  M1 dashdash-v1              - drop deleted lines starting with `--` AND drop the
                                numstat equality check            (v1's whole D1 blind spot)
  M1b dashdash-filter-only    - drop `--` lines, keep numstat     (defense in depth)
  M2 newline-normalised       - CRLF/lone CR folded to LF on both the diff and blob read
                                (v1 read git through text=True)  (D1 byte identity)
  M3 multiset->set            - a deleted text counts once per occurrence while present,
                                regardless of held multiplicity  (v1 set membership)
  M4 tip-only-max             - restored_max measured at the audited tip only  (D2)
  M5 later-only-witness       - restored_by searched only after the event commit
  M6 hard-coded-files         - the contract is read but its expansion is ignored, the
                                five v1 files are used instead

Usage:
  v2_mutation_power.py --v2-tool PATH [--scratch DIR] [--json OUT]

Read-only outside --scratch. Fixtures removed on exit.
Exit: 0 all mutations applied and the selftest ran; 2 could not evaluate.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

CASES = ["no-deletion", "below-threshold", "exact-threshold-unrestored", "restored-later",
         "partial", "undeclared-file", "declared-file-removed", "merge-first-parent",
         "dashdash-lines", "crlf-and-eof", "multiset", "window-max", "relocation",
         "contract", "threshold-flag"]

NUMSTAT_GUARD = """            if len(dl) != ns[f]:
                raise AuditError(f"{c[:12]} {f}: hunk count {len(dl)} != numstat {ns[f]}")
"""
MAX_BLOCK_STATUS = "            status = \"restored\" if best == len(dl) else (\"unrestored\" if best == 0 else \"partial\")\n"

MUTATIONS = [
    {
        "name": "M0-identity",
        "hypothesis": "control: the unmodified selftest is green on all 15 cases",
        "edits": [],
        "target": None,
    },
    {
        "name": "M1-dashdash-v1",
        "hypothesis": "v1's D1 blind spot: `--`-prefixed deleted lines dropped and no numstat cross-check",
        "edits": [
            ("            i += 1\n    return out\n",
             "            i += 1\n    out = [x for x in out if not x.startswith(b\"--\")]\n    return out\n"),
            (NUMSTAT_GUARD,
             "            if False:  # mutation M1: v1 had no numstat cross-check\n"
             "                raise AuditError(f\"{c[:12]} {f}: hunk count {len(dl)} != numstat {ns[f]}\")\n"),
        ],
        "target": "dashdash-lines",
    },
    {
        "name": "M1b-dashdash-filter-only",
        "hypothesis": "drop `--` lines but keep the numstat equality check (defense in depth)",
        "edits": [
            ("            i += 1\n    return out\n",
             "            i += 1\n    out = [x for x in out if not x.startswith(b\"--\")]\n    return out\n"),
        ],
        "target": "dashdash-lines",
    },
    {
        "name": "M2-newline-normalised",
        "hypothesis": "v1 read git output and blobs through text=True, folding CRLF/CR to LF",
        "edits": [
            ("                out.append(ln[1:])\n",
             "                out.append(ln[1:].rstrip(b\"\\r\"))  # mutation M2: v1's text-mode newline folding\n"),
            ("            self._lines[blob] = collections.Counter(split_lines(_git(self.path, \"cat-file\", \"blob\", blob)))\n",
             "            _raw = _git(self.path, \"cat-file\", \"blob\", blob).replace(b\"\\r\\n\", b\"\\n\").replace(b\"\\r\", b\"\\n\")\n"
             "            self._lines[blob] = collections.Counter(split_lines(_raw))\n"),
        ],
        "target": "crlf-and-eof",
    },
    {
        "name": "M3-multiset-to-set",
        "hypothesis": "v1 set membership: every deleted occurrence counts when the text is present",
        "edits": [
            ("                h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())\n",
             "                h = sum(n for l, n in D.items() if M[l] - K[l] > 0)  # mutation M3: v1 set membership\n"),
        ],
        "target": "multiset",
    },
    {
        "name": "M4-tip-only-max",
        "hypothesis": "v1/D2: the restoration figure is measured at the audited tip, not maximised over the window",
        "edits": [
            (MAX_BLOCK_STATUS,
             "            _tip = window[-1]  # mutation M4: v1 reports the audited tip's figure\n"
             "            _htip = sum(min(n, max(0, r.lines(wb[f\"{_tip}:{f}\"])[l] - K[l])) for l, n in D.items())\n"
             "            if _htip != best:\n"
             "                best, best_c = _htip, (_tip if _htip else None)\n"
             + MAX_BLOCK_STATUS),
        ],
        "target": "window-max",
    },
    {
        "name": "M5-later-only-witness",
        "hypothesis": "v1 searched restored_by only in commits after the event commit",
        "edits": [
            ("            for x in window:\n",
             "            for x in window[1:]:  # mutation M5: v1 searched only commits after the event\n"),
        ],
        "target": "relocation",
    },
    {
        "name": "M6-hard-coded-files",
        "hypothesis": "v1's fixed five-file set, ignoring the contract's expansion",
        "edits": [
            ("        label, text = contract\n"
             "        files = expand(repo_path, to_full, [row[0] for row in parse_contract(text)])\n",
             "        label, text = contract\n"
             "        files = [\"SCORECARD.md\", \"LOG.md\", \"corpus/QUALITY.md\", \"corpus/README.md\", \"corpus/SOURCES.md\"]\n"
             "        parse_contract(text)  # mutation M6: v1's hard-coded set\n"),
        ],
        "target": "contract",
    },
    # ---- coverage probes: each disables a v2 mechanism that no selftest case may cover.
    # A probe that leaves all 15 cases green marks a mechanism the selftest cannot see.
    {
        "name": "P1-binary-numstat",
        "kind": "probe",
        "hypothesis": "a binary change (numstat `-`) is counted as 0 deletions",
        "edits": [
            ("        if len(parts) >= 3 and parts[1].isdigit():\n            res[parts[2]] = int(parts[1])\n",
             "        if len(parts) >= 3:  # probe P1: binary numstat reads as 0, not skipped\n"
             "            res[parts[2]] = int(parts[1]) if parts[1].isdigit() else 0\n"),
        ],
        "target": None,
    },
    {
        "name": "P2-threshold-guard",
        "kind": "probe",
        "hypothesis": "the `--threshold < 1` -> exit 2 guard",
        "edits": [
            ("    if a.threshold < 1:\n",
             "    if False:  # probe P2: no exit-2 guard on --threshold\n"),
        ],
        "target": None,
    },
    {
        "name": "P3-rule-validation",
        "kind": "probe",
        "hypothesis": "the contract row rule in A | A-row | A-corr",
        "edits": [
            ("        if not pat or rule not in RULES or not re.fullmatch(r\"[^:]+:\\d+\", decl):\n",
             "        if not pat or not re.fullmatch(r\"[^:]+:\\d+\", decl):  # probe P3: any rule accepted\n"),
        ],
        "target": None,
    },
    {
        "name": "P4-declared-at-validation",
        "kind": "probe",
        "hypothesis": "the contract declared_at <path>:<line> shape",
        "edits": [
            ("        if not pat or rule not in RULES or not re.fullmatch(r\"[^:]+:\\d+\", decl):\n",
             "        if not pat or rule not in RULES:  # probe P4: any declared_at accepted\n"),
        ],
        "target": None,
    },
    {
        "name": "P5-schema-string",
        "kind": "probe",
        "hypothesis": "the schema field `append-only-audit/v2`",
        "edits": [
            ("SCHEMA = \"append-only-audit/v2\"\n",
             "SCHEMA = \"append-only-audit/probe\"  # probe P5\n"),
        ],
        "target": None,
    },
    {
        "name": "P6-earlier-to-ignored",
        "kind": "probe",
        "hypothesis": "an earlier --to rev (v1 had a to-earlier-rev case; v2's list dropped it)",
        "edits": [
            ("    to_full = _text(repo_path, \"rev-parse\", \"--verify\", to + \"^{commit}\").strip()\n",
             "    to_full = _text(repo_path, \"rev-parse\", \"HEAD\").strip()  # probe P6: --to resolved as HEAD\n"),
        ],
        "target": None,
    },
]


def load_from_source(source, path, name):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(source)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_selftest(mod, root):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.selftest(root)
    verdicts = {}
    reasons = {}
    for line in buf.getvalue().split("\n"):
        parts = line.split()
        if len(parts) >= 2 and parts[0] in ("pass", "FAIL"):
            name = parts[1].rstrip(":")
            verdicts[name] = parts[0] == "pass"
            if parts[0] == "FAIL":
                reasons[name] = line.split(":", 1)[1].strip()[:220]
    tail = [ln for ln in buf.getvalue().split("\n") if ln.startswith("AOA_SELFTEST")]
    return rc, verdicts, reasons, (tail[-1] if tail else ""), buf.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--v2-tool", required=True)
    ap.add_argument("--scratch", default=None)
    ap.add_argument("--json", help="write the matrix JSON here")
    a = ap.parse_args(argv)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    work = tempfile.mkdtemp(prefix="x1mut-", dir=root)
    try:
        with open(a.v2_tool, encoding="utf-8") as fh:
            base = fh.read()
        rows = []
        for spec in MUTATIONS:
            kind = spec.get("kind") or ("mutation" if spec.get("target") else "control")
            src = base
            applied = []
            for old, new in spec["edits"]:
                n = src.count(old)
                if n != 1:
                    print(f"could-not-evaluate: mutation {spec['name']}: anchor count {n} (want 1): {old[:60]!r}")
                    return 2
                src = src.replace(old, new)
                applied.append(old.split("\n")[0].strip()[:70])
            mod_dir = tempfile.mkdtemp(prefix="mutsrc-", dir=work)
            mod = load_from_source(src, os.path.join(mod_dir, "append_only_audit.py"),
                                   "aoa_mut_" + spec["name"].replace("-", "_"))
            run_root = tempfile.mkdtemp(prefix="mutrun-", dir=work)
            rc, verdicts, reasons, tail, raw = run_selftest(mod, run_root)
            missing = [c for c in CASES if c not in verdicts]
            killed = [c for c in CASES if verdicts.get(c) is False]
            row = {"mutation": spec["name"], "kind": kind, "hypothesis": spec["hypothesis"],
                   "target": spec["target"], "exit": rc, "cases": len(verdicts),
                   "killed": killed, "reasons": {c: reasons.get(c, "") for c in killed},
                   "missing_cases": missing, "summary_line": tail,
                   "target_killed": (spec["target"] in killed) if spec["target"] else None,
                   "probe_gap": (not killed) if kind == "probe" else None,
                   "applied": applied}
            rows.append(row)
            verdict = ("target_killed" if row["target_killed"] else
                       ("no_case_covers" if kind == "probe" and not killed else "-"))
            print(f"{spec['name']:26s} kind={kind:8s} exit={rc} cases={len(verdicts)} "
                  f"killed={','.join(killed) or '-'} target={spec['target'] or '-'} {verdict}")
            for c in killed:
                print(f"  FAIL {c}: {reasons.get(c, '')}")
            if missing:
                print(f"  MISSING CASES: {missing}")
            if spec["target"] and spec["target"] not in killed:
                print(f"  TARGET NOT KILLED: {spec['target']}")
                for line in raw.split("\n"):
                    if "could-not-evaluate" in line or "AOA_SELFTEST" in line:
                        print(f"  {line.strip()[:200]}")
        targets = [r for r in rows if r["kind"] == "mutation"]
        probes = [r for r in rows if r["kind"] == "probe"]
        gaps = [r["mutation"] for r in probes if r["probe_gap"]]
        covered = [r["mutation"] for r in probes if not r["probe_gap"]]
        ok = (all(r["target_killed"] for r in targets) and rows[0]["cases"] == len(CASES)
              and not rows[0]["killed"])
        print(f"X1_MUTATION_POWER mutations={len(targets)} targets_killed="
              f"{sum(1 for r in targets if r['target_killed'])}/{len(targets)} "
              f"identity_green={rows[0]['cases'] == len(CASES) and not rows[0]['killed']}")
        print(f"X1_PROBE_GAPS probes={len(probes)} no_case_covers={len(gaps)} coverage_gaps={','.join(gaps) or '-'} "
              f"probe_covered={','.join(covered) or '-'}")
        if a.json:
            with open(a.json, "w", encoding="utf-8") as fh:
                json.dump({"v2_tool": os.path.abspath(a.v2_tool), "cases": CASES, "rows": rows,
                           "targets_killed": f"{sum(1 for r in targets if r['target_killed'])}/{len(targets)}",
                           "coverage_gaps": gaps, "probe_covered": covered, "ok": ok}, fh, indent=1)
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
