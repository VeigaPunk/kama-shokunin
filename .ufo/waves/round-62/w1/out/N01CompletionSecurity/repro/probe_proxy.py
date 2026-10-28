#!/usr/bin/env python3
"""Seat N01: proxy-env capture — env must be present before the first
urlopen, because urllib builds its default opener lazily and caches env
proxies at that moment."""
import http.server
import importlib.util
import json
import os
import threading

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tool = load('kcl', os.path.join(LANE, 'tools', 'kama-completion-live.py'))
counter = load('r62c1', os.path.join(LANE, 'tools', 'round62-c1-counter.py'))

HITS = []


class Canary(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        HITS.append(('GET', self.path))
        b = b'DIRECT'
        self.send_response(200)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        self.rfile.read(n)
        HITS.append(('POST', self.path))
        b = b'DIRECT'
        self.send_response(200)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass


class Proxy(http.server.BaseHTTPRequestHandler):
    """A plain forwarding HTTP proxy that answers every request itself and
    records the absolute-form target it was handed."""
    def _any(self):
        HITS.append(('PROXY', self.command, self.path))
        b = b'VIA-PROXY'
        self.send_response(200)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    do_GET = _any
    do_POST = _any

    def log_message(self, *a):
        pass


def serve(h):
    srv = http.server.HTTPServer(('127.0.0.1', 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


canary, CPORT = serve(Canary)
proxy, PPORT = serve(Proxy)
os.environ.update({'http_proxy': f'http://127.0.0.1:{PPORT}',
                   'HTTP_PROXY': f'http://127.0.0.1:{PPORT}',
                   'all_proxy': f'http://127.0.0.1:{PPORT}',
                   'ALL_PROXY': f'http://127.0.0.1:{PPORT}'})
for k in ('no_proxy', 'NO_PROXY'):
    os.environ.pop(k, None)

out = {'canary_port': CPORT, 'proxy_port': PPORT}
HITS.clear()
r = tool.http_post(CPORT, '/v1/completions', {'prompt': 'p'})
out['tool_http_post'] = {'status': r['status'], 'body': r['body'][:24].decode(),
                         'hits': list(HITS)}
HITS.clear()
r = live_get = tool._live.http_get(CPORT, '/health')
out['dependency_http_get'] = {'status': r['status'], 'body': r['body'][:24].decode(),
                              'hits': list(HITS)}
HITS.clear()
st, body = counter.post(CPORT, {'prompt': 'p'})
out['counter_post'] = {'status': st, 'body': body[:24], 'hits': list(HITS)}
print(json.dumps(out, indent=1, sort_keys=True))
