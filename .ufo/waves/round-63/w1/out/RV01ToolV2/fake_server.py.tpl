#!/usr/bin/env python3
# Fake llama-server for reviewing kama-completion-live.py error paths. MODE is baked in.
import json, os, signal, socketserver, sys, time
MODE = "__MODE__"
ARGS = sys.argv[1:]
ALIAS = ARGS[ARGS.index('--alias') + 1]
PORT = int(ARGS[ARGS.index('--port') + 1])
N = {'completion': 0}
TOK = [1, 2, 3, 4, 5]

def good(text=" mat on the floor"):
    return {"id": "cmpl-1", "object": "text_completion", "created": 1800000000,
            "model": ALIAS, "system_fingerprint": "b11755-704366d76",
            "choices": [{"index": 0, "text": text, "logprobs": None, "finish_reason": "length"}],
            "usage": {"completion_tokens": 8, "prompt_tokens": 5, "total_tokens": 13,
                      "prompt_tokens_details": {"cached_tokens": 0}},
            "timings": {"predicted_n": 8, "cache_n": 0, "prompt_n": 5, "predicted_ms": 1.0}}

class H(socketserver.StreamRequestHandler):
    def send(self, status, body, ctype="application/json", extra=(), raw=None):
        data = raw if raw is not None else (body if isinstance(body, bytes) else json.dumps(body).encode())
        hdr = f"HTTP/1.1 {status}\r\nContent-Type: {ctype}\r\n" + "".join(f"{k}: {v}\r\n" for k, v in extra)
        if not any(k.lower() == 'transfer-encoding' for k, _ in extra):
            hdr += f"Content-Length: {len(data)}\r\n"
        self.wfile.write(hdr.encode() + b"Connection: close\r\n\r\n" + data)
        self.wfile.flush()

    def handle(self):
        line = self.rfile.readline().decode()
        if not line:
            return
        method, path, _ = line.split(' ', 2)
        clen = 0
        while True:
            h = self.rfile.readline()
            if h in (b'\r\n', b'\n', b''):
                break
            k, _, v = h.decode().partition(':')
            if k.strip().lower() == 'content-length':
                clen = int(v.strip())
        body = self.rfile.read(clen) if clen else b''
        if path == '/health':
            return self.send('200 OK', b'{"status":"ok"}')
        if path == '/v1/models':
            return self.send('200 OK', {"object": "list", "data": [{"id": ALIAS, "object": "model"}]})
        if path == '/props':
            return self.send('200 OK', {"model_alias": ALIAS})
        if path == '/tokenize':
            toks = TOK if MODE != 'tokenize_mismatch' else TOK[:4]
            return self.send('200 OK', {"tokens": toks})
        if path == '/v1/completions':
            req = json.loads(body or b'{}')
            if 'prompt' not in req:
                return self.send('400 Bad Request', {"error": {"message": "prompt required"}})
            N['completion'] += 1
            n = N['completion']
            if MODE == 'sigterm_ignore':
                pass
            if MODE == 'timeout' and n == 1:
                time.sleep(6)
            if MODE == 'bigbody' and n == 1:
                return self.send('200 OK', good("x" * 70000))
            if MODE == 'nonutf8':
                raw = json.dumps(good()).encode().replace(b' mat', b' \xff mat')
                return self.send('200 OK', None, raw=raw)
            if MODE == 'bad_status_line' and n == 1:
                self.wfile.write(b"HTTP/1.1 garbage\r\n\r\n"); self.wfile.flush(); return
            if MODE == 'chunked_cut' and n == 1:
                self.wfile.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n")
                self.wfile.write(b"20\r\n" + b'{"object":"text_completion",' + b"\r\n"); self.wfile.flush(); return
            if MODE == 'trunc_cl' and n == 1:
                data = json.dumps(good()).encode()[:120]
                self.wfile.write(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 900\r\nConnection: close\r\n\r\n".encode() + data); self.wfile.flush(); return
            if MODE == 'envelope_object' and n == 1:
                g = good(); g['object'] = 'chat.completion'; return self.send('200 OK', g)
            if MODE == 'usage_str' and n == 1:
                g = good(); g['usage'] = 'oops'; return self.send('200 OK', g)
            if MODE == 'fp_newline' and n == 1:
                g = good(); g['system_fingerprint'] = 'b11755-704366d76\n'; return self.send('200 OK', g)
            if MODE == 'nondet_nonobj' and n == 2:
                return self.send('200 OK', {"object": "text_completion", "choices": [1]})
            if MODE == 'nondet_empty' and n == 2:
                return self.send('200 OK', {"object": "text_completion", "choices": []})
            if MODE == 'nondet_text' and n == 2:
                return self.send('200 OK', good(" different"))
            if MODE == 'pad' and n == 1:
                return self.send('200 OK', None, raw=json.dumps(good()).encode() + b' '*70000)
            return self.send('200 OK', good())
        return self.send('404 Not Found', {"error": "nf"})

class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if MODE == 'sigterm_ignore':
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
with S(('127.0.0.1', PORT), H) as srv:
    srv.serve_forever()
