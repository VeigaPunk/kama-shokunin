#!/usr/bin/env python3
"""EX03: run kama-probe.sh (base B and C1 measured M) with HAVE_PY=1 and HAVE_PY=0
against stub cells carrying hostile bytes. One stub server per cell, in-process."""
import http.server
import json
import os
import socket
import subprocess
import sys
import threading
import time

SCRATCH = os.path.dirname(os.path.abspath(__file__))
NOPY_BIN = os.path.join(SCRATCH, "bin-nopy")
PROBE = {"B": os.path.join(SCRATCH, "probe-B.sh"), "M": os.path.join(SCRATCH, "probe-M.sh")}
ESC = b"\x1b"


class Stub:
    def __init__(self, routes):
        self.routes = routes
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                path = self.path.split("?")[0]
                r = stub.routes.get(path)
                if r is None:
                    body = b'{"error":"not found"}'
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                hdrs = r.get("headers") or [(b"Content-Type", b"application/json")]
                raw = b"HTTP/1.0 %d OK\r\n" % r.get("code", 200)
                raw += b"".join(k + b": " + v + b"\r\n" for k, v in hdrs)
                body = r["body"]
                raw += b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                self.wfile.write(raw + b"\r\n")
                self.wfile.flush()
                try:
                    self.connection.sendall(body)
                except (BrokenPipeError, ConnectionResetError, OSError):
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
                time.sleep(0.02)
        raise RuntimeError("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def run(probe, port, expect, as_json, env):
    cmd = ["bash", probe, "check", "--port", str(port), "--expect", expect,
           "--timeout", "5", "--connect-timeout", "2"]
    if as_json:
        cmd.append("--json")
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=90, env=env, cwd=SCRATCH)
    except subprocess.TimeoutExpired:
        return None, b"", "timeout"
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")[-300:]


def json_probe(out: bytes):
    try:
        doc = json.loads(out.decode("utf-8"))
        return doc, doc["rows"][0]
    except Exception as e:
        return None, str(e)


def has_c0(obj):
    if isinstance(obj, str):
        return any(ord(c) < 0x20 or ord(c) == 0x7F for c in obj)
    if isinstance(obj, dict):
        return any(has_c0(k) or has_c0(v) for k, v in obj.items())
    if isinstance(obj, list):
        return any(has_c0(v) for v in obj)
    return False


def models_doc(ids, status=None):
    data = []
    for i in ids:
        e = {"id": i, "object": "model"}
        if status is not None:
            e["status"] = {"value": status}
        data.append(e)
    return {"object": "list", "data": data}


def doc_raw(ids, status=None) -> bytes:
    """json.dumps of models_doc: control chars in ids become \\uXXXX / \\n / \\t TEXT."""
    return json.dumps(models_doc(ids, status)).encode()


def doc_bytes_rawctrl(ids) -> bytes:
    """Hand-built body where the id carries RAW control bytes (invalid JSON per RFC 8259 §7,
    but a hostile listener can send it)."""
    parts = []
    for i in ids:
        parts.append(b'{"id":"' + i.encode() + b'","object":"model"}')
    return b'{"object":"list","data":[' + b",".join(parts) + b"]}"


CELLS = []


def cell(name, routes, expect="good", want="good"):
    CELLS.append((name, routes, expect, want))


# --- H4 equivalents: id with \n + tabs (table column forging)
cell("H4x-escaped-nl-tab", {"/v1/models": {"body": doc_raw(["good", "evil\nFORGED-ROW\tx\tMODEL_OK"])}}, want="good")
cell("H4raw-tab", {"/v1/models": {"body": doc_bytes_rawctrl(["good", "evil\tFORGED-ROW\tx\tMODEL_OK"])}}, want="good")
cell("H4raw-nl", {"/v1/models": {"body": doc_bytes_rawctrl(["good", "evil\nFORGED-ROW"])}}, want="good")

# --- H5 equivalents: id with U+0001
cell("H5x-escaped-u0001", {"/v1/models": {"body": doc_raw(["good", "a\u0001b"])}}, want="good")
cell("H5raw-u0001", {"/v1/models": {"body": doc_bytes_rawctrl(["good", "a\x01b"])}}, want="good")

# --- H6 equivalents: id with ESC
cell("H6x-escaped-u001b", {"/v1/models": {"body": doc_raw(["good", "\u001b[31mRED"])}}, want="good")
cell("H6raw-esc", {"/v1/models": {"body": doc_bytes_rawctrl(["good", "\x1b[31mRED"])}}, want="good")

# --- H7: Server header with raw ESC
cell("H7-server-hdr-esc", {"/v1/models": {
    "body": doc_raw(["good"]),
    "headers": [(b"Content-Type", b"application/json"), (b"Server", b"evil\x1b[2Jx")]}}, want="good")

# --- H8: router status value with ESC (escaped in JSON text vs raw byte)
cell("H8x-escaped-status", {"/v1/models": {"body": doc_raw(["good"], "bad\u001b[31m")},
                            "/props": {"body": b'{"role":"router","models_autoload":false}'}}, want="good")
cell("H8raw-esc-status", {"/v1/models": {
    "body": b'{"object":"list","data":[{"id":"good","status":{"value":"bad\x1b[31m"}}]}'},
    "/props": {"body": b'{"role":"router","models_autoload":false}'}}, want="good")

# --- extra held-out: DEL and U+0085 in an id
cell("X-del-raw", {"/v1/models": {"body": doc_bytes_rawctrl(["good", "a\x7fb"])}}, want="good")
cell("X-u0085-raw", {"/v1/models": {"body": doc_bytes_rawctrl(["good", "a\u0085b"])}}, want="good")
cell("X-nul-raw", {"/v1/models": {"body": doc_bytes_rawctrl(["good", "a\x00b"])}}, want="good")


def table_checks(out: bytes):
    lines = out.split(b"\n")
    head = [c.strip() for c in lines[0].split(b" | ")] if lines else []
    forged = [l for l in lines if l.startswith(b"FORGED-ROW")]
    return {
        "esc": ESC in out,
        "forged_rows": len(forged),
        "header_cols": len(head),
        "empty_header_cols": sum(1 for c in head if not c),
        "body_cols": len(lines[1].split(b"\t")) if len(lines) > 1 else 0,
        "linecount": len(lines),
    }


def main():
    env_py = dict(os.environ)
    env_nopy = dict(os.environ)
    env_nopy["PATH"] = NOPY_BIN
    env_nopy.pop("PYTHONPATH", None)
    for k in ("PYTHONHOME", "PYTHONSTARTUP"):
        env_nopy.pop(k, None)
    results = []
    for name, routes, expect, _want in CELLS:
        for rev in ("B", "M"):
            for mode in ("HAVE_PY=1", "HAVE_PY=0"):
                env = env_py if mode == "HAVE_PY=1" else env_nopy
                with Stub(routes) as st:
                    rc_t, so_t, se_t = run(PROBE[rev], st.port, expect, False, env)
                    rc_j, so_j, se_j = run(PROBE[rev], st.port, expect, True, env)
                tc = table_checks(so_t or b"")
                doc, row = json_probe(so_j or b"")
                r = {
                    "cell": name, "rev": rev, "py": mode,
                    "table_rc": rc_t, "table_esc": tc["esc"],
                    "table_forged": tc["forged_rows"], "table_hdr_cols": tc["header_cols"],
                    "table_empty_hdr": tc["empty_header_cols"], "table_lines": tc["linecount"],
                    "json_rc": rc_j,
                    "json_parse": "ok" if doc is not None else f"unparsed:{row}",
                    "json_c0": (has_c0(doc) if doc is not None else None),
                    "verdict": (row.get("verdict") if isinstance(row, dict) else None),
                    "reason": (row.get("reason") if isinstance(row, dict) else None),
                    "served": (repr(row.get("served_model"))[:90] if isinstance(row, dict) else None),
                    "table_stderr": se_t.strip().splitlines()[-1][:120] if se_t and se_t.strip() else "",
                }
                results.append(r)
                print(json.dumps(r, ensure_ascii=True), flush=True)
    with open(os.path.join(SCRATCH, "results.jsonl"), "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
