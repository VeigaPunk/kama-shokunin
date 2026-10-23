#!/usr/bin/env python3
"""Live probe for the label-keyed control: verify candidate rows against the
pinned llama-server b11755 with the counter's four fixed profiles.
Loopback only, ports 47700-47799, every child killed by process group."""
import json, os, signal, socket, subprocess, time, urllib.error, urllib.request
from pathlib import Path

SERVER = Path.home() / ".local/opt/llama-b11755/llama-server"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
HOST = "127.0.0.1"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
PROFILES = {"default": [], "no-jinja": ["--no-jinja"], "embeddings": ["--embeddings"]}


def env():
    return {"PATH": "/usr/bin:/bin", "HOME": str(Path.home()), "LANG": "C.UTF-8"}


def port_free(p):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, p)) != 0


def pick_port():
    for p in range(47700, 47800):
        if port_free(p):
            return p
    raise SystemExit("no free port")


def http(port, method, path, body):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"http://{HOST}:{port}{path}", data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with OPENER.open(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except (urllib.error.URLError, OSError) as e:
        return -1, repr(e).encode()


def msg(data):
    try:
        d = json.loads(data.decode())
    except Exception:
        return None
    e = d.get("error") if isinstance(d, dict) else None
    if isinstance(e, dict):
        return e.get("message")
    return e if isinstance(e, str) else None


def run(profile, cases):
    port = pick_port()
    argv = [str(SERVER), "-m", str(MODEL), "--host", HOST, "--port", str(port)] + PROFILES[profile]
    log = open(f"/fast/scratch/hyaku/kama-r27/probe-{profile}-{port}.log", "wb")
    proc = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                            start_new_session=True, env=env())
    try:
        end = time.time() + 60
        while time.time() < end:
            if proc.poll() is not None:
                print(f"[{profile}] server died")
                return
            if http(port, "GET", "/health", None)[0] == 200:
                break
            time.sleep(0.25)
        else:
            print(f"[{profile}] never healthy")
            return
        for name, method, path, body in cases:
            st, data = http(port, method, path, body)
            print(f"[{profile}] {name:52s} {method} {path:28s} -> {st} {msg(data)!r}")
    finally:
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=10)
        log.close()


TOOLS = [{"type": "function", "function": {"name": "get_weather", "description": "d",
                                           "parameters": {"type": "object", "properties": {}}}}]

run("default", [
    ("ctl-chat", "POST", "/v1/chat/completions", {"messages": [{"role": "user", "content": "Hi"}], "max_tokens": 4}),
    ("ctl-completion", "POST", "/completion", {"prompt": "Hi", "n_predict": 4}),
    ("prompt-empty-array", "POST", "/completion", {"prompt": []}),
    ("prompt-object", "POST", "/completion", {"prompt": {"not_prompt": True}}),
    ("prompt-long", "POST", "/completion", {"prompt": "hello world " * 20000, "n_predict": 1}),
    ("control-missing-id", "POST", "/v1/chat/completions/control", {}),
])
run("no-jinja", [
    ("ctl-chat", "POST", "/v1/chat/completions", {"messages": [{"role": "user", "content": "Hi"}], "max_tokens": 4}),
    ("tools", "POST", "/v1/chat/completions", {"messages": [{"role": "user", "content": "hi"}], "tools": TOOLS}),
    ("tool-choice", "POST", "/v1/chat/completions", {"messages": [{"role": "user", "content": "hi"}], "tool_choice": "required"}),
])
run("embeddings", [
    ("embedding-empty", "POST", "/embedding", {}),
    ("ctl-embedding-content", "POST", "/embedding", {"content": "Hello"}),
    ("embedding-input-empty-array", "POST", "/embedding", {"input": []}),
    ("embedding-input-empty-str", "POST", "/embedding", {"input": [""]}),
    ("ctl-embedding-input", "POST", "/embedding", {"input": "Hello"}),
    ("oai-embeddings-input", "POST", "/v1/embeddings", {"input": "Hello"}),
    ("oai-embeddings-empty", "POST", "/v1/embeddings", {}),
])
