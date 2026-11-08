#!/usr/bin/env python3
"""MT01 (round-97 w1) independent detector.

Not the counters' Runner: own stub, own GGUF writer, own fixture set. Answers one
question per invocation: what does `bash <probe> check --port <p> --expect good --json`
say about one router listing that names these absolute files with -m.

  harness.py --build DIR               write the fixture set
  harness.py --probe P --fixture F [--entries K]      one listing, K entries -> verdict/reason
  harness.py --probe P --rewrite F     three invocations, same-size rewrite w/ mtime restored
"""
import argparse
import http.server
import json
import os
import socket
import struct
import subprocess
import sys
import threading
import time

PROPS = b'{"role":"router","models_autoload":true}'


def gguf(n_tensors, elems=1, nd=1, with_data=False, magic=b"GGUF"):
    out = [magic, struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        dims = struct.pack("<" + "Q" * nd, elems, *([1] * (nd - 1)))
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims
                   + struct.pack("<IQ", 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


def gguf_bigstring(nbytes, bad_offset=1 << 40):
    """1 KV string of nbytes, then 1 tensor whose data offset is wrong -> invalid."""
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<I", 8))          # GGUF string
    out.append(struct.pack("<Q", nbytes))
    out.append(b"\0" * 64)
    name = b"t0"
    head = b"".join(out)
    tail = (struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 1, 0, bad_offset))
    return head + b"\0" * (nbytes - 64) + tail


def build(d):
    os.makedirs(d, exist_ok=True)
    fx = {}
    fx["t833334"] = os.path.join(d, "t833334.gguf")      # real 4+6*833334=5,000,008 -> -
    open(fx["t833334"], "wb").write(gguf(833_334, 1, 1))
    fx["n555556"] = os.path.join(d, "n555556.gguf")      # nd=4: real 4+9*555556=5,000,008 -> -
    open(fx["n555556"], "wb").write(gguf(555_556, 1, 4))
    fx["s120m"] = os.path.join(d, "s120m.gguf")          # 120 MiB KV string + bad offset
    open(fx["s120m"], "wb").write(gguf_bigstring(120 * 1024 ** 2))
    fx["ok"] = os.path.join(d, "ok.gguf")
    open(fx["ok"], "wb").write(gguf(1, 32, 1, True))
    fx["slow"] = os.path.join(d, "slow.gguf")            # 600k nd=1 -> invalid, ~1.5 s
    open(fx["slow"], "wb").write(gguf(600_000, 1, 1))
    hd = []
    for k in range(4):
        p = os.path.join(d, "hl%d.gguf" % k)
        if os.path.exists(p):
            os.unlink(p)
        os.link(fx["slow"], p)
        hd.append(p)
    fx["hardlinks"] = hd
    print(json.dumps(fx))


class Stub:
    def __init__(self, routes):
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                body = stub.routes.get(self.path.split("?")[0])
                code = 200 if body is not None else 404
                if body is None:
                    body = b'{"error":"nf"}'
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
        end = time.time() + 10
        while time.time() < end:
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=1):
                    return self
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def body(arg_lists):
    data = [{"id": "good", "status": {"value": "unloaded", "args": a}} for a in arg_lists]
    return json.dumps({"object": "list", "data": data}, separators=(",", ":")).encode()


def check(probe, exe, targets):
    """One probe invocation against one listing of `targets`, each -m <path>."""
    args = [[exe, "-m", t] for t in targets]
    tmp = os.path.join(os.path.dirname(probe), "tmp")
    os.makedirs(tmp, exist_ok=True)
    env = dict(os.environ, TMPDIR=tmp)
    with Stub({"/v1/models": body(args), "/props": PROPS}) as st:
        p = subprocess.run(["bash", probe, "check", "--port", str(st.port), "--expect", "good",
                            "--timeout", "5", "--connect-timeout", "2", "--json"],
                           capture_output=True, env=env, cwd=tmp, timeout=1200)
    try:
        row = json.loads(p.stdout.decode())["rows"][0]
        return "%s/%s" % (row.get("verdict"), row.get("reason"))
    except Exception:
        return "unparsed(rc=%d,stdout=%r)" % (p.returncode, p.stdout[:120])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build")
    ap.add_argument("--probe")
    ap.add_argument("--fixture")
    ap.add_argument("--entries", type=int, default=1)
    ap.add_argument("--rewrite", action="store_true")
    a = ap.parse_args()
    if a.build:
        build(a.build)
        return 0
    # status.args[0] must be an existing absolute local file; the fixture itself is one.
    if a.rewrite:
        target = a.fixture
        orig = open(target, "rb").read()
        st0 = os.stat(target)
        v1 = check(a.probe, target, [target])
        valid = gguf(1, 32, 1, True)
        if len(valid) < len(orig):
            valid += b"\0" * (len(orig) - len(valid))
        with open(target, "wb") as f:
            f.write(valid[:len(orig)])
        os.utime(target, ns=(st0.st_atime_ns, st0.st_mtime_ns))
        v2 = check(a.probe, target, [target])
        with open(target, "wb") as f:
            f.write(orig)
        os.utime(target, ns=(st0.st_atime_ns, st0.st_mtime_ns))
        v3 = check(a.probe, target, [target])
        print("rewrite v1=%s v2=%s v3=%s" % (v1, v2, v3))
        return 0
    print(check(a.probe, a.fixture, [a.fixture] * a.entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
