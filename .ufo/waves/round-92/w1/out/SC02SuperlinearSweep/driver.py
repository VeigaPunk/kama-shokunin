#!/usr/bin/env python3
"""SC02SuperlinearSweep driver: doubling-ratio measurements of probe paths at M2 and BASE.

Usage: driver.py <phase>
Phases:
  A  re-measure round-91 SC02 F1-F3 shapes at M2 and BASE
  B  sweep candidate remaining constructs (new stub shapes)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import (Stub, Runner, ids_doc, router_doc, jbody, uptime_str)

SCRATCH = Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
M2 = SCRATCH / "probe-M2.sh"
BASE = SCRATCH / "probe-BASE.sh"
OUT = SCRATCH / "out"


def log(*a):
    print(*a, flush=True)


def row_of(out: bytes):
    try:
        return json.loads(out.decode("utf-8"))["rows"][0]
    except Exception:
        return None


def measure_check(runner: Runner, routes, expect, label, note=""):
    with Stub(routes) as s:
        rc, so, se, dt = runner.check(s.port, expect)
    r = row_of(so)
    v = r.get("verdict") if r else ("killed" if rc is None else "unparsed")
    reason = r.get("reason") if r else "-"
    served_len = len(r.get("served_model") or "") if r else -1
    log(f"{label} rc={rc} seconds={dt:.2f} verdict={v} reason={reason} served_len={served_len} {note} {uptime_str()}")
    return dt, rc, v, reason, r


def measure_snap(runner: Runner, routes, expect, label, note=""):
    with Stub(routes) as s:
        rc, so, se, dt, tsv = runner.snapshot(s.port, expect)
    served = ""
    if tsv:
        for line in tsv.decode("utf-8", "replace").splitlines():
            f = line.split("\t")
            if f and f[0] == "cell" and len(f) >= 4:
                served = f[3]
    log(f"{label} rc={rc} seconds={dt:.2f} served_len={len(served)} {note} {uptime_str()}")
    return dt, rc, served


def phase_a():
    log("=== PHASE A: round-91 F1-F3 shapes at M2 and BASE ===")
    for tag, probe in (("M2", M2), ("BASE", BASE)):
        R = Runner(SCRATCH, probe.read_bytes(), tag)
        # F1: jstr backslash id
        for n in (100000, 200000, 400000):
            measure_check(R, {"/v1/models": jbody(ids_doc(["\\" * n]))}, "good",
                          f"A-F1-{tag}-backslash-n{n}")
        # F2: jstr quote id
        for n in (100000, 200000, 400000):
            measure_check(R, {"/v1/models": jbody(ids_doc(['"' * n]))}, "good",
                          f"A-F2-{tag}-quote-n{n}")
        # F3: router_refine, wildcard, unloaded entries
        for n in (10000, 20000, 40000):
            measure_check(R, {"/v1/models": jbody(router_doc([(f"r{i:05d}", "unloaded", None, None) for i in range(n)]))},
                          "*", f"A-F3a-{tag}-router-wild-n{n}")
        # F3b: router_refine, same id unloaded then loaded
        for n in (10000, 20000, 40000):
            measure_check(R, {"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] * n + [("good", "loaded", None, None)]))},
                          "good", f"A-F3b-{tag}-router-sameid-n{n}")
        # F3c: served_persist snapshot, many path ids
        for n in (4000, 8000, 16000):
            measure_snap(R, {"/v1/models": jbody(ids_doc([f"/m/x{i:05d}.gguf" for i in range(n)]))},
                         "x00000", f"A-F3c-{tag}-snap-paths-n{n}")
        # F3d: served_persist snapshot, one slash-free id
        for n in (50000, 100000, 200000):
            measure_snap(R, {"/v1/models": jbody(ids_doc(["a" * n]))}, "a",
                         f"A-F3d-{tag}-snap-noslash-n{n}")


def phase_b():
    log("=== PHASE B: remaining-construct sweep ===")
    for tag, probe in (("M2", M2),):
        R = Runner(SCRATCH, probe.read_bytes(), tag)
        # B1: listener-controlled router status.value of arbitrary length -> reason string
        for n in (500000, 1000000, 2000000):
            measure_check(R, {"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] +
                                                               [("other", "x" * n, None, None)]))},
                          "good", f"B1-{tag}-router-status-value-n{n}")
        # B2: many served ids in /v1/models
        for n in (5000, 10000, 20000):
            measure_check(R, {"/v1/models": jbody(ids_doc([f"id{i:05d}" for i in range(n)]))},
                          "id00000", f"B2-{tag}-many-served-ids-n{n}")
        # B3: many served ids, snapshot path (served_persist + persist_clean + jstr)
        for n in (5000, 10000, 20000):
            measure_snap(R, {"/v1/models": jbody(ids_doc([f"/m/x{i:05d}.gguf" for i in range(n)]))},
                         "x00000", f"B3-{tag}-snap-many-ids-n{n}")
        # B6: served ids that are many a/ pairs (AWK_NORM split on "/")
        for n in (50000, 100000, 200000):
            measure_check(R, {"/v1/models": jbody(ids_doc(["a/" * n]))}, "a",
                          f"B6-{tag}-id-many-slashes-n{n}")


if __name__ == "__main__":
    ph = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    if ph == "A":
        phase_a()
    elif ph == "B":
        phase_b()
    else:
        raise SystemExit("unknown phase")
