#!/usr/bin/env python3
# SCRATCH CANDIDATE (not registered): committed fa3b62ae counter plus verdict_ok checks.
"""Round 25 C2 counting command (registered by preregistration amendment 2,
made stricter by amendments 3 and 4).

Amendment 4 registers the stricter counter proposed by wave-1 critic seat
CriticC2SizingA2 (.ufo/waves/round-25/a2-build/out/CriticC2SizingA2/): the
5388b7c bytes with only stricter checks (each change shrinks the accepted
set): positive integers; one /slots entry per slot; the recorded argv ends
with the registered args and carries the launch flags including -v; the pool
equals the last `llama_context: n_ctx = N` line; an `n_slots ... kv_unified`
startup line; load cells have exactly two requests with HTTP status 100-599,
integer token counts, start and end times, and overlap if and only if the
mode is concurrent; exact build and commit binding.

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
import re
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


BUILD = re.compile(r"\(build 11755, commit 704366d76\)")
POOL = re.compile(r"\bllama_context: n_ctx +=  ?(\d+)\s*$")
SLOT = re.compile(r"n_slots = \d+, n_ctx_slot = \d+, kv_unified = '(true|false)'")
LAUNCH = ["--host", "127.0.0.1", "--no-webui", "--offline", "-v"]


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def pos(v):
    return is_int(v) and v > 0


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def cell_ok(c, kind):
    if not (pos(c.get("props_n_ctx")) and pos(c.get("total_slots"))
            and pos(c.get("models_n_ctx_train"))
            and pos(c.get("kv_pool_n_ctx"))):
        return False
    s = c.get("slots_n_ctx")
    if not (isinstance(s, list) and len(s) == c["total_slots"]
            and all(pos(x) for x in s)):
        return False
    argv = c.get("argv")
    if not (isinstance(argv, list) and all(isinstance(x, str) for x in argv)
            and argv[-len(c["args"].split()):] == c["args"].split()
            and all(x in argv for x in LAUNCH)):
        return False
    lines = c.get("log_lines")
    if not (isinstance(lines, list) and lines
            and all(isinstance(x, str) and x for x in lines)):
        return False
    pools = [int(m.group(1)) for m in map(POOL.search, lines) if m]
    if not (pools and pools[-1] == c["kv_pool_n_ctx"]):
        return False
    if not any(SLOT.search(x) for x in lines):
        return False
    if kind.startswith("load"):
        want = "sequential" if kind == "load-sequential" else "concurrent"
        if c.get("request_mode") != want:
            return False
        r = c.get("requests")
        if not (isinstance(r, list) and len(r) == 2):
            return False
        for q in r:
            if not (isinstance(q, dict) and is_int(q.get("status"))
                    and 100 <= q["status"] <= 599
                    and is_int(q.get("prompt_tokens"))
                    and q["prompt_tokens"] == LOAD_REQUEST["prompt_tokens"]
                    and is_int(q.get("n_predict"))
                    and q["n_predict"] == LOAD_REQUEST["n_predict"]
                    and is_num(q.get("t_start")) and is_num(q.get("t_end"))
                    and q["t_start"] < q["t_end"]):
                return False
        overlap = max(q["t_start"] for q in r) < min(q["t_end"] for q in r)
        if overlap != (want == "concurrent"):
            return False
    return True


NSLOT_LINE = re.compile(r"n_slots = (\d+), n_ctx_slot = (\d+), kv_unified = '(true|false)'")


def flag_value(argv, name):
    if name not in argv or argv.index(name) + 1 >= len(argv):
        return None
    return argv[argv.index(name) + 1]


def verdict_ok(c, d):
    """Candidate (scratch): the tool's own verdict plus cross-field facts."""
    if c.get("observed") is not True or c.get("error") is not None:
        return False
    t = c.get("teardown")
    if not (isinstance(t, dict) and t.get("port_closed") is True
            and is_int(t.get("child_returncode"))
            and t.get("ss_listen_lines_after") == []):
        return False
    srv = d.get("server")
    if not (isinstance(srv, dict) and isinstance(srv.get("sha256"), str)
            and c.get("server_sha256") == srv["sha256"]):
        return False
    argv = c["argv"]
    model = d.get("model")
    if not (flag_value(argv, "--port") == str(c.get("port"))
            and isinstance(model, dict)
            and flag_value(argv, "-m") == model.get("realpath")):
        return False
    slots = c["slots_n_ctx"]
    logged = [m.groups() for m in map(NSLOT_LINE.search, c["log_lines"]) if m]
    if not logged:
        return False
    ns, nc, _ = logged[-1]
    if int(ns) != c["total_slots"] or any(s != int(nc) for s in slots):
        return False
    if any(s != c["props_n_ctx"] for s in slots):
        return False
    if c.get("args") and c["id"].startswith("L"):
        for q in c["requests"]:
            if q.get("status") == 200 and (
                    q.get("tokens_predicted") != LOAD_REQUEST["n_predict"]
                    or q.get("truncated") is not False):
                return False
        if c["id"] in ("L1", "L2"):
            delta = c.get("concurrency_delta_s")
            if not (is_num(delta) and delta <= 0.05):
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
        if not isinstance(cid, str) or cid not in CELLS or ids.count(cid) != 1:
            continue
        args, kind = CELLS[cid]
        if c.get("args") == args and cell_ok(c, kind) and verdict_ok(c, d):
            observed.append(cid)
    ver = d.get("server_version") if isinstance(d, dict) else None
    sha = d.get("model_sha256") if isinstance(d, dict) else None
    bound = (isinstance(ver, str) and bool(BUILD.search(ver)) and sha == MODEL_SHA
             and all(c.get(k, v) == v for c in cells if isinstance(c, dict)
                     for k, v in (("server_version", ver),
                                  ("model_sha256", sha))))
    if not (isinstance(d, dict) and d.get("exit_code") == 0
            and d.get("error") is None):
        observed = []
    missing = [k for k in CELLS if k not in observed]
    print("registered", len(CELLS), "observed", len(observed), "bound", bound,
          "missing", missing)
    return 0


if __name__ == "__main__":
    sys.exit(main())
