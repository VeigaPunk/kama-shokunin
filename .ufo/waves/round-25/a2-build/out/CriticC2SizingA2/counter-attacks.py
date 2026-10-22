#!/usr/bin/env python3
"""Synthetic-receipt attacks on the committed round-25 C2 counter.

Runs the counter bytes from commit 5388b7c (blob 1c78a96b, unchanged at
1fc41e3) read out of a private clone, against receipts written only under
the scratch directory. No llama-server is started.

Usage: python3 counter-attacks.py <clone-dir> <scratch-dir>
"""
import copy
import json
import os
import random
import subprocess
import sys

CLONE, SCRATCH = sys.argv[1], sys.argv[2]
os.makedirs(SCRATCH, exist_ok=True)
if len(sys.argv) > 3:
    CPATH = sys.argv[3]
    COUNTER = open(CPATH).read()
else:
    COUNTER = subprocess.run(
        ["git", "-C", CLONE, "show", "5388b7c:.ufo/waves/round-25/count-c2.py"],
        check=True, capture_output=True, text=True).stdout
    CPATH = os.path.join(SCRATCH, "count-c2-5388b7c.py")
    open(CPATH, "w").write(COUNTER)
print(f"counter under test: {CPATH}")

ns = {}
exec(compile(COUNTER, "count-c2", "exec"), ns)
CELLS = ns["CELLS"]
SHA = ns["MODEL_SHA"]


SLOT_LINE = ("0.00.015.663 I srv    load_model: initializing, n_slots = 4, "
             "n_ctx_slot = 2048, kv_unified = 'true'")


def cell(cid, pool=2048, lines=None):
    args, kind = CELLS[cid]
    c = {"id": cid, "args": args, "props_n_ctx": 2048, "total_slots": 4,
         "slots_n_ctx": [2048, 2048, 2048, 2048], "models_n_ctx_train": 2048,
         "kv_pool_n_ctx": pool,
         "argv": ["/home/vgpnk/.local/bin/llama-server", "-m",
                  "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf",
                  "--host", "127.0.0.1", "--port", "47999", "--no-webui",
                  "--offline", "-v"] + args.split(),
         "log_lines": lines or [
             f"0.00.012.649 I llama_context: n_ctx                 = {pool}",
             SLOT_LINE]}
    if kind.startswith("load"):
        seq = kind == "load-sequential"
        c["request_mode"] = "sequential" if seq else "concurrent"
        c["requests"] = [
            {"status": 200, "prompt_tokens": 1000, "n_predict": 600,
             "t_start": 10.0 + (5.0 * i if seq else 0.01 * i),
             "t_end": 14.0 + (5.0 * i if seq else 0.01 * i)}
            for i in range(2)]
    return c


def receipt(cells, ver="version: 0.7.0-dev (build 11755, commit 704366d76)"):
    return {"server_version": ver, "model_sha256": SHA, "cells": cells}


def base():
    return receipt([cell(k) for k in CELLS])


def run(name, rec, note, raw=None):
    p = os.path.join(SCRATCH, name + ".json")
    if raw is not None:
        open(p, "w").write(raw)
    elif rec is not None:
        json.dump(rec, open(p, "w"))
    r = subprocess.run([sys.executable, CPATH, p], capture_output=True,
                       text=True)
    err = r.stderr.strip().splitlines()[-1:] if r.stderr.strip() else []
    print(f"== {name}: {note}")
    print(f"   exit={r.returncode} stdout={r.stdout.strip()!r} stderr_tail={err}")


def with_cell(cid, **kw):
    d = base()
    for c in d["cells"]:
        if c["id"] == cid:
            c.update(kw)
    return d


run("A00-shaped", base(), "well-formed 14-cell receipt (control)")
def pool_line(n):
    return f"I llama_context: n_ctx                 = {n}"


def req(status=200, pt=1000, npred=600, t0=10.0):
    return {"status": status, "prompt_tokens": pt, "n_predict": npred,
            "t_start": t0, "t_end": t0 + 4.0}


run("A01-suffix-pool",
    with_cell("K1", kv_pool_n_ctx=48, log_lines=[pool_line(2048), SLOT_LINE]),
    "K1 kv_pool_n_ctx 48 against a log line '= 2048' (string endswith)")
run("A02-suffix-pool-8",
    with_cell("X2", kv_pool_n_ctx=192, log_lines=[pool_line(8192), SLOT_LINE]),
    "X2 kv_pool_n_ctx 192 against '= 8192'")
x1_log = [pool_line(2048), pool_line(8192), pool_line(8192), SLOT_LINE]
run("A03-x1-probe-2048", with_cell("X1", kv_pool_n_ctx=2048, log_lines=x1_log),
    "X1 log has fit-probe 2048 then final 8192; receipt claims pool 2048")
run("A04-x1-final-8192", with_cell("X1", kv_pool_n_ctx=8192, log_lines=x1_log),
    "same log, receipt claims pool 8192 (control: final value)")
run("A05-warning-only",
    with_cell("K6", kv_pool_n_ctx=1536, log_lines=[
        "W llama_context: n_ctx is not divisible by n_seq_max - rounding down to 1536",
        SLOT_LINE]),
    "K6 with only the warning-level rounding line (no -v info line)")
run("A06-status-zero",
    with_cell("L1", requests=[req(status=0), req(status=-1, t0=10.01)]),
    "L1 requests with status 0 and -1 (no HTTP response)")
run("A07-float-tokens",
    with_cell("L2", requests=[req(pt=1000.0, npred=600.0),
                              req(pt=1000.0, npred=600.0, t0=10.01)]),
    "L2 prompt_tokens 1000.0, n_predict 600.0 (floats)")
run("A08-five-requests",
    with_cell("L1", requests=[req(t0=10.0 + 0.01 * i) for i in range(5)]),
    "L1 with five overlapping requests (amendment says two)")
run("A09-concurrent-label-sequential-times",
    with_cell("L1", requests=[req(t0=10.0), req(t0=20.0)]),
    "L1 labelled 'concurrent' but the two requests never overlap (an L3 run)")
run("A09b-no-timing",
    with_cell("L1", requests=[{"status": 200, "prompt_tokens": 1000,
                               "n_predict": 600}] * 2),
    "L1 'concurrent' with no start/end times at all")
run("A10-slots-short",
    with_cell("K1", total_slots=4, slots_n_ctx=[7]),
    "K1 total_slots 4 but slots_n_ctx [7] (one entry, disagreeing)")
run("A11-negative",
    with_cell("K2", props_n_ctx=-1, total_slots=-5, models_n_ctx_train=0),
    "K2 props_n_ctx -1, total_slots -5, n_ctx_train 0")
d = base()
d["server_version"] = "build 117559"
run("A12-build-substring", d, "server_version 'build 117559'")
d = base()
for c in d["cells"]:
    c["server_version"] = "build 9999"
    c["model_sha256"] = "0" * 64
run("A13-per-cell-binding", d,
    "every cell says build 9999 / zero sha; only receipt-level fields checked")
d = base()
d["cells"].append({"id": ["K1"]})
run("A14-unhashable-id", d, "extra cell with list id")
run("A15-absent", None, "receipt path absent (the amendment-2 before value)")
run("A16-attempt1-receipt", None,
    "attempt-1 tool receipt (committed record, not claim evidence)",
    raw=open(os.path.join(CLONE, ".ufo/waves/round-25/build/out/"
                          "ExecCapacityTool/context-capacity-receipt.json")).read())
d = base()
d["cells"][0]["log_lines"] = d["cells"][1]["log_lines"] = [
    pool_line(2048), SLOT_LINE]
run("A17-shared-log", d, "two cells carry the same pasted log lines; no raw-log "
    "hash or per-cell log file binding (residual, no counter catches it)")
d = base()
for c in d["cells"]:
    c["argv"] = [x for x in c["argv"] if x != "-v"]
run("A18-no-v-flag", d, "every argv lacks -v (launch_rule universal)")

# Non-narrowing check: amendment-1 counting rule (K1-K8, field types and one
# log line) as a predicate; count-c2 acceptance on K cells must imply it.
def amend1_ok(c):
    def i(v):
        return isinstance(v, int) and not isinstance(v, bool)
    s, ls = c.get("slots_n_ctx"), c.get("log_lines")
    return (c.get("args") == CELLS[c["id"]][0] and i(c.get("props_n_ctx"))
            and i(c.get("total_slots")) and i(c.get("models_n_ctx_train"))
            and isinstance(s, list) and bool(s) and all(i(x) for x in s)
            and isinstance(ls, list) and bool(ls))


random.seed(25)
JUNK = [None, True, "2048", 2048.0, [], [2048], ["x"], "", 0, 512, {"a": 1},
        [True], ["I llama_context: n_ctx = 512"]]
viol = 0
trials = 20000
for _ in range(trials):
    c = cell(random.choice([k for k in CELLS if k.startswith("K")]),
             pool=random.choice([512, 1024, 1536, 2048, 4096]))
    for f in list(c):
        if f != "id" and random.random() < 0.3:
            if random.random() < 0.2:
                del c[f]
            else:
                c[f] = random.choice(JUNK)
    if (c.get("args") == CELLS[c["id"]][0]
            and ns["cell_ok"](c, CELLS[c["id"]][1]) and not amend1_ok(c)):
        viol += 1
print(f"== N01-implication: {trials} mutated K cells; count-c2 accepts but "
      f"amendment-1 rule rejects: {viol}")
if len(sys.argv) > 3:
    ref = {}
    exec(compile(subprocess.run(
        ["git", "-C", CLONE, "show",
         "5388b7c:.ufo/waves/round-25/count-c2.py"],
        check=True, capture_output=True, text=True).stdout, "ref", "exec"), ref)
    JUNK2 = JUNK + [-1, 8192, 1000.0, 600, 1000, 200, 0.5, "concurrent",
                    "sequential", [pool_line(2048), SLOT_LINE],
                    [pool_line(2048).replace(" = ", "\t= "), SLOT_LINE],
                    [req(), req(t0=10.01)], [req(), req(t0=20.0)]]
    wider = 0
    for _ in range(trials):
        cid = random.choice(list(CELLS))
        c = cell(cid, pool=random.choice([512, 1536, 2048, 8192]))
        for f in list(c):
            if f != "id" and random.random() < 0.25:
                if random.random() < 0.2:
                    del c[f]
                else:
                    c[f] = random.choice(JUNK2)
        kind = CELLS[cid][1]
        if c.get("args") != CELLS[cid][0]:
            continue
        if ns["cell_ok"](c, kind) and not ref["cell_ok"](c, kind):
            wider += 1
    print(f"== N03-proposal-subset: {trials} mutated cells (all 14 ids); "
          f"proposal accepts but committed counter rejects: {wider}")
pre = json.load(open(os.path.join(
    CLONE, ".ufo/waves/round-25/preregistration.json")))
c2 = [c for c in pre["claims"] if c["id"] == "C2"][0]
same = all(CELLS[x["id"]][0] == x["args"] for x in c2["cells"])
am2 = json.load(open(os.path.join(
    CLONE, ".ufo/waves/round-25/preregistration-amendment-2.json")))
same2 = all(CELLS[x["id"]][0] == x["args"] for x in am2["C2"]["cells_added"])
print(f"== N02-args: preregistration.json K cells ({len(c2['cells'])}) equal "
      f"count-c2 args: {same}; amendment-2 cells_added "
      f"({len(am2['C2']['cells_added'])}) equal: {same2}; K kinds all "
      f"'config': {all(CELLS[x['id']][1] == 'config' for x in c2['cells'])}")
