#!/usr/bin/env python3
"""SC01HeldOutListings - repeat the SAME H3b listing against the r95 probe N times.

Same bytes, same listing, same probe -> any verdict change is load-dependence.
"""
import json, os, socket, subprocess, sys, threading, time, http.server
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"
FX = WORK / "fx"
PROPS = b'{"role":"router","models_autoload":true}'


class Stub:
    def __init__(self, body):
        self.body = body
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                q = self.path.split("?")[0]
                if q == "/v1/models":
                    body, code = stub.body, 200
                elif q == "/props":
                    body, code = PROPS, 200
                elif q == "/health":
                    body, code = b'{"status":"ok"}', 200
                else:
                    body, code = b'{"error":"nf"}', 404
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
        dl = time.time() + 10
        while time.time() < dl:
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=1):
                    return self
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def load1():
    return open("/proc/loadavg").read().split()[0]


def run_probe(probe, port, timeout=900):
    env = dict(os.environ, TMPDIR=str(WORK))
    t0 = time.monotonic()
    p = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect", "good",
                        "--timeout", "5", "--connect-timeout", "2", "--json"],
                       capture_output=True, timeout=timeout, env=env, cwd=str(WORK))
    dt = time.monotonic() - t0
    try:
        row = json.loads(p.stdout.decode())["rows"][0]
        return row.get("verdict"), row.get("reason"), round(dt, 2)
    except Exception:
        return "unparsed", "-", round(dt, 2)


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    which = sys.argv[3] if len(sys.argv) > 3 else "r95"
    probe = HERE / ("r95-probe.sh" if which == "r95" else "base-probe.sh")
    exe = str(FX / "ok.gguf")
    args = [exe]
    for k in range(K):
        args += ["-m", str(FX / f"slow_{k}.gguf")]
    body = json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": args}}]}, separators=(",", ":")).encode()
    print(f"# listing: ONE entry naming {K} distinct slow files; probe={which}; body_sha256="
          f"{__import__('hashlib').sha256(body).hexdigest()[:16]}", flush=True)
    for i in range(N):
        with Stub(body) as st:
            v, r, dt = run_probe(probe, st.port)
        print(json.dumps({"run": i + 1, "probe": which, "K": K, "verdict": v, "reason": r,
                          "seconds": dt, "load1": load1()}), flush=True)


if __name__ == "__main__":
    main()
