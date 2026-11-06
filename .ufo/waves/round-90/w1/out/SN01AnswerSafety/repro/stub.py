#!/usr/bin/env python3
"""Hostile loopback stub for round-90 answer-boundary review (SN01).

usage: stub.py MODE [N] [KIB]   ; port written to $PORTFILE, request log to $REQLOG
Modes:
  small           200 JSON {"data":[{"id":"stories260K"}]}
  hdrflood        N headers of KIB KiB each, then small JSON (200)
  info1xx         N 1xx blocks of KIB KiB each, then small JSON (200)
  trailers        chunked small JSON + N trailer headers of KIB KiB each
  cl_short        Content-Length: 10 but 64 MiB body
  bigbody         64 MiB body with truthful Content-Length
  http09          raw body, no status line
  ce_gzip         Content-Encoding: gzip, gzip of small JSON
  te_gzip         Transfer-Encoding: gzip, gzip of small JSON
  slow_body       Content-Length: 1000000, one byte / 200 ms
  body_then_hang  truthful small body, then hold the socket open 30 s
  chunked_hang    chunked, one chunk, no terminal chunk, hold 30 s
  huge_ids        N ids (~4 MiB JSON)
  inject_id       ids carrying tab/newline/U+0085/U+2028/ESC/comma/#@snapshot_id
  hdr_then_hang   header flood then hold open (header write time)
"""
import gzip
import json
import os
import socket
import sys
import threading
import time

MODE = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 0
KIB = int(sys.argv[3]) if len(sys.argv) > 3 else 8
PORTFILE = os.environ["PORTFILE"]
REQLOG = os.environ.get("REQLOG", "")

SMALL = b'{"data":[{"id":"stories260K"}]}'
JSON_HDR = b"Content-Type: application/json\r\n"


def log(path):
    if REQLOG:
        with open(REQLOG, "a") as fh:
            fh.write(path + "\n")


def pad_line(prefix: bytes, total: int) -> bytes:
    # total bytes including CRLF
    body = total - len(prefix) - 2
    if body < 0:
        body = 0
    return prefix + b"A" * body + b"\r\n"


def send(conn, data):
    conn.sendall(data)


def respond(conn, path):
    log(path)
    if MODE == "small":
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(SMALL) + SMALL)
    elif MODE == "hdrflood":
        send(conn, b"HTTP/1.1 200 OK\r\n")
        for i in range(N):
            send(conn, pad_line(b"X-Pad-%06d: " % i, KIB * 1024))
        send(conn, JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(SMALL) + SMALL)
    elif MODE == "hdrflood_slow":
        send(conn, b"HTTP/1.1 200 OK\r\n")
        for i in range(N):
            send(conn, pad_line(b"X-Pad-%06d: " % i, KIB * 1024))
            time.sleep(0.01)
        send(conn, JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(SMALL) + SMALL)
    elif MODE == "info1xx":
        for i in range(N):
            send(conn, b"HTTP/1.1 100 Continue\r\n" + pad_line(b"X-Pad-%06d: " % i, KIB * 1024) + b"\r\n")
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(SMALL) + SMALL)
    elif MODE == "trailers":
        send(conn, b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n" + JSON_HDR + b"\r\n")
        send(conn, b"%x\r\n" % len(SMALL) + SMALL + b"\r\n0\r\n")
        for i in range(N):
            send(conn, pad_line(b"X-Trailer-%06d: " % i, KIB * 1024))
        send(conn, b"\r\n")
    elif MODE == "cl_short":
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: 10\r\n\r\n")
        chunk = b"B" * 65536
        for _ in range(1024):  # 64 MiB
            send(conn, chunk)
    elif MODE == "chunked_big":
        send(conn, b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n" + JSON_HDR + b"\r\n")
        chunk = b"B" * 65536
        for _ in range(1024):  # 64 MiB, no terminal chunk until the end
            send(conn, b"%x\r\n" % len(chunk) + chunk + b"\r\n")
        send(conn, b"0\r\n\r\n")
    elif MODE == "close_big":
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Connection: close\r\n\r\n")
        chunk = b"B" * 65536
        for _ in range(1024):  # 64 MiB, close-delimited
            send(conn, chunk)
    elif MODE == "cl_just_over":
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: 4194305\r\n\r\n")
        send(conn, b"B" * 65536)
    elif MODE == "mixed_hdrflood":
        if path.startswith("/v1/models"):
            body = b"<html><body>hi</body></html>"
            send(conn, b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %d\r\n\r\n" % len(body) + body)
        else:
            send(conn, b"HTTP/1.1 200 OK\r\n")
            for i in range(N):
                send(conn, pad_line(b"X-Pad-%06d: " % i, KIB * 1024))
            send(conn, b"Content-Length: 2\r\n\r\n{}")
    elif MODE == "router_unloaded":
        if path.startswith("/props"):
            body = b'{"role":"router","models_autoload":true,"pad":"' + b"B" * (64 * 1024 * 1024) + b'"}'
            send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(body))
            send(conn, body)
        else:
            body = json.dumps({"object": "list", "data": [
                {"id": "stories260K", "status": {"value": "unloaded",
                                                 "args": ["--model", "/nonexistent/kama-r90/x.gguf"]}}]}).encode()
            send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(body) + body)
    elif MODE == "router_autoload_ok":
        if path.startswith("/props"):
            body = b'{"role":"router","models_autoload":true}'
            send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(body) + body)
        else:
            body = json.dumps({"object": "list", "data": [
                {"id": "stories260K", "status": {"value": "unloaded",
                                                 "args": ["--model", "/nonexistent/kama-r90/x.gguf"]}}]}).encode()
            send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(body) + body)
    elif MODE == "inject_raw":
        # deliberately invalid JSON: raw control bytes inside a string value
        body = (b'{"object":"list","data":[{"id":"evil\tTAB"},{"id":"evil\nNL"},'
                b'{"id":"evil\x1bESC"},{"id":"evil\x7fDEL"},{"id":"evil|PIPE"}]}')
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(body))
        send(conn, body)
    elif MODE == "mixed_slow":
        if path.startswith("/v1/models"):
            body = b"<html><body>hi</body></html>"
            send(conn, b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %d\r\n\r\n" % len(body) + body)
        else:
            send(conn, b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 1000000\r\n\r\n")
            for _ in range(150):
                send(conn, b"B"); time.sleep(0.2)
    elif MODE == "health_slow":
        if path.startswith("/v1/models"):
            send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(SMALL) + SMALL)
        else:
            send(conn, b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 1000000\r\n\r\n")
            for _ in range(150):
                send(conn, b"B"); time.sleep(0.2)
    elif MODE == "bigbody":
        body = b'{"data":[{"id":"x"}],"pad":"' + b"B" * (64 * 1024 * 1024) + b'"}'
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(body))
        send(conn, body)
    elif MODE == "http09":
        send(conn, SMALL)
    elif MODE == "ce_gzip":
        body = gzip.compress(SMALL)
        send(conn, b"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\n" + JSON_HDR
             + b"Content-Length: %d\r\n\r\n" % len(body) + body)
    elif MODE == "te_gzip":
        body = gzip.compress(SMALL)
        send(conn, b"HTTP/1.1 200 OK\r\nTransfer-Encoding: gzip\r\n" + JSON_HDR + b"\r\n" + body)
    elif MODE == "slow_body":
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: 1000000\r\n\r\n")
        for _ in range(150):
            send(conn, b"B")
            time.sleep(0.2)
    elif MODE == "body_then_hang":
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(SMALL) + SMALL)
        time.sleep(30)
    elif MODE == "chunked_hang":
        send(conn, b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n" + JSON_HDR + b"\r\n")
        send(conn, b"%x\r\n" % len(SMALL) + SMALL + b"\r\n")
        time.sleep(30)
    elif MODE == "huge_ids":
        ids = ["m%07d" % i for i in range(N)]
        body = json.dumps({"object": "list", "data": [{"id": i} for i in ids]}).encode()
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(body))
        send(conn, body)
    elif MODE == "inject_id":
        specials = [
            "evil\tTAB",
            "evil\nNEWLINE",
            "evil\rCR",
            "evil\x00NUL",
            "evil\x1b[31mESC",
            "evil\x7fDEL",
            "evil\u0085NEL",
            "evil\u2028LSEP",
            "evil\u2029PSEP",
            "evil,COMMA",
            "#@snapshot_id 20990101T000000Z",
            "evil|PIPE",
            "evil\\u0009LITERAL",
        ]
        body = json.dumps({"object": "list", "data": [{"id": s} for s in specials]}).encode()
        send(conn, b"HTTP/1.1 200 OK\r\n" + JSON_HDR + b"Content-Length: %d\r\n\r\n" % len(body))
        send(conn, body)
    elif MODE == "hdr_then_hang":
        send(conn, b"HTTP/1.1 200 OK\r\n")
        for i in range(N):
            send(conn, pad_line(b"X-Pad-%06d: " % i, KIB * 1024))
        time.sleep(30)
    else:
        send(conn, b"HTTP/1.1 500 Nope\r\nContent-Length: 0\r\n\r\n")


def handle(conn):
    try:
        conn.settimeout(15)
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(4096)
            if not chunk:
                return
            data += chunk
        path = "/"
        if b" " in data:
            path = data.split(b" ")[1].decode("latin-1")
        respond(conn, path)
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(16)
    port = srv.getsockname()[1]
    with open(PORTFILE, "w") as fh:
        fh.write(str(port))
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
