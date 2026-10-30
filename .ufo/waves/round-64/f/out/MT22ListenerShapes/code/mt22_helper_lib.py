"""mt22 helper library (functions only; no module-level argv use)."""
import http.server
import json
import os
import socket
import sys
import threading
import time


def log(msg):
    LOG.write(('mt22[' + MODE + '] ' + str(msg) + '\n').encode())


def serve_canned(sock, alias='kama-completion-probe'):
    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.0'

        def _send(self, status, payload):
            b = json.dumps(payload, separators=(',', ':')).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path == '/health':
                self._send(200, {'status': 'ok'})
            elif self.path == '/v1/models':
                self._send(200, {'object': 'list',
                                 'data': [{'id': alias, 'object': 'model'}]})
            elif self.path == '/props':
                self._send(200, {'model_alias': alias})
            else:
                self._send(404, {'error': {'code': 404, 'message': 'nf'}})

        def do_POST(self):
            n = int(self.headers.get('Content-Length') or 0)
            try:
                body = json.loads(self.rfile.read(n))
            except ValueError:
                body = {}
            if self.path == '/tokenize':
                toks = list(range(len(str(body.get('content', '')).split()) + 1))
                self._send(200, {'tokens': toks})
            elif self.path == '/v1/completions':
                np = body.get('n_predict', 8)
                np = np if isinstance(np, int) and np > 0 else 8
                self._send(200, {
                    'object': 'text_completion', 'model': alias,
                    'id': 'cmpl-mt22', 'created': int(time.time()),
                    'system_fingerprint': 'b11755-mt22',
                    'choices': [{'text': ' canned' * np, 'index': 0,
                                 'logprobs': None,
                                 'finish_reason': 'length'}],
                    'usage': {'completion_tokens': np, 'prompt_tokens': 1,
                              'total_tokens': np + 1,
                              'prompt_tokens_details': {'cached_tokens': 0}},
                    'timings': {'cache_n': 0, 'prompt_n': 1, 'prompt_ms': 1.0,
                                'predicted_n': np, 'predicted_ms': 1.0}})
            else:
                self._send(404, {'error': {'code': 404, 'message': 'nf'}})

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H,
                                          bind_and_activate=False)
    srv.socket.close()
    srv.socket = sock
    srv.server_address = sock.getsockname()
    threading.Thread(target=srv.serve_forever,
                     kwargs={'poll_interval': 0.1}, daemon=True).start()
    return srv


def bind_listener(mode, port):
    if mode in ('v6', 'mapped'):
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY,
                     1 if mode == 'v6' else 0)
        s.bind(('::1' if mode == 'v6' else '::ffff:127.0.0.2', port))
    elif mode == 'v4':
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.2', port))
    elif mode == 'ns':
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.unshare(0x10000000 | 0x40000000) != 0:
            raise OSError('unshare(CLONE_NEWUSER|CLONE_NEWNET) failed')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', port))
    elif mode in ('fwd', 'tcpfront'):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', port))
    else:
        raise ValueError('mode ' + mode)
    s.listen(64)
    return s


def pump(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except OSError:
        pass
    try:
        b.shutdown(socket.SHUT_WR)
    except OSError:
        pass


def connect_target(target):
    for _ in range(80):
        try:
            return socket.create_connection(('127.0.0.1', target), timeout=2)
        except OSError:
            time.sleep(0.1)
    return None


def relay_pair(conn, target):
    up = connect_target(target)
    if up is None:
        try:
            conn.close()
        except OSError:
            pass
        return
    threading.Thread(target=pump, args=(conn, up), daemon=True).start()
    threading.Thread(target=pump, args=(up, conn), daemon=True).start()


def accept_loop(sock, handler):
    def loop():
        while True:
            try:
                conn, _ = sock.accept()
            except OSError:
                return
            threading.Thread(target=handler, args=(conn,),
                             daemon=True).start()
    threading.Thread(target=loop, daemon=True).start()


def main():
    closers = []
    try:
        if MODE == 'fwd':
            s = bind_listener(MODE, PORT)
            accept_loop(s, lambda c: relay_pair(c, TARGET))
            closers.append(s)
        elif MODE == 'unixfront':
            upath = os.path.join(WORK, 'mt22.sock')
            try:
                os.unlink(upath)
            except OSError:
                pass
            u = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            u.bind(upath)
            os.chmod(upath, 0o666)
            u.listen(64)
            accept_loop(u, lambda c: relay_pair(c, TARGET))
            closers.append(u)
            s = bind_listener('tcpfront', PORT)
            closers.append(s)

            def to_unix(conn):
                up = None
                for _ in range(80):
                    try:
                        up = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        up.settimeout(2)
                        up.connect(upath)
                        break
                    except OSError:
                        time.sleep(0.1)
                        up = None
                if up is None:
                    try:
                        conn.close()
                    except OSError:
                        pass
                    return
                threading.Thread(target=pump, args=(conn, up),
                                 daemon=True).start()
                threading.Thread(target=pump, args=(up, conn),
                                 daemon=True).start()
            accept_loop(s, to_unix)
        elif MODE == 'unixcanned':
            upath = os.path.join(WORK, 'mt22.sock')
            try:
                os.unlink(upath)
            except OSError:
                pass
            u = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            u.bind(upath)
            os.chmod(upath, 0o666)
            u.listen(64)
            closers.append(u)

            def handle(conn):
                try:
                    data = b''
                    while b'\r\n\r\n' not in data:
                        d = conn.recv(65536)
                        if not d:
                            return
                        data += d
                    body = json.dumps({
                        'object': 'text_completion',
                        'model': 'kama-completion-probe',
                        'choices': [{'text': ' canned-unix-front',
                                     'index': 0,
                                     'finish_reason': 'length'}],
                        'usage': {'completion_tokens': 8,
                                  'prompt_tokens': 1,
                                  'total_tokens': 9}}).encode()
                    resp = (b'HTTP/1.1 200 OK\r\n'
                            b'Content-Type: application/json\r\n'
                            b'Content-Length: ' + str(len(body)).encode()
                            + b'\r\n\r\n' + body)
                    conn.sendall(resp)
                except OSError:
                    pass
                finally:
                    try:
                        conn.close()
                    except OSError:
                        pass
            accept_loop(u, handle)
        else:
            s = bind_listener(MODE, PORT)
            closers.append(s)
            if MODE != 'ns':
                serve_canned(s)
    except Exception as exc:
        log('stage failed: ' + repr(exc))
        sys.exit(3)
    with open(READY, 'w') as f:
        f.write('ok\n')
    log('listening; waiting for release in ' + HOLD)
    t0 = time.time()
    while time.time() - t0 < 240:
        if os.path.exists(os.path.join(HOLD, 'release')):
            break
        time.sleep(0.05)
    log('release seen; closing')
    for c in closers:
        try:
            if hasattr(c, 'shutdown'):
                c.shutdown()
            c.close()
        except OSError:
            pass
    try:
        os.unlink(READY)
    except OSError:
        pass

