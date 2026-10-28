#!/usr/bin/env python3
"""Seat N01: does kama-completion-live.http_post / round62-c1-counter.post
follow a 30x off the loopback target, and does the ambient proxy env capture
the request? All servers here are my own children on 127.0.0.1:0."""
import importlib.util
import json
import os
import sys
import threading
import http.server

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tool = load('kcl', os.path.join(LANE, 'tools', 'kama-completion-live.py'))
counter = load('r62c1', os.path.join(LANE, 'tools', 'round62-c1-counter.py'))
live = tool._live

HITS = []


class Canary(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        HITS.append(('GET', self.path, self.headers.get('Host')))
        b = b'CANARY-BODY'
        self.send_response(200)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        self.rfile.read(n)
        HITS.append(('POST', self.path, self.headers.get('Host')))
        b = b'CANARY-POST'
        self.send_response(200)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass


class Redirector(http.server.BaseHTTPRequestHandler):
    def _go(self, code):
        n = int(self.headers.get('Content-Length') or 0)
        self.rfile.read(n)
        self.send_response(code)
        self.send_header('Location', f'http://127.0.0.1:{CANARY_PORT}/sink')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_GET(self):
        self._go(302)

    def do_POST(self):
        self._go(302)

    def log_message(self, *a):
        pass


def serve(handler):
    srv = http.server.HTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


canary, CANARY_PORT = serve(Canary)
redir, REDIR_PORT = serve(Redirector)

out = {'canary_port': CANARY_PORT, 'redirect_port': REDIR_PORT}

# 1) tool.http_post against a 302: followed or surfaced?
HITS.clear()
r = tool.http_post(REDIR_PORT, '/v1/completions', {'prompt': 'p'})
out['tool_http_post_on_302'] = {'status': r['status'], 'body': r['body'][:32].decode(),
                                'canary_hits': list(HITS)}

# 2) dependency's hardened GET on the same 302
HITS.clear()
r = live.http_get(REDIR_PORT, '/health')
out['dependency_http_get_on_302'] = {'status': r['status'], 'body': r['body'][:32].decode(),
                                     'canary_hits': list(HITS)}

# 3) counter.post against a 302
HITS.clear()
st, body = counter.post(REDIR_PORT, {'prompt': 'p'})
out['counter_post_on_302'] = {'status': st, 'body': body[:32], 'canary_hits': list(HITS)}

# 4) ambient proxy env: point every proxy var at a dead loopback port
dead = 9  # discard port on 127.0.0.1; nothing listens
os.environ.update({'http_proxy': f'http://127.0.0.1:{dead}',
                   'HTTP_PROXY': f'http://127.0.0.1:{dead}',
                   'all_proxy': f'http://127.0.0.1:{dead}',
                   'ALL_PROXY': f'http://127.0.0.1:{dead}'})
os.environ.pop('no_proxy', None)
os.environ.pop('NO_PROXY', None)
HITS.clear()
r = tool.http_post(CANARY_PORT, '/v1/completions', {'prompt': 'p'})
out['tool_http_post_with_proxy_env'] = {'status': r['status'], 'error': r['error'],
                                        'body': r['body'][:32].decode(),
                                        'canary_hits': list(HITS)}
HITS.clear()
r = live.http_get(CANARY_PORT, '/health')
out['dependency_http_get_with_proxy_env'] = {'status': r['status'], 'error': r['error'],
                                             'body': r['body'][:32].decode(),
                                             'canary_hits': list(HITS)}

# 5) counter.post unbounded read: a server that declares an enormous body
class Flood(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        self.rfile.read(n)
        self.send_response(200)
        self.send_header('Content-Length', str(64 * 1024 * 1024))
        self.end_headers()
        try:
            for _ in range(64):
                self.wfile.write(b'A' * (1024 * 1024))
        except OSError:
            pass

    def log_message(self, *a):
        pass


flood, FLOOD_PORT = serve(Flood)
st, body = counter.post(FLOOD_PORT, {'prompt': 'p'})
out['counter_post_flood'] = {'status': st, 'bytes_read': len(body)}

# 6) tool.http_post flood: is the cap enforced?
r = tool.http_post(FLOOD_PORT, '/v1/completions', {'prompt': 'p'})
out['tool_http_post_flood'] = {'status': r['status'], 'bytes': len(r['body']),
                               'truncated': r['body_truncated']}

print(json.dumps(out, indent=1, sort_keys=True))
