#!/usr/bin/env python3
"""Phase C: candidate remaining constructs at M2 (and BASE where it matters).

C1 json_array quadratic string append, amplified by the listener's answer size.
C2 print_table column-width amplification (one listener widens every other row).
C3 router autoload + many unloaded candidates: verdict stability / false green.
C4 many served ids (count-driven paths).
C5 many ids on the snapshot path.
C6 served id with many '/' (AWK_NORM split cost).
C7 served id of control bytes (jstr escaped-text path).
C8 listener-controlled router status.value of arbitrary length.
C9 giant listener header (Content-Type / Server).
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
BASE = SCRATCH / "probe-BASE.sh"


def log(*a):
    print(*a, flush=True)


def row_of(out: bytes):
    try:
        return json.loads(out.decode("utf-8"))["rows"][0]
    except Exception:
        return None


def check(runner: Runner, port, expect, label, kill=120):
    rc, so, se, dt = runner.check(port, expect, kill=kill)
    r = row_of(so)
    v = r.get("verdict") if r else ("killed" if rc is None else "unparsed")
    reason = r.get("reason") if r else "-"
    slen = len(r.get("served_model") or "") if r else -1
    log(f"{label} rc={rc} seconds={dt:.2f} verdict={v} reason={reason} served_len={slen} {uptime_str()}")
    return dt, v, reason


def snap(runner: Runner, port, expect, label, kill=120):
    rc, so, se, dt, tsv = runner.snapshot(port, expect, kill=kill)
    served = ""
    if tsv:
        for line in tsv.decode("utf-8", "replace").splitlines():
            f = line.split("\t")
            if f and f[0] == "cell" and len(f) >= 4:
                served = f[3]
    log(f"{label} rc={rc} seconds={dt:.2f} served_len={len(served)} {uptime_str()}")
    return dt


def registry_check(runner: Runner, port, nrows, label, served_id_len=200000, kill=120):
    """check --json over a registry of nrows rows, every row hitting the same stub."""
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
    log(f"{label} rc={rc} seconds={dt:.2f} stdout_bytes={len(so)} {uptime_str()}")
    return dt


def main():
    R = Runner(SCRATCH, M2.read_bytes(), "M2")
    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    if which in ("all", "c1"):
        log("--- C1: json_array quadratic (registry rows x big served answer) ---")
        for nrows in (1, 2, 4, 8, 16):
            with Stub({"/v1/models": jbody(ids_doc(["a" * 200000]))}) as s:
                registry_check(R, s.port, nrows, f"C1-M2-rows-{nrows}")

    if which in ("all", "c2"):
        log("--- C2: print_table width amplification (one big answer + several plain ports) ---")
        with Stub({"/v1/models": jbody(ids_doc(["a" * 200000]))}) as s:
            registry_check(R, s.port, 8, "C2-M2-8rows-1big", served_id_len=200000)

    if which in ("all", "c3"):
        log("--- C3: router autoload, many unloaded candidates with missing model files ---")
        for n in (1000, 5000, 20000, 60000):
            with Stub({"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] * n)),
                       "/props": b'{"role":"router","models_autoload":true}'}) as s:
                check(R, s.port, "good", f"C3-M2-autoload-missing-n{n}")

    if which in ("all", "c4"):
        log("--- C4: many served ids (count-driven) ---")
        for n in (5000, 10000, 20000, 40000):
            with Stub({"/v1/models": jbody(ids_doc([f"id{i:05d}" for i in range(n)]))}) as s:
                check(R, s.port, "id00000", f"C4-M2-many-ids-n{n}")

    if which in ("all", "c5"):
        log("--- C5: many ids on the snapshot path ---")
        for n in (5000, 10000, 20000):
            with Stub({"/v1/models": jbody(ids_doc([f"/m/x{i:05d}.gguf" for i in range(n)]))}) as s:
                snap(R, s.port, "x00000", f"C5-M2-snap-ids-n{n}")

    if which in ("all", "c6"):
        log("--- C6: served id with many '/' ---")
        for n in (50000, 100000, 200000):
            with Stub({"/v1/models": jbody(ids_doc(["a/" * n]))}) as s:
                check(R, s.port, "a", f"C6-M2-many-slashes-n{n}")

    if which in ("all", "c7"):
        log("--- C7: served id of control bytes ---")
        for n in (50000, 100000, 200000):
            with Stub({"/v1/models": jbody(ids_doc(["\x01" * n]))}) as s:
                check(R, s.port, "good", f"C7-M2-control-id-n{n}")

    if which in ("all", "c8"):
        log("--- C8: listener-controlled router status.value of arbitrary length ---")
        for n in (500000, 1000000, 2000000):
            with Stub({"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] +
                                                    [("other", "x" * n, None, None)]))}) as s:
                check(R, s.port, "good", f"C8-M2-status-value-n{n}")


if __name__ == "__main__":
    main()
