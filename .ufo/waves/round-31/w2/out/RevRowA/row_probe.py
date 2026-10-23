#!/usr/bin/env python3
"""Read-only-to-lane probe: capture raw slots, then attack K31-02 precedence."""
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

clone = Path(sys.argv[1])
out = Path(sys.argv[2])
registry = json.loads((clone / "registry/chat-param-outcomes-r31.json").read_text())
server = Path.home() / ".local/opt/llama-b11755/llama-server"
model = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
library = server.parent / "libllama-server-impl.so"
for name, path in (("server", server), ("model", model), ("library", library)):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != registry["build"][name + "_sha256"]:
        raise RuntimeError(f"{name} pin mismatch: {actual}")

port = None
for candidate in range(47900, 48000):
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", candidate))
        except OSError:
            continue
        port = candidate
        break
if port is None:
    raise RuntimeError("no free port in 47900-47999")

def request(method, path, body=None):
    payload = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=payload, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        response = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read()
        return response.status, dict(response.headers), raw

env = {k: v for k, v in os.environ.items() if k not in (
    "PYTHONPATH", "PYTHONSTARTUP", "PYTHONHOME", "LD_PRELOAD", "LD_LIBRARY_PATH"
)}
env["LD_LIBRARY_PATH"] = str(server.parent)
argv = [str(server), "-m", str(model), "--host", "127.0.0.1", "--port", str(port)]
records = []
result = {"argv": argv, "hypothesis": "With both OAI limit keys present, native n_predict can override max_completion_tokens.", "records": records}
with (out / "row-probe-server.log").open("wb") as logfile:
    process = subprocess.Popen(argv, stdout=logfile, stderr=subprocess.STDOUT,
                               env=env, start_new_session=True)
    result["pid"] = process.pid
    try:
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("owned server exited before readiness")
            try:
                status, _, _ = request("GET", "/health")
                if status == 200:
                    break
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(0.15)
        else:
            raise RuntimeError("owned server did not become ready")
        status, _, raw = request("GET", "/props")
        props = json.loads(raw)
        result["props"] = props
        if status != 200 or Path(props.get("model_path", "")).resolve() != model.resolve():
            raise RuntimeError("server did not serve pinned model")
        cases = [("BASE", dict(registry["base_body"]))]
        for row in registry["rows"]:
            if row["id"] in ("K31-01", "K31-02", "K31-03"):
                body = dict(registry["base_body"])
                body[row["param"]] = row["sent"]
                body.update(row.get("also") or {})
                cases.append((row["id"], body))
        attack = dict(registry["base_body"])
        attack.update({"max_completion_tokens": 3, "n_predict": 5})
        cases.append(("K31-02-native-override", attack))
        for name, body in cases:
            if process.poll() is not None:
                raise RuntimeError("owned server exited during requests")
            status, headers, raw = request("POST", "/v1/chat/completions", body)
            slots_status, slots_headers, slots_raw = request("GET", "/slots")
            slots = json.loads(slots_raw)
            newest = max(slots, key=lambda value: value.get("id_task", -1))
            record = {"id": name, "request": body, "status": status,
                      "response_headers": headers, "response_body": raw.decode(),
                      "slots_status": slots_status, "slots_headers": slots_headers,
                      "slots_body": slots_raw.decode(), "newest": newest}
            records.append(record)
            params = newest.get("params") or {}
            doc = json.loads(raw)
            print(json.dumps({"id": name, "status": status,
                              "slot_task": newest.get("id_task"),
                              "stored": {key: params.get(key) for key in ("max_tokens", "n_predict", "n_probs")},
                              "completion_tokens": (doc.get("usage") or {}).get("completion_tokens")},
                             separators=(",", ":")))
    finally:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=15)
        result["server_exit_code"] = process.returncode
        (out / "row-probe.json").write_text(json.dumps(result, indent=2) + "\n")
