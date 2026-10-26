#!/usr/bin/env python3
"""X1Nonce bulk: on a fourth witnessed rerun, 300 counter-form nonces + 16
homogeneous-hex nonces + the same 10 edge forms, aggregated."""
import importlib.util
import json
import os
import secrets
import subprocess
import sys
import time
import urllib.request

S = "/fast/scratch/hyaku/kama-r49/X1Nonce"
LANE = os.path.join(S, "lane")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-3.json")
WORK = os.path.join(S, "work4")
WD = os.path.join(S, "wd4")
OUTJ = os.path.join(S, "replay4.json")

spec = importlib.util.spec_from_file_location(
    "c1_counter4", os.path.join(LANE, "tools", "round49-replay-witness-audit.py"))
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

os.makedirs(WD, exist_ok=True)
log = open(os.path.join(S, "replay4.log"), "wb")
cmd = [sys.executable, os.path.join(LANE, "tools", "kama-live-replay.py"),
       "--receipt", RECEIPT, "--work", WORK, "--out", OUTJ,
       "--witness-dir", WD, "--witness-timeout", "600"]
p = subprocess.Popen(cmd, cwd=LANE, env=dict(os.environ, TMPDIR=S), stdout=log, stderr=subprocess.STDOUT)
res = {"schema": "kama-x1-nonce-bulk/v1", "replay_cmd": cmd}
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

    def rule(nonce):
        tk = c1.post(port, "/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
        ids = [t["id"] for t in tk]
        bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                     and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
        if not ids or bad:
            return {"nonce": nonce, "holds": False, "stage": "pieces", "bad": bad}
        dt = c1.post(port, "/detokenize", {"tokens": ids})["content"]
        return {"nonce": nonce, "holds": dt in (nonce, " " + nonce),
                "stage": "ok" if dt in (nonce, " " + nonce) else "detok",
                "detok": dt, "exact": dt == nonce, "ntok": len(ids)}

    t1 = time.monotonic()
    samples = [f"kama witness {secrets.token_hex(8)}" for _ in range(300)]
    bulk = [rule(n) for n in samples]
    res["bulk_seconds"] = round(time.monotonic() - t1, 2)
    homog = [f"kama witness {c * 16}" for c in "0123456789abcdef"]
    hom = [rule(n) for n in homog]
    edge = [rule(n) for n in (
        "kama witness 0123456789ABCDEF",
        "KAMA WITNESS 0123456789abcdef",
        "kama witness 0123456789012345",
        " kama witness 0123456789abcdef",
        "kama witness " + "a" * 187,
        "kama witness " + "0" * 200,
        "kama witness caf\u00e9" + "0123456789ab",
        "kama witness 0123456789abcdef\n",
        "kama witness ",
        "kama witness 0123456789abcdef0")]
    res["bulk"] = {"total": len(bulk), "holds": sum(x["holds"] for x in bulk),
                   "stages": sorted({x["stage"] for x in bulk}),
                   "exact_detok": sum(1 for x in bulk if x.get("exact")),
                   "failures": [x for x in bulk if not x["holds"]],
                   "ntok_range": [min(x["ntok"] for x in bulk), max(x["ntok"] for x in bulk)]}
    res["homogeneous"] = [{"suffix": n[13:], "holds": x["holds"], "ntok": x.get("ntok"),
                           "detok": x.get("detok")} for n, x in zip(homog, hom)]
    res["edge"] = edge
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    res["health_during"] = json.loads(opener.open(f"http://127.0.0.1:{port}/health", timeout=10).read())
finally:
    with open(os.path.join(WD, "release"), "w") as fh:
        fh.write("released by X1Nonce bulk\n")
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
    with open(os.path.join(S, "nonce-bulk.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps({k: res.get(k) for k in ("bulk", "bulk_seconds", "homogeneous", "replay_exit",
                                              "replay_match", "rerun_outcome", "rerun_witness",
                                              "pid_alive_after", "port_refuses_after", "health_during")},
                     indent=1))
    print("edge", [{"holds": e["holds"], "stage": e["stage"], "exact": e.get("exact")} for e in res["edge"]])
