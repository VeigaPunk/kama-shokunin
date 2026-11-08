#!/usr/bin/env python3
"""SC01HeldOutListings - realistic multi-path candidate under the counter's own load.

The counter's load pass raises 64 burners.  Under that load the r95 limit for
ncand=1 is 20+15*1 = 35 s, but one candidate naming --model/--mmproj/--model-draft
(the argv llama.cpp actually renders for a child) is K distinct parses.
"""
import json, os, signal, subprocess, sys, threading, time, http.server
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"
FX = WORK / "fx"
PROBES = {"r95": HERE / "r95-probe.sh", "base": HERE / "base-probe.sh"}
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
        import socket
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
        return row.get("verdict"), row.get("reason"), round(dt, 2), p.returncode
    except Exception:
        return "unparsed", "-", round(dt, 2), p.returncode


def burners(n, tag):
    ps = []
    for _ in range(n):
        p = subprocess.Popen([sys.executable, "-c", f"# {tag}\nwhile True: pass"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        ps.append(p)
    time.sleep(2.0)
    return ps


def stop_burners(ps):
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


def main():
    nburn = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    exe = str(FX / "ok.gguf")
    args = [exe]
    for k in range(K):
        args += ["-m", str(FX / f"slow_{k}.gguf")]
    body = json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": args}}]}, separators=(",", ":")).encode()
    tag = f"SC01R95LOAD{os.getpid()}"
    ps = burners(nburn, tag) if nburn else []
    try:
        for i in range(N):
            rec = {"burners": nburn, "K": K, "run": i + 1, "r95_limit_s": 20 + 15 * 1,
                   "load1_start": load1()}
            for which in ("r95", "base"):
                with Stub(body) as st:
                    v, r, dt, rc = run_probe(PROBES[which], st.port)
                rec[which] = {"verdict": v, "reason": r, "seconds": dt, "rc": rc}
                rec["load1_" + which] = load1()
            rec["agree"] = (rec["r95"]["verdict"], rec["r95"]["reason"]) == \
                           (rec["base"]["verdict"], rec["base"]["reason"])
            print(json.dumps(rec), flush=True)
    finally:
        stop_burners(ps)


if __name__ == "__main__":
    main()
