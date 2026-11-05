#!/usr/bin/env python3
"""MT02 cardinality-forgery probe: feed forged debt-selftest outputs to the committed
round86-mutant-owners.py classifier (bytes at 67eddac) and print its verdict token.

The instrument is imported read-only; classify() is the exact reconciliation engine that
grade() calls on every mutant run, so a verdict here is the verdict the instrument would
assign to a mutant that emitted those bytes.
"""
import importlib.util
import json
import pathlib
import sys

INSTRUMENT = pathlib.Path(__file__).with_name("mo.py")
spec = importlib.util.spec_from_file_location("r86_mutant_owners", INSTRUMENT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ARMS_OK = "APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0\n"
GREEN = "APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34\n"

PROBES = [
    # name, stdout, stderr, rc, owner
    ("P2_a1_forged-summary-arms-retained",
     ARMS_OK + "APPEND_DEBT_SELFTEST pass=0 fail=0 arms=34\n", "", 0, "summary-cardinality"),
    ("P3_a2_forged-summary-no-arms-field",
     ARMS_OK + "APPEND_DEBT_SELFTEST pass=0 fail=0\n", "", 0, "summary-cardinality"),
    ("P4_a3_forged-summary-arms-zero",
     ARMS_OK + "APPEND_DEBT_SELFTEST pass=0 fail=0 arms=0\n", "", 0, "summary-cardinality"),
    ("P5_b1_dropped-case-forged-arms34-rc1",
     ARMS_OK + "APPEND_DEBT_SELFTEST pass=33 fail=0 arms=33\n", "", 1, "arm-count"),
    ("P6_b2_dropped-case-forged-arms34-rc0",
     ARMS_OK + "APPEND_DEBT_SELFTEST pass=33 fail=0 arms=33\n", "", 0, "arm-count"),
    ("P7_c1_extra-fail-line-counted-by-arms",
     "APPEND_DEBT_SELFTEST_FAIL note-deletion-equals-subject exit=1 want=0\n" + ARMS_OK + GREEN,
     "", 0, "summary-cardinality"),
    ("P8_c2_extra-fail-line-no-arms-line",
     "APPEND_DEBT_SELFTEST_FAIL note-deletion-equals-subject exit=1 want=0\n"
     "APPEND_DEBT_SELFTEST_FAIL arm-count arms=33 want=34\n"
     "APPEND_DEBT_SELFTEST pass=34 fail=0\n", "", 0, "summary-cardinality"),
    ("P8b_c3_fail-line-no-name-token",
     "APPEND_DEBT_SELFTEST_FAIL note-deletion-equals-subject\n" + ARMS_OK + GREEN,
     "", 0, "summary-cardinality"),
    ("P9_d_two-summary-lines", ARMS_OK + GREEN + GREEN, "", 0, "summary-cardinality"),
    ("P10_e1_traceback-stderr-exit0", ARMS_OK + GREEN,
     "Traceback (most recent call last):\n  File \"x\", line 1, in <module>\nRuntimeError\n",
     0, "summary-cardinality"),
    ("P11_e2_stderr-noise-exit0", ARMS_OK + GREEN,
     "warning: internal diagnostic on stderr\n", 0, "summary-cardinality"),
]

rows = []
for name, stdout, stderr, rc, owner in PROBES:
    verdict, label, detail = mod.classify(stdout, stderr, rc, owner)
    rows.append({"probe": name, "verdict": verdict, "label": label, "detail": detail,
                 "owner_declared": owner, "owner_matches": label == owner,
                 "stdout": stdout, "stderr": stderr, "rc": rc})
    print(f"{name:44s} verdict={verdict:8s} label={label:22s} detail={detail}")

print(json.dumps({"instrument_sha256": __import__("hashlib").sha256(
    INSTRUMENT.read_bytes()).hexdigest(), "probes": rows}))
