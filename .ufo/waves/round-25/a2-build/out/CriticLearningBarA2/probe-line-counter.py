#!/usr/bin/env python3
"""Show that count-c2.py accepts a fit-probe `llama_context: n_ctx` line as the KV pool.

Builds two synthetic receipts from the attempt-2 sibling receipts (read-only inputs):
genuine (as recorded) and probe (X1 kv_pool_n_ctx replaced by 2048, the value on the
fit-probe line 283 of the X1 server log, which is also the round-20 pool). Writes under
the scratch dir given as argv[1] and runs count-c2.py on each. Also prints, per config
cell, every `llama_context: n_ctx ` value in order and the last one before
`srv    load_model: initializing` (the served context).
"""
import copy, json, os, re, subprocess, sys
OUT = sys.argv[1]
A2 = ".ufo/waves/round-25/a2-build/out"
cfg = json.load(open(f"{A2}/ExecRawReplicate/receipt-config-cells.json"))
load = json.load(open(f"{A2}/ExecLoadReplicate/l-cells-receipt.json"))
cells = [c for c in cfg["cells"]] + [c for c in load["cells"]]
base = {"server_version": cfg.get("server_version"), "model_sha256": cfg.get("model_sha256"), "cells": cells}
probe = copy.deepcopy(base)
for c in probe["cells"]:
    if c.get("id") == "X1":
        print("X1 recorded kv_pool_n_ctx", c.get("kv_pool_n_ctx"))
        c["kv_pool_n_ctx"] = 2048
        print("X1 probe lines kept in receipt:", [x for x in c["log_lines"] if "llama_context: n_ctx " in x])
for name, d in (("genuine", base), ("probe", probe)):
    p = os.path.join(OUT, f"{name}.json")
    json.dump(d, open(p, "w"))
    r = subprocess.run([sys.executable, ".ufo/waves/round-25/count-c2.py", p], capture_output=True, text=True)
    print(name, "exit", r.returncode, r.stdout.strip(), r.stderr.strip())
for cid in ("K1","K5","K6","K7","K8","X1","X2","X3"):
    log = open(f"{A2}/ExecRawReplicate/{cid}/server.log").read().splitlines()
    vals, served = [], None
    for ln in log:
        m = re.search(r"llama_context: n_ctx +=\s*(\d+)", ln)
        if m: vals.append(int(m.group(1)))
        if "load_model: initializing" in ln:
            served = vals[-1] if vals else None
            break
    print(cid, "n_ctx lines in order", vals, "served (last before load_model)", served)
