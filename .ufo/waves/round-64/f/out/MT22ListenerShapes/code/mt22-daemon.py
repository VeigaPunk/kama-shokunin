#!/usr/bin/env python3
"""mt22 pre-started root daemon (test-only). argv: <sockpath>

Started by the driver BEFORE the counter's tool process, so its start ticks
precede the tool's. Accepts one command per connection:
  {"mode": "v6"|"mapped", "port": P, "hold": DIR, "work": DIR}
binds the requested listener, signals readiness via <work>/mt22-ready.<mode>,
and closes everything when <hold>/release appears (or after 240 s).
"""
import json
import os
import socket
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mt22_helper_lib as H

SOCK = sys.argv[1]
ACTIVE = []
LOCK = threading.Lock()


def run_listener(mode, port, hold, work):
    s = H.bind_listener(mode, port)
    H.serve_canned(s)
    with LOCK:
        ACTIVE.append(s)
    ready = os.path.join(work, 'mt22-ready.' + mode)
    try:
        os.makedirs(work, exist_ok=True)
    except OSError:
        pass
    with open(ready, 'w') as f:
        f.write('ok\n')
    t0 = time.time()
    while time.time() - t0 < 400:
        if os.path.exists(os.path.join(hold, 'release')):
            break
        with LOCK:
            if s not in ACTIVE:
                break  # closed by a 'close' command
        time.sleep(0.02)
    with LOCK:
        if s in ACTIVE:
            ACTIVE.remove(s)
    try:
        s.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        s.close()
    except OSError:
        pass
    try:
        os.unlink(ready)
    except OSError:
        pass


def handle(conn):
    try:
        hdr = b''
        while b'\n' not in hdr:
            d = conn.recv(1)
            if not d:
                conn.close()
                return
            hdr += d
        n = int(hdr.strip() or 0)
        payload = b''
        while len(payload) < n:
            d = conn.recv(n - len(payload))
            if not d:
                break
            payload += d
        req = json.loads(payload)
        if req.get('mode') == 'close':
            for s in list(ACTIVE):
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    s.close()
                except OSError:
                    pass
            with LOCK:
                ACTIVE.clear()
            conn.sendall(b'closed')
            return
        threading.Thread(target=run_listener,
                         args=(req['mode'], int(req['port']), req['hold'],
                               req['work']), daemon=True).start()
        conn.sendall(b'ok')
    except Exception as exc:
        try:
            conn.sendall(b'ERR ' + repr(exc).encode())
        except OSError:
            pass
    finally:
        try:
            conn.close()
        except OSError:
            pass


def main():
    try:
        os.unlink(SOCK)
    except OSError:
        pass
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(SOCK)
    os.chmod(SOCK, 0o666)
    s.listen(16)
    sys.stderr.write('mt22 daemon up at ' + SOCK + '\n')
    sys.stderr.flush()
    t0 = time.time()
    while time.time() - t0 < 1800:
        try:
            conn, _ = s.accept()
        except OSError:
            break
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


main()
