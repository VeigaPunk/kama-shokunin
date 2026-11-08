#!/usr/bin/env python3
"""SC01HeldOutListings - realistic multi-path-per-candidate shapes.

llama.cpp renders a router child's argv through preset.to_args(bin_path)
(tools/server/server-models.cpp:322 at b12177), so ONE candidate entry's
status.args legitimately names SEVERAL distinct local files: --model,
--mmproj, --model-draft.  The round-95 pass limit is
  20 + 15 * ncand   (ncand = number of candidate ENTRIES)
while the work of one candidate is the number of DISTINCT FILES its args name.
"""
import json, os, socket, subprocess, sys, threading, time, http.server
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


def slow(k):
    return str(FX / f"slow_{k}.gguf")


def main():
    exe = str(FX / "ok.gguf")
    shapes = {}

    # R1: ONE candidate naming 3 distinct heavy files the way llama.cpp renders a
    #     multimodal/draft child argv: --model, --mmproj, --model-draft.
    shapes["R1-one-cand-model-mmproj-draft"] = [
        {"id": "good", "status": {"value": "unloaded", "args": [
            exe, "--model", slow(0), "--mmproj", slow(1), "--model-draft", slow(2)]}}]

    # R2: 4 candidates, each naming 3 distinct heavy files (4 multimodal models).
    e = []
    for m in range(4):
        e.append({"id": "good", "status": {"value": "unloaded", "args": [
            exe, "--model", slow(m), "--mmproj", slow(m + 4), "--model-draft", slow(m + 8)]}})
    shapes["R2-4cand-x3files"] = e

    # R3: 16 candidates, each naming 3 distinct heavy files.
    e = []
    for m in range(16):
        e.append({"id": "good", "status": {"value": "unloaded", "args": [
            exe, "--model", slow(m % 16), "--mmproj", slow((m + 16) % 32),
            "--model-draft", slow((m + 32) % 48)]}})
    shapes["R3-16cand-x3files"] = e

    # R4: 40 candidates, each naming 3 distinct heavy files (the counter's W03
    #     count, with the realistic 3-path argv).
    e = []
    for m in range(40):
        e.append({"id": "good", "status": {"value": "unloaded", "args": [
            exe, "--model", slow(m % 40), "--mmproj", slow((m + 8) % 48),
            "--model-draft", slow((m + 16) % 56)]}})
    shapes["R4-40cand-x3files"] = e

    only = sys.argv[1:] or None
    for name, entries in shapes.items():
        if only and not any(name.startswith(o) for o in only):
            continue
        body = json.dumps({"object": "list", "data": entries}, separators=(",", ":")).encode()
        ncand = len(entries)
        rec = {"shape": name, "candidates": ncand,
               "distinct_files_named": ncand * 3,
               "r95_limit_s": 20 + 15 * ncand, "body_bytes": len(body),
               "load1_start": load1()}
        for which in ("r95", "base"):
            with Stub(body) as st:
                v, r, dt, rc = run_probe(PROBES[which], st.port)
            rec[which] = {"verdict": v, "reason": r, "seconds": dt, "rc": rc}
            rec["load1_" + which] = load1()
        rec["agree"] = (rec["r95"]["verdict"], rec["r95"]["reason"]) == \
                       (rec["base"]["verdict"], rec["base"]["reason"])
        print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
