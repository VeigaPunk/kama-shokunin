#!/usr/bin/python3
"""Round-28 DataG13 live probe: echo, preserved_tokens, grammar_triggers, reasoning_control.

Starts the pinned llama-server on 127.0.0.1:48213, sends the counter's base request
plus one extra request field per probe, saves every raw body, kills the process group.
"""
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOST = "127.0.0.1"
PORT = 48213
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG13"
LOG = "/fast/scratch/hyaku/kama-r28/w1/DataG13/server.log"
BIN = os.path.expanduser("~/.local/opt/llama-b11755/llama-server")
MODEL = os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf")
BASE = {"prompt": "Once upon a time", "n_predict": 1}
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def http(path, body=None, timeout=60.0):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"http://{HOST}:{PORT}{path}", data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST" if body is not None else "GET")
    try:
        with OPENER.open(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # noqa: BLE001
        return -1, repr(e).encode()


def wait_ready(deadline):
    while time.time() < deadline:
        st, body = http("/health", timeout=5.0)
        if st == 200:
            return True
        time.sleep(0.5)
    return False


def save(tag, body):
    path = os.path.join(OUT, f"resp-{tag}.json")
    with open(path, "wb") as f:
        f.write(body)
    return hashlib.sha256(body).hexdigest(), path


def main():
    os.makedirs(OUT, exist_ok=True)
    dfd = open(LOG, "wb")
    proc = subprocess.Popen(
        [BIN, "-m", MODEL, "--host", HOST, "--port", str(PORT)],
        stdout=dfd, stderr=subprocess.STDOUT, start_new_session=True,
        cwd="/fast/scratch/hyaku/kama-r28/w1/DataG13")
    results = []
    try:
        if not wait_ready(time.time() + 120):
            print(json.dumps({"error": "server not ready"}))
            return 1
        probes = [
            ("p01-base", dict(BASE)),
            ("p02-echo-true", BASE | {"echo": True}),
            ("p03-echo-string", BASE | {"echo": "yes"}),
            ("p04-preserved", BASE | {"preserved_tokens": ["Once", " upon", "Once"]}),
            ("p05-preserved-multitok", BASE | {"preserved_tokens": ["Once upon a time"]}),
            ("p06-triggers-bare", BASE | {"grammar_triggers": ["Once"]}),
            ("p07-trigger-word", BASE | {"grammar_triggers": [{"type": 1, "value": "Once"}]}),
            ("p08-trigger-pattern", BASE | {"grammar_triggers": [{"type": 2, "value": "Once"}]}),
            ("p09-trigger-word-preserved", BASE | {"grammar_triggers": [{"type": 1, "value": "Once"}],
                                                   "preserved_tokens": ["Once"]}),
            ("p10-reasoning-control-true", BASE | {"reasoning_control": True}),
            ("p11-reasoning-control-int", BASE | {"reasoning_control": 1}),
            ("p12-reasoning-control-str", BASE | {"reasoning_control": "true"}),
            ("p13-base-again", dict(BASE)),
        ]
        for tag, body in probes:
            st, raw = http("/completion", body)
            sha, path = save(tag, raw)
            doc = None
            try:
                doc = json.loads(raw)
            except Exception:  # noqa: BLE001
                pass
            gs = doc.get("generation_settings") if isinstance(doc, dict) else None
            msg = None
            if isinstance(doc, dict):
                if isinstance(doc.get("error"), dict):
                    msg = doc["error"].get("message")
                elif isinstance(doc.get("error"), str):
                    msg = doc["error"]
            results.append({
                "tag": tag,
                "request": body,
                "status": st,
                "response_sha256": sha,
                "body_file": path,
                "message": msg,
                "generation_settings_subset": None if not isinstance(gs, dict) else {
                    k: gs.get(k) for k in ("preserved_tokens", "grammar_triggers",
                                           "reasoning_control", "echo") },
                "gs_has_preserved": None if not isinstance(gs, dict) else "preserved_tokens" in gs,
                "gs_has_triggers": None if not isinstance(gs, dict) else "grammar_triggers" in gs,
                "gs_has_echo": None if not isinstance(gs, dict) else "echo" in gs,
                "gs_has_reasoning_control": None if not isinstance(gs, dict) else "reasoning_control" in gs,
                "content": None if not isinstance(doc, dict) else doc.get("content"),
                "prompt_echo_field": None if not isinstance(doc, dict) else doc.get("prompt"),
                "top_keys": None if not isinstance(doc, dict) else sorted(doc),
            })
            print(tag, st, sha[:12], msg, flush=True)
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=10)
        dfd.close()

    # confirm the port is closed
    time.sleep(0.5)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        closed = s.connect_ex((HOST, PORT)) != 0
    with open(os.path.join(OUT, "probe-results.json"), "w", encoding="utf-8") as f:
        json.dump({"port_closed": closed, "probes": results}, f, indent=1)
        f.write("\n")
    print("port_closed", closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
