#!/usr/bin/env python3
"""MT01 direct behavioural probe driver (round-95 C1).

Drives a kama-probe.sh copy end-to-end (`check --json`) against a lane-owned stub router on
127.0.0.1, so the reported state is the verdict, not an internal function return.

Fixtures (built from bytes here, never read back from the probe):
  slow    600 000-tensor GGUF header, data absent -> `invalid`, ~2 s of parser work
  sparse  GGUF v3, 1 KV whose 600 000 000-byte string pushes the header position past
          MAX_META (512 MiB); the file ends at the first tensor-info field -> the pristine
          probe says `-` (header position cap), a probe without the cap reads the truncation
          and says `invalid`.
Modes:
  sparse                       one entry -m <sparse>
  slow [--burners N --core C]  one entry -m <slow>; N burners and the probe pinned to core C
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

CAP = 4194304


class Stub:
    def __init__(self, routes):
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

        self.routes = routes
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
        raise SystemExit("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def gguf(n_tensors: int, elems: int, with_data: bool) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, elems, 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


def make_t900k(p: Path) -> Path:
    p.write_bytes(gguf(900_000, 1, False))
    return p


def make_slow(p: Path) -> Path:
    p.write_bytes(gguf(600_000, 1, False))
    return p


def make_sparse(p: Path) -> Path:
    """Header position 45 + 600 000 000 > MAX_META; file ends 8 bytes later."""
    L = 600_000_000
    head = b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 1, 1)          # 24
    head += struct.pack("<Q", 1) + b"x" + struct.pack("<I", 8) + struct.pack("<Q", L)  # 21
    size = len(head) + L + 8
    with open(p, "wb") as f:
        f.write(head)
        f.seek(size - 8)
        f.write(b"\0" * 8)
    st = p.stat()
    pathlib_du = os.stat(p)
    print(f"FIXTURE sparse logical={st.st_size} blocks512={pathlib_du.st_blocks} "
          f"pos_after_kv={len(head) + L} max_meta={512 * 1024 ** 2}", flush=True)
    return p


def router_body(arg_lists) -> bytes:
    data = [{"id": "good", "status": {"value": "unloaded", "args": a}} for a in arg_lists]
    b = json.dumps({"object": "list", "data": data}, separators=(",", ":")).encode()
    if len(b) >= CAP:
        raise SystemExit("body too large")
    return b


PROPS = b'{"role":"router","models_autoload":true}'


def run_check(probe: Path, port: int, cwd: Path, core: int | None, kill=400):
    env = dict(os.environ, TMPDIR=str(cwd))
    cmd = ["bash", str(probe), "check", "--port", str(port), "--expect", "good",
           "--timeout", "5", "--connect-timeout", "2", "--json"]
    if core is not None:
        cmd = ["taskset", "-c", str(core)] + cmd
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=kill, env=env, cwd=cwd)
    except subprocess.TimeoutExpired:
        return f"KILLED@{kill}s", "-", time.monotonic() - t0
    dt = time.monotonic() - t0
    try:
        row = json.loads(p.stdout.decode())["rows"][0]
        return row.get("verdict"), row.get("reason"), dt
    except Exception:
        return f"unparsed(rc={p.returncode})", "-", dt


def start_burners(n: int, core: int | None, tag: str):
    ps = []
    for k in range(n):
        cmd = [sys.executable, "-c", "while True: pass", f"{tag}-{k}"]
        if core is not None:
            cmd = ["taskset", "-c", str(core)] + cmd
        ps.append(subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   start_new_session=True))
    time.sleep(1.5)
    return ps


def stop_burners(ps, tag: str):
    for p in ps:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    for p in ps:
        try:
            p.wait(timeout=5)
        except Exception:
            pass
    left = subprocess.run(["pgrep", "-f", tag], capture_output=True, text=True)
    if left.returncode == 0:
        print(f"BURNERS-LEFT {tag}: {left.stdout.strip()}", flush=True)
    else:
        print(f"BURNERS-REAPED {tag} pgrep=empty", flush=True)


def loadavg() -> str:
    return open("/proc/loadavg").read().split()[0]


def run_race(a, cwd: Path, ok: Path) -> int:
    """Two-entry listing of one inode; rewrite in place (same size, mtime restored) between
    the two gguf_state() calls, inside one probe invocation. ctime is the only changed key."""
    target = a.work / "race.gguf"
    orig = gguf(600_000, 1, False)
    target.write_bytes(orig)
    valid = gguf(1, 32, True)
    if len(valid) < len(orig):
        valid += b"\0" * (len(orig) - len(valid))
    valid = valid[:len(orig)]
    args = [str(ok), "-m", str(target)]
    routes = {"/v1/models": router_body([args, args]), "/props": PROPS}
    results = []
    with Stub(routes) as st:
        for rep in range(a.race_reps):
            target.write_bytes(orig)
            st0 = target.stat()

            def rewrite(st0=st0):
                time.sleep(a.race_delay)
                with open(target, "r+b") as f:
                    f.write(valid)
                os.utime(target, ns=(st0.st_atime_ns, st0.st_mtime_ns))

            th = threading.Thread(target=rewrite, daemon=True)
            th.start()
            verdict, reason, dt = run_check(a.probe, st.port, cwd, a.core)
            th.join()
            results.append((verdict, reason, dt))
            target.write_bytes(orig)
            print(f"RACE {a.label} rep={rep + 1} verdict={verdict} reason={reason} "
                  f"elapsed={dt:.2f}s load1={loadavg()}", flush=True)
    target.write_bytes(orig)
    print(f"DIRECT {a.label} mode=race reps={a.race_reps} delay={a.race_delay}s "
          f"verdicts={[v for v, _, _ in results]}", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--fixture", choices=["slow", "sparse", "t900k"])
    ap.add_argument("--burners", type=int, default=0)
    ap.add_argument("--core", type=int, default=None)
    ap.add_argument("--label", default="run")
    ap.add_argument("--race-reps", type=int, default=0)
    ap.add_argument("--race-delay", type=float, default=0.5)
    a = ap.parse_args()
    a.probe = a.probe.resolve()
    a.work.mkdir(parents=True, exist_ok=True)
    cwd = a.work / "probe-cwd"
    cwd.mkdir(exist_ok=True)
    ok = a.work / "exe.bin"
    ok.write_bytes(b"exe")
    if a.race_reps:
        return run_race(a, cwd, ok)
    if a.fixture == "slow":
        target = make_slow(a.work / "slow.gguf")
    elif a.fixture == "t900k":
        target = make_t900k(a.work / "t900k.gguf")
    else:
        target = make_sparse(a.work / "sparse.gguf")
    args = [str(ok), "-m", str(target)]
    tag = f"MT01PIN-{a.label}"
    burners = start_burners(a.burners, a.core, tag) if a.burners else []
    try:
        with Stub({"/v1/models": router_body([args]), "/props": PROPS}) as st:
            verdict, reason, dt = run_check(a.probe, st.port, cwd, a.core)
    finally:
        if burners:
            stop_burners(burners, tag)
    print(f"DIRECT {a.label} fixture={a.fixture} probe={a.probe.name} burners={a.burners} "
          f"core={a.core} verdict={verdict} reason={reason} elapsed={dt:.2f}s load1={loadavg()}",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
