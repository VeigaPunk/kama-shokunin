#!/usr/bin/env python3
"""Fourth pass: empty-inventory signatures (no models imported at all)."""
import http.client
import json
import sys
import time

PORT = int(sys.argv[1])
OUT = sys.argv[2]
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
        status = r.status
        got = {k.lower(): v for k, v in r.getheaders()}
    except Exception as e:  # noqa: BLE001
        status, raw, got = -1, str(e).encode(), {}
    finally:
        conn.close()
    row = {"case": case, "method": method, "path": path, "status": status,
           "content_type": got.get("content-type", ""), "content_length": got.get("content-length", ""),
           "allow": got.get("allow", ""), "location": got.get("location", ""),
           "body": raw.decode("utf-8", "replace")[:6000], "body_len": len(raw),
           "ms": round((time.time() - t0) * 1000, 1)}
    rows.append(row)
    print(f"{status:>4} {method:<5} {path:<26} ct={row['content_type'] or '-'} body={row['body']!r}", flush=True)
    return row


j = lambda **kw: json.dumps(kw).encode()
req("empty_v1_models", "GET", "/v1/models")
req("empty_api_tags", "GET", "/api/tags")
req("empty_api_ps", "GET", "/api/ps")
req("empty_v1_models_unknown", "GET", "/v1/models/p01-does-not-exist")
req("empty_show_unknown", "POST", "/api/show", j(model="p01-does-not-exist"))
req("empty_generate_unknown", "POST", "/api/generate", j(model="p01-does-not-exist", prompt="x", stream=False))
req("empty_v1_chat_unknown", "POST", "/v1/chat/completions",
    j(model="p01-does-not-exist", messages=[{"role": "user", "content": "hi"}]))
req("empty_version", "GET", "/api/version")
req("empty_v1_models_slash", "GET", "/v1/models/")

with open(OUT, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"WROTE {OUT} rows={len(rows)}", flush=True)
