#!/usr/bin/env python3
"""Phase B: candidate remaining super-linear / fork-per-item constructs at M2 (and BASE)."""
from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, ids_doc, router_doc, jbody, uptime_str

SCRATCH = Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
M2 = SCRATCH / "probe-M2.sh"
BASE = SCRATCH / "probe-BASE.sh"


def log(*a):
    print(*a, flush=True)


class RawStub:
    """Answers every GET with a fixed raw byte blob (lets us send a giant header)."""

    def __init__(self, raw: bytes):
        self.raw = raw
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind(("127.0.0.1", 0))
        self.srv.listen(16)
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


def giant_header_blob(n: int) -> bytes:
    head = b"HTTP/1.1 200 OK\r\nContent-Type: " + b"a" * n + b"\r\nContent-Length: 2\r\n\r\n{}"
    return head


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
    return dt


def main():
    R = Runner(SCRATCH, M2.read_bytes(), "M2")
    RB = Runner(SCRATCH, BASE.read_bytes(), "BASE")
    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    if which in ("all", "hdr"):
        # B4: giant Content-Type header -> ${w%%|*}, ${w#*|} suffix/prefix removal on a
        # listener-controlled multi-MB string, in the ambient (UTF-8) locale.
        for tag, run in (("M2", R), ("BASE", RB)):
            for n in (200000, 400000, 800000, 1600000):
                with RawStub(giant_header_blob(n)) as s:
                    check(run, s.port, "good", f"B4-{tag}-giant-ct-header-n{n}")
        # control: same body, ordinary header
        with Stub({"/v1/models": jbody(ids_doc(["plain"]))}) as s:
            for tag, run in (("M2", R),):
                check(run, s.port, "good", f"B4-{tag}-control-normal-header")

    if which in ("all", "rows"):
        # B5: registry rows -> json_array's quadratic string append, amplified by the
        # listener-controlled served list in every row.
        for R_rows in (1, 2, 4, 8, 16):
            with Stub({"/v1/models": jbody(ids_doc(["a" * 200000]))}) as s:
                d = SCRATCH / "rows"
                d.mkdir(exist_ok=True)
                pin = d / "pin.txt"
                pin.write_text(f"http://127.0.0.1:{s.port}/v1\n")
                reg = d / "registry.tsv"
                lines = ["id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes"]
                for i in range(R_rows):
                    lines.append(f"row{i}\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{s.port}/v1\ta\tr")
                reg.write_text("\n".join(lines) + "\n")
                hist = d / "history"
                rc, so, se, dt = run.__class__.run(run, ["check", "--json", "--registry", str(reg),
                                                        "--history", str(hist), "--timeout", "5",
                                                        "--connect-timeout", "2"])
                log(f"B5-M2-json-array-rows-{R_rows} rc={rc} seconds={dt:.2f} {uptime_str()}")

    if which in ("all", "misc"):
        # B1: listener-controlled router status.value (no control chars) -> reason string
        for n in (500000, 1000000, 2000000):
            with Stub({"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] +
                                                    [("other", "x" * n, None, None)]))}) as s:
                check(R, s.port, "good", f"B1-M2-router-status-value-n{n}")
        # B7: one served id made of control bytes (jstr awk per-char path)
        for n in (50000, 100000, 200000):
            with Stub({"/v1/models": jbody(ids_doc(["\x01" * n]))}) as s:
                check(R, s.port, "good", f"B7-M2-control-char-id-n{n}")
        # B8: router autoload with many unloaded candidates (argv + per-index file_state)
        for n in (5000, 10000, 20000, 40000):
            with Stub({"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] * n)),
                       "/props": b'{"role":"router","models_autoload":true}'}) as s:
                check(R, s.port, "good", f"B8-M2-router-autoload-many-n{n}")


if __name__ == "__main__":
    main()
