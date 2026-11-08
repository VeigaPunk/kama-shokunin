#!/usr/bin/env python3
"""Raw-socket stub probes for RV02WordingC2: outcomes the 9 cells do NOT grade."""
import json, os, socket, struct, subprocess, sys, threading, time
from pathlib import Path

WORK = Path("/fast/scratch/hyaku/kama-r100/RV02WordingC2/work")
WORK.mkdir(parents=True, exist_ok=True)
MODEL = WORK / "model.gguf"
MODEL.write_bytes(b"GGUF\x03\x00\x00\x00" + b"\x00" * 64)
MODELS_BODY = json.dumps({"object": "list", "data": [{
    "id": "fixture-model",
    "status": {"value": "unloaded", "args": [str(MODEL), "-m", str(MODEL)]}}]}).encode()
ROUTER_ON = b'{"role":"router","models_autoload":true}'
ROUTER_OFF = b'{"role":"router","models_autoload":false}'
PROBE = str(WORK / "probe-tip.sh")
REAL_CURL = "/usr/bin/curl"

def models_resp():
    return (b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
            b"Content-Length: %d\r\n\r\n" % len(MODELS_BODY)) + MODELS_BODY

def send_http(conn, status, body, extra=b"", chunked=False, close_delim=False,
              interim=False, delay=0.0, partial=None):
    if delay:
        time.sleep(delay)
    head = b"HTTP/1.1 %d X\r\nContent-Type: application/json\r\n" % status
    if interim:
        head = b"HTTP/1.1 100 Continue\r\n\r\n" + head
    if partial is not None:
        head += b"Content-Length: %d\r\n" % partial + extra + b"\r\n"
        payload = body
    elif chunked:
        head += b"Transfer-Encoding: chunked\r\n" + extra + b"\r\n"
        payload = b"%x\r\n" % len(body) + body + b"\r\n0\r\n\r\n"
    elif close_delim:
        head += b"Connection: close\r\n" + extra + b"\r\n"
        payload = body
    else:
        head += b"Content-Length: %d\r\n" % len(body) + extra + b"\r\n"
        payload = body
    conn.sendall(head + payload)

def rst_close(conn):
    try:
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                        struct.pack("ii", 1, 0))
    except OSError:
        pass
    conn.close()

class Stub(threading.Thread):
    def __init__(self, props_fn):
        super().__init__(daemon=True)
        self.props_fn = props_fn
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(50)
        self.port = self.sock.getsockname()[1]
        self.stop = False
    def run(self):
        self.sock.settimeout(0.5)
        while not self.stop:
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                conn.settimeout(30)
                data = b""
                while b"\r\n" not in data and len(data) < 65536:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                first = data.split(b"\r\n", 1)[0]
                if b"/v1/models" in first:
                    conn.sendall(models_resp())
                    conn.close()
                elif b"/props" in first:
                    try:
                        self.props_fn(conn)
                    except (BrokenPipeError, ConnectionResetError, OSError):
                        pass
                    try:
                        conn.close()
                    except OSError:
                        pass
                else:
                    conn.sendall(b"HTTP/1.1 404 X\r\nContent-Length: 0\r\n\r\n")
                    conn.close()
            except OSError:
                pass
    def close(self):
        self.stop = True
        try:
            self.sock.close()
        except OSError:
            pass

def run_probe(port, mode="check", shim=None):
    env = dict(os.environ)
    env["TMPDIR"] = str(WORK)
    if shim:
        env["PATH"] = str(shim) + ":" + env["PATH"]
    if mode == "check":
        cmd = ["bash", PROBE, "check", "--port", str(port), "--expect",
               "fixture-model", "--id", "r100", "--json"]
    else:
        cmd = ["bash", PROBE, mode, "--port", str(port), "--expect",
               "fixture-model", "--json"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
    try:
        doc = json.loads(p.stdout)
    except json.JSONDecodeError:
        return ("NOJSON", p.stdout[:120], p.returncode, p.stderr[:120])
    rows = doc.get("rows") or doc.get("listeners") or doc.get("consumers") or []
    if len(rows) != 1:
        return ("NROWS%d" % len(rows), str(doc)[:120], p.returncode, "")
    r = rows[0]
    return (r.get("verdict"), r.get("reason"), p.returncode, "")

def make_shim(rc, out=b"000", dirn="shim"):
    d = WORK / dirn
    d.mkdir(exist_ok=True)
    script = ("#!/bin/sh\n"
              "for a in \"$@\"; do case \"$a\" in */props) printf '%%s' '%s'; exit %d ;; esac; done\n"
              "exec %s \"$@\"\n") % (out.decode(), rc, REAL_CURL)
    (d / "curl").write_text(script)
    (d / "curl").chmod(0o755)
    return d

def main():
    results = []
    def case(cid, props_fn=None, shim=None, want_note="", mode="check"):
        st = Stub(props_fn or (lambda c: send_http(c, 200, ROUTER_ON)))
        st.start()
        try:
            got = run_probe(st.port, mode=mode, shim=shim)
        finally:
            st.close()
        line = "CASE %s verdict=%s reason=%s exit=%s %s" % (cid, got[0], got[1], got[2], want_note)
        print(line, flush=True)
        results.append(line)

    # --- raw HTTP statuses, not in the 9 cells ---
    case("X-204-router-on", lambda c: send_http(c, 204, ROUTER_ON), want_note="(other 2xx, line-only)")
    case("X-201-router-on", lambda c: send_http(c, 201, ROUTER_ON), want_note="(other 2xx, line-only)")
    case("X-301-router-on", lambda c: send_http(c, 301, ROUTER_ON, extra=b"Location: /x\r\n"), want_note="(other 3xx, line-only)")
    case("X-304-router-on", lambda c: send_http(c, 304, ROUTER_ON), want_note="(other 3xx, line-only)")
    case("X-400-router-on", lambda c: send_http(c, 400, ROUTER_ON), want_note="(other 4xx, line-only)")
    case("X-404-router-on", lambda c: send_http(c, 404, ROUTER_ON), want_note="(other 4xx, line-only)")
    case("X-418-router-on", lambda c: send_http(c, 418, ROUTER_ON), want_note="(other 4xx, line-only)")
    case("X-501-router-on", lambda c: send_http(c, 501, ROUTER_ON), want_note="(other 5xx, line-only)")
    case("X-502-router-on", lambda c: send_http(c, 502, ROUTER_ON), want_note="(other 5xx, line-only)")
    case("X-500-router-off", lambda c: send_http(c, 500, ROUTER_OFF), want_note="(off-body under 5xx; cells use on-body S2)")
    # --- 1xx interim behaviour ---
    case("X-100-then-200-on", lambda c: send_http(c, 200, ROUTER_ON, interim=True), want_note="(final 200 after interim; 'final' wording)")
    case("X-100-then-hang", lambda c: (c.sendall(b"HTTP/1.1 100 Continue\r\n\r\n"), time.sleep(7), send_http(c, 200, ROUTER_ON)), want_note="(interim only then silence -> rc28)")
    # --- body framing on 200 ---
    case("X-200-chunked-on", lambda c: send_http(c, 200, ROUTER_ON, chunked=True), want_note="(chunked 200; cells always Content-Length)")
    case("X-200-close-delimited-on", lambda c: send_http(c, 200, ROUTER_ON, close_delim=True), want_note="(no length, HTTP/1.0 style)")
    case("X-200-chunked-oversize", lambda c: send_http(c, 200, b"A" * 4500000, chunked=True), want_note="(chunked over 4MiB cap -> rc63 or size check)")
    # --- transport failures ---
    case("X-empty-reply", lambda c: None, want_note="(rc52; server accepts /props then closes silently)")
    def http09(c):
        c.sendall(ROUTER_ON)
    case("X-http09-body", http09, want_note="(body bytes, no status line; observe curl)")
    def malformed(c):
        c.sendall(b"GARBAGE NOT HTTP\r\n\r\n" + ROUTER_ON)
    case("X-malformed-statusline", malformed, want_note="(observe curl rc)")
    def partial(c):
        try:
            send_http(c, 200, ROUTER_ON, partial=100)
        finally:
            pass
        # close with RST so curl sees partial transfer
        try:
            c.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
        except OSError:
            pass
    # partial(): sends CL=100 header + 40-byte body then RST
    case("X-partial-transfer", partial, want_note="(CL=100, 40 bytes, RST -> rc18)")
    # --- curl-shim transport errors (probe line `|| return 2`) ---
    for rc, name in [(7, "rc7-refused"), (28, "rc28-timeout"), (52, "rc52-empty"), (56, "rc56-reset"), (63, "rc63-maxfilesize")]:
        shim = make_shim(rc, dirn="shim%d" % rc)
        case("X-shim-%s" % name, shim=shim, want_note="(probe line ||return2; /v1/models delegated to real curl)")
    # --- plain-call subcommands under `set -euo pipefail` (shim rc28 on /props) ---
    shim28 = make_shim(28, dirn="shim-plain")
    case("X-plain-listeners-rc28", shim=shim28, mode="listeners", want_note="(must not abort; exit 0, reason unread)")
    case("X-plain-consumers-rc28", shim=shim28, mode="consumers", want_note="(must not abort; exit 0, reason unread)")
    (WORK / "results.txt").write_text("\n".join(results) + "\n")
    print("DONE %d cases" % len(results))

if __name__ == "__main__":
    sys.exit(main())
