#!/usr/bin/env python3
r"""Live probe of the S137 echo site on llama-server b11755 (commit 704366d76).

Writes raw request bodies, POSTs them to /v1/chat/completions, stores the raw
response bytes, and emits a receipt with sha256 and echo/frame checks.

Cases:
  req1-plain        signature A, plain ASCII spelling
  req2-firstesc     signature A, first character as \u00XX
  req3-fullesc      signature A, every character as \u00XX
  req5-altsig-plain signature B, plain ASCII (distinct request-chosen value)
  req6-altsig-full  signature B, every character as \u00XX
  req4-control      no response_format (healthy control)
"""
import hashlib
import http.client
import json
import os
import sys

OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
SIGA = b"echo_sig_9f3a"
SIGB = b"alt_sig_4b7e"

MSG = b'{"messages":[{"role":"user","content":"hi"}],"max_tokens":1'


def esc(s):
    return b"".join(b"\\u%04x" % c for c in s)


REQ = {
    "req4-control": MSG + b"}",
    "req1-plain": MSG + b',"response_format":{"type":"echo_sig_9f3a"}}',
    "req2-firstesc": MSG + b',"response_format":{"type":"\\u0065cho_sig_9f3a"}}',
    "req3-fullesc": MSG + b',"response_format":{"type":"' + esc(SIGA) + b'"}}',
    "req5-altsig-plain": MSG + b',"response_format":{"type":"alt_sig_4b7e"}}',
    "req6-altsig-full": MSG + b',"response_format":{"type":"' + esc(SIGB) + b'"}}',
}

ORDER = ["req4-control", "req1-plain", "req2-firstesc", "req3-fullesc",
         "req5-altsig-plain", "req6-altsig-full"]
ERROR_CASES = ORDER[1:]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def post(body):
    conn = http.client.HTTPConnection("127.0.0.1", 47680, timeout=120)
    conn.request("POST", "/v1/chat/completions", body=body,
                 headers={"Content-Type": "application/json"})
    r = conn.getresponse()
    data = r.read()
    status = r.status
    hdrs = dict(r.getheaders())
    conn.close()
    return status, hdrs, data


def get(path):
    conn = http.client.HTTPConnection("127.0.0.1", 47680, timeout=30)
    conn.request("GET", path)
    r = conn.getresponse()
    data = r.read()
    conn.close()
    return r.status, data


def frame_of(message, sig):
    """Message with the signature cut out, case-folded, whitespace removed."""
    return "".join(message.replace(sig, "").split()).lower()


def main():
    os.makedirs(OUT, exist_ok=True)
    receipt = {
        "target": "X1 evidence: S137 live echo site, llama-server b11755 @ 704366d76",
        "server": "127.0.0.1:47680",
        "signature_A": SIGA.decode(),
        "signature_B": SIGB.decode(),
        "requests": {},
    }

    hs, hb = get("/health")
    receipt["health"] = {"status": hs, "body": hb.decode("utf-8", "replace")}
    ps, pb = get("/props")
    receipt["props_status"] = ps
    open(os.path.join(OUT, "props.json"), "wb").write(pb)
    receipt["props_sha256"] = sha(pb)

    for name in ORDER:
        body = REQ[name]
        open(os.path.join(SCRATCH, name + ".json"), "wb").write(body)
        open(os.path.join(OUT, name + ".req"), "wb").write(body)
        status, hdrs, data = post(body)
        open(os.path.join(OUT, name + ".resp"), "wb").write(data)
        rec = {
            "request_file": name + ".req",
            "request_bytes": len(body),
            "request_sha256": sha(body),
            "decoded_type": None,
            "status": status,
            "content_type": hdrs.get("Content-Type"),
            "response_file": name + ".resp",
            "response_bytes": len(data),
            "response_sha256": sha(data),
            "response_json": None,
            "error_message": None,
            "sig_in_request_raw": None,
            "sig_in_response_raw": None,
            "escaped_spelling_in_response_raw": None,
            "decoded_sig_in_message": None,
            "frame": None,
        }
        try:
            jreq = json.loads(body.decode("ascii"))
            rec["decoded_type"] = jreq.get("response_format", {}).get("type")
        except Exception as e:  # noqa: BLE001
            rec["decoded_type_error"] = str(e)
        if rec["decoded_type"]:
            sigb = rec["decoded_type"].encode()
            rec["sig_in_request_raw"] = sigb in body
            rec["sig_in_response_raw"] = sigb in data
            rec["escaped_spelling_in_response_raw"] = esc(sigb) in data
        try:
            j = json.loads(data.decode("utf-8"))
            rec["response_json"] = j
            msg = None
            if isinstance(j, dict) and isinstance(j.get("error"), dict):
                msg = j["error"].get("message")
            rec["error_message"] = msg
            if isinstance(msg, str) and rec["decoded_type"]:
                rec["decoded_sig_in_message"] = rec["decoded_type"] in msg
                rec["frame"] = frame_of(msg, rec["decoded_type"])
        except Exception as e:  # noqa: BLE001
            rec["response_json_error"] = str(e)
        receipt["requests"][name] = rec

    frames = {n: receipt["requests"][n]["frame"] for n in ERROR_CASES}
    receipt["frames_equal_all_error_cases"] = (
        len(set(frames.values())) == 1 and None not in frames.values())
    receipt["frame_sha256"] = sha((frames["req1-plain"] or "").encode())
    receipt["all_decoded_sig_in_message"] = all(
        receipt["requests"][n]["decoded_sig_in_message"] for n in ERROR_CASES)
    receipt["all_error_status_400"] = all(
        receipt["requests"][n]["status"] == 400 for n in ERROR_CASES)
    receipt["escaped_cases_sig_absent_from_request_raw"] = all(
        not receipt["requests"][n]["sig_in_request_raw"]
        for n in ("req2-firstesc", "req3-fullesc", "req6-altsig-full"))
    receipt["escaped_cases_sig_present_in_response_raw"] = all(
        receipt["requests"][n]["sig_in_response_raw"]
        for n in ("req2-firstesc", "req3-fullesc", "req6-altsig-full"))
    receipt["control_status"] = receipt["requests"]["req4-control"]["status"]
    receipt["control_2xx"] = 200 <= receipt["requests"]["req4-control"]["status"] < 300

    rp = os.path.join(OUT, "receipt.json")
    with open(rp, "w") as f:
        json.dump(receipt, f, indent=1, sort_keys=True)
    print(json.dumps({
        "health": receipt["health"]["status"],
        "control_status": receipt["control_status"],
        "control_2xx": receipt["control_2xx"],
        "frames_equal_all_error_cases": receipt["frames_equal_all_error_cases"],
        "frame_sha256": receipt["frame_sha256"],
        "all_decoded_sig_in_message": receipt["all_decoded_sig_in_message"],
        "escaped_cases_sig_absent_from_request_raw": receipt["escaped_cases_sig_absent_from_request_raw"],
        "escaped_cases_sig_present_in_response_raw": receipt["escaped_cases_sig_present_in_response_raw"],
        "rows": {n: {
            "status": receipt["requests"][n]["status"],
            "decoded_type": receipt["requests"][n]["decoded_type"],
            "sig_in_request_raw": receipt["requests"][n]["sig_in_request_raw"],
            "sig_in_response_raw": receipt["requests"][n]["sig_in_response_raw"],
            "decoded_sig_in_message": receipt["requests"][n]["decoded_sig_in_message"],
            "request_sha256": receipt["requests"][n]["request_sha256"],
            "response_sha256": receipt["requests"][n]["response_sha256"],
            "message": receipt["requests"][n]["error_message"],
        } for n in ORDER},
        "receipt": rp,
    }, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
