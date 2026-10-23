#!/usr/bin/env python3
"""Scoped raw HTTP probe: RevRowB, frozen round-31 fixture, no judge invocation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
COUNTER = Path(sys.argv[1])
REGISTRY = Path(sys.argv[2])
COUNTER_PIN = "d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216"

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

assert digest(COUNTER) == COUNTER_PIN
spec = importlib.util.spec_from_file_location("r31_frozen", COUNTER)
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)
reg = json.loads(REGISTRY.read_bytes())
for path, key in ((frozen.SERVER, "server_sha256"), (frozen.IMPL, "library_sha256"), (frozen.MODEL, "model_sha256")):
    assert digest(path) == reg["build"][key], (str(path), key)

server = frozen.Server()
# The unmodified frozen helper only owns startup/shutdown. HTTP requests,
# full responses, /slots snapshots, and observations below are independent
# of its render/count/meaning logic.
def request(method, path, body=None):
    payload = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{server.port}{path}", data=payload, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as response:
        return response.code, response.read(), dict(response.headers)

receipt = {"port": server.port, "pid": server.proc.pid, "counter_sha256": COUNTER_PIN, "fixture_pins": reg["build"], "requests": []}
try:
    base = reg["base_body"]
    cases = [("base", base), ("logprobs-only", {**base, "logprobs": True})]
    for rid in ("K31-04", "K31-05", "K31-06"):
        row = next(r for r in reg["rows"] if r["id"] == rid)
        cases.append((rid, {**base, row["param"]: row["sent"], **row.get("also", {})}))
    for label, body in cases:
        status, raw, headers = request("POST", "/v1/chat/completions", body)
        slots_status, slots_raw, slots_headers = request("GET", "/slots")
        (OUT / f"probe-{label}.response.raw").write_bytes(raw)
        (OUT / f"probe-{label}.slots.raw").write_bytes(slots_raw)
        doc = json.loads(raw)
        slots = json.loads(slots_raw)
        latest = max(slots, key=lambda slot: slot.get("id_task", -1))
        content = (((doc.get("choices") or [{}])[0].get("logprobs") or {}).get("content") or [])
        counts = [len(token.get("top_logprobs") or []) for token in content]
        record = {"label": label, "request": body, "status": status, "response_headers": headers, "response": doc, "slots_status": slots_status, "slots_headers": slots_headers, "slots": slots, "stored_n_probs": latest.get("params", {}).get("n_probs"), "latest_slot_task": latest.get("id_task"), "top_logprobs_lengths": counts}
        receipt["requests"].append(record)
        print(f"{label} status={status} stored_n_probs={record['stored_n_probs']} top_logprobs_lengths={json.dumps(counts)} error={json.dumps(doc.get('error'), sort_keys=True)}", flush=True)
finally:
    server.fh.flush()
    (OUT / "probe-server.log").write_bytes(server.log.read_bytes())
    (OUT / "meaning-probe.json").write_text(json.dumps(receipt, indent=2) + "\n")
    server.close()
