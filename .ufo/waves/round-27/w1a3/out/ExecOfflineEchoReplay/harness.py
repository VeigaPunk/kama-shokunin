#!/usr/bin/env python3
"""Offline replay of the 12 committed round-26 shortcut rows through two echo tests.

Test R26 (round-26 count-c1.py:366-374, eb09e742): req_bytes = "\n".join([trig_key,
args, path, json.dumps(headers), body_text]) with body_text = the stored body when it
is a str, then `e_not_echoed = sig not in req_bytes` (line 384).  A row is FLAGGED as
an echo when that test says the signature IS present in req_bytes; round-26 credited a
row only when it was NOT flagged.

Test A3(f) (frozen round-27 count-c1.py:347-372, sha256 49491b80...2765, used at
line 585-587): `any(occurs(sig, s) for s in request_surfaces(req))` where
request_surfaces = [path] + json_strings(body) + json.dumps(body) +
json.dumps(body, ensure_ascii=False).

No server, no port, no subprocess; the frozen counter is imported via importlib and
its main() is never called.  Read-only on all inputs; writes only --out.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

COUNTER_SHA256 = "49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765"
R26_SHA256 = "6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_counter(path: Path):
    spec = importlib.util.spec_from_file_location("a3_count_c1_frozen", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot build import spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # module has an `if __name__ == "__main__"` guard
    return mod


def r26_req_bytes(entry: dict) -> str:
    """Exact rebuild of round-26 count-c1.py:366-374."""
    trig_key = json.dumps({k: entry.get(k) for k in
                           ("channel", "args", "model", "occupy_port", "request")},
                          sort_keys=True)
    req = entry.get("request") or {}
    body = req.get("body")
    body_text = body if isinstance(body, str) else json.dumps(body)
    return "\n".join([trig_key, " ".join(map(str, entry.get("args", []))),
                      str(req.get("path", "")), json.dumps(req.get("headers")),
                      body_text or ""])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--r26-counter", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    counter_p = Path(a.counter).resolve()
    registry_p = Path(a.registry).resolve()
    receipt_p = Path(a.receipt).resolve()
    r26_p = Path(a.r26_counter).resolve()
    out_p = Path(a.out).resolve()

    counter_b = counter_p.read_bytes()
    registry_b = registry_p.read_bytes()
    receipt_b = receipt_p.read_bytes()
    r26_b = r26_p.read_bytes()
    inputs = {
        "a3_counter": {"path": str(counter_p), "sha256": sha256_bytes(counter_b),
                       "bytes": len(counter_b)},
        "r26_counter": {"path": str(r26_p), "sha256": sha256_bytes(r26_b),
                        "bytes": len(r26_b)},
        "shortcut_registry": {"path": str(registry_p), "sha256": sha256_bytes(registry_b),
                              "bytes": len(registry_b)},
        "shortcut_receipt": {"path": str(receipt_p), "sha256": sha256_bytes(receipt_b),
                             "bytes": len(receipt_b)},
    }
    integrity_errors = []
    if inputs["a3_counter"]["sha256"] != COUNTER_SHA256:
        integrity_errors.append(f"a3 counter sha256 {inputs['a3_counter']['sha256']} != {COUNTER_SHA256}")
    if inputs["r26_counter"]["sha256"] != R26_SHA256:
        integrity_errors.append(f"r26 counter sha256 {inputs['r26_counter']['sha256']} != {R26_SHA256}")
    if integrity_errors:
        for e in integrity_errors:
            print(f"INPUT-INTEGRITY-FAIL {e}", file=sys.stderr)
        return 3

    mod = load_counter(counter_p)          # main() never called
    doc = json.loads(registry_b)
    entries = doc["signatures"]
    rec = json.loads(receipt_b)
    rec_rows = {r["id"]: r for r in rec.get("rows", [])}

    rows, frames = [], []
    totals = {"rows": len(entries), "r26_flags_echo": 0, "a3_f_flags_echo": 0,
              "a3_f_flags_echo_if_body_json_decoded": 0, "a3_schema_e_rejects_body": 0,
              "receipt_message_contains_signature": 0,
              "receipt_message_sha256_matches": 0}
    selfcheck = []
    for e in entries:
        rid, sig = e["id"], e["signature"]
        req = e["request"]
        body = req.get("body")
        req_bytes = r26_req_bytes(e)
        r26_flags = sig in req_bytes          # echo seen by the round-26 raw-text test

        surfaces = mod.request_surfaces(req)
        hits = [s for s in surfaces if mod.occurs(sig, s)]
        a3_f_flags = bool(hits)

        decoded_ok, decoded_hits = None, []
        if isinstance(body, str):
            try:
                decoded = json.loads(body)
                dsurf = mod.request_surfaces({"path": req.get("path"), "body": decoded})
                decoded_hits = [s for s in dsurf if mod.occurs(sig, s)]
                decoded_ok = bool(decoded_hits)
            except json.JSONDecodeError:
                decoded_ok = None
        schema_ok = body is None or isinstance(body, (dict, list))

        rrow = rec_rows.get(rid, {})
        msg = rrow.get("observed", {}).get("channel_excerpt", "")
        msg_sha = rrow.get("observed", {}).get("channel_sha256", "")
        msg_has_sig = sig in msg
        msg_decoded_has_sig = False
        try:
            msg_decoded_has_sig = any(sig in s for s in mod.json_strings(json.loads(msg)))
        except (json.JSONDecodeError, TypeError):
            pass
        msg_sha_ok = sha256_bytes(msg.encode()) == msg_sha

        # A3 (h) same-message-frame test (count-c1.py:721-725), applied verbatim.
        frame = msg.replace(sig, "\0").lower().strip("\0 ")
        frames.append(frame)

        r26_receipt_ok = rrow.get("checks", {}).get("e_not_echoed")
        if isinstance(r26_receipt_ok, bool) and r26_receipt_ok == (not r26_flags):
            pass
        else:
            selfcheck.append(f"{rid}: recomputed e_not_echoed={not r26_flags} vs receipt {r26_receipt_ok}")

        totals["r26_flags_echo"] += int(r26_flags)
        totals["a3_f_flags_echo"] += int(a3_f_flags)
        totals["a3_f_flags_echo_if_body_json_decoded"] += int(bool(decoded_ok))
        totals["a3_schema_e_rejects_body"] += int(not schema_ok)
        totals["receipt_message_contains_signature"] += int(msg_has_sig)
        totals["receipt_message_sha256_matches"] += int(msg_sha_ok)
        rows.append({
            "id": rid,
            "signature": sig,
            "signature_bytes": len(sig.encode()),
            "body_type": type(body).__name__,
            "raw_body": body if isinstance(body, str) else json.dumps(body),
            "raw_body_sha256": sha256_bytes(req_bytes.encode()),
            "r26_req_bytes_sha256": sha256_bytes(req_bytes.encode()),
            "r26_flags_echo": r26_flags,
            "r26_receipt_e_not_echoed": r26_receipt_ok,
            "a3_f_flags_echo": a3_f_flags,
            "a3_f_surfaces": len(surfaces),
            "a3_f_hit_surfaces": [s[:120] for s in hits[:2]],
            "a3_f_flags_echo_if_body_json_decoded": decoded_ok,
            "a3_schema_e_body_ok": schema_ok,
            "server_message": msg,
            "server_message_contains_signature": msg_has_sig,
            "server_message_json_strings_contain_signature": msg_decoded_has_sig,
            "server_message_sha256_matches_receipt": msg_sha_ok,
            "message_frame_sha256": sha256_bytes(frame.encode()),
        })

    distinct_frames = len(set(frames))
    # Apply the A3 (h) same-message-frame rule in registry order to the 12 messages:
    # a later row whose signature-stripped frame equals an earlier row's is a clash.
    survived, seen_frames = [], {}
    for r in rows:
        if r["message_frame_sha256"] in seen_frames:
            continue
        seen_frames[r["message_frame_sha256"]] = r["id"]
        survived.append(r["id"])

    # Counterfactual: if (f) decoded string bodies and (h) ran, how many rows survive?
    f_fixed_survivors = []
    seen_f2 = {}
    for r in rows:
        if not r["a3_f_flags_echo_if_body_json_decoded"]:
            f_fixed_survivors.append(r["id"])       # would not be refused by (f)
        if r["message_frame_sha256"] in seen_f2:
            continue
        seen_f2[r["message_frame_sha256"]] = r["id"]

    receipt = {
        "schema": "kama-r27-x1-offline-echo-replay/v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": "offline function-level replay; no server started, counter main() not called",
        "inputs": inputs,
        "tests": {
            "r26_raw_bytes": "round-26 count-c1.py:366-374 + :384 (sig in req_bytes)",
            "a3_clause_f": "frozen count-c1.py request_surfaces/json_strings/occurs "
                           "(lines 347-372) applied at line 585-587",
        },
        "rows": rows,
        "totals": totals,
        "message_frames": {
            "distinct_signature_stripped_frames": distinct_frames,
            "ids_surviving_a3_h_same_message_frame": survived,
            "max_rows_creditable_if_only_h_applies": distinct_frames,
        },
        "selfcheck": {"r26_recompute_vs_receipt_mismatches": selfcheck,
                      "r26_recompute_all_agree": not selfcheck},
    }
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n", "utf-8")

    for r in rows:
        print(f"{r['id']} r26_flags_echo={str(r['r26_flags_echo']).lower():5} "
              f"a3_f={str(r['a3_f_flags_echo']).lower():5} "
              f"a3_f_if_decoded={str(r['a3_f_flags_echo_if_body_json_decoded']).lower():5} "
              f"body={r['body_type']:5} e_body_ok={str(r['a3_schema_e_body_ok']).lower():5} "
              f"msg_has_sig={str(r['server_message_contains_signature']).lower():5} "
              f"frame={r['message_frame_sha256'][:12]} sig={r['signature'][:38]!r}")
    print(f"TOTALS r26_flags_echo {totals['r26_flags_echo']}/{len(rows)} "
          f"a3_flags_echo {totals['a3_f_flags_echo']}/{len(rows)} "
          f"a3_if_decoded {totals['a3_f_flags_echo_if_body_json_decoded']}/{len(rows)} "
          f"a3_schema_e_rejects {totals['a3_schema_e_rejects_body']}/{len(rows)} "
          f"msg_has_sig {totals['receipt_message_contains_signature']}/{len(rows)} "
          f"msg_sha_ok {totals['receipt_message_sha256_matches']}/{len(rows)}")
    print(f"FRAMES distinct_signature_stripped={distinct_frames}/{len(rows)} "
          f"survivors_a3_h={survived}")
    print(f"SELFCHECK r26_recompute_vs_receipt={('agree' if not selfcheck else selfcheck)}")
    print(f"OUT {out_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
