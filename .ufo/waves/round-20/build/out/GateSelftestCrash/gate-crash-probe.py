#!/usr/bin/env python3
"""Error-vs-verdict probe for tests/llamacpp-live/check-receipt.py --selftest.

census GATE    run GATE's own _selftest() unchanged, recording every gate
               subprocess it spawns: exit, verdict token on stdout, and
               whether stderr carries an uncaught-exception traceback.
               Exits with _selftest()'s own return code.
receipts GATE DIR
               write the two crash receipts (A: str element in
               port_refusal_set; B: lone surrogate in probes[0]
               result.summary.exit) derived from GATE's _selftest_receipt().
Stdlib only; GATE is imported, never modified.
"""
import collections
import copy
import importlib.util
import json
import os
import sys

VERDICTS = ("VALID ", "INVALID ", "NOT-EVALUATED ")


def load(gate):
    spec = importlib.util.spec_from_file_location("gate_under_probe", gate)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def classify(rc, out, err):
    token = next((v.strip() for v in VERDICTS if out.startswith(v)), "-")
    crashed = "Traceback (most recent call last)" in err
    if rc == 1 and token == "INVALID":
        cls = "rejected+crash" if crashed else "rejected"
    elif crashed:
        cls = "crash-no-verdict"
    else:
        cls = f"rc{rc}-{token}"
    return token, crashed, cls


def census(gate):
    mod = load(gate)
    real_run = mod.subprocess.run
    rows = []

    def recording_run(argv, *a, **kw):
        proc = real_run(argv, *a, **kw)
        case = os.path.basename(argv[2]) if len(argv) > 2 else "?"
        token, crashed, cls = classify(proc.returncode, proc.stdout,
                                       proc.stderr)
        last = (proc.stderr.strip().splitlines() or ["-"])[-1]
        rows.append((case, proc.returncode, token, crashed, cls, last))
        return proc

    mod.subprocess = type("S", (), {"run": staticmethod(recording_run)})
    rc = mod._selftest()
    for case, prc, token, crashed, cls, last in rows:
        if cls not in ("rejected", "rc0-VALID", "rc3-NOT-EVALUATED") \
                or case == "receipt.json":
            print(f"CASE {case} exit={prc} token={token} "
                  f"traceback={crashed} class={cls} stderr_last={last[:160]!r}")
    counts = collections.Counter(r[4] for r in rows)
    print("SUMMARY gate_runs=%d %s selftest_return=%d"
          % (len(rows), " ".join(f"{k}={v}" for k, v in sorted(counts.items())),
             rc))
    return rc


def receipts(gate, outdir):
    mod = load(gate)
    base = mod._selftest_receipt()
    a = copy.deepcopy(base)
    a["port_refusal_set"].append("x")
    b = copy.deepcopy(base)
    b["probes"][0]["result"]["summary"].update(exit="\ud800")
    for name, r in (("receipt-A-refusal-set-str.json", a),
                    ("receipt-B-surrogate-summary-exit.json", b)):
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
            json.dump(r, fh)
        print(f"wrote {name}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "census":
        sys.exit(census(sys.argv[2]))
    if len(sys.argv) == 4 and sys.argv[1] == "receipts":
        sys.exit(receipts(sys.argv[2], sys.argv[3]))
    print(__doc__, file=sys.stderr)
    sys.exit(2)
