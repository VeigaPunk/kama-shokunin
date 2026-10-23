#!/usr/bin/python3
"""Capture the round-31 stream parameter against the pinned b11755 fixture."""
import json
import os
import signal
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVER = Path.home() / ".local/opt/llama-b11755/llama-server"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
LIBDIR = Path.home() / ".local/opt/llama-b11755"
OUT = Path(__file__).resolve().parent / "measurement.json"
BASE = {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}


def free_port():
    for port in range(47900, 48000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("no free port in 47900-47999")


def request(port, method, path, body=None, timeout=120):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def newest_slot(port):
    status, body, _ = request(port, "GET", "/slots")
    if status != 200:
        raise RuntimeError(f"GET /slots status {status}: {body!r}")
    slots = json.loads(body.decode())
    return max(slots, key=lambda slot: slot.get("id_task", -1))


port = free_port()
argv = [str(SERVER), "-m", str(MODEL), "--host", "127.0.0.1", "--port", str(port)]
env = os.environ.copy()
env["LD_LIBRARY_PATH"] = str(LIBDIR)
log = tempfile.TemporaryFile(mode="w+b")
proc = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
try:
    deadline = time.monotonic() + 90
    while True:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early with status {proc.returncode}")
        try:
            ready_status, _, _ = request(port, "GET", "/health", timeout=2)
            if ready_status == 200:
                break
        except Exception:
            pass
        if time.monotonic() >= deadline:
            raise RuntimeError("server did not become ready within 90 seconds")
        time.sleep(0.15)

    base_status, base_raw, base_headers = request(port, "POST", "/v1/chat/completions", BASE)
    if base_status != 200:
        raise RuntimeError(f"base request status {base_status}: {base_raw!r}")
    base_doc = json.loads(base_raw.decode())
    base_slot = newest_slot(port)

    stream_body = dict(BASE)
    stream_body["stream"] = True
    stream_status, stream_raw, stream_headers = request(
        port, "POST", "/v1/chat/completions", stream_body
    )
    stream_slot = newest_slot(port)
    stream_text = stream_raw.decode("utf-8", errors="replace")
    before = base_slot.get("params") or {}
    after = stream_slot.get("params") or {}
    slot_delta = {
        key: {"before": before.get(key), "after": after.get(key)}
        for key in sorted(set(before) | set(after))
        if before.get(key) != after.get(key)
    }
    prompt_tokens = (base_doc.get("usage") or {}).get("prompt_tokens")
    stream_usage_prompt_tokens = None
    for line in stream_text.splitlines():
        if line.startswith("data: ") and line[6:].strip() != "[DONE]":
            try:
                usage = json.loads(line[6:]).get("usage") or {}
                if "prompt_tokens" in usage:
                    stream_usage_prompt_tokens = usage["prompt_tokens"]
            except Exception:
                pass

    record = {
        "port": port,
        "argv": argv,
        "ld_library_path": str(LIBDIR),
        "base_body": BASE,
        "base": {
            "status": base_status,
            "headers": base_headers,
            "body_exact": base_raw.decode("utf-8", errors="replace"),
            "newest_slot_id_task": base_slot.get("id_task"),
            "params": before,
        },
        "stream_request_body": stream_body,
        "stream": {
            "status": stream_status,
            "headers": stream_headers,
            "body_exact": stream_text,
            "excerpt_300": stream_text[:300],
            "newest_slot_id_task": stream_slot.get("id_task"),
            "params": after,
            "slot_delta": slot_delta,
            "stream_usage_prompt_tokens": stream_usage_prompt_tokens,
        },
        "prompt_tokens": prompt_tokens,
    }
finally:
    if proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    log.flush()
    log.seek(0)
    log_lines = log.read().decode("utf-8", errors="replace").splitlines()
    log.close()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        port_free_after = sock.connect_ex(("127.0.0.1", port)) != 0
    if not port_free_after:
        raise RuntimeError(f"port {port} remains occupied")
record["server_log_tail"] = log_lines[-5:]
OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "status": stream_status,
    "response_excerpt": stream_text[:300],
    "prompt_tokens": prompt_tokens,
    "stream_usage_prompt_tokens": stream_usage_prompt_tokens,
    "slot_delta": slot_delta,
    "port": port,
    "port_free": port_free_after,
    "server_log_tail": log_lines[-5:],
}, separators=(",", ":")))
