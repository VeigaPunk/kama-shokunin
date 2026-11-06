#!/usr/bin/env python3
"""Auxiliary reachability demos for escaping mutants (M7, M9, M11) at M=f968fb19.

Each demo runs two probe files (M = landed bytes, X = one-change revert) against one
in-process stub on 127.0.0.1 and prints what differs. This is NOT the frozen counter; it
only shows where an unowned rule is still load-bearing (or provably inert).
"""
import http.server, json, os, subprocess, sys, tempfile, threading
from pathlib import Path

M = Path("probe-M.sh").resolve()
ESC = "\x1b"


class Stub:
    def __init__(self, body: bytes, headers=None):
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                hs = headers or [(b"Content-Type", b"application/json")]
                raw = b"HTTP/1.0 200 OK\r\n" + b"".join(k + b": " + v + b"\r\n" for k, v in hs)
                raw += b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
                try:
                    self.wfile.write(raw)
                except OSError:
                    pass

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.t.start()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def run(probe, port, args, cwd):
    p = subprocess.run(["bash", str(probe), "check", "--port", str(port),
                        "--timeout", "5", "--connect-timeout", "2", *args],
                       capture_output=True, timeout=90, cwd=cwd,
                       env=dict(os.environ, TMPDIR=str(cwd)))
    return p.returncode, p.stdout


def doc(ids, status=None):
    data = []
    for i in ids:
        e = {"id": i, "object": "model"}
        if status is not None:
            e["status"] = {"value": status}
        data.append(e)
    return json.dumps({"object": "list", "data": data}).encode()


def demo(tag, probe, body, args, headers=None, expect=None):
    wd = Path(tempfile.mkdtemp(dir="work"))
    with Stub(body, headers) as s:
        rc, out = run(probe, s.port, args, wd)
    return {"tag": tag, "probe": probe.name, "rc": rc,
            "esc": int(b"\x1b" in out), "out": out.decode("utf-8", "replace")}


print("== M11 jstr loop: operator --expect carrying U+0001 (listener fields are pre-sanitized)")
for probe in (M, Path("mutants/M11.sh").resolve()):
    r = demo("jstr", probe, doc(["good"]), ["--expect", "a\x01b", "--json"])
    try:
        json.loads(r["out"])
        valid = 1
    except Exception:
        valid = 0
    print(f"  {r['probe']:9s} rc={r['rc']} json_parses={valid} stderr_tail="
          f"{'die' if r['rc'] else ''}{' '.join(r['out'].split())[-60:]}")

print("== M9 router id filter: router-shaped listing whose ids carry ESC / U+0001")
body = doc(["good", "bad\x1bX", "c\x01d"], "unloaded")
for probe in (M, Path("mutants/M9.sh").resolve()):
    r = demo("ids", probe, body, ["--expect", "good"], )
    print(f"  {r['probe']:9s} table_rc={r['rc']} esc={r['esc']} last={r['out'].splitlines()[-2] if len(r['out'].splitlines())>1 else ''}")

print("== M7 F_CT strip_ctl: listener Content-Type carrying ESC (healthy model body)")
for probe in (M, Path("mutants/M7.sh").resolve()):
    r = demo("ct", probe, doc(["good"]), ["--expect", "good"],
             headers=[(b"Content-Type", b"application/json; x=1\x1b[2J")])
    print(f"  {r['probe']:9s} rc={r['rc']} esc={r['esc']}")
    for line in r["out"].splitlines():
        if "Server" in line or "application" in line:
            print("      ", repr(line[-90:]))
