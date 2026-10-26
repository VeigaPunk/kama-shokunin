#!/usr/bin/env python3
"""compare-verdicts.py - X1Observe: my observer's verdicts vs the C1 counter's.

Inputs (paths given on the command line):
  --counter  the C1 counter's receipt at the measured commit (its text receipt)
  --obs N    this seat's observer receipt for receipt-N
  --replay N the lane replay tool's own result for receipt-N
Prints a table and writes --out (JSON). Agreement is judged per leg the counter
also reports (exe, listen, model, nonce round trip) plus the witness release the
counter requires; nothing is inferred from the counter's code.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

COUNTER_WITNESS = re.compile(
    r"detail: witness w(\d+): pid (\d+) port (\d+) exe\+listen\+model ok, "
    r"nonce '(?P<nonce>[^']+)' round-tripped")
COUNTER_VOCAB = re.compile(r"detail: counter vocabulary: (\d+) tokens")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--obs", nargs=3, required=True)
    ap.add_argument("--replay", nargs=3, required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    text = open(a.counter).read()
    counter = {"tip": None, "summary": None, "witness": {}, "vocab": None,
               "lines": []}
    for line in text.splitlines():
        if line.startswith("tip="):
            counter["tip"] = line.split("=", 1)[1]
        if line.startswith("witness="):
            counter["summary"] = line
        m = COUNTER_VOCAB.search(line)
        if m:
            counter["vocab"] = int(m.group(1))
        m = COUNTER_WITNESS.search(line)
        if m:
            counter["witness"][int(m.group(1))] = {
                "pid": int(m.group(2)), "port": int(m.group(3)),
                "nonce": m.group("nonce"),
                "exe": True, "listen": True, "model": True, "nonce_ok": True,
                "raw": line}
        if line.startswith("detail:"):
            counter["lines"].append(line)

    rows, mismatches = [], []
    for i in range(3):
        obs = json.load(open(a.obs[i]))
        replay = json.load(open(a.replay[i]))
        rerun = json.load(open(replay["rerun_receipt"])) if replay.get("rerun_receipt") else {}
        checks = {c["id"]: c for c in obs.get("checks", [])}
        mine = {
            "exe": checks.get("exe_digest", {}).get("passed"),
            "listen": checks.get("listen_ownership", {}).get("passed"),
            "model": checks.get("model_digest", {}).get("passed"),
            "nonce_tokenize": checks.get("nonce_tokenize", {}).get("passed"),
            "nonce_detokenize": checks.get("nonce_detokenize", {}).get("passed"),
            "pid_gone": checks.get("pid_gone_after_release", {}).get("passed"),
        }
        cw = counter["witness"].get(i + 1)
        same = {
            "exe": bool(cw and cw["exe"]) == bool(mine["exe"]),
            "listen": bool(cw and cw["listen"]) == bool(mine["listen"]),
            "model": bool(cw and cw["model"]) == bool(mine["model"]),
            # the counter's line reports one nonce leg; mine splits tokenize/
            # detokenize, so compare its round trip with both halves together
            "nonce": bool(cw and cw["nonce_ok"]) == bool(mine["nonce_tokenize"]
                                                         and mine["nonce_detokenize"]),
        }
        row = {
            "receipt": obs.get("receipt"),
            "counter": {"present": cw is not None,
                        "pid": (cw or {}).get("pid"),
                        "port": (cw or {}).get("port"),
                        "nonce": (cw or {}).get("nonce")},
            "mine": {"verdict": obs.get("verdict"),
                     "pid": (obs.get("ready") or {}).get("pid"),
                     "port": (obs.get("ready") or {}).get("port"),
                     "nonce": obs.get("nonce"),
                     "checks": mine},
            "replay": {"exit": replay.get("live_exit"),
                       "match": replay.get("match"),
                       "mismatches": len(replay.get("mismatches") or []),
                       "witness_released": (rerun.get("witness") or {}).get("released"),
                       "witness_pid": (rerun.get("witness") or {}).get("pid"),
                       "witness_port": (rerun.get("witness") or {}).get("port")},
            "agree": same,
            "all_agree": all(same.values()),
        }
        if not row["all_agree"]:
            mismatches.append({"receipt": row["receipt"], "legs": same})
        rows.append(row)

    result = {"counter": {k: counter[k] for k in ("tip", "summary", "vocab")},
              "rows": rows, "disagreements": mismatches,
              "agreement": f"{sum(1 for r in rows if r['all_agree'])}/3"}
    print(f"counter: {counter['summary']} (vocab {counter['vocab']})")
    for r in rows:
        c, m = r["counter"], r["mine"]
        print(f"{r['receipt'].split('/')[-1]}: counter(exe/listen/model/nonce)="
              f"{c['present'] and 'all ok'} mine(exe/listen/model/tok/detok/pidgone)="
              f"{[m['checks'][k] for k in ('exe','listen','model','nonce_tokenize','nonce_detokenize','pid_gone')]} "
              f"released={r['replay']['witness_released']} replay_match={r['replay']['match']} "
              f"agree={r['all_agree']}")
    print(f"agreement {result['agreement']} disagreements={len(mismatches)}")
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(result, fh, indent=1)
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
