#!/usr/bin/env python3
"""X1Offline: a reused --witness-dir whose ready.json names an EARLIER run's live server.

Run A holds its server in D_A. Its ready.json (live pid/port) is copied into D_B,
then run B starts with --witness-dir D_B. An observer following the documented
protocol reads D_B/ready.json at once and applies the frozen C1 counter's own
observe() to it - if that reports no problems, the observer certified A's server
as B's witness while B's own server had not been announced (or even started).
"""
import importlib.util
import json
import os
import subprocess
import sys
import time

import probe as P

COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-replay-witness-audit.py"


def load_counter():
    spec = importlib.util.spec_from_file_location("c1", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def spawn(S, out, D, timeout_s):
    logs = open(os.path.join(S, f"live-{os.path.basename(out)}.log"), "wb")
    p = subprocess.Popen([sys.executable, P.LIVE, "--server", P.SERVER, "--model", P.MODEL,
                          "--model-sha256", P.MODEL_SHA, "--alias", "kama-alias",
                          "--ctx", "256", "--threads", "1", "--probe", P.PROBE,
                          "--out", out, "--witness-dir", D,
                          "--witness-timeout", str(timeout_s)],
                         cwd=S, stdout=logs, stderr=logs)
    logs.close()
    return p


def main():
    S = sys.argv[1]
    c1 = load_counter()
    vocab = c1.gguf_tokens(P.MODEL)
    DA, DB = os.path.join(S, "wd-alias-a"), os.path.join(S, "wd-alias-b")
    P.fresh(DA)
    P.fresh(DB)
    outA, outB = os.path.join(S, "receipt-alias-a.json"), os.path.join(S, "receipt-alias-b.json")
    pa = spawn(S, outA, DA, 60)
    res = {"steps": []}
    try:
        readyA = None
        t0 = time.monotonic()
        while time.monotonic() - t0 < 30:
            readyA = P.read_json(os.path.join(DA, "ready.json"))
            if isinstance(readyA, dict) and P.pid_alive(readyA.get("pid", 0)):
                break
            time.sleep(0.02)
        res["ready_A"] = readyA
        res["A_alive_before_B"] = P.pid_alive(readyA["pid"])
        # the "reused" dir already carries the previous run's handshake
        with open(os.path.join(DB, "ready.json"), "w") as fh:
            json.dump(readyA, fh)
        res["stale_ready_in_B"] = P.read_json(os.path.join(DB, "ready.json"))
        pb = spawn(S, outB, DB, 15)
        seen = P.read_json(os.path.join(DB, "ready.json"))
        probs = []
        nonce = c1.observe(seen["pid"], seen["port"], vocab, probs)
        res["observer_read"] = {"pid": seen["pid"], "port": seen["port"],
                                "A_child_pid": (P.read_json(outA) or {}).get("child_pid"),
                                "problems": probs, "nonce": nonce,
                                "accepted": not probs}
        time.sleep(0.4)  # B has surely reached its own hold by now
        own = P.read_json(os.path.join(DB, "ready.json"))
        res["B_own_ready"] = own
        with open(os.path.join(DB, "release"), "w") as fh:
            fh.write("released by x1offline\n")
        res["B_exit"] = pb.wait(timeout=60)
        with open(os.path.join(DA, "release"), "w") as fh:
            fh.write("released by x1offline\n")
        res["A_exit"] = pa.wait(timeout=60)
    finally:
        for p in (pa, pb):
            if p.poll() is None:
                p.kill()
                p.wait()
    for name, out in (("A", outA), ("B", outB)):
        r = P.read_json(out) or {}
        res[f"receipt_{name}"] = {"outcome": r.get("outcome"), "child_pid": r.get("child_pid"),
                                  "witness": r.get("witness"),
                                  "setup_error": r.get("setup_error")}
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
