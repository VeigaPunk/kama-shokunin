#!/usr/bin/env python3
"""ReviewerRawHashes: re-derive the committed round-25 C2 receipt from its raw bytes.

Reads committed bytes at fa3b62ae through `git show`, hashes the on-disk model,
llama-server binary and tool file read-only, runs the committed counter
count-c2.py, and reads the pinned llama.cpp source copies from scratch. Starts no
server. Writes TSV tables and mismatches.txt under OUT; synthetic negatives go to
SCRATCH/mutants and are never written to the lane.

Usage: python3 check_receipt_raw.py
"""
import copy
import hashlib
import json
import os
import re
import shlex
import subprocess
from datetime import datetime

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "fa3b62ae6475d111eb466d79af616aeebb08bbb9"
RD = ".ufo/waves/round-25/final"
RECEIPT_PATH = f"{RD}/context-capacity-receipt.json"
COUNTER_PATH = ".ufo/waves/round-25/count-c2.py"
TOOL_PATH = "tools/kama-context-capacity.py"
OUT = os.path.join(LANE, ".ufo/waves/round-25/a2-falsify/out/ReviewerRawHashes")
SCRATCH = "/fast/scratch/hyaku/kama-r25a2w2/ReviewerRawHashes"
SERVER_REAL = "/home/vgpnk/.local/opt/llama-b11755/llama-server"
MODEL_REAL = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"
SUFFIX = {"raw_health": "health.body", "raw_models": "models.body",
          "raw_props": "props.body", "raw_slots": "slots.body",
          "server_log": "server.log"}
LOG_KEEP = re.compile(r"n_ctx|kv_unified|n_seq|capping|rounding|KV pool|llama_kv_cache: size",
                      re.IGNORECASE)
KV_POOL_RE = re.compile(r"llama_context: n_ctx\s*=\s*(\d+)")
SLOT_RE = re.compile(r"n_slots = (\d+), n_ctx_slot = (\d+), kv_unified = '(true|false)'")
TRAIN_RE = re.compile(r"print_info: n_ctx_train\s*=\s*(\d+)")
TS_RE = re.compile(r"^(\d+)\.(\d{2})\.(\d{3})\.(\d{3}) ")
PROC_RE = re.compile(r"slot launch_slot_: id\s+\d+ \| task (\d+) \| processing task, is_child = 0")
RELEASE_RE = re.compile(
    r"slot\s+release: id\s+\d+ \| task (\d+) \| stop processing: n_tokens = (\d+), truncated = (\d)")
DECODE_RE = re.compile(
    r"slot handle_last_: id\s+\d+ \| task (\d+) \| slot decode token, id=\d+, "
    r"n_ctx = (\d+), n_tokens = (\d+), truncated = (\d)")
NGEN_RE = re.compile(r"slot process_toke: id\s+\d+ \| task (\d+) \| n_gen = (\d+), n_remaining = 0")
SEND_ERR_RE = re.compile(r"srv\s+send_error: task id = (\d+), error: (.*)$")
BUILD_TEXT = "build 11755 (704366d76)"
LOAD_PROMPT = 1000
LOAD_NPRED = 600
CONCURRENT_WINDOW = 0.05

CHECKS = [0]
MISMATCH = []


def expect(ok, cid, what, receipt_val, derived_val):
    CHECKS[0] += 1
    if not ok:
        MISMATCH.append((cid, what, repr(receipt_val)[:200], repr(derived_val)[:200]))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    with open(path, "rb") as fh:
        return sha(fh.read())


def git_show(path, rev=TIP):
    return subprocess.run(["git", "-C", LANE, "show", f"{rev}:{path}"],
                          capture_output=True, check=True).stdout


def ts_s(line):
    m = TS_RE.match(line)
    if not m:
        return None
    f1, f2, f3, f4 = (int(x) for x in m.groups())
    return f1 * 3600 + f2 * 60 + f3 / 1000.0 + f4 / 1e6


def iso(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")


def load_committed_raw(cell_ids):
    return {(cid, key): git_show(f"{RD}/raw/{cid}.{suf}")
            for cid in cell_ids for key, suf in SUFFIX.items()}


def derive_load(c, text, tables):
    """Check the two load requests of an L cell against the server log."""
    cid = c["id"]
    procs, rel, first_tok, truncs, ngen, serr = [], {}, {}, {}, {}, {}
    for line in text.splitlines():
        m = PROC_RE.search(line)
        if m:
            procs.append((ts_s(line), int(m.group(1))))
        m = RELEASE_RE.search(line)
        if m:
            rel.setdefault(int(m.group(1)), (ts_s(line), int(m.group(2)), int(m.group(3))))
        m = DECODE_RE.search(line)
        if m:
            tk = int(m.group(1))
            first_tok.setdefault(tk, int(m.group(3)))
            truncs.setdefault(tk, set()).add(int(m.group(4)))
        m = NGEN_RE.search(line)
        if m:
            ngen[int(m.group(1))] = int(m.group(2))
        m = SEND_ERR_RE.search(line)
        if m:
            serr.setdefault(int(m.group(1)), m.group(2))
    procs = sorted(procs)[:2]
    expect(len(procs) == 2, cid, "two load tasks in server log", len(procs), 2)
    if len(procs) != 2:
        return
    (s1, t1), (s2, t2) = procs
    e1 = rel.get(t1, (None,))[0]
    overlap = e1 is not None and s2 < e1
    expect(overlap == (c["request_mode"] == "concurrent"), cid,
           "log overlap of the two tasks matches request_mode", c["request_mode"], overlap)
    expect(len(c["requests"]) == 2, cid, "receipt request count", len(c["requests"]), 2)
    if len(c["requests"]) != 2:
        return
    q0, q1 = c["requests"]
    if c["request_mode"] == "concurrent":
        gap = abs(q0["t_start"] - q1["t_start"])
        expect(c["concurrency_delta_s"] is not None and c["concurrency_delta_s"] <= CONCURRENT_WINDOW
               and abs(c["concurrency_delta_s"] - gap) < 1e-4,
               cid, "concurrency_delta_s equals start gap and is within window",
               c["concurrency_delta_s"], round(gap, 6))
    else:
        expect(c["concurrency_delta_s"] is None, cid, "concurrency_delta_s on sequential cell",
               c["concurrency_delta_s"], None)
    for idx, ((st, tk), q) in enumerate(zip(procs, c["requests"])):
        end = rel.get(tk, (None,))[0]
        err = serr.get(tk)
        n_gen = ngen.get(tk)
        expect(q["prompt_tokens"] == LOAD_PROMPT and first_tok.get(tk) == LOAD_PROMPT, cid,
               f"request {idx}: prompt tokens equal first decode n_tokens",
               q["prompt_tokens"], first_tok.get(tk))
        expect(q["n_predict"] == LOAD_NPRED, cid, f"request {idx}: n_predict",
               q["n_predict"], LOAD_NPRED)
        if err is None:
            expect(q["status"] == 200 and q["error"] is None and q["tokens_predicted"] == LOAD_NPRED
                   and n_gen == LOAD_NPRED and q["truncated"] is False and truncs.get(tk) == {0},
                   cid, f"request {idx}: no send_error, 600 tokens generated, not truncated",
                   (q["status"], q["tokens_predicted"], q["truncated"]),
                   ("no send_error", n_gen, sorted(truncs.get(tk, []))))
        else:
            expect(q["status"] == 500 and q["error"] == err and q["error_type"] == "server_error",
                   cid, f"request {idx}: send_error in log is status 500 server_error with same text",
                   (q["status"], q["error"], q["error_type"]), (500, err, "server_error"))
        dur = (end - st) if (end is not None and st is not None) else None
        expect(dur is not None and abs(dur - q["elapsed_s"]) <= 0.01, cid,
               f"request {idx}: log task duration within 10 ms of elapsed_s",
               q["elapsed_s"], round(dur, 4) if dur is not None else None)
        expect(abs(round(q["t_end"] - q["t_start"], 3) - q["elapsed_s"]) <= 0.001, cid,
               f"request {idx}: elapsed_s equals t_end - t_start",
               q["elapsed_s"], round(q["t_end"] - q["t_start"], 3))
        tables["lout"].append([cid, idx, tk, q["status"], q["error"], q["error_type"],
                               q["tokens_predicted"], q["truncated"], q["prompt_tokens"],
                               q["n_predict"], q["elapsed_s"], round(st, 6),
                               round(end, 6) if end is not None else None,
                               round(dur, 4) if dur is not None else None,
                               first_tok.get(tk), n_gen, err or "", c["request_mode"], overlap])


def check_receipt(rec, raw, registered, tables):
    ids = [c["id"] for c in rec["cells"]]
    expect(sorted(ids) == sorted(registered), "ALL", "cell id set equals registered set",
           sorted(ids), sorted(registered))
    for c in rec["cells"]:
        cid = c["id"]
        expect(set(c["raw"]) == set(SUFFIX), cid, "raw map keys", sorted(c["raw"]), sorted(SUFFIX))
        for key, suf in SUFFIX.items():
            body = raw[(cid, key)]
            h = sha(body)
            ok = h == c["raw"].get(key)
            expect(ok, cid, f"sha256 of {cid}.{suf} equals receipt raw.{key}", c["raw"].get(key), h)
            tables["raw"].append([cid, key, f"{RD}/raw/{cid}.{suf}", len(body), h,
                                  c["raw"].get(key), ok])
        props = json.loads(raw[(cid, "raw_props")])
        slots = json.loads(raw[(cid, "raw_slots")])
        models = json.loads(raw[(cid, "raw_models")])
        health = json.loads(raw[(cid, "raw_health")])
        text = raw[(cid, "server_log")].decode("utf-8")
        lines = text.splitlines()
        d_props_n = props["default_generation_settings"]["n_ctx"]
        d_total = props["total_slots"]
        d_slots = [s["n_ctx"] for s in slots]
        d_trn = models["data"][0]["meta"]["n_ctx_train"]
        d_trn_log = [int(m.group(1)) for m in (TRAIN_RE.search(x) for x in lines) if m]
        d_pool = [int(m.group(1)) for m in KV_POOL_RE.finditer(text)]
        d_slot_lines = [m.groups() for m in (SLOT_RE.search(x) for x in lines) if m]
        d_keep = [x for x in lines if LOG_KEEP.search(x)]
        argv_exp = ([SERVER_REAL, "-m", MODEL_REAL, "--host", "127.0.0.1", "--port", str(c["port"]),
                     "--no-webui", "--offline", "-v"] + shlex.split(c["args"]))
        expect(c["props_n_ctx"] == d_props_n, cid,
               "props_n_ctx equals props.body default_generation_settings.n_ctx",
               c["props_n_ctx"], d_props_n)
        expect(c["total_slots"] == d_total, cid, "total_slots equals props.body total_slots",
               c["total_slots"], d_total)
        expect(c["slots_n_ctx"] == d_slots and len(d_slots) == d_total, cid,
               "slots_n_ctx equals slots.body n_ctx list", c["slots_n_ctx"], d_slots)
        expect(c["models_n_ctx_train"] == d_trn, cid,
               "models_n_ctx_train equals models.body meta.n_ctx_train",
               c["models_n_ctx_train"], d_trn)
        expect(bool(d_trn_log) and all(x == d_trn for x in d_trn_log), cid,
               "n_ctx_train in server log print_info equals models.body", d_trn_log, d_trn)
        expect(health == {"status": "ok"}, cid, "health.body is status ok", health, {"status": "ok"})
        expect(c["log_lines"] == d_keep, cid,
               "log_lines equals exact LOG_KEEP filter of server.log",
               len(c["log_lines"]), len(d_keep))
        expect(c["kv_pool_candidates"] == d_pool, cid,
               "kv_pool_candidates equals every llama_context n_ctx line in server.log",
               c["kv_pool_candidates"], d_pool)
        expect(bool(d_pool) and c["kv_pool_n_ctx"] == d_pool[-1], cid,
               "kv_pool_n_ctx equals last llama_context n_ctx line",
               c["kv_pool_n_ctx"], d_pool[-1:])
        slot_ok = (len(d_slot_lines) == 1 and int(d_slot_lines[0][0]) == c["total_slots"]
                   and all(int(x) == int(d_slot_lines[0][1]) for x in d_slots))
        expect(slot_ok, cid, "one startup slot line: n_slots equals total_slots, n_ctx_slot equals /slots",
               d_slot_lines, (c["total_slots"], d_slots))
        expect(c["argv"] == argv_exp, cid, "argv equals launch command built from args",
               c["argv"], argv_exp)
        expect(f"listening on http://127.0.0.1:{c['port']}" in text, cid,
               "server log names the receipt port", c["port"], "absent")
        expect(BUILD_TEXT in text, cid, "server log build line", BUILD_TEXT, "absent")
        expect("cleaning up before exit" in text, cid, "server log clean-exit line",
               "present", "absent")
        td = c["teardown"]
        expect(td.get("child_returncode") == 0 and td.get("port_closed") is True
               and td.get("ss_listen_lines_after") == [], cid,
               "teardown: child rc 0, port closed, no listener after", td, "rc 0, closed, no listener")
        tables["rederive"].append([cid, c["args"], c["props_n_ctx"], d_props_n,
                                   c["total_slots"], d_total, c["slots_n_ctx"], d_slots,
                                   c["models_n_ctx_train"], d_trn,
                                   d_trn_log[0] if d_trn_log else None,
                                   c["kv_pool_n_ctx"], d_pool[-1] if d_pool else None,
                                   " ".join(d_slot_lines[0]) if d_slot_lines else None,
                                   c["port"]])
        if cid.startswith("L"):
            derive_load(c, text, tables)
        else:
            expect(c["requests"] == [] and c["request_mode"] is None, cid,
                   "config cell has no requests", c["requests"], [])


def top_level(rec):
    s = rec["summary"]
    expect(s["observed"] == 14 and s["cells"] == 14 and s["all_ports_closed"] is True, "ALL",
           "summary: 14 of 14 observed, all ports closed", s, "14 of 14, closed")
    expect(rec["cells_drift"] == [] and rec["error"] is None and rec["exit_code"] == 0, "ALL",
           "cells_drift, error, exit_code", (rec["cells_drift"], rec["error"], rec["exit_code"]),
           ([], None, 0))
    lo, hi = rec["port_range"]
    ports = [c["port"] for c in rec["cells"]]
    expect(len(set(ports)) == len(ports) and all(lo <= p <= hi and p not in rec["port_refusal_set"]
                                                 for p in ports), "ALL",
           "ports unique, inside port_range, outside port_refusal_set", ports, rec["port_range"])
    prev = None
    for c in rec["cells"]:
        st, sp = iso(c["started_utc"]), iso(c["stopped_utc"])
        expect(st < sp, c["id"], "started_utc before stopped_utc", c["started_utc"], c["stopped_utc"])
        if prev is not None:
            expect(prev <= st, c["id"], "cell starts after previous cell stopped", prev, st)
        prev = sp
    expect(iso(rec["started_utc"]) <= iso(rec["cells"][0]["started_utc"]) and prev <= iso(rec["ended_utc"]),
           "ALL", "run window encloses all cells", (rec["started_utc"], rec["ended_utc"]),
           (rec["cells"][0]["started_utc"], prev))
    expect(rec["model_sha256"] == sha_file(MODEL_REAL) and rec["model"]["size_bytes"] == os.path.getsize(MODEL_REAL),
           "ALL", "model file on disk: sha256 and size", rec["model_sha256"], sha_file(MODEL_REAL))
    expect(rec["server"]["sha256"] == sha_file(SERVER_REAL), "ALL",
           "llama-server binary on disk sha256", rec["server"]["sha256"], sha_file(SERVER_REAL))
    tool_tip = sha(git_show(TOOL_PATH))
    tool_wt = sha_file(os.path.join(LANE, TOOL_PATH))
    expect(rec["tool"]["sha256"] == tool_tip == tool_wt, "ALL",
           "tool sha256: receipt equals committed equals working copy", rec["tool"]["sha256"], tool_tip)
    expect(isinstance(rec["server_version"], str) and "build 11755, commit 704366d76" in rec["server_version"],
           "ALL", "server_version names build 11755, commit 704366d76", rec["server_version"],
           "build 11755, commit 704366d76")
    expect(all(c["server_sha256"] == rec["server"]["sha256"] and c["model_sha256"] == rec["model_sha256"]
               for c in rec["cells"]), "ALL", "per-cell binding equals top-level binding", "", "")


def run_counter(counter_bytes, receipt_path):
    res = subprocess.run(["python3", "-", receipt_path], cwd=LANE, input=counter_bytes,
                         capture_output=True)
    return res.returncode, res.stdout.decode().strip(), res.stderr.decode().strip()


def mutants(rec, raw):
    out = []
    m = copy.deepcopy(rec)
    next(c for c in m["cells"] if c["id"] == "K1")["props_n_ctx"] = 2047
    out.append(("M1", "K1 props_n_ctx 2048 -> 2047, receipt field only", m, raw))
    m = copy.deepcopy(rec)
    for q in next(c for c in m["cells"] if c["id"] == "L1")["requests"]:
        q["status"] = 200
    out.append(("M2", "L1 both requests status 500 -> 200, error text kept", m, raw))
    m = copy.deepcopy(rec)
    k5 = next(c for c in m["cells"] if c["id"] == "K5")
    k5["log_lines"] = [x.replace("= 4096", "= 2048") if "llama_context: n_ctx" in x else x
                       for x in k5["log_lines"]]
    k5["kv_pool_candidates"] = [2048 if v == 4096 else v for v in k5["kv_pool_candidates"]]
    k5["kv_pool_n_ctx"] = 2048
    out.append(("M3", "K5 pool 4096 -> 2048 in embedded log and pool fields, self-consistent", m, raw))
    m = copy.deepcopy(rec)
    k2 = next(c for c in m["cells"] if c["id"] == "K2")
    k2["raw"]["raw_props"] = k2["raw"]["raw_health"]
    out.append(("M4", "K2 raw_props hash replaced in receipt map only", m, raw))
    raw2 = dict(raw)
    body = raw[("K2", "raw_props")]
    new = body.replace(b'"n_ctx":1024', b'"n_ctx":1025', 1)
    assert new != body
    raw2[("K2", "raw_props")] = new
    out.append(("M5", "K2 props.body bytes changed in memory (n_ctx 1024 -> 1025), receipt unchanged",
                rec, raw2))
    return out


def write_tsv(name, header, rows):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join("" if v is None else str(v) for v in r) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    mut_dir = os.path.join(SCRATCH, "mutants")
    os.makedirs(mut_dir, exist_ok=True)
    rec = json.loads(git_show(RECEIPT_PATH))
    counter_bytes = git_show(COUNTER_PATH)
    ns = {"__name__": "count_c2_tip"}
    exec(compile(counter_bytes, COUNTER_PATH, "exec"), ns)
    registered = list(ns["CELLS"].keys())
    raw = load_committed_raw(registered)
    tables = {"raw": [], "rederive": [], "lout": []}
    CHECKS[0] = 0
    MISMATCH.clear()
    top_level(rec)
    check_receipt(rec, raw, registered, tables)
    main_mismatch = list(MISMATCH)
    main_checks = CHECKS[0]
    rc, counter_out, counter_err = run_counter(counter_bytes, RECEIPT_PATH)

    write_tsv("raw-sha-table.tsv", ["cell", "raw_key", "path", "bytes", "sha256_derived",
                                    "sha256_receipt", "match"], tables["raw"])
    write_tsv("rederivation-table.tsv", ["cell", "args", "props_n_ctx_receipt", "props_n_ctx_raw",
                                         "total_slots_receipt", "total_slots_raw",
                                         "slots_n_ctx_receipt", "slots_n_ctx_raw",
                                         "n_ctx_train_receipt", "n_ctx_train_models_raw",
                                         "n_ctx_train_log_raw", "kv_pool_receipt",
                                         "kv_pool_last_line_raw", "slot_line_raw", "port"],
              tables["rederive"])
    write_tsv("l-outcome-table.tsv", ["cell", "request_index", "log_task", "status", "error",
                                      "error_type", "tokens_predicted", "truncated",
                                      "prompt_tokens", "n_predict", "elapsed_s_receipt",
                                      "log_task_start_s", "log_task_release_s", "log_duration_s",
                                      "log_first_decode_n_tokens", "log_n_gen_final",
                                      "log_send_error", "request_mode", "log_overlap"],
              tables["lout"])
    with open(os.path.join(OUT, "mismatches.txt"), "w") as fh:
        fh.write(f"committed receipt at {TIP}: {len(main_mismatch)} mismatches over {main_checks} checks\n")
        for cid, what, rv, dv in main_mismatch:
            fh.write(f"{cid}\t{what}\treceipt={rv}\traw={dv}\n")

    neg_rows = []
    for name, desc, mrec, mraw in mutants(rec, raw):
        path = os.path.join(mut_dir, f"{name}.json")
        with open(path, "w") as fh:
            json.dump(mrec, fh)
        mrc, mout, merr = run_counter(counter_bytes, path)
        MISMATCH.clear()
        check_receipt(mrec, mraw, registered, {"raw": [], "rederive": [], "lout": []})
        first = "; ".join(f"{a}: {w}" for a, w, _, _ in MISMATCH[:3])
        neg_rows.append([name, desc, mout, mrc, len(MISMATCH), first])
    write_tsv("synthetic-negatives.tsv", ["mutant", "description", "committed_counter_output",
                                          "counter_exit", "raw_mismatch_count", "first_raw_mismatches"],
              neg_rows)

    print(f"committed receipt: checks={main_checks} mismatches={len(main_mismatch)}")
    for item in main_mismatch:
        print("  MISMATCH", item)
    print(f"committed counter on committed receipt: exit={rc} out='{counter_out}' err='{counter_err}'")
    for r in neg_rows:
        print(f"mutant {r[0]}: counter='{r[2]}' exit={r[3]} raw_mismatches={r[4]} first=[{r[5]}]")


if __name__ == "__main__":
    main()
