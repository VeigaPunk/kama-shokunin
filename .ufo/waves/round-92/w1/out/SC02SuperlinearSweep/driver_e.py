#!/usr/bin/env python3
"""Doubling battery for the remaining-candidate constructs (N, 2N, 4N) with
one-construct-changed attribution copies. All shapes answer under the 4 MiB cap.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, ids_doc, router_doc, jbody, uptime_str

SCRATCH = Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
M2 = SCRATCH / "probe-M2.sh"
CAND = {
    "M2": SCRATCH / "probe-M2.sh",
    "cand-json_array": SCRATCH / "cand-json_array.sh",
    "cand-print_table": SCRATCH / "cand-print_table.sh",
    "cand-persist_clean": SCRATCH / "cand-persist_clean.sh",
}


def log(*a):
    print(*a, flush=True)


def row_of(out: bytes):
    try:
        return json.loads(out.decode("utf-8"))["rows"][0]
    except Exception:
        return None


def check(runner, port, expect, label, kill=120):
    rc, so, se, dt = runner.check(port, expect, kill=kill)
    r = row_of(so)
    v = r.get("verdict") if r else ("killed" if rc is None else "unparsed")
    reason = r.get("reason") if r else "-"
    slen = len(r.get("served_model") or "") if r else -1
    log(f"{label:<52} rc={rc} t={dt:7.2f}s verdict={v:<16} reason={reason:<24} served_len={slen}  {uptime_str()}")
    return dt


def snap(runner, port, expect, label, kill=120):
    rc, so, se, dt, tsv = runner.snapshot(port, expect, kill=kill)
    served = ""
    if tsv:
        for line in tsv.decode("utf-8", "replace").splitlines():
            f = line.split("\t")
            if f and f[0] == "cell" and len(f) >= 4:
                served = f[3]
    log(f"{label:<52} rc={rc} t={dt:7.2f}s served_len={len(served)}  {uptime_str()}")
    return dt


def registry_check(runner, port, nrows, label, kill=120):
    d = SCRATCH / "rows"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    pin = d / "pin.txt"
    pin.write_text(f"http://127.0.0.1:{port}/v1\n")
    reg = d / "registry.tsv"
    lines = ["id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes"]
    for i in range(nrows):
        lines.append(f"row{i}\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{port}/v1\ta\tr")
    reg.write_text("\n".join(lines) + "\n")
    hist = d / "history"
    rc, so, se, dt = runner.run(["check", "--json", "--registry", str(reg), "--history", str(hist),
                                  "--timeout", "5", "--connect-timeout", "2"], kill=kill)
    log(f"{label:<52} rc={rc} t={dt:7.2f}s stdout={len(so)}B  {uptime_str()}")
    return dt


def main():
    which = sys.argv[1]
    R = {k: Runner(SCRATCH, v.read_bytes(), k) for k, v in CAND.items()}

    if which == "ctl":
        # E1: AWK_JSTR per-character path (id of control bytes), N/2N/4N
        for tag in ("M2",):
            for n in (200000, 400000, 800000):
                with Stub({"/v1/models": jbody(ids_doc(["\x01" * n]))}) as s:
                    check(R[tag], s.port, "good", f"E1-{tag}-ctrl-id-n{n}")

    if which == "slash":
        # E2: AWK_NORM split on '/' inside model_matches, N/2N/4N
        for tag in ("M2",):
            for n in (100000, 200000, 400000):
                with Stub({"/v1/models": jbody(ids_doc(["a/" * n]))}) as s:
                    check(R[tag], s.port, "a", f"E2-{tag}-slash-id-n{n}")
        # E2b: same id on the snapshot path (served_persist -> AWK_NORM)
        for n in (100000, 200000, 400000):
            with Stub({"/v1/models": jbody(ids_doc(["a/" * n]))}) as s:
                snap(R["M2"], s.port, "a", f"E2b-M2-snap-slash-id-n{n}")

    if which == "json":
        # E3: json_array quadratic append; M2 vs the one-construct-changed copy
        for tag in ("M2", "cand-json_array"):
            for nrows in (8, 16, 32, 64):
                with Stub({"/v1/models": jbody(ids_doc(["a" * 200000]))}) as s:
                    registry_check(R[tag], s.port, nrows, f"E3-{tag}-json-rows-{nrows}")

    if which == "table":
        # E4: print_table width amplification; M2 vs the one-construct-changed copy
        for tag in ("M2", "cand-print_table"):
            for nrows in (8, 16, 32, 64):
                with Stub({"/v1/models": jbody(ids_doc(["a" * 200000]))}) as s:
                    registry_check(R[tag], s.port, nrows, f"E4-{tag}-table-rows-{nrows}")

    if which == "pc":
        # E5: persist_clean's three global replacements; M2 vs the one-construct-changed copy
        #     (listener drives the served column -> EV_SERVED -> persist_clean on the reason/port)
        for tag in ("M2", "cand-persist_clean"):
            for n in (200000, 400000, 800000):
                with Stub({"/v1/models": jbody(ids_doc(["\x01" * n]))}) as s:
                    snap(R[tag], s.port, "good", f"E5-{tag}-persist-n{n}")

    if which == "argv":
        # E6: router_file_states argv (one word per candidate) + per-candidate file_state
        for n in (20000, 40000, 80000):
            body = {"object": "list", "data": [
                {"id": "good", "status": {"value": "unloaded",
                                          "args": ["/etc/hostname", "--model", "/nonexistent/r92/x.gguf"]}}
                for _ in range(n)]}
            with Stub({"/v1/models": jbody(body),
                       "/props": b'{"role":"router","models_autoload":true}'}) as s:
                check(R["M2"], s.port, "good", f"E6-M2-autoload-args-n{n}")

    if which == "rstatus":
        # E7: listener-controlled router status.value of arbitrary length (reason string)
        for n in (500000, 1000000, 2000000):
            with Stub({"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] +
                                                    [("other", "x" * n, None, None)]))}) as s:
                check(R["M2"], s.port, "good", f"E7-M2-router-status-value-n{n}")


if __name__ == "__main__":
    main()
