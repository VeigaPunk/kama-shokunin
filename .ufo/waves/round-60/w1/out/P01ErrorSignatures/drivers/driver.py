#!/usr/bin/env python3
"""Capture exact HTTP signatures from a lane-owned Ollama server. Read-only probes."""
import http.client
import json
import sys
import time

PORT = int(sys.argv[1])
MODEL = sys.argv[2]
OUT = sys.argv[3]

rows = []


def req(case, method, path, body=None, headers=None):
    hdrs = {"Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    if body is not None:
        hdrs.setdefault("Content-Type", "application/json")
    t0 = time.time()
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=30)
    try:
        conn.request(method, path, body=body, headers=hdrs)
        r = conn.getresponse()
        raw = r.read()
        status, reason = r.status, r.reason
        got = {k.lower(): v for k, v in r.getheaders()}
    except Exception as e:  # noqa: BLE001
        status, reason, raw, got = -1, type(e).__name__, str(e).encode(), {}
    finally:
        conn.close()
    text = raw.decode("utf-8", "replace")
    row = {
        "case": case,
        "method": method,
        "path": path,
        "req_body": body.decode("utf-8", "replace") if isinstance(body, bytes) else body,
        "status": status,
        "reason": reason,
        "content_type": got.get("content-type", ""),
        "content_length": got.get("content-length", ""),
        "server": got.get("server", ""),
        "allow": got.get("allow", ""),
        "location": got.get("location", ""),
        "body": text[:6000],
        "body_len": len(raw),
        "ms": round((time.time() - t0) * 1000, 1),
    }
    rows.append(row)
    print(f"{status:>4} {method:<6} {path:<32} ct={row['content_type'] or '-'} len={row['body_len']} body={text[:160]!r}", flush=True)
    return row


UNKNOWN = "p01-does-not-exist"
j = lambda **kw: json.dumps(kw).encode()
msg = [{"role": "user", "content": "hi"}]

# ---- phase 1: server up, model imported, never loaded ----------------------
req("version", "GET", "/api/version")
req("root_get", "GET", "/")
req("root_head", "HEAD", "/")
req("tags", "GET", "/api/tags")
req("ps_before_load", "GET", "/api/ps")
req("v1_models", "GET", "/v1/models")
req("v1_models_trailing_slash", "GET", "/v1/models/")
req("v1_models_known", "GET", f"/v1/models/{MODEL}")
req("show_known", "POST", "/api/show", j(model=MODEL))
req("ps_after_show", "GET", "/api/ps")

# unknown model, all documented surfaces
req("show_unknown", "POST", "/api/show", j(model=UNKNOWN))
req("show_unknown_latest", "POST", "/api/show", j(model=UNKNOWN + ":latest"))
req("generate_unknown", "POST", "/api/generate", j(model=UNKNOWN, prompt="hi", stream=False))
req("chat_unknown", "POST", "/api/chat", j(model=UNKNOWN, messages=msg, stream=False))
req("embed_unknown", "POST", "/api/embed", j(model=UNKNOWN, input="hi"))
req("v1_chat_unknown", "POST", "/v1/chat/completions", j(model=UNKNOWN, messages=msg))
req("v1_models_unknown", "GET", f"/v1/models/{UNKNOWN}")
req("v1_models_unknown_latest", "GET", f"/v1/models/{UNKNOWN}:latest")

# malformed / empty bodies
req("generate_malformed", "POST", "/api/generate", b'{"model": ')
req("generate_not_json", "POST", "/api/generate", b"not-json")
req("chat_not_json", "POST", "/api/chat", b"not-json")
req("show_malformed", "POST", "/api/show", b'{"model": "')
req("v1_chat_malformed", "POST", "/v1/chat/completions", b"{")
req("generate_empty_body", "POST", "/api/generate", b"")
req("show_empty_object", "POST", "/api/show", b"{}")
req("generate_empty_object", "POST", "/api/generate", b"{}")

# wrong methods
req("tags_post", "POST", "/api/tags")
req("tags_delete", "DELETE", "/api/tags")
req("version_post", "POST", "/api/version")
req("version_put", "PUT", "/api/version")
req("version_head", "HEAD", "/api/version")
req("generate_get", "GET", "/api/generate")
req("ps_post", "POST", "/api/ps")
req("v1_chat_get", "GET", "/v1/chat/completions")
req("options_tags", "OPTIONS", "/api/tags")

# llama.cpp-style routes the lane's conventions use
req("health", "GET", "/health")
req("props", "GET", "/props")
req("slots", "GET", "/slots")
req("metrics", "GET", "/metrics")
req("unknown_route", "GET", "/nope")

# ---- phase 2: load exactly one generation, then re-probe -------------------
req("generate_known_load", "POST", "/api/generate",
    j(model=MODEL, prompt="Once", stream=False, options={"num_predict": 2}))
req("ps_after_load", "GET", "/api/ps")
req("tags_after_load", "GET", "/api/tags")
req("v1_models_after_load", "GET", "/v1/models")
req("v1_chat_unknown_after_load", "POST", "/v1/chat/completions", j(model=UNKNOWN, messages=msg))
req("generate_unknown_after_load", "POST", "/api/generate", j(model=UNKNOWN, prompt="hi", stream=False))
req("show_unknown_after_load", "POST", "/api/show", j(model=UNKNOWN))
req("v1_models_unknown_after_load", "GET", f"/v1/models/{UNKNOWN}")
req("v1_chat_known_after_load", "POST", "/v1/chat/completions",
    j(model=MODEL, messages=msg, max_tokens=1, stream=False))

with open(OUT, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"WROTE {OUT} rows={len(rows)}", flush=True)
