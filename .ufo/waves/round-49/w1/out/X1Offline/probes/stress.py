#!/usr/bin/env python3
"""X1Offline: K live runs sharing one --witness-dir, started together.

Counts how often a run dies in the handshake (the fixed ready.json.tmp name is
written by every run, and os.replace then finds it already renamed away) and how
one release file ends every hold.
"""
import json
import os
import subprocess
import sys
import time

import probe as P

K = int(sys.argv[2]) if len(sys.argv) > 2 else 8
ROUNDS = int(sys.argv[3]) if len(sys.argv) > 3 else 3


def main():
    S = sys.argv[1]
    res = {"K": K, "rounds": []}
    for rnd in range(1, ROUNDS + 1):
        D = os.path.join(S, f"wd-stress{rnd}")
        P.fresh(D)
        procs, outs, logs = [], [], []
        for n in range(1, K + 1):
            out = os.path.join(S, f"receipt-stress{rnd}-{n}.json")
            lf = open(os.path.join(S, f"live-stress{rnd}-{n}.log"), "wb")
            logs.append(lf)
            outs.append(out)
            procs.append(subprocess.Popen(
                [sys.executable, P.LIVE, "--server", P.SERVER, "--model", P.MODEL,
                 "--model-sha256", P.MODEL_SHA, "--alias", f"kama-stress{rnd}-{n}",
                 "--ctx", "256", "--threads", "1", "--probe", P.PROBE,
                 "--out", out, "--witness-dir", D, "--witness-timeout", "20"],
                cwd=S, stdout=lf, stderr=lf))
        time.sleep(1.5)
        ready = P.read_json(os.path.join(D, "ready.json"))
        with open(os.path.join(D, "release"), "w") as fh:
            fh.write("one release for all\n")
        codes = [p.wait(timeout=60) for p in procs]
        for lf in logs:
            lf.close()
        runs = []
        for n, out in enumerate(outs, 1):
            r = P.read_json(out) or {}
            runs.append({"run": n, "exit": codes[n - 1], "outcome": r.get("outcome"),
                         "setup_error": r.get("setup_error"),
                         "witness": r.get("witness")})
        res["rounds"].append({"round": rnd, "ready_slot_at_release": ready,
                              "runs": runs,
                              "errors": [x["setup_error"] for x in runs if x["setup_error"]],
                              "released": sum(1 for x in runs
                                              if x["witness"] and x["witness"].get("released") is True),
                              "not_released": sum(1 for x in runs
                                                  if x["witness"] and x["witness"].get("released") is not True)})
    tot = [x for r in res["rounds"] for x in r["runs"]]
    res["summary"] = {
        "runs": len(tot),
        "handshake_errors": {e: sum(1 for x in tot if x["setup_error"] == e)
                             for e in sorted({x["setup_error"] for x in tot if x["setup_error"]})},
        "released": sum(1 for x in tot if x["witness"] and x["witness"].get("released") is True),
        "no_witness_block": sum(1 for x in tot if not x["witness"]),
        "distinct_ready_pids_seen": len({r["ready_slot_at_release"].get("pid")
                                         for r in res["rounds"]
                                         if isinstance(r["ready_slot_at_release"], dict)}),
        "runs_started_vs_ready_slots": (len(tot), len(res["rounds"])),
    }
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
