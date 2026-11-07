#!/usr/bin/env python3
"""Phase D: sharp remaining-construct candidates at M2 (attribution copies included).

D1  json_array's quadratic string append, amplified by a listener-sized served list.
D2  print_table's column-width amplification (one wide row pads every row).
D3  router_file_states argv: the per-candidate index list is passed as command-line
    words; the ceiling can turn a MODEL_UNLOADED verdict into a false MODEL_OK.
D4  the curl -w output parsing (%{content_type} is listener-controlled) under a header
    full of '|' characters.
D5  served id made of many 'a/' pairs (AWK_NORM's split on '/' inside awk).
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, ids_doc, router_doc, jbody, uptime_str

SCRATCH = Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
M2 = SCRATCH / "probe-M2.sh"
BASE = SCRATCH / "probe-BASE.sh"
WORK = SCRATCH / "phaseD"


def log(*a):
    print(*a, flush=True)


def row_of(out: bytes):
    try:
        return json.loads(out.decode("utf-8"))["rows"][0]
    except Exception:
        return None


def registry_run(runner: Runner, port, nrows, label, mode="check", kill=120, expect="a"):
    d = WORK / "rows"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    pin = d / "pin.txt"
    pin.write_text(f"http://127.0.0.1:{port}/v1\n")
    reg = d / "registry.tsv"
    lines = ["id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes"]
    for i in range(nrows):
        lines.append(f"row{i}\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{port}/v1\t{expect}\tr")
    reg.write_text("\n".join(lines) + "\n")
    hist = d / "history"
    args = [mode, "--registry", str(reg), "--history", str(hist), "--timeout", "5", "--connect-timeout", "2"]
    if mode == "check":
        args.insert(1, "--json")
    rc, so, se, dt = runner.run(args, kill=kill)
    log(f"{label} rc={rc} seconds={dt:.2f} stdout_bytes={len(so)} {uptime_str()}")
    return dt, rc, so


class RawStub:
    """Raw byte blob for every GET (lets a header carry many '|' or be huge)."""

    def __init__(self, raw: bytes):
        self.raw = raw
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind(("127.0.0.1", 0))
        self.srv.listen(32)
        self.port = self.srv.getsockname()[1]
        self.stop = False
        self.t = threading.Thread(target=self._serve, daemon=True)

    def _serve(self):
        while not self.stop:
            try:
                c, _ = self.srv.accept()
            except OSError:
                return
            try:
                c.settimeout(5)
                c.recv(65536)
                c.sendall(self.raw)
            except OSError:
                pass
            finally:
                try:
                    c.close()
                except OSError:
                    pass

    def __enter__(self):
        self.t.start()
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=1):
                    return self
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("raw stub never accepted")

    def __exit__(self, *a):
        self.stop = True
        try:
            self.srv.close()
        except OSError:
            pass


def main():
    R = Runner(SCRATCH, M2.read_bytes(), "M2")
    RB = Runner(SCRATCH, BASE.read_bytes(), "BASE")
    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    if which in ("all", "d1"):
        log("--- D1: json_array quadratic append (registry rows x 200 000-byte served id) ---")
        for nrows in (1, 2, 4, 8, 16, 32):
            with Stub({"/v1/models": jbody(ids_doc(["a" * 200000]))}) as s:
                registry_run(R, s.port, nrows, f"D1-M2-json-rows-{nrows}")

    if which in ("all", "d2"):
        log("--- D2: print_table width amplification (non-json check) ---")
        for nrows in (1, 2, 4, 8):
            with Stub({"/v1/models": jbody(ids_doc(["a" * 200000]))}) as s:
                registry_run(R, s.port, nrows, f"D2-M2-table-rows-{nrows}", mode="check")

    if which in ("all", "d3"):
        log("--- D3: router_file_states argv ceiling (many unloaded candidates, args present) ---")
        for n in (1000, 20000, 60000, 200000):
            ents = [("good", "unloaded", None, None)] * n
            body = {"object": "list", "data": [
                {"id": "good", "status": {"value": "unloaded",
                                          "args": ["/etc/hostname", "--model", "/nonexistent/r92/x.gguf"]}}
                for _ in range(n)]}
            with Stub({"/v1/models": jbody(body),
                       "/props": b'{"role":"router","models_autoload":true}'}) as s:
                rc, so, se, dt = R.check(s.port, "good")
                r = row_of(so)
                v = r.get("verdict") if r else ("killed" if rc is None else "unparsed")
                reason = r.get("reason") if r else "-"
                log(f"D3-M2-autoload-args-n{n} rc={rc} seconds={dt:.2f} verdict={v} reason={reason} {uptime_str()}")

    if which in ("all", "d4"):
        log("--- D4: curl -w output parsing with a '|'-heavy listener header ---")
        for n in (1000, 10000, 100000, 400000):
            ct = "x" + "|y" * (n // 2)
            raw = (b"HTTP/1.1 200 OK\r\nContent-Type: " + ct.encode() +
                   b"\r\nContent-Length: 2\r\n\r\n{}")
            with RawStub(raw) as s:
                rc, so, se, dt = R.check(s.port, "good")
                log(f"D4-M2-pipe-header-n{n} rc={rc} seconds={dt:.2f} {uptime_str()}")

    if which in ("all", "d5"):
        log("--- D5: served id of many 'a/' pairs (awk split on '/') ---")
        for n in (50000, 100000, 200000):
            with Stub({"/v1/models": jbody(ids_doc(["a/" * n]))}) as s:
                rc, so, se, dt = R.check(s.port, "a")
                r = row_of(so)
                v = r.get("verdict") if r else "unparsed"
                log(f"D5-M2-many-slash-n{n} rc={rc} seconds={dt:.2f} verdict={v} {uptime_str()}")


if __name__ == "__main__":
    main()
