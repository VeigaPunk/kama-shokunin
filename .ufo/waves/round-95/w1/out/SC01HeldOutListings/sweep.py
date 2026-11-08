#!/usr/bin/env python3
"""SC01HeldOutListings - sweep K = distinct slow files named by ONE candidate entry.

The round-95 pass-level limit is `20 + 15 * ncand` seconds, where ncand is the
number of candidate ENTRIES in the listing.  The parse work of one candidate is
the sum over the DISTINCT FILES its status.args names (each parsed once, memoised
by file identity), so work is not bounded by ncand when a single entry names
several paths.

Usage: sweep.py [--burners N] [--ks 2,3,4,5,6,7,8] [--tensors N]
"""
import json, os, signal, struct, subprocess, sys, threading, time, http.server
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"
FX = WORK / "sweepfx"
PROBES = {"r95": HERE / "r95-probe.sh", "base": HERE / "base-probe.sh"}
PROPS = b'{"role":"router","models_autoload":true}'
CAP = 4194304


def gguf(n_tensors, elems=1, with_data=False):
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, elems, 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    p = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * p + (b"\0" * off if with_data else b"\0" * 16)


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


def run_probe(probe, port, timeout=1200):
    env = dict(os.environ, TMPDIR=str(WORK))
    t0 = time.monotonic()
    p = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect", "good",
                        "--timeout", "5", "--connect-timeout", "2", "--json"],
                       capture_output=True, timeout=timeout, env=env, cwd=str(WORK))
    dt = time.monotonic() - t0
    try:
        row = json.loads(p.stdout.decode())["rows"][0]
        return row.get("verdict"), row.get("reason"), round(dt, 2), p.returncode
    except Exception as e:
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
    tensors = 600_000
    ks = [2, 3, 4, 5, 6, 7, 8]
    nburn = 0
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--burners":
            nburn = int(argv[i + 1])
        if a == "--ks":
            ks = [int(x) for x in argv[i + 1].split(",")]
        if a == "--tensors":
            tensors = int(argv[i + 1])
    WORK.mkdir(parents=True, exist_ok=True)
    FX.mkdir(exist_ok=True)
    slow = []
    for k in range(max(ks) + 1):
        p = FX / f"s{tensors}_{k}.gguf"
        if not p.exists():
            p.write_bytes(gguf(tensors))
        slow.append(str(p))
    ok = FX / "ok.gguf"
    if not ok.exists():
        ok.write_bytes(gguf(1, 32, True))
    exe = str(ok)

    tag = f"SC01R95SWEEP{os.getpid()}"
    ps = burners(nburn, tag) if nburn else []
    try:
        for K in ks:
            args = [exe]
            for k in range(K):
                args += ["-m", slow[k]]
            body = json.dumps({"object": "list", "data": [
                {"id": "good", "status": {"value": "unloaded", "args": args}}]},
                separators=(",", ":")).encode()
            rec = {"K": K, "tensors": tensors, "ncand": 1, "limit_s": 20 + 15 * 1,
                   "distinct_slow_files": K, "burners": nburn, "load1_start": load1()}
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
