#!/usr/bin/env python3
"""DataG11 live probe: request-field outcomes on port 48211 (llama-server b11755)."""
import hashlib
import json
import os
import pathlib
import signal
import socket
import subprocess
import sys
import time
import urllib.request

HOST = "127.0.0.1"
PORT = 48211
OPT = pathlib.Path.home() / ".local/opt/llama-b11755"
SERVER = OPT / "llama-server"
MODEL = pathlib.Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
OUT = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG11")
SCRATCH = pathlib.Path("/fast/scratch/hyaku/kama-r28/w1/DataG11")
BASE = {"prompt": "Once upon a time", "n_predict": 1}
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

VARIANTS = [
    ("base", {}),
    ("unknown_control", {"not_a_field": 1}),
    ("ngram_size_m_7", {"speculative.ngram_size_m": 7}),
    ("ngram_size_m_neg1", {"speculative.ngram_size_m": -1}),
    ("ngram_size_m_huge", {"speculative.ngram_size_m": 2147483648}),
    ("ngram_min_hits_9", {"speculative.ngram_min_hits": 9}),
    ("ngram_min_hits_neg5", {"speculative.ngram_min_hits": -5}),
    ("lora_one", {"lora": [{"id": 0, "scale": 0.5}]}),
    ("lora_str", {"lora": "x"}),
    ("lora_empty", {"lora": []}),
    ("lora_dup", {"lora": [{"id": 0, "scale": 1.0}, {"id": 0, "scale": 0.5}]}),
    ("lora_noscale", {"lora": [{"id": 0}]}),
    ("lora_negscale", {"lora": [{"id": 0, "scale": -2.5}]}),
    ("dry_one", {"dry_sequence_breakers": ["\n"]}),
    ("dry_two", {"dry_sequence_breakers": ["\n", "::"]}),
    ("dry_empty", {"dry_sequence_breakers": []}),
    ("dry_str", {"dry_sequence_breakers": "x"}),
    ("dry_blank", {"dry_sequence_breakers": [""]}),
    ("dry_dup", {"dry_sequence_breakers": ["\n", "\n"]}),
]

KEYS = ["lora", "dry_sequence_breakers", "speculative.ngram_size_m",
        "speculative.ngram_min_hits", "n_predict", "samplers"]


def wait_ready(proc, deadline):
    while time.time() < deadline:
        if proc.poll() is not None:
            return False
        try:
            with OPENER.open(f"http://{HOST}:{PORT}/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.25)
    return False


def post(body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"http://{HOST}:{PORT}/completion", data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with OPENER.open(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return -1, repr(e).encode()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    with socket.socket() as s:
        if s.connect_ex((HOST, PORT)) == 0:
            print("port busy", file=sys.stderr)
            return 2
    log = open(SCRATCH / "server.log", "wb")
    argv = [str(SERVER), "-m", str(MODEL), "--host", HOST, "--port", str(PORT)]
    proc = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True, cwd=str(SCRATCH))
    results = []
    try:
        if not wait_ready(proc, time.time() + 90):
            print("server did not become ready", proc.poll(), file=sys.stderr)
            return 3
        for tag, extra in VARIANTS:
            body = dict(BASE)
            body.update(extra)
            status, raw = post(body)
            path = OUT / f"resp_{tag}.json"
            path.write_bytes(raw)
            entry = {"tag": tag, "request": body, "status": status,
                     "response_sha256": hashlib.sha256(raw).hexdigest(),
                     "bytes": len(raw)}
            try:
                doc = json.loads(raw)
                if isinstance(doc, dict):
                    gs = doc.get("generation_settings")
                    entry["error"] = doc.get("error")
                    if isinstance(doc.get("error"), dict):
                        entry["error_message"] = doc["error"].get("message")
                    else:
                        entry["error_message"] = doc.get("error")
                    if gs is not None:
                        entry["gs"] = {k: gs.get(k, "<absent>") for k in KEYS}
                        entry["gs_keys_count"] = len(gs)
                    content = doc.get("content")
                    entry["content"] = content if isinstance(content, str) else None
            except Exception as e:
                entry["parse_error"] = repr(e)
            results.append(entry)
            print(json.dumps({k: entry.get(k) for k in
                              ("tag", "status", "error_message", "gs")}, ensure_ascii=False))
        (SCRATCH / "probe-log.json").write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n")
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=10)
        log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
