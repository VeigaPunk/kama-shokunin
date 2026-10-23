#!/usr/bin/env python3
r"""Function-level replay of live probe fixtures through the frozen A3 counter
clauses, versus the round-26 line-384 raw-byte echo test.

Imports count-c1.py as a module (module level holds only constants; main() is
guarded by `if __name__ == "__main__"` at line 744) and calls `occurs`,
`json_strings`, `request_surfaces` without invoking main().
"""
import hashlib
import importlib.util
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
COUNTER = os.path.join(LANE, ".ufo/waves/round-27/count-c1.py")
OUT = os.path.join(LANE, ".ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe")
CASES = ["req1-plain", "req2-firstesc", "req3-fullesc",
         "req5-altsig-plain", "req6-altsig-full"]


def load_counter():
    spec = importlib.util.spec_from_file_location("count_c1_frozen", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    mod = load_counter()
    rows = {}
    frames = {}
    for name in CASES:
        raw = open(os.path.join(OUT, name + ".req"), "rb").read()
        resp = json.load(open(os.path.join(OUT, name + ".resp")))
        msg = resp["error"]["message"]
        body = json.loads(raw.decode("ascii"))
        sig = body["response_format"]["type"]
        req = {"path": "/v1/chat/completions", "body": body}
        surfaces = mod.request_surfaces(req)
        rows[name] = {
            "signature": sig,
            "raw_request_sha256": hashlib.sha256(raw).hexdigest(),
            "round26_line384_credit_not_echoed": sig not in raw.decode("ascii"),
            "round26_predicate": "sig not in req_bytes",
            "a3_clause_f_refuses_echo": any(mod.occurs(sig, s) for s in surfaces),
            "a3_surface_hits": sorted({s for s in surfaces if mod.occurs(sig, s)}),
            "live_message_contains_sig": sig in msg,
            "a3_clause_h_frame": msg.replace(sig, "\0").lower(),
        }
        frames[name] = rows[name]["a3_clause_h_frame"]
    out = {
        "counter_path": ".ufo/waves/round-27/count-c1.py",
        "counter_sha256_file": hashlib.sha256(open(COUNTER, "rb").read()).hexdigest(),
        "counter_functions_used": ["request_surfaces", "json_strings", "occurs"],
        "main_not_invoked": True,
        "rows": rows,
        "clause_h_all_frames_equal": len(set(frames.values())) == 1,
        "clause_h_frames": frames,
        "note": ("Live fixtures: three raw spellings of one signature and two of "
                 "a second signature. Round-26 credit test is the raw-byte "
                 "substring check from eb09e742:count-c1.py line 384."),
    }
    p = os.path.join(OUT, "replay-function-level.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps({k: out[k] for k in (
        "counter_sha256_file", "clause_h_all_frames_equal")}, indent=1))
    for name, r in rows.items():
        print(name, "| round26_credit=", r["round26_line384_credit_not_echoed"],
              "| a3f_refuses=", r["a3_clause_f_refuses_echo"],
              "| live_echo=", r["live_message_contains_sig"])
    print("receipt:", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
