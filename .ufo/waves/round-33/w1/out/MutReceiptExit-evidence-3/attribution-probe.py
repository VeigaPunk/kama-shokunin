#!/usr/bin/env python3
"""Diagnostic attribution for a baseline/invalid split in the round-33 C2 audit.

Imports the commit's own predicates (parse_receipt, expected_receipts, output_ok)
and reports, per case, exactly which header/stdout/stderr fields differ between
the committed receipt blob at <tip> and the freshly replayed expected receipt.
Read-only; no writes outside stdout.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
tip = sys.argv[2]
source_rev = sys.argv[3]
receipt_dir = sys.argv[4]

spec = importlib.util.spec_from_file_location(
    "r33gate", repo / "tools" / "round33-gate-receipts.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

expected = mod.expected_receipts(repo, source_rev)
gate_hash = mod.hashlib.sha256(mod.read_blob(repo, source_rev, mod.GATE_PATH)).hexdigest()
runner_hashes = mod.known_runner_hashes(repo, tip)
print(f"runner_hashes_known={len(runner_hashes)}")

for case, (relative, expected_exit, expected_line) in mod.CASES.items():
    path = f"{receipt_dir}/{relative}"
    blob = mod.receipt_blob(repo, tip, path)
    label = case
    if blob is None:
        print(f"{label}: MISSING")
        continue
    actual = mod.parse_receipt(blob)
    exp = mod.parse_receipt(expected[case])
    if actual is None or exp is None:
        print(f"{label}: parse failure actual={actual is not None} expected={exp is not None}")
        continue
    headers, stdout, stderr = actual
    eh, es, ee = exp
    diffs = {k: (headers.get(k), eh.get(k)) for k in set(headers) | set(eh)
             if headers.get(k) != eh.get(k)}
    print(f"{label}: header_diffs={diffs}")
    print(f"{label}: stdout_equal={stdout == es} stderr_equal={stderr == ee}")
    print(f"{label}: runner_hash_known={headers.get('RUNNER_SHA256') in runner_hashes}")
    ok = mod.output_ok(case, blob, expected_exit, expected_line,
                       source_rev, gate_hash, headers.get("RUNNER_SHA256", ""))
    print(f"{label}: output_ok={ok!r} EXIT_CODE={headers.get('EXIT_CODE')!r} expected_exit={expected_exit}")
