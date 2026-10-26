#!/usr/bin/env python3
"""X1Nonce confirmation: hold a second witnessed rerun and call the frozen C1
counter's own observe() on it, recording the problems list it returns."""
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
WORK = os.path.join(S, "work2")
WD = os.path.join(S, "wd2")
OUTJ = os.path.join(S, "replay2.json")

path = os.path.join(LANE, "tools", "round49-replay-witness-audit.py")
spec = importlib.util.spec_from_file_location("c1_counter2", path)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

os.makedirs(WD, exist_ok=True)
log = open(os.path.join(S, "replay2.log"), "wb")
cmd = [sys.executable, os.path.join(LANE, "tools", "kama-live-replay.py"),
       "--receipt", RECEIPT, "--work", WORK, "--out", OUTJ,
       "--witness-dir", WD, "--witness-timeout", "600"]
p = subprocess.Popen(cmd, cwd=LANE, env=dict(os.environ, TMPDIR=S), stdout=log, stderr=subprocess.STDOUT)
res = {"schema": "kama-x1-observe-confirm/v1", "replay_cmd": cmd}
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
    if ready:
        vocab = c1.gguf_tokens(os.path.join(WORK, "download", "stories260K.gguf"))
        probs = []
        detail = []
        nonce = c1.observe(ready["pid"], ready["port"], vocab, probs)
        res.update(problems=probs, detail=detail, nonce=nonce,
                   observe_clean=not probs)
        if nonce:
            tk = c1.post(ready["port"], "/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
            res["nonce_pieces"] = [t["piece"] for t in tk]
            res["nonce_ids"] = [t["id"] for t in tk]
            res["nonce_detok"] = c1.post(ready["port"], "/detokenize",
                                         {"tokens": res["nonce_ids"]})["content"]
        with open(f"/proc/{ready['pid']}/cmdline", "rb") as fh:
            res["argv"] = [a.decode("utf-8", "replace") for a in fh.read().split(b"\0")]
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        res["health_during"] = json.loads(opener.open(
            f"http://127.0.0.1:{ready['port']}/health", timeout=10).read())
finally:
    with open(os.path.join(WD, "release"), "w") as fh:
        fh.write("released by X1Nonce confirm\n")
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
    with open(os.path.join(S, "observe-confirm.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps({k: res.get(k) for k in
                      ("nonce", "problems", "observe_clean", "replay_exit", "replay_match",
                       "rerun_outcome", "rerun_witness", "pid_alive_after", "port_refuses_after",
                       "nonce_detok", "health_during")}, indent=1))
