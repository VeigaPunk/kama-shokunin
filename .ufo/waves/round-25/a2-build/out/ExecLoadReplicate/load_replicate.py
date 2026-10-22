#!/usr/bin/env python3
"""Round 25 C2 seat ExecLoadReplicate: independent replicate of L cells.

For each load cell (L1 concurrent, L2 concurrent, L3 sequential) with the
preregistered args, launches the lane-owned llama-server fixture on a free
loopback port in 47420-47439, builds a 1000-token prompt via /tokenize,
sends two /completion requests (n_predict 600, ignore_eos true,
cache_prompt false) concurrently (L1/L2) or one after the other (L3),
and records HTTP status, error text, tokens_predicted, timings and server
log lines around failures. Each cell is repeated 3 times, each repetition on
a freshly started server (one child at a time; port confirmed closed after).

Outputs:
  runs.json - full per-run records (cell, rep, ports, props, slots, log excerpts)
  runs.md   - per-run markdown table (the acceptance artifact)
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

SERVER = os.path.expanduser("~/.local/bin/llama-server")
MODEL = os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf")
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecLoadReplicate"
SCRATCH = "/fast/scratch/hyaku/kama-r25a2/ExecLoadReplicate"
PORT_BASE = 47420  # range 47420-47439, 127.0.0.1 only
REPS = 3
PROMPT_TOKENS = 1000
N_PREDICT = 600
STARTUP_TIMEOUT = 60.0
REQ_TIMEOUT = 180.0
KILL_GRACE = 5.0

CELLS = {
    "L1": {"args": "-c 0", "mode": "concurrent"},
    "L2": {"args": "-c 8192 -np 4 --no-kv-unified", "mode": "concurrent"},
    "L3": {"args": "-c 0", "mode": "sequential"},
}

ERROR_RE = re.compile(
    r"(?i)(context size|kv cache|kv_cache|exceed|out of (context|memory)|decode|"
    r"slot|failed|error|abort|invalid|insufficient)")
LOG_KEEP_RE = re.compile(
    r"(?i)(llama_context: n_ctx|kv_unified|n_ctx_slot|n_slots|slot|context|"
    r"kv cache|exceed|decode|error|fail|warn|abort|fit)")


def http_json(method, url, body=None, timeout=REQ_TIMEOUT):
    """Return (status, payload) where payload is parsed JSON or raw body text."""
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read()
        status = e.code
    try:
        return status, json.loads(raw)
    except Exception:
        return status, raw.decode("utf-8", "replace")


def port_free(port):
    r = subprocess.run(["ss", "-ltn"], capture_output=True, text=True)
    return f":{port} " not in r.stdout


def wait_ready(port, timeout=STARTUP_TIMEOUT):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            status, payload = http_json("GET", f"http://127.0.0.1:{port}/health", timeout=2)
            if status == 200 and isinstance(payload, dict) and payload.get("status") == "ok":
                return True, payload
            last = (status, payload)
        except Exception as e:
            last = ("exc", repr(e))
        time.sleep(0.25)
    return False, last


def launch_server(port, args, logpath):
    logf = open(logpath, "ab", buffering=0)
    cmd = [SERVER, "-m", MODEL, "--host", "127.0.0.1", "--port", str(port),
           "--no-webui", "--offline", "-v"] + args.split()
    proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT)
    return proc, logf


def stop_server(proc, logf, port):
    logf.close()
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=KILL_GRACE)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    # confirm port closed
    for _ in range(40):
        if port_free(port):
            return True
        time.sleep(0.25)
    return False


def tokenize_1000(port):
    """Build a >=1000-token prompt via /tokenize; return first 1000 token ids."""
    content = "The quick brown fox jumps over the lazy dog. " * 4000  # ~120k chars
    status, payload = http_json("POST", f"http://127.0.0.1:{port}/tokenize",
                                {"content": content})
    if status != 200 or not isinstance(payload, dict) or "tokens" not in payload:
        raise RuntimeError(f"/tokenize failed status={status} payload={payload!r}")
    tokens = payload["tokens"]
    if len(tokens) < PROMPT_TOKENS:
        raise RuntimeError(f"tokenize returned only {len(tokens)} tokens")
    return tokens[:PROMPT_TOKENS]


def read_props(port):
    status, p = http_json("GET", f"http://127.0.0.1:{port}/props")
    if status != 200 or not isinstance(p, dict):
        raise RuntimeError(f"/props failed status={status}")
    dg = p.get("default_generation_settings", {})
    return {
        "props_n_ctx": dg.get("n_ctx"),
        "total_slots": p.get("total_slots"),
    }


def read_slots(port):
    status, s = http_json("GET", f"http://127.0.0.1:{port}/slots")
    if status != 200 or not isinstance(s, list):
        raise RuntimeError(f"/slots failed status={status}")
    return [x.get("n_ctx") for x in s]


def read_models(port):
    status, m = http_json("GET", f"http://127.0.0.1:{port}/v1/models")
    if status != 200 or not isinstance(m, dict):
        raise RuntimeError(f"/v1/models failed status={status}")
    meta = {}
    data = m.get("data") or []
    if data and isinstance(data[0], dict):
        meta = data[0].get("meta") or {}
    return meta.get("n_ctx_train")


def extract_log(logpath):
    with open(logpath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    kv = []
    for ln in lines:
        ln = ln.rstrip("\n")
        if "llama_context: n_ctx" in ln:
            kv.append(ln)
    keep = [ln.rstrip("\n") for ln in lines if LOG_KEEP_RE.search(ln)]
    return kv, keep, lines


def log_excerpts(lines, width=3):
    """Return excerpts (up to 2*width+1 lines) around error-ish lines."""
    excerpts = []
    idx = [i for i, ln in enumerate(lines) if ERROR_RE.search(ln)]
    seen = set()
    for i in idx:
        lo, hi = max(0, i - width), min(len(lines), i + width + 1)
        if any(j in seen for j in range(lo, hi)):
            continue
        seen.update(range(lo, hi))
        excerpts.append("".join(lines[lo:hi]))
    return excerpts


def parse_kv_pool(kv_lines):
    """Return (pool_n_ctx, seq_n_ctx) from `llama_context: n_ctx` lines."""
    pool = seq = None
    for ln in kv_lines:
        m = re.search(r"llama_context: n_ctx\s*=\s*(\d+)", ln)
        if m and pool is None:
            pool = int(m.group(1))
        m = re.search(r"llama_context: n_ctx_seq\s*=\s*(\d+)", ln)
        if m and seq is None:
            seq = int(m.group(1))
    return pool, seq


def run_request(port, prompt_tokens, req_no, mode):
    body = {"prompt": prompt_tokens, "n_predict": N_PREDICT,
            "ignore_eos": True, "cache_prompt": False}
    t0 = time.time()
    status, payload = http_json("POST", f"http://127.0.0.1:{port}/completion", body)
    elapsed = time.time() - t0
    rec = {
        "req_no": req_no,
        "mode": mode,
        "status": status,
        "prompt_tokens": PROMPT_TOKENS,
        "n_predict": N_PREDICT,
        "elapsed_s": round(elapsed, 3),
    }
    if isinstance(payload, dict):
        err = payload.get("error")
        if err is not None:
            rec["error_text"] = err.get("message") if isinstance(err, dict) else str(err)
        rec["tokens_predicted"] = payload.get("tokens_predicted")
        rec["content_length"] = len(payload.get("content") or "")
        rec["timings"] = payload.get("timings")
        fr = payload.get("finished_reason")
        if fr is not None:
            rec["finished_reason"] = fr
    else:
        rec["error_text"] = str(payload)[:500]
    return rec


def run_cell(cell_id, rep):
    spec = CELLS[cell_id]
    port = PORT_BASE + (rep - 1) + {"L1": 0, "L2": 3, "L3": 6}[cell_id]
    if not port_free(port):
        raise RuntimeError(f"port {port} not free")
    logpath = os.path.join(SCRATCH, f"{cell_id}-rep{rep}.log")
    proc, logf = launch_server(port, spec["args"], logpath)
    run = {"cell": cell_id, "rep": rep, "port": port, "args": spec["args"],
           "request_mode": spec["mode"], "server_version": None,
           "launch_exit": None}
    try:
        ok, last = wait_ready(port)
        if not ok:
            run["ready"] = False
            run["ready_last"] = last
            raise RuntimeError(f"server not ready on {port}: {last!r}")
        run["ready"] = True
        props = read_props(port)
        run.update(props)
        run["slots_n_ctx"] = read_slots(port)
        run["models_n_ctx_train"] = read_models(port)
        prompt = tokenize_1000(port)
        run["prompt_tokens_used"] = len(prompt)
        if spec["mode"] == "concurrent":
            results = [None, None]
            def do(req_no):
                results[req_no] = run_request(port, prompt, req_no, spec["mode"])
            ths = [threading.Thread(target=do, args=(i,)) for i in (0, 1)]
            for t in ths:
                t.start()
            for t in ths:
                t.join()
            run["requests"] = results
        else:
            r0 = run_request(port, prompt, 0, spec["mode"])
            r1 = run_request(port, prompt, 1, spec["mode"])
            run["requests"] = [r0, r1]
        kv_lines, keep, all_lines = extract_log(logpath)
        pool, seq = parse_kv_pool(kv_lines)
        run["kv_pool_n_ctx"] = pool
        run["kv_pool_n_ctx_seq"] = seq
        run["log_lines"] = keep
        run["log_excerpts"] = log_excerpts(all_lines)
    finally:
        run["launch_exit"] = proc.poll()
        closed = stop_server(proc, logf, port)
        run["port_closed"] = closed
        if not closed:
            run["port_closed_warning"] = f"port {port} still open after grace"
    if run.get("ready"):
        run.pop("ready_last", None)
    return run


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    all_runs = []
    for cell_id in ("L1", "L2", "L3"):
        for rep in range(1, REPS + 1):
            run = run_cell(cell_id, rep)
            all_runs.append(run)
            print(f"{cell_id} rep{rep}: port {run['port']} "
                  f"kv_pool={run.get('kv_pool_n_ctx')} "
                  f"statuses={[r.get('status') for r in run['requests']]} "
                  f"errors={[r.get('error_text') for r in run['requests']]} "
                  f"pred={[r.get('tokens_predicted') for r in run['requests']]} "
                  f"port_closed={run['port_closed']}",
                  flush=True)
    with open(os.path.join(OUT, "runs.json"), "w") as f:
        json.dump({"cells": all_runs}, f, indent=2)
    # markdown table
    md = ["# ExecLoadReplicate per-run table (C2 L1-L3 replicate)",
          "", "| cell | rep | port | mode | /props n_ctx | slots | /v1/models n_ctx_train | kv pool (log) | req | HTTP status | error text | tokens_predicted | finished_reason | timing predicted_ms |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in all_runs:
        for q in r["requests"]:
            t = q.get("timings") or {}
            md.append(
                f"| {r['cell']} | {r['rep']} | {r['port']} | {r['request_mode']} | "
                f"{r.get('props_n_ctx')} | {r.get('slots_n_ctx')} | "
                f"{r.get('models_n_ctx_train')} | {r.get('kv_pool_n_ctx')} | "
                f"{q.get('req_no')} | {q.get('status')} | "
                f"{(q.get('error_text') or '')[:60]!r} | {q.get('tokens_predicted')} | "
                f"{q.get('finished_reason')} | {t.get('predicted_ms')} |")
    with open(os.path.join(OUT, "runs.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
