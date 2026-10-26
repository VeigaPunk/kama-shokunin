#!/usr/bin/env python3
"""X1Nonce depth probe: on a third witnessed rerun, localise the C1 nonce-rule
failure for non-ASCII/control content (pieces check vs detokenize check) and show
the class boundary: any byte whose GGUF entry is the <0xXX> byte-fallback token."""
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.request

S = "/fast/scratch/hyaku/kama-r49/X1Nonce"
LANE = os.path.join(S, "lane")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-3.json")
WORK = os.path.join(S, "work3")
WD = os.path.join(S, "wd3")
OUTJ = os.path.join(S, "replay3.json")

spec = importlib.util.spec_from_file_location(
    "c1_counter3", os.path.join(LANE, "tools", "round49-replay-witness-audit.py"))
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

os.makedirs(WD, exist_ok=True)
log = open(os.path.join(S, "replay3.log"), "wb")
cmd = [sys.executable, os.path.join(LANE, "tools", "kama-live-replay.py"),
       "--receipt", RECEIPT, "--work", WORK, "--out", OUTJ,
       "--witness-dir", WD, "--witness-timeout", "600"]
p = subprocess.Popen(cmd, cwd=LANE, env=dict(os.environ, TMPDIR=S), stdout=log, stderr=subprocess.STDOUT)
res = {"schema": "kama-x1-nonce-depth/v1", "replay_cmd": cmd}
ready = None
try:
    t0 = time.monotonic()
    while time.monotonic() - t0 < 600 and p.poll() is None:
        try:
            with open(os.path.join(WD, "ready.json")) as fh:
                ready = json.load(fh)
            break
        except (OSError, ValueError):
            time.sleep(0.1)
    res["ready"] = ready
    vocab = c1.gguf_tokens(os.path.join(WORK, "download", "stories260K.gguf"))
    port = ready["port"]

    def detail(nonce, label):
        tk = c1.post(port, "/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
        ids = [t["id"] for t in tk]
        bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                     and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
        dt = c1.post(port, "/detokenize", {"tokens": ids})["content"]
        return {"label": label, "nonce": nonce, "ids": ids,
                "pieces": [t.get("piece") for t in tk],
                "bad": [{"id": t["id"], "piece": t.get("piece"), "vocab": vocab[t["id"]]} for t in bad],
                "pieces_rule_holds": bool(ids) and not bad,
                "detok": dt,
                "detok_rule_holds": dt in (nonce, " " + nonce),
                "joint_rule_holds": bool(ids) and not bad and dt in (nonce, " " + nonce)}

    cases = [
        ("kama witness 0123456789abcdef\n", "newline"),
        ("kama witness 0123456789abcdef\t", "tab"),
        ("kama witness 0123456789abcde\x01", "0x01"),
        ("kama witness caf\u4e2d0123456789", "CJK 中"),
        ("kama witness 0123456789abcdef", "control counter form"),
    ]
    res["cases"] = [detail(n, l) for n, l in cases]
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    res["health_during"] = json.loads(opener.open(f"http://127.0.0.1:{port}/health", timeout=10).read())
finally:
    with open(os.path.join(WD, "release"), "w") as fh:
        fh.write("released by X1Nonce depth\n")
    try:
        code = p.wait(timeout=300)
    except subprocess.TimeoutExpired:
        p.kill()
        code = None
    res["replay_exit"] = code
    log.close()
    if ready:
        time.sleep(0.5)
        res["pid_alive_after"] = c1.pid_alive(ready["pid"])
        res["port_refuses_after"] = c1.port_refuses(ready["port"])
    with open(OUTJ) as fh:
        rj = json.load(fh)
    res["replay_match"] = rj.get("match")
    res["replay_mismatches"] = rj.get("mismatches")
    with open(rj["rerun_receipt"]) as fh:
        rr = json.load(fh)
    res["rerun_witness"] = rr.get("witness")
    res["rerun_outcome"] = rr.get("outcome")
    with open(os.path.join(S, "nonce-depth.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    for c in res["cases"]:
        print(json.dumps({"label": c["label"], "pieces": c["pieces_rule_holds"],
                          "detok": c["detok_rule_holds"], "joint": c["joint_rule_holds"],
                          "bad": c["bad"], "detok_str": c["detok"],
                          "pieces": c["pieces"] if c["label"] != "control counter form" else None}))
    print(json.dumps({k: res.get(k) for k in ("replay_exit", "replay_match", "rerun_outcome",
                                              "rerun_witness", "pid_alive_after",
                                              "port_refuses_after", "health_during")}, indent=1))
