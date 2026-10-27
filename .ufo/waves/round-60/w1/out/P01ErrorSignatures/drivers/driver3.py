#!/usr/bin/env python3
"""Third pass: untruncated bodies for the identity surfaces, plus load/unload gate flip."""
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
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=60)
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
           "allow": got.get("allow", ""), "location": got.get("location", ""),
           "body": text[:30000], "body_len": len(raw), "truncated": len(text) > 30000,
           "ms": round((time.time() - t0) * 1000, 1)}
    rows.append(row)
    print(f"{status:>4} {case:<26} len={len(raw)} ms={row['ms']}", flush=True)
    return row


j = lambda **kw: json.dumps(kw).encode()

show = req("show_known_full", "POST", "/api/show", j(model=MODEL))
try:
    d = json.loads(show["body"])
    print("SHOW_KEYS=", sorted(d.keys()))
    print("SHOW_DETAILS=", json.dumps(d.get("details")))
    print("SHOW_PARAMETERS=", repr(d.get("parameters")))
    print("SHOW_CAPS=", json.dumps(d.get("capabilities")))
    print("SHOW_TEMPLATE_SRC=", repr(d.get("template_source")))
except Exception as e:  # noqa: BLE001
    print("SHOW_PARSE_ERR", e)

tags = req("tags_full", "GET", "/api/tags")
print("TAGS_FULL=", tags["body"])

req("generate_keepalive_default", "POST", "/api/generate",
    j(model=MODEL, prompt="Once", stream=False, options={"num_predict": 2}))
ps1 = req("ps_loaded", "GET", "/api/ps")
try:
    m = json.loads(ps1["body"])["models"][0]
    print("PS_KEYS=", sorted(m.keys()), "size_vram=", m.get("size_vram"), "ctx=", m.get("context_length"))
except Exception as e:  # noqa: BLE001
    print("PS_PARSE_ERR", e)

req("show_while_loaded", "POST", "/api/show", j(model=MODEL))
req("generate_unload_keepalive0", "POST", "/api/generate",
    j(model=MODEL, prompt="x", stream=False, keep_alive=0, options={"num_predict": 1}))
req("ps_after_unload", "GET", "/api/ps")
req("show_after_unload", "POST", "/api/show", j(model=MODEL))
req("v1_models_after_unload", "GET", "/v1/models")

with open(OUT, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"WROTE {OUT} rows={len(rows)}", flush=True)
