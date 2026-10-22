#!/usr/bin/env python3
"""ExecRawReplicate -- C2 independent replicate of registered config cells K1-K8 and X1-X3.

For each cell: launch llama-server b11755 with the amendment-2 launch rule
(127.0.0.1, free unregistered port in 47440-47459, --no-webui --offline -v),
wait for /health 200, save raw /props, /slots, /v1/models bytes and the full
log, extract the registered fields, kill the child and confirm the port is
closed. One child at a time. No capacity tool used.
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request

OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecRawReplicate"
SERVER = os.path.expanduser("~/.local/bin/llama-server")
MODEL = os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf")
PORT_MIN, PORT_MAX = 47440, 47459
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"

# (id, registered args string) -- exact bytes of the amendment-2 CELLS table
CELLS = [
    ("K1", "-c 0"),
    ("K2", "-c 2048 -np 2 --no-kv-unified"),
    ("K3", "-c 2048 -np 2 --kv-unified"),
    ("K4", "-c 1024 -np 1"),
    ("K5", "-c 4096 -np 1"),
    ("K6", "-c 1000 -np 3 --no-kv-unified"),
    ("K7", "-np 2 --kv-unified-per-slot 512"),
    ("K8", "-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512"),
    ("X1", "-np 4 --no-kv-unified"),
    ("X2", "-c 8192 -np 4 --no-kv-unified"),
    ("X3", "-np 4 --no-kv-unified --fit off"),
]

# amendment-2 predictions for grading; only fields the amendment claims are
# asserted. K1-K8 are replication-level (K6 measurement-only); X1-X3 carry
# source/author predictions (pool and per-slot).
PREDICTIONS = {
    "K1": {"slots": [2048] * 4, "pool": 2048, "total_slots": 4,
            "kv_unified": True,
            "note": "prediction: total_slots 4 (auto), kv_unified true, per-slot n_ctx 2048 (training context)"},
    "K2": {"slots": [1024, 1024],
            "note": "prediction: per-slot n_ctx 1024"},
    "K3": {"slots": [2048, 2048],
            "note": "prediction: per-slot n_ctx 2048"},
    "K4": {"slots": [1024], "kv_unified": False,
            "note": "prediction: kv_unified false (slots set explicitly), per-slot n_ctx 1024"},
    "K5": {"slots": [2048],
            "note": "prediction: per-slot n_ctx capped at training context 2048"},
    "K6": {"note": "no prediction (measurement only)"},
    "K7": {"slots": [512, 512], "pool": 1024,
            "note": "prediction: pool 1024, per-slot n_ctx 512"},
    "K8": {"slots": [512] * 4,
            "note": "prediction: per-slot n_ctx 512"},
    "X1": {"slots": [2048] * 4, "pool": 8192,
            "note": "source prediction (CriticLearningBar): pool 8192, per-slot 2048; round-20 nctx-crosscheck predicts 512"},
    "X2": {"slots": [2048] * 4, "pool": 8192,
            "note": "prediction: pool 8192, per-slot 2048; /props, /slots, /v1/models equal K1's"},
    "X3": {"slots": [512] * 4, "pool": 2048,
            "note": "author inference: pool 2048, per-slot 512 (fit off -> n_ctx_train 2048 split over 4)"},
}


def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def listening_ports():
    out = subprocess.run(["ss", "-ltn"], capture_output=True, text=True).stdout
    ports = set()
    for m in re.finditer(r"[:.](\d{4,5})\s", out):
        p = int(m.group(1))
        if PORT_MIN <= p <= PORT_MAX:
            ports.add(p)
    return ports


def free_port(used):
    busy = listening_ports() | set(used)
    for p in range(PORT_MIN, PORT_MAX + 1):
        if p not in busy:
            return p
    return None


def wait_ready(port, timeout=30):
    url = "http://127.0.0.1:%d/health" % port
    t0 = time.time()
    attempts = 0
    while time.time() - t0 < timeout:
        attempts += 1
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True, attempts
        except Exception:
            pass
        time.sleep(0.2)
    return False, attempts


def fetch_raw(path, port):
    url = "http://127.0.0.1:%d/%s" % (port, path)
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.read(), r.status


def sha256b(data):
    return hashlib.sha256(data).hexdigest()


def kill_and_confirm(proc, port):
    res = {"child_returncode": None, "sigterm": False, "sigkill": False,
           "port_closed": None, "error": None}
    try:
        proc.terminate()
        res["sigterm"] = True
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            res["sigkill"] = True
            proc.wait(timeout=10)
        res["child_returncode"] = proc.returncode
    except Exception as exc:
        res["error"] = str(exc)
    # confirm port closed
    t0 = time.time()
    while time.time() - t0 < 10:
        if port not in listening_ports():
            res["port_closed"] = True
            break
        time.sleep(0.2)
    if res["port_closed"] is None:
        res["port_closed"] = False
    return res


def extract(props_b, slots_b, models_b, log_text):
    props = json.loads(props_b)
    slots = json.loads(slots_b)
    models = json.loads(models_b)
    props_n_ctx = props["default_generation_settings"]["n_ctx"]
    total_slots = props["total_slots"]
    slots_n_ctx = [s["n_ctx"] for s in slots]
    meta = models["data"][0]["meta"]
    models_n_ctx_train = meta["n_ctx_train"]
    models_n_ctx = meta.get("n_ctx")
    pat = re.compile(r"n_ctx_slot|kv_unified|capp|rounding|n_ctx_seq|llama_context: n_ctx|llama_kv_cache: size|padding", re.I)
    log_lines = [ln.rstrip() for ln in log_text.splitlines() if pat.search(ln)]
    # llama_context blocks: each "llama_context: n_ctx = N" line opens a block;
    # the following "llama_context: n_ctx_seq = M" belongs to it. The last
    # block is the operative server slot context (a fit probe may print an
    # earlier block with different values, e.g. X1).
    blocks = []
    cur = None
    for ln in log_lines:
        m = re.search(r"llama_context: n_ctx\s*=\s*(\d+)$", ln)
        if m:
            cur = {"n_ctx": int(m.group(1))}
            blocks.append(cur)
            continue
        m = re.search(r"llama_context: n_ctx_seq\s*=\s*(\d+)$", ln)
        if m and cur is not None and "n_ctx_seq" not in cur:
            cur["n_ctx_seq"] = int(m.group(1))
    last = blocks[-1] if blocks else {}
    kv_pool_n_ctx = last.get("n_ctx")
    kv_seq_n_ctx = last.get("n_ctx_seq")
    load_model_lines = [ln for ln in log_lines if "load_model: initializing" in ln]
    return {
        "props_n_ctx": props_n_ctx,
        "total_slots": total_slots,
        "slots_n_ctx": slots_n_ctx,
        "models_n_ctx_train": models_n_ctx_train,
        "models_n_ctx": models_n_ctx,
        "kv_pool_n_ctx": kv_pool_n_ctx,
        "kv_seq_n_ctx": kv_seq_n_ctx,
        "blocks": blocks,
        "load_model_lines": load_model_lines,
        "kv_unified_lines": [ln for ln in log_lines if "kv_unified" in ln],
        "log_lines": log_lines,
    }


def run_cell(cid, args_str, port):
    cell_dir = os.path.join(OUT, cid)
    os.makedirs(cell_dir, exist_ok=True)
    argv = [SERVER, "-m", MODEL, "--host", "127.0.0.1", "--port", str(port),
            "--no-webui", "--offline", "-v"] + args_str.split()
    log_path = os.path.join(cell_dir, "server.log")
    meta = {"id": cid, "args": args_str, "port": port,
            "started_utc": now_utc(), "port_free_before": port not in listening_ports(),
            "argv": argv}
    with open(log_path, "wb") as logf:
        proc = subprocess.Popen(argv, stdout=logf, stderr=subprocess.STDOUT)
    meta["pid"] = proc.pid
    ready, attempts = wait_ready(port)
    meta["ready"] = ready
    meta["health_attempts"] = attempts
    if not ready:
        # give the child a moment to dump its error into the log
        time.sleep(1.0)
        meta["error"] = "server did not become ready"
        meta["teardown"] = kill_and_confirm(proc, port)
        with open(log_path, "r", errors="replace") as f:
            meta["log_tail"] = f.read()[-2000:]
        return meta, None
    raw = {}
    for name, path in (("props", "props"), ("slots", "slots"),
                       ("v1_models", "v1/models")):
        data, status = fetch_raw(path, port)
        raw[name] = data
        fn = os.path.join(cell_dir, {"props": "props.json", "slots": "slots.json",
                                     "v1_models": "v1_models.json"}[name])
        with open(fn, "wb") as f:
            f.write(data)
        meta["http_%s" % name] = status
        meta["bytes_%s" % name] = len(data)
        meta["sha256_%s" % name] = sha256b(data)
    with open(log_path, "r", errors="replace") as f:
        log_text = f.read()
    meta["teardown"] = kill_and_confirm(proc, port)
    meta["ended_utc"] = now_utc()
    ex = extract(raw["props"], raw["slots"], raw["v1_models"], log_text)
    return meta, ex


def main():
    used_ports = []
    cells_out = []
    summary = []
    for cid, args_str in CELLS:
        port = free_port(used_ports)
        if port is None:
            print("no free port in 47440-47459 for %s" % cid)
            sys.exit(1)
        used_ports.append(port)
        meta, ex = run_cell(cid, args_str, port)
        row = {"id": cid, "args": args_str, "port": port,
               "ready": meta.get("ready"), "teardown": meta.get("teardown")}
        if ex is not None:
            row["props_n_ctx"] = ex["props_n_ctx"]
            row["total_slots"] = ex["total_slots"]
            row["slots_n_ctx"] = ex["slots_n_ctx"]
            row["models_n_ctx_train"] = ex["models_n_ctx_train"]
            row["models_n_ctx"] = ex["models_n_ctx"]
            row["kv_pool_n_ctx"] = ex["kv_pool_n_ctx"]
            row["kv_seq_n_ctx"] = ex["kv_seq_n_ctx"]
            row["blocks"] = ex["blocks"]
            row["load_model_lines"] = ex["load_model_lines"]
            row["sha256"] = {k: meta["sha256_" + k] for k in
                             ("props", "slots", "v1_models")}
            # grading against amendment-2 predictions (only claimed fields)
            pred = PREDICTIONS[cid]
            flag = []
            if "slots" in pred and ex["slots_n_ctx"] != pred["slots"]:
                flag.append("slots_n_ctx %s != predicted %s" %
                            (ex["slots_n_ctx"], pred["slots"]))
            if "pool" in pred and ex["kv_pool_n_ctx"] != pred["pool"]:
                flag.append("kv_pool_n_ctx %s != predicted %s" %
                            (ex["kv_pool_n_ctx"], pred["pool"]))
            if "total_slots" in pred and ex["total_slots"] != pred["total_slots"]:
                flag.append("total_slots %s != predicted %s" %
                            (ex["total_slots"], pred["total_slots"]))
            if "kv_unified" in pred:
                kv_has_true = any("kv_unified " in ln and "true" in ln
                                  for ln in ex["kv_unified_lines"])
                kv_has_false = any("kv_unified " in ln and "false" in ln
                                   for ln in ex["kv_unified_lines"])
                if pred["kv_unified"] and not kv_has_true:
                    flag.append("kv_unified expected true, not seen in log")
                if not pred["kv_unified"] and not kv_has_false:
                    flag.append("kv_unified expected false, not seen in log")
            row["prediction_note"] = pred["note"]
            row["flag"] = flag
            # register-shaped cell record for the final receipt
            cells_out.append({
                "id": cid,
                "args": args_str,
                "props_n_ctx": ex["props_n_ctx"],
                "total_slots": ex["total_slots"],
                "slots_n_ctx": ex["slots_n_ctx"],
                "models_n_ctx_train": ex["models_n_ctx_train"],
                "kv_pool_n_ctx": ex["kv_pool_n_ctx"],
                "log_lines": ex["log_lines"],
            })
        else:
            row["error"] = meta.get("error")
            row["log_tail"] = meta.get("log_tail")
        summary.append(row)
        with open(os.path.join(OUT, "run-progress.json"), "w") as f:
            json.dump(summary, f, indent=1)
        print("cell", cid, "ready", meta.get("ready"),
              "props_n_ctx", row.get("props_n_ctx"),
              "slots", row.get("slots_n_ctx"),
              "pool", row.get("kv_pool_n_ctx"),
              "flags", row.get("flag"))
    receipt = {
        "schema": "kama-context-capacity/v1-count-c2-config-cells",
        "seat": "ExecRawReplicate",
        "attempt": 2,
        "scope": "config cells K1-K8, X1-X3 (L1-L3 load cells not in this seat)",
        "server_version": "0.7.0-dev (build 11755, commit 704366d76)",
        "model_sha256": MODEL_SHA,
        "model_path": MODEL,
        "host": "127.0.0.1",
        "port_range": [PORT_MIN, PORT_MAX],
        "cells": cells_out,
        "summary": summary,
        "written_utc": now_utc(),
    }
    with open(os.path.join(OUT, "receipt-config-cells.json"), "w") as f:
        json.dump(receipt, f, indent=1)
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print("cells_run", len(summary), "cells_extracted", len(cells_out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
