#!/usr/bin/env python3
"""SN01StepFlips - measure the REAL probe's step boundary on my own GGUF fixtures.

Runs the lane's probe (unmodified bytes, copied into scratch) `check --json --port <stub>`
against a stub router, exactly the shape the frozen counters use:
  /v1/models -> {"object":"list","data":[{"id":"good","status":{"value":"unloaded",
                   "args":[<existing abs file>, "-m", <fixture>]}}]}
  /props     -> {"role":"router","models_autoload":true}

Then, as an independent measurement of the step boundary, sweeps MAX_STEPS in a SCRATCH COPY
of the probe bytes (the tracked lane file is never touched) to find the exact value at which
the parse flips from `invalid` to `-`. That threshold is the number of steps the real parser
charges for the fixture, so the plan's arithmetic `4 + T x (5 + nd)` is checked against the
running code rather than against prose.

Also applies the +1/header overcharge patch (same byte anchor the frozen counter uses) to a
scratch copy, to see which side of MAX_STEPS the mutated parser lands on.

Usage: drive.py <scratch-dir> <probe-file> <fixture-dir>
"""
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

PROPS = b'{"role":"router","models_autoload":true}'


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


def router_body(args_list):
    data = [{"id": "good", "status": {"value": "unloaded", "args": a}} for a in args_list]
    return json.dumps({"object": "list", "data": data}, separators=(",", ":")).encode()


def run_probe(probe: Path, cwd: Path, port: int):
    t0 = time.monotonic()
    env = dict(os.environ, TMPDIR=str(cwd))
    p = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect", "good",
                        "--timeout", "5", "--connect-timeout", "2", "--json"],
                       capture_output=True, timeout=3600, env=env, cwd=str(cwd))
    dt = time.monotonic() - t0
    try:
        row = json.loads(p.stdout.decode("utf-8"))["rows"][0]
        return p.returncode, row.get("verdict"), row.get("reason"), dt, row.get("evidence", "")
    except Exception as e:
        return p.returncode, f"unparsed({e})", "-", dt, p.stderr.decode("utf-8", "replace")[:400]


def extract_router_py(probe_text: str) -> str:
    m = re.search(r"ROUTER_PY=\$\(cat <<'PY'\n(.*?)\nPY\n\)", probe_text, re.S)
    if not m:
        raise SystemExit("ROUTER_PY not found in probe bytes")
    return m.group(1)


def direct_parse(router_py: str, body_file: Path, idx: int, cwd: Path):
    """Run the probe's OWN parser (ROUTER_PY) on one candidate - the same call the probe makes
    in router_file_states. Returns (state, seconds)."""
    t0 = time.monotonic()
    p = subprocess.run(["python3", "-c", router_py, str(body_file), "files", str(idx)],
                       capture_output=True, timeout=3600, cwd=str(cwd))
    dt = time.monotonic() - t0
    out = p.stdout.decode().strip()
    state = out.split("\t")[1] if "\t" in out else f"rc={p.returncode}"
    return state, dt


def main() -> int:
    scratch = Path(sys.argv[1]).resolve()
    probe = Path(sys.argv[2]).resolve()
    fdir = Path(sys.argv[3]).resolve()
    cwd = scratch / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    probe_text = probe.read_text()
    router_py = extract_router_py(probe_text)
    exe = str(fdir / "ok.gguf")
    assert os.path.isfile(exe)

    fixtures = [("t800k_nd1", 800_000, 1), ("t520k_nd4", 520_000, 4),
                ("t714286_nd1", 714_286, 1), ("t555554_nd4", 555_554, 4)]
    results = []
    for name, T, nd in fixtures:
        path = fdir / f"{name}.gguf"
        # numeric facts read from the bytes on disk, not from the writer
        b = path.read_bytes()
        n_t = struct.unpack_from("<Q", b, 8)[0]
        n_kv = struct.unpack_from("<Q", b, 16)[0]
        nl = struct.unpack_from("<Q", b, 24)[0]
        nd_read = struct.unpack_from("<I", b, 32 + nl)[0]
        size = len(b)
        size_guard_bytes = n_kv * 13 + n_t * 24
        size_guard_fires = size_guard_bytes > size
        max_tensors = 1_000_000
        maxtensors_fires = n_t > max_tensors
        plan_steps = 4 + n_t * (5 + nd_read)
        print(f"FIXTURE {name} T={n_t} nd={nd_read} size={size} "
              f"size_guard_needs={size_guard_bytes} size_guard_fires={int(size_guard_fires)} "
              f"MAX_TENSORS_fires={int(maxtensors_fires)} plan_steps={plan_steps} "
              f"plan_verdict={'invalid' if plan_steps <= 5_000_000 else '-'}")
        # three probe runs, report every one
        runs = []
        for _ in range(3):
            routes = {"/v1/models": router_body([[exe, "-m", str(path)]]), "/props": PROPS}
            with Stub(routes) as st:
                runs.append(run_probe(probe, cwd, st.port))
            print(f"PROBE {name} rc={runs[-1][0]} verdict={runs[-1][1]} reason={runs[-1][2]} "
                  f"wall={runs[-1][3]:.2f}s")
        # the parser's own answer for the same bytes (the call the probe makes internally)
        body = scratch / f"{name}.body.json"
        body.write_bytes(router_body([[exe, "-m", str(path)]]))
        state, sdt = direct_parse(router_py, body, 0, cwd)
        print(f"PARSE {name} state={state} seconds={sdt:.2f}")
        results.append(dict(name=name, T=n_t, nd=nd_read, size=size, size_guard_fires=size_guard_fires,
                            maxtensors_fires=maxtensors_fires, plan_steps=plan_steps, runs=runs,
                            parse_state=state, parse_seconds=sdt))
    (scratch / "results.json").write_text(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
