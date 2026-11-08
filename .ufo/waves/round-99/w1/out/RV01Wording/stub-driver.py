#!/usr/bin/env python3
"""Drive one probe against one stub /props outcome at a time; print verdict/reason."""
import http.server, json, socket, subprocess, sys, threading, pathlib, tempfile

PROBE = pathlib.Path(sys.argv[1])
MODEL = pathlib.Path(sys.argv[2])

SCENARIOS = {
    # (status, content-type, body-bytes-or-None-for-reset)
    "absent-field-router": (200, "application/json", b'{"role":"router"}'),
    "field-null": (200, "application/json", b'{"role":"router","models_autoload":null}'),
    "field-string-false": (200, "application/json", b'{"role":"router","models_autoload":"false"}'),
    "field-int-1": (200, "application/json", b'{"role":"router","models_autoload":1}'),
    "role-worker-false": (200, "application/json", b'{"role":"worker","models_autoload":false}'),
    "http-401-router-false": (401, "application/json", b'{"role":"router","models_autoload":false}'),
    "http-403-html": (403, "text/html", b"<html>forbidden</html>"),
    "empty-body-200": (200, "application/json", b""),
    "json-array": (200, "application/json", b'[{"role":"router","models_autoload":false}]'),
    "field-true-fast": (200, "application/json", b'{"role":"router","models_autoload":true}'),
    "http-401-error-json": (401, "application/json", b'{"error":{"message":"unauthorized"}}'),
    "http-500-props-false": (500, "application/json", b'{"role":"router","models_autoload":false}'),
    "reset-props": (None, None, None),
}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.split("?")[0] == "/v1/models":
            body = json.dumps({"object": "list", "data": [
                {"id": "fixture-model",
                 "status": {"value": "unloaded", "args": [str(MODEL), "-m", str(MODEL)]}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.split("?")[0] != "/props":
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        status, ctype, body = self.server.scenario
        if status is None:  # accept then close: curl sees an empty reply
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()
            return
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


for name, sc in SCENARIOS.items():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    srv.daemon_threads = True
    srv.scenario = sc
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    port = srv.server_address[1]
    try:
        p = subprocess.run(["bash", str(PROBE), "check", "--port", str(port),
                            "--expect", "fixture-model", "--id", "rv01", "--json"],
                           capture_output=True, text=True, timeout=120)
        try:
            row = json.loads(p.stdout)["rows"][0]
            print(f"{name:24s} verdict={row.get('verdict')} reason={row.get('reason')} exit={p.returncode}")
        except Exception as e:
            print(f"{name:24s} UNPARSABLE rc={p.returncode} out={p.stdout[:160]!r} err={p.stderr[:120]!r} ({e})")
    finally:
        srv.shutdown()
        srv.server_close()
        th.join(timeout=5)
