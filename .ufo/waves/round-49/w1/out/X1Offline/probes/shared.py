#!/usr/bin/env python3
"""X1Offline: two live runs sharing one --witness-dir (the reuse hazard, concurrent)."""
import json
import os
import subprocess
import sys
import time

import probe as P


def main():
    S = sys.argv[1]
    D = os.path.join(S, "wd-shared")
    P.fresh(D)
    outs = [os.path.join(S, f"receipt-shared-{n}.json") for n in (1, 2)]
    logs = [open(os.path.join(S, f"live-shared-{n}.log"), "wb") for n in (1, 2)]
    procs, events, seen = [], [], set()
    t0 = time.monotonic()
    try:
        for n, out in enumerate(outs, 1):
            argv = [sys.executable, P.LIVE, "--server", P.SERVER, "--model", P.MODEL,
                    "--model-sha256", P.MODEL_SHA, "--alias", f"kama-shared-{n}",
                    "--ctx", "256", "--threads", "1", "--probe", P.PROBE,
                    "--out", out, "--witness-dir", D, "--witness-timeout", "20"]
            procs.append(subprocess.Popen(argv, cwd=S, stdout=logs[n - 1], stderr=logs[n - 1]))
        while time.monotonic() - t0 < 30:
            r = P.read_json(os.path.join(D, "ready.json"))
            if isinstance(r, dict) and r.get("pid") not in seen:
                seen.add(r.get("pid"))
                events.append({"t_ms": int((time.monotonic() - t0) * 1000), "pid": r.get("pid"),
                               "port": r.get("port"), "written_utc": r.get("written_utc")})
            if len(procs) == 2 and len(seen) >= 2:
                break
            time.sleep(0.02)
        time.sleep(0.3)  # both holds are up if the ready slot is per-run
        with open(os.path.join(D, "release"), "w") as fh:
            fh.write("one release for both runs\n")
        codes = [p.wait(timeout=60) for p in procs]
    finally:
        for p in procs:
            if p.poll() is None:
                p.kill()
                p.wait()
        for fh in logs:
            fh.close()
    res = {"events_ready_slot": events, "exit": codes, "runs": []}
    for n, out in enumerate(outs, 1):
        r = P.read_json(out) or {}
        res["runs"].append({"run": n, "outcome": r.get("outcome"), "child_pid": r.get("child_pid"),
                            "port": r.get("port"), "witness": r.get("witness")})
    res["ready_json_after"] = P.read_json(os.path.join(D, "ready.json"))
    res["listing_after"] = sorted(os.listdir(D))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
