#!/usr/bin/env python3
"""SC02ProbeVerdictSweep harness: stub router + probe runs at BASE and M1.

Read-only use of the lane's frozen counter module (tools/round93-router-repeat.py)
for its Stub/gguf/router_body/Runner helpers. All fixtures live under --work.
"""
import argparse, http.server, importlib.util, json, os, socket, struct, subprocess, sys, tempfile, threading, time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
BASE = "5af794958b0fc08f574aa2e67650282269549b02"
M1 = "fe5f031cb1b9d33e1160360d892149b8ac3c7771"

spec = importlib.util.spec_from_file_location("rr", LANE / "tools/round93-router-repeat.py")
rr = importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)


class DelayStub:
    """Same as rr.Stub but /props may be delayed by `delay` seconds."""

    def __init__(self, routes, delay=0.0, delay_paths=("/props",)):
        self.routes = routes
        self.delay = delay
        self.delay_paths = delay_paths
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                p = self.path.split("?")[0]
                if p in stub.delay_paths and stub.delay:
                    time.sleep(stub.delay)
                body = stub.routes.get(p)
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


REV_ALIAS = {"BASE": BASE, "M1": M1}


def show(rev):
    rev = REV_ALIAS.get(rev, rev)
    p = subprocess.run(["git", "-C", str(LANE), "show", f"{rev}:tools/kama-probe.sh"], capture_output=True, check=True)
    return p.stdout


def load1():
    try:
        return open("/proc/loadavg").read().split()[0]
    except OSError:
        return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--revs", default="BASE,M1")
    a = ap.parse_args()
    work = Path(tempfile.mkdtemp(prefix="sc02-", dir=a.work)).resolve()
    R = rr.Runner(work)
    fx = work / "fx"; fx.mkdir()
    slow = fx / "slow.gguf"; slow.write_bytes(rr.gguf(rr.TENSORS, 1, False))
    ok = fx / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
    ok2 = fx / "ok2.gguf"; ok2.write_bytes(rr.gguf(2, 32, True))
    missing = str(fx / "absent" / "missing.gguf")
    exe = str(ok)
    s = str(slow)
    print(f"# scenario={a.scenario} load1={load1()} work={work}")

    def run(name, body, delay=0.0, routes_extra=None):
        routes = {"/v1/models": body, "/props": rr.PROPS}
        if routes_extra:
            routes.update(routes_extra)
        for rev in a.revs.split(","):
            R.install(show(rev))
            with DelayStub(routes, delay=delay) as st:
                t0 = time.monotonic()
                rc, v, r, dt = R.check(st.port)
                wall = time.monotonic() - t0
            print(f"SC02 {name} rev={rev[:8]} rc={rc} verdict={v} reason={r} probe_s={dt:.2f} wall_s={wall:.2f} "
                  f"body_bytes={len(body)}", flush=True)

    sc = a.scenario
    if sc == "distinct":
        # K DISTINCT slow invalid files, K router entries -> count dependence of the verdict
        for k in (1, 2, 3, 4, 6, 8, 12):
            files = []
            for i in range(k):
                f = fx / f"slow{i}.gguf"
                f.write_bytes(rr.gguf(rr.TENSORS, 1, False))
                files.append(str(f))
            body = rr.router_body([[exe, "-m", files[i]] for i in range(k)])
            run(f"distinct-k{k}", body)
    elif sc == "repeat":
        for n in (1, 8, 64, 512, 2048):
            body = rr.router_body([[exe, "-m", s]] * n)
            run(f"repeat-n{n}", body)
    elif sc == "size":
        # file size -> steps/deadline budget -> undecidable -> loadable
        for tens in (150000, 300000, 450000, 600000, 700000, 1000000, 1200000):
            f = fx / f"t{tens}.gguf"
            if not f.exists():
                f.write_bytes(rr.gguf(tens, 1, False))
            body = rr.router_body([[exe, "-m", str(f)]])
            run(f"size-t{tens}", body)
    elif sc == "props-delay":
        # /props slow -> autoload unknown -> verdict reason changes
        for delay in (0.0, 1.0, 3.0, 5.5, 7.0):
            body = rr.router_body([[exe, "-m", s]])
            run(f"props-delay-{delay}", body, delay=delay)
            body2 = rr.router_body([[exe, "-m", str(ok)]])
            run(f"props-delay-ok-{delay}", body2, delay=delay)
    elif sc == "mixed-order":
        # invalid + missing, order swapped: reason (not verdict) changes
        body = rr.router_body([[exe, "-m", missing], [exe, "-m", s]])
        run("missing-then-invalid", body)
        body = rr.router_body([[exe, "-m", s], [exe, "-m", missing]])
        run("invalid-then-missing", body)
    else:
        raise SystemExit("unknown scenario")
    print(f"# done scenario={sc} load1={load1()}")


if __name__ == "__main__":
    main()
