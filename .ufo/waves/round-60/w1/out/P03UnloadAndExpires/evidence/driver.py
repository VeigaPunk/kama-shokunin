#!/usr/bin/env python3
"""Round-60 P03: observe Ollama v0.40.11 residency transitions on a lane-owned server."""
import datetime as dt
import hashlib
import http.client
import json
import os
import re
import subprocess
import sys
import time

PORT = int(sys.argv[1])
S = sys.argv[2]
NAME = sys.argv[3]
BIN = os.path.expanduser("~/.local/opt/ollama-v0.40.11/bin/ollama")

caps = []
notes = {}


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def parse_expiry(raw):
    """RFC3339 -> (aware datetime, fractional digit count, offset string)."""
    m = re.match(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?(Z|[+-]\d\d:\d\d)$", raw)
    if not m:
        return None, None, None
    frac = m.group(2) or ""
    norm = m.group(1) + (frac[:7] if len(frac) > 7 else frac) + ("+00:00" if m.group(3) == "Z" else m.group(3))
    return dt.datetime.fromisoformat(norm), len(frac) - 1 if frac else 0, m.group(3)


def call(label, method, path, body=None, timeout=120):
    t0 = time.time_ns()
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=timeout)
    headers = {}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    conn.request(method, path, body=data, headers=headers)
    resp = conn.getresponse()
    raw = resp.read()
    t1 = time.time_ns()
    hdrs = {k.lower(): v for k, v in resp.getheaders()}
    conn.close()
    rec = {
        "seq": len(caps),
        "label": label,
        "route": path,
        "method": method,
        "status": resp.status,
        "reason": resp.reason,
        "content_type": hdrs.get("content-type"),
        "headers": hdrs,
        "req_body": body,
        "body": raw.decode("utf-8", "replace"),
        "body_sha256": hashlib.sha256(raw).hexdigest(),
        "t_start_utc": dt.datetime.fromtimestamp(t0 / 1e9, dt.timezone.utc).isoformat(),
        "client_ms": round((t1 - t0) / 1e6, 3),
    }
    caps.append(rec)
    return rec


def payload(rec):
    try:
        return json.loads(rec["body"])
    except Exception:
        return None


def ps_models(rec):
    p = payload(rec)
    return p.get("models", []) if isinstance(p, dict) else None


# ---- 0. version + inventory, before any generate --------------------------------
call("version", "GET", "/api/version")
tags_before = call("tags-before", "GET", "/api/tags")
ps0 = call("ps-before-any-load", "GET", "/api/ps")
notes["ps_before_models"] = ps_models(ps0)
notes["tags_before_names"] = [m.get("name") for m in (payload(tags_before) or {}).get("models", [])]

# ---- 1. generate with keep_alive 30s ------------------------------------------
g1 = call("generate-keep-alive-30s", "POST", "/api/generate",
          {"model": NAME, "prompt": "Hello", "stream": False, "keep_alive": "30s"})
b1 = payload(g1) or {}
notes["gen30"] = {k: b1.get(k) for k in ("total_duration", "load_duration", "prompt_eval_duration",
                                         "eval_duration", "eval_count", "done", "done_reason", "response")}
ps1_t = now_utc()
ps1 = call("ps-after-keep-alive-30s", "GET", "/api/ps")
m1 = (ps_models(ps1) or [{}])[0] if ps_models(ps1) else None
if m1 and m1.get("expires_at"):
    exp, ndig, off = parse_expiry(m1["expires_at"])
    created = dt.datetime.fromisoformat(b1["created_at"].replace("Z", "+00:00"))
    notes["expires_30s"] = {
        "raw": m1["expires_at"],
        "fractional_digits": ndig,
        "offset": off,
        "expires_minus_created_s": round((exp - created).total_seconds(), 6),
        "expires_minus_client_now_s": round((exp - ps1_t).total_seconds(), 6),
        "client_now_utc": ps1_t.isoformat(),
        "size_vram": m1.get("size_vram"),
        "context_length": m1.get("context_length"),
        "size": m1.get("size"),
        "digest": m1.get("digest"),
        "keys": sorted(m1.keys()),
    }
time.sleep(0.25)
ps1b = call("ps-after-keep-alive-30s-repeat", "GET", "/api/ps")
m1b = (ps_models(ps1b) or [{}])[0] if ps_models(ps1b) else None
notes["expires_30s_repeat_equal"] = bool(m1 and m1b and m1.get("expires_at") == m1b.get("expires_at"))

# ---- 2. generate with keep_alive 0: how fast does ps empty? --------------------
g2 = call("generate-keep-alive-0", "POST", "/api/generate",
          {"model": NAME, "prompt": "Hello", "stream": False, "keep_alive": 0})
b2 = payload(g2) or {}
t_unload0 = time.time_ns()
polls = []
empty_at_ms = None
while True:
    rel = (time.time_ns() - t_unload0) / 1e6
    rec = call(f"ps-after-keep-alive-0-poll-{len(polls)}", "GET", "/api/ps")
    mods = ps_models(rec)
    polls.append({"rel_ms": round(rel, 3), "n": None if mods is None else len(mods),
                  "names": [m.get("name") for m in (mods or [])]})
    if mods == [] and empty_at_ms is None:
        empty_at_ms = round(rel, 3)
        break
    if rel > 3000:
        break
    time.sleep(0.003)
notes["keep_alive_0"] = {
    "first_ps_rel_ms": polls[0]["rel_ms"],
    "first_ps_n": polls[0]["n"],
    "first_ps_empty": polls[0]["n"] == 0,
    "empty_at_ms": empty_at_ms,
    "polls": len(polls),
    "gen_total_duration": b2.get("total_duration"),
    "gen_load_duration": b2.get("load_duration"),
    "gen_done": b2.get("done"),
    "gen_created_at": b2.get("created_at"),
}
time.sleep(0.5)
ps2s = call("ps-after-keep-alive-0-settled", "GET", "/api/ps")
notes["ps_after_ka0_500ms_n"] = len(ps_models(ps2s) or [])

# ---- 3. reload then `ollama stop` ---------------------------------------------
g3 = call("generate-reload-before-stop", "POST", "/api/generate",
          {"model": NAME, "prompt": "Hi", "stream": False})
b3 = payload(g3) or {}
notes["gen_default_keep_alive"] = {k: b3.get(k) for k in ("total_duration", "load_duration", "done")}
ps3 = call("ps-before-stop", "GET", "/api/ps")
m3 = (ps_models(ps3) or [{}])[0] if ps_models(ps3) else None
if m3 and m3.get("expires_at"):
    exp3, nd3, off3 = parse_expiry(m3["expires_at"])
    created3 = dt.datetime.fromisoformat(b3["created_at"].replace("Z", "+00:00")) if b3.get("created_at") else None
    notes["expires_default"] = {"raw": m3["expires_at"], "offset": off3,
                                "expires_minus_created_s": round((exp3 - created3).total_seconds(), 6) if created3 else None,
                                "expires_minus_client_now_s": round((exp3 - now_utc()).total_seconds(), 6)}

env = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home"),
       "OLLAMA_HOST": f"127.0.0.1:{PORT}"}
t_stop0 = time.time_ns()
stop = subprocess.run([BIN, "stop", NAME], capture_output=True, env=env, timeout=60)
t_stop1 = time.time_ns()
notes["ollama_stop"] = {
    "argv": [BIN, "stop", NAME],
    "exit": stop.returncode,
    "stdout": stop.stdout.decode("utf-8", "replace"),
    "stderr": stop.stderr.decode("utf-8", "replace"),
    "cli_ms": round((t_stop1 - t_stop0) / 1e6, 3),
}
polls2 = []
empty_at_stop = None
while True:
    rel = (time.time_ns() - t_stop1) / 1e6
    rec = call(f"ps-after-ollama-stop-poll-{len(polls2)}", "GET", "/api/ps")
    mods = ps_models(rec)
    polls2.append({"rel_ms": round(rel, 3), "n": None if mods is None else len(mods)})
    if mods == [] and empty_at_stop is None:
        empty_at_stop = round(rel, 3)
        break
    if rel > 3000:
        break
    time.sleep(0.003)
notes["stop_polls"] = polls2[:12]
notes["stop_empty_at_ms"] = empty_at_stop

# ---- 4. empty-prompt preload form ---------------------------------------------
g4 = call("generate-empty-prompt-no-key", "POST", "/api/generate", {"model": NAME})
b4 = payload(g4) or {}
notes["gen_empty_prompt"] = {
    "req": {"model": NAME},
    "status": g4["status"],
    "content_type": g4["content_type"],
    "body": g4["body"],
    "keys": sorted(b4.keys()) if isinstance(b4, dict) else None,
    "total_duration": b4.get("total_duration"),
    "load_duration": b4.get("load_duration"),
    "response": b4.get("response"),
    "done": b4.get("done"),
    "done_reason": b4.get("done_reason"),
}
ps4 = call("ps-after-empty-prompt", "GET", "/api/ps")
m4 = (ps_models(ps4) or [{}])[0] if ps_models(ps4) else None
notes["ps_after_empty_prompt"] = {
    "n": len(ps_models(ps4) or []),
    "names": [m.get("name") for m in (ps_models(ps4) or [])],
    "expires_at": (m4 or {}).get("expires_at"),
    "size_vram": (m4 or {}).get("size_vram"),
    "context_length": (m4 or {}).get("context_length"),
}
if m4 and m4.get("expires_at"):
    exp4, nd4, off4 = parse_expiry(m4["expires_at"])
    created4 = dt.datetime.fromisoformat(b4["created_at"].replace("Z", "+00:00")) if b4.get("created_at") else None
    notes["ps_after_empty_prompt"].update({
        "expires_minus_client_now_s": round((exp4 - now_utc()).total_seconds(), 6),
        "expires_minus_created_s": round((exp4 - created4).total_seconds(), 6) if created4 else None,
        "offset": off4,
    })

# variant with explicit empty string prompt (second documented shape)
g5 = call("generate-empty-prompt-empty-string", "POST", "/api/generate",
          {"model": NAME, "prompt": "", "stream": False})
notes["gen_empty_string"] = {"status": g5["status"], "body": g5["body"][:600],
                             "content_type": g5["content_type"]}
ps5 = call("ps-after-empty-string", "GET", "/api/ps")
notes["ps_after_empty_string_n"] = len(ps_models(ps5) or [])

# ---- 5. clean unload for teardown ---------------------------------------------
call("generate-final-keep-alive-0", "POST", "/api/generate",
     {"model": NAME, "prompt": "x", "stream": False, "keep_alive": 0})
time.sleep(0.3)
psf = call("ps-final", "GET", "/api/ps")
notes["ps_final_n"] = len(ps_models(psf) or [])

out = {"name": NAME, "port": PORT, "captures": caps, "notes": notes,
       "capture_count": len(caps),
       "route_set": sorted({(c["method"], c["route"].split("?")[0]) for c in caps})}
with open(os.path.join(S, "out", "captures.jsonl"), "w") as f:
    for c in caps:
        f.write(json.dumps(c, sort_keys=True) + "\n")
with open(os.path.join(S, "out", "summary.json"), "w") as f:
    json.dump(out, f, indent=1, sort_keys=True)
print(json.dumps(notes, indent=1, sort_keys=True))
