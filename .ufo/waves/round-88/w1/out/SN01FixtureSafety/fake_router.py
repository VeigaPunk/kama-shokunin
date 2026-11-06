import http.server, importlib.util, json, os, pathlib, socket, tempfile, threading
RC = "/fast/scratch/hyaku/kama-r88/SN01FixtureSafety/counter.py"
spec = importlib.util.spec_from_file_location("rc", RC); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
STATE = {"value": "unloaded"}
SEEN = []
def models():
    return {"object": "list", "data": [{"id": "stories260K", "object": "model", "owned_by": "llamacpp",
            "status": {"value": STATE["value"], "args": ["llama-server", "-ctx", "4096"]}}]}
class H(http.server.BaseHTTPRequestHandler):
    def _j(self, code, body):
        b = json.dumps(body).encode(); self.send_response(code)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p = self.path.split("?")[0]; SEEN.append("GET " + p)
        if p == "/v1/models": self._j(200, models())
        elif p == "/health": self._j(200, {"status": "ok"})
        elif p == "/props": self._j(200, {"model_path": "stories260K.gguf", "total_slots": 1})
        else: self.send_response(404); self.end_headers()
    def do_POST(self):
        p = self.path.split("?")[0]; SEEN.append("POST " + p)
        if p == "/models/load": STATE["value"] = "loaded"; self._j(200, {"success": True})
        elif p == "/models/unload": STATE["value"] = "unloaded"; self._j(200, {"success": True})
        elif p == "/v1/chat/completions":
            if STATE["value"] == "loaded": self._j(200, {"choices": [{"message": {"content": "hi"}}]})
            else: self._j(400, {"error": {"code": 400, "message": "model is not loaded"}})
        else: self.send_response(404); self.end_headers()
    def version_string(self): return "llama.cpp"
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
m.free_port = lambda: port          # squat the port the counter would pick
base = pathlib.Path("/fast/scratch/hyaku/kama-r88/SN01FixtureSafety")
work = pathlib.Path(tempfile.mkdtemp(prefix="squat-", dir=base))
probe = work / "kama-probe.sh"
probe.write_bytes(__import__("subprocess").run(["git","-C","/home/vgpnk/Projects/shokunin/kama-shokunin","show","f77d2ae9f2797a19e7548989fb9e64d8f9411d3f:tools/kama-probe.sh"],capture_output=True).stdout)
rows = m.live_cells(probe, work, dict(os.environ, TMPDIR=str(work)))
print("SQUAT rows:", rows)
print("SQUAT requests seen:", sorted(set(SEEN)))
print("SQUAT any llama-server started:", __import__("subprocess").run(["pgrep","-af",str(work)+"/models"],capture_output=True,text=True).stdout.strip() or "none")
