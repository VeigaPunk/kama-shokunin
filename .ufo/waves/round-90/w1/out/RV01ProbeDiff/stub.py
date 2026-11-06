#!/usr/bin/env python3
# RV01 stub: one raw-socket HTTP listener on one loopback port, one hostile scenario per process.
# Bytes are sent exactly as built here (raw control bytes, invalid UTF-8, lone surrogates in JSON).
import json, socketserver, sys

MB = 1 << 20
MODEL = "stories260K.gguf"
BIN = "/home/vgpnk/.local/opt/llama-b12177/llama-server"
GGUF = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"
MODE, PORT = sys.argv[1], int(sys.argv[2])


def jb(doc, ensure_ascii=True):
    return json.dumps(doc, ensure_ascii=ensure_ascii).encode()


def padded(doc, total):
    doc = dict(doc, pad="")
    n = total - len(jb(doc))
    assert n >= 0, n
    doc["pad"] = "x" * n
    out = jb(doc)
    assert len(out) == total, (len(out), total)
    return out


def http(status, headers, body=b"", cl=True):
    head = b"HTTP/1.1 " + status + b"\r\n"
    for h in headers:
        head += h + b"\r\n"
    if cl:
        head += b"Content-Length: %d\r\n" % len(body)
    head += b"Connection: close\r\n\r\n"
    return head + body


def listing(entries, ensure_ascii=True):
    return {"object": "list", "data": entries}


def unl(value="unloaded"):
    return {"id": MODEL, "status": {"value": value, "args": [BIN, "-m", GGUF]}}


JSON_H = [b"Server: llama.cpp", b"Content-Type: application/json"]


def models_answer(mode):
    if mode == "ok":
        return http(b"200 OK", JSON_H, jb(listing([{"id": MODEL, "object": "model"}])))
    if mode == "exact":
        return http(b"200 OK", JSON_H, padded(listing([{"id": MODEL}]), 4 * MB), cl=True)
    if mode == "over1":
        return http(b"200 OK", JSON_H, padded(listing([{"id": MODEL}]), 4 * MB + 1), cl=True)
    if mode == "overclose":
        return http(b"200 OK", JSON_H, padded(listing([{"id": MODEL}]), 4 * MB + 1), cl=False)
    if mode == "big401":
        return http(b"401 Unauthorized", [b"Content-Type: text/html"], b"<html>" + b"x" * (5 * MB), cl=True)
    if mode == "legit1m":
        return http(b"200 OK", JSON_H, padded(listing([{"id": MODEL}]), 1 * MB))
    if mode == "ctlid":
        ids = ["a\x01b", "x\x1b[31mred", "tab\there", "nl\nfake\tcol", "del\x7f", "c1\x9b31m", MODEL]
        return http(b"200 OK", JSON_H, jb(listing([{"id": i} for i in ids])))
    if mode == "u2028":
        ids = ["a\u2028b", "c\u202ed", "e\u0085f", MODEL]
        return http(b"200 OK", JSON_H, jb(listing([{"id": i} for i in ids])))
    if mode == "pos-nonascii":
        return http(b"200 OK", JSON_H, jb(listing([{"id": "mod\u00e8le-\u00e9.gguf"}])))
    if mode == "pos-quote":
        return http(b"200 OK", JSON_H, jb(listing([{"id": 'q"b\\c.gguf'}])))
    if mode == "ctlserver":
        return http(b"200 OK", [b"Server: llama.cpp\x1b[31mRED\x09col\x7f", b"Content-Type: application/json"], jb(listing([{"id": MODEL}])))
    if mode == "c1server":
        return http(b"200 OK", [b"Server: llama.cpp\xc2\x9b31m\xe2\x80\xaeEVIL", b"Content-Type: application/json"], jb(listing([{"id": MODEL}])))
    if mode == "badutf8server":
        return http(b"200 OK", [b"Server: llama.cpp\xff\xfe", b"Content-Type: application/json"], jb(listing([{"id": MODEL}])))
    if mode == "ctype-esc":
        return http(b"200 OK", [b"Server: llama.cpp", b"Content-Type: application/json\x1b[0m"], jb(listing([{"id": MODEL}])))
    if mode == "bom":
        return http(b"200 OK", JSON_H, b"\xef\xbb\xbf" + jb(listing([{"id": MODEL}])))
    if mode == "surr-only":
        return http(b"200 OK", JSON_H, b'{"object":"list","data":[{"id":"\\ud800"}]}')
    if mode == "surr-mixed":
        return http(b"200 OK", JSON_H, b'{"object":"list","data":[{"id":"%s"},{"id":"\\ud800"}]}' % MODEL.encode())
    if mode == "router-unl":
        return http(b"200 OK", JSON_H, jb(listing([unl()])))
    if mode == "router-esc":
        return http(b"200 OK", JSON_H, jb(listing([unl("unloaded\x1b[0m")])))
    if mode == "router-surr":
        return http(b"200 OK", JSON_H, b'{"object":"list","data":[{"id":"%s","status":{"value":"unloaded","args":["%s","-m","%s"]}},{"id":"\\ud800","status":{"value":"loaded"}}]}' % (MODEL.encode(), BIN.encode(), GGUF.encode()))
    if mode == "props-big":
        return http(b"200 OK", JSON_H, jb(listing([unl()])))
    if mode == "router-unl-junk":
        return http(b"200 OK", JSON_H, jb(listing([{"id": "junk\x1b", "status": {"value": "loaded"}}, unl()])))
    if mode == "hdrflood":
        return None  # streamed by handler
    if mode == "props-empty":
        return http(b"200 OK", JSON_H, jb(listing([unl()])))
    if mode == "router-ctlid-loading":
        return http(b"200 OK", JSON_H, jb(listing([{"id": "bad\x1bid", "status": {"value": "loading"}}])))
    if mode == "router-surr-first":
        return http(b"200 OK", JSON_H, b'{"object":"list","data":[{"id":"\\ud800","status":{"value":"loaded"}},{"id":"%s","status":{"value":"unloaded","args":["%s","-m","%s"]}}]}' % (MODEL.encode(), BIN.encode(), GGUF.encode()))
    if mode == "router-ctlid-unl":
        return http(b"200 OK", JSON_H, jb(listing([{"id": "bad\x1bid", "status": {"value": "unloaded"}}])))
    if mode == "root-big":
        return http(b"404 Not Found", [b"Content-Type: text/html"], b"<html>nope</html>")
    return http(b"404 Not Found", [b"Content-Type: text/plain"], b"nope")


def props_answer(mode):
    if mode == "props-empty":
        return http(b"200 OK", JSON_H, b"", cl=True)
    if mode in ("router-unl", "router-esc", "router-surr", "router-unl-junk"):
        return http(b"200 OK", JSON_H, jb({"role": "router", "models_autoload": True}))
    if mode == "props-big":
        return http(b"200 OK", JSON_H, padded({"role": "router", "models_autoload": True}, 5 * MB))
    return http(b"404 Not Found", [b"Content-Type: text/plain"], b"nope")


class H(socketserver.BaseRequestHandler):
    def handle(self):
        data = b""
        try:
            while b"\r\n\r\n" not in data:
                chunk = self.request.recv(65536)
                if not chunk:
                    return
                data += chunk
            path = data.split(b"\r\n", 1)[0].split(b" ")[1].decode("latin1")
            if path == "/v1/models":
                if MODE == "hdrflood":
                    self.request.sendall(b"HTTP/1.1 200 OK\r\nServer: llama.cpp\r\nContent-Type: application/json\r\n")
                    for _ in range(2048):
                        self.request.sendall(b"X-Pad: " + b"a" * (64 * 1024) + b"\r\n")
                    self.request.sendall(b"\r\n" + jb(listing([{"id": MODEL}])))
                    return
                self.request.sendall(models_answer(MODE))
            elif path == "/props":
                self.request.sendall(props_answer(MODE))
            elif path == "/" and MODE == "root-big":
                self.request.sendall(http(b"200 OK", [b"Content-Type: text/html"], b"<html>" + b"x" * (5 * MB)))
            else:
                self.request.sendall(http(b"404 Not Found", [b"Content-Type: text/plain"], b"nope"))
        except OSError:
            pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with S(("127.0.0.1", PORT), H) as srv:
        srv.serve_forever()
