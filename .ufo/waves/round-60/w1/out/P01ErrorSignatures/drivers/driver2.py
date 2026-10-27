#!/usr/bin/env python3
"""Second pass: name normalization, legacy field, OpenAI-compat edges, gate matrix."""
import http.client
import json
import sys
import time

PORT = int(sys.argv[1])
MODEL = sys.argv[2]
OUT = sys.argv[3]
rows = []


def req(case, method, path, body=None):
    hdrs = {"Accept": "*/*"}
    if body is not None:
        hdrs["Content-Type"] = "application/json"
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
    row = {"case": case, "method": method, "path": path,
           "req_body": body.decode("utf-8", "replace") if isinstance(body, bytes) else body,
           "status": status, "reason": reason,
           "content_type": got.get("content-type", ""), "content_length": got.get("content-length", ""),
           "server": got.get("server", ""), "allow": got.get("allow", ""), "location": got.get("location", ""),
           "body": text[:6000], "body_len": len(raw), "ms": round((time.time() - t0) * 1000, 1)}
    rows.append(row)
    print(f"{status:>4} {method:<7} {path:<40} ct={row['content_type'] or '-'} body={text[:150]!r}", flush=True)
    return row


UNKNOWN = "p01-does-not-exist"
j = lambda **kw: json.dumps(kw).encode()
msg = [{"role": "user", "content": "hi"}]

req("ps_fresh_server", "GET", "/api/ps")
req("show_known_unloaded", "POST", "/api/show", j(model=MODEL))
req("ps_after_show_unloaded", "GET", "/api/ps")
req("show_known_latest", "POST", "/api/show", j(model=MODEL + ":latest"))
req("show_legacy_name_known", "POST", "/api/show", j(name=MODEL))
req("show_legacy_name_unknown", "POST", "/api/show", j(name=UNKNOWN))
req("v1_models_known_bare", "GET", f"/v1/models/{MODEL}")
req("v1_models_known_latest", "GET", f"/v1/models/{MODEL}:latest")
req("show_uppercase_unknown", "POST", "/api/show", j(model="P01-DOES-NOT-EXIST"))
req("v1_models_uppercase_unknown", "GET", "/v1/models/P01-DOES-NOT-EXIST")
req("v1_completions_unknown", "POST", "/v1/completions", j(model=UNKNOWN, prompt="hi"))
req("v1_embeddings_unknown", "POST", "/v1/embeddings", j(model=UNKNOWN, input="hi"))
req("v1_chat_stream_unknown", "POST", "/v1/chat/completions", j(model=UNKNOWN, messages=msg, stream=True))
req("generate_stream_unknown", "POST", "/api/generate", j(model=UNKNOWN, prompt="hi", stream=True))
req("chat_stream_unknown", "POST", "/api/chat", j(model=UNKNOWN, messages=msg, stream=True))
req("show_get", "GET", "/api/show")
req("head_tags", "HEAD", "/api/tags")
req("head_health", "HEAD", "/health")
req("post_v1_models", "POST", "/v1/models")
req("options_generate", "OPTIONS", "/api/generate")
req("tags_post_after_load_attempt", "POST", "/api/tags", b'{"x":1}')

with open(OUT, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"WROTE {OUT} rows={len(rows)}", flush=True)
