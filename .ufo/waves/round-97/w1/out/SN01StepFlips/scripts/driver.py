#!/usr/bin/env python3
"""SN01StepFlips driver.

Runs the REAL probe (bytes taken from `git show HEAD:tools/kama-probe.sh`, copied read-only
into the scratch tree) against a stub router, exactly the way tools/round97-router-budget.py
does it, for six (T, nd) fixtures.

Two probe copies are used:
  * pristine  -> the authoritative verdict/reason (byte-identical to the tracked probe)
  * traced    -> the same bytes with a scratch-only instrumentation patch that names the
                 guard which fired (steps / meta / size / max_tensors / ok)

Outputs one JSON blob on stdout and a human table on stderr.
"""
from __future__ import annotations

import http.server
import json
import os
import re
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips")
FIX = SCRATCH / "fix"
PROBE_DIR = SCRATCH / "probe"
CAP = 4194304
PROPS = b'{"role":"router","models_autoload":true}'
KILL = 1200

CASES = [(833332, 1), (833333, 1), (900000, 1), (700000, 4), (555555, 4), (555556, 4)]
CLAIM = {
    (833332, 1): ("invalid", "MODEL_UNLOADED", "router-model-invalid"),
    (833333, 1): ("-", "MODEL_OK", "router-unloaded-autoload"),
    (900000, 1): ("-", "MODEL_OK", "router-unloaded-autoload"),
    (700000, 4): ("-", "MODEL_OK", "router-unloaded-autoload"),
    (555555, 4): ("invalid", "MODEL_UNLOADED", "router-model-invalid"),
    (555556, 4): ("-", "MODEL_OK", "router-unloaded-autoload"),
}


class Stub:
    def __init__(self, routes):
        self.routes = routes
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                body = stub.routes.get(self.path.split("?")[0])
                code = 200
                if body is None:
                    body, code = b'{"error":"not found"}', 404
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except OSError:
                    pass

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.t.start()
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=1):
                    return self
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def router_body(arg_lists) -> bytes:
    data = [{"id": "good", "status": {"value": "unloaded", "args": a}} for a in arg_lists]
    return json.dumps({"object": "list", "data": data}, separators=(",", ":")).encode()


def gguf_ok(path: Path):
    """A minimal valid GGUF (one F32 tensor, 32 elements, data present) -> probe state `ok`."""
    name = b"t0"
    dims = struct.pack("<Q", 32)
    head = (b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 1, 0)
            + struct.pack("<Q", len(name)) + name + struct.pack("<I", 1) + dims
            + struct.pack("<IQ", 0, 0))
    pad = (len(head) + 31) // 32 * 32 - len(head)
    blob = head + b"\0" * pad + b"\0" * 128
    path.write_bytes(blob)
    return str(path)


def probe_bytes() -> bytes:
    p = subprocess.run(["git", "-C", str(LANE), "show", "HEAD:tools/kama-probe.sh"],
                       capture_output=True)
    assert p.returncode == 0, p.stderr
    return p.stdout


def traced_bytes(mb: bytes) -> bytes:
    """Scratch-only instrumentation: name the guard that decided."""
    s = mb.decode()
    # 1. Unknown reasons
    s = s.replace("""            if steps[0] > MAX_STEPS:
                raise Unknown()
            pos = f.tell()
            if pos > MAX_META:
                raise Unknown()""",
                  """            if steps[0] > MAX_STEPS:
                raise Unknown("steps:" + str(steps[0]))
            pos = f.tell()
            if pos > MAX_META:
                raise Unknown("meta:" + str(pos))""")
    s = s.replace("""            if n < 0 or pos + n > size:
                raise Bad()""",
                  """            if n < 0 or pos + n > size:
                raise Bad("size:" + str(pos) + "+" + str(n) + ">" + str(size))""")
    # 2. early returns
    s = s.replace("""            if n_kv * 13 + n_tensors * 24 > size:
                return "invalid"
            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:
                return "-"'""".replace("'", ""),
                  """            if n_kv * 13 + n_tensors * 24 > size:
                return "invalid-guard-size"
            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:
                return "-guard-max_tensors\"""")
    # 3. except clauses report
    s = s.replace("""        except Bad:
            return "invalid"
        except Unknown:
            return "-"'""".replace("'", ""),
                  """        except Bad as e:
            sys.stderr.write("TRACE_BAD " + str(e) + "\\n")
            return "invalid"
        except Unknown as e:
            sys.stderr.write("TRACE_UNKNOWN " + str(e) + "\\n")
            return "-"'""".replace("'", ""))
    assert "TRACE_UNKNOWN" in s and "invalid-guard-size" in s, "trace patch did not apply"
    return s.encode()


def run_check(probe_path: Path, port: int, cwd: Path):
    env = dict(os.environ, TMPDIR=str(cwd))
    t0 = time.monotonic()
    try:
        p = subprocess.run(["bash", str(probe_path), "check", "--port", str(port),
                            "--expect", "good", "--timeout", "5", "--connect-timeout", "2",
                            "--json"],
                           capture_output=True, timeout=KILL, env=env, cwd=cwd)
    except subprocess.TimeoutExpired:
        return {"rc": None, "verdict": "TIMEOUT", "reason": "-", "wall": time.monotonic() - t0,
                "stderr": ""}
    wall = time.monotonic() - t0
    try:
        row = json.loads(p.stdout.decode("utf-8"))["rows"][0]
        return {"rc": p.returncode, "verdict": row.get("verdict"), "reason": row.get("reason"),
                "wall": wall, "stderr": p.stderr.decode("utf-8", "replace")}
    except Exception as e:
        return {"rc": p.returncode, "verdict": f"unparsed({e})", "reason": "-", "wall": wall,
                "stderr": p.stderr.decode("utf-8", "replace")}


def main() -> int:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    mb = probe_bytes()
    pristine = PROBE_DIR / "pristine" / "kama-probe.sh"
    traced = PROBE_DIR / "traced" / "kama-probe.sh"
    pristine.parent.mkdir(parents=True, exist_ok=True)
    traced.parent.mkdir(parents=True, exist_ok=True)
    pristine.write_bytes(mb)
    traced.write_bytes(traced_bytes(mb))

    exe = gguf_ok(FIX / "ok.gguf")
    cwd = SCRATCH / "cwd"
    cwd.mkdir(exist_ok=True)

    rows = []
    for T, nd in CASES:
        for fam in ("A", "B"):
            f = FIX / f"t{T}_nd{nd}_{fam}.gguf"
            assert f.exists()
            body = router_body([[exe, "-m", str(f)]])
            rec = {"T": T, "nd": nd, "fam": fam, "path": str(f)}
            for label, probe in (("pristine", pristine), ("traced", traced)):
                with Stub({"/v1/models": body, "/props": PROPS}) as st:
                    r = run_check(probe, st.port, cwd)
                rec[label] = {k: v for k, v in r.items() if k != "stderr"}
                rec[label + "_stderr"] = r["stderr"]
            rec["claim"] = CLAIM[(T, nd)]
            rec["matches_claim"] = (rec["pristine"]["verdict"], rec["pristine"]["reason"]) == \
                                   (CLAIM[(T, nd)][1], CLAIM[(T, nd)][2])
            rows.append(rec)
            trace = rec["traced_stderr"].strip().replace("\n", " | ")
            print(f"T={T} nd={nd} fam={fam} | pristine {rec['pristine']['verdict']}/"
                  f"{rec['pristine']['reason']} in {rec['pristine']['wall']:.2f}s | traced "
                  f"{rec['traced']['verdict']}/{rec['traced']['reason']} in "
                  f"{rec['traced']['wall']:.2f}s | claim {CLAIM[(T,nd)][1]}/"
                  f"{CLAIM[(T,nd)][2]} | match={rec['matches_claim']} | trace: {trace}",
                  file=sys.stderr, flush=True)
    out = SCRATCH / "results.json"
    out.write_text(json.dumps(rows, indent=1))
    print(f"WROTE {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
