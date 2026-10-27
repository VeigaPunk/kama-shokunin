#!/usr/bin/env python3
"""Probe harness for tools/round60-c2-counter.py safe_compile/evaluate.

Reads one predicate expression from argv[1] (a file), runs the counter's own
safe_compile -> evaluate -> falsifiable path, prints one JSON line.
Only ever run inside `ulimit -v 2000000` + `timeout 10`.
"""
import importlib.util
import json
import os
import resource
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("c2", os.path.join(HERE, "round60-c2-counter.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

expr = open(sys.argv[1], "r", encoding="utf-8").read()
mode = sys.argv[2] if len(sys.argv) > 2 else "full"
caps, receipt_ok = m.receipt_caps(open(os.path.join(HERE, "receipt.json"), encoding="utf-8").read())

rec = {"expr_bytes": len(expr), "caps": len(caps), "receipt_ok": receipt_ok, "mode": mode}
try:
    t0 = time.perf_counter()
    tree = m.safe_compile(expr)
    rec["safe_compile"] = "accepted"
    rec["compile_s"] = round(time.perf_counter() - t0, 4)
except BaseException as e:  # noqa: BLE001 - we want RecursionError/MemoryError too
    rec["safe_compile"] = "rejected"
    rec["exc"] = type(e).__name__
    rec["msg"] = str(e)[:160]
    rec["compile_s"] = round(time.perf_counter() - t0, 4)
    rec["maxrss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(rec))
    sys.exit(0)

if mode == "full":
    t0 = time.perf_counter()
    try:
        rec["evaluate"] = m.evaluate(tree, caps)
    except BaseException as e:  # noqa: BLE001
        rec["evaluate_exc"] = type(e).__name__
    rec["eval_s"] = round(time.perf_counter() - t0, 4)
    t0 = time.perf_counter()
    try:
        rec["falsifiable"] = m.falsifiable(tree, caps)
    except BaseException as e:  # noqa: BLE001
        rec["falsifiable_exc"] = type(e).__name__
    rec["falsifiable_s"] = round(time.perf_counter() - t0, 4)

rec["maxrss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(json.dumps(rec))
