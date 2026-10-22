#!/usr/bin/env python3
"""Round 25 C2 counting command (registered by preregistration amendment 2).

Counts the registered context-capacity cells that the committed receipt
observed. A cell counts only when its id and args equal the registered cell,
its id occurs once in the receipt, and every required field is present with
the required type. Truthy strings, duplicate ids and extra cells never count.
The receipt-level binding (llama-server build 11755, fixture sha256) is
printed separately and must be True for the claim value to stand.

Usage: python3 .ufo/waves/round-25/count-c2.py [receipt.json]
Prints: registered N observed M bound B
Exit 0 always when the receipt parses; exit 2 when it cannot be read.
"""
import json
import sys

RECEIPT = ".ufo/waves/round-25/final/context-capacity-receipt.json"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
LOAD_REQUEST = {"prompt_tokens": 1000, "n_predict": 600}
CELLS = {
    "K1": ("-c 0", "config"),
    "K2": ("-c 2048 -np 2 --no-kv-unified", "config"),
    "K3": ("-c 2048 -np 2 --kv-unified", "config"),
    "K4": ("-c 1024 -np 1", "config"),
    "K5": ("-c 4096 -np 1", "config"),
    "K6": ("-c 1000 -np 3 --no-kv-unified", "config"),
    "K7": ("-np 2 --kv-unified-per-slot 512", "config"),
    "K8": ("-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512", "config"),
    "X1": ("-np 4 --no-kv-unified", "config"),
    "X2": ("-c 8192 -np 4 --no-kv-unified", "config"),
    "X3": ("-np 4 --no-kv-unified --fit off", "config"),
    "L1": ("-c 0", "load-concurrent"),
    "L2": ("-c 8192 -np 4 --no-kv-unified", "load-concurrent"),
    "L3": ("-c 0", "load-sequential"),
}


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cell_ok(c, kind):
    if not (is_int(c.get("props_n_ctx")) and is_int(c.get("total_slots"))
            and is_int(c.get("models_n_ctx_train"))
            and is_int(c.get("kv_pool_n_ctx"))):
        return False
    s = c.get("slots_n_ctx")
    if not (isinstance(s, list) and s and all(is_int(x) for x in s)):
        return False
    lines = c.get("log_lines")
    if not (isinstance(lines, list) and lines
            and all(isinstance(x, str) and x for x in lines)):
        return False
    if not any("llama_context: n_ctx " in x and x.rstrip().endswith(
            str(c["kv_pool_n_ctx"])) for x in lines):
        return False
    if kind.startswith("load"):
        want = "sequential" if kind == "load-sequential" else "concurrent"
        if c.get("request_mode") != want:
            return False
        r = c.get("requests")
        if not (isinstance(r, list) and len(r) >= 2):
            return False
        for q in r:
            if not (isinstance(q, dict) and is_int(q.get("status"))
                    and q.get("prompt_tokens") == LOAD_REQUEST["prompt_tokens"]
                    and q.get("n_predict") == LOAD_REQUEST["n_predict"]):
                return False
    return True


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else RECEIPT
    try:
        d = json.load(open(path))
    except (OSError, ValueError) as exc:
        print(f"cannot read receipt: {exc}", file=sys.stderr)
        return 2
    cells = d.get("cells") if isinstance(d, dict) else None
    cells = cells if isinstance(cells, list) else []
    ids = [c.get("id") for c in cells if isinstance(c, dict)]
    observed = []
    for c in cells:
        if not isinstance(c, dict):
            continue
        cid = c.get("id")
        if cid not in CELLS or ids.count(cid) != 1:
            continue
        args, kind = CELLS[cid]
        if c.get("args") == args and cell_ok(c, kind):
            observed.append(cid)
    ver = d.get("server_version") if isinstance(d, dict) else None
    sha = d.get("model_sha256") if isinstance(d, dict) else None
    bound = isinstance(ver, str) and "build 11755" in ver and sha == MODEL_SHA
    missing = [k for k in CELLS if k not in observed]
    print("registered", len(CELLS), "observed", len(observed), "bound", bound,
          "missing", missing)
    return 0


if __name__ == "__main__":
    sys.exit(main())
