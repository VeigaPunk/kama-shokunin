#!/usr/bin/env python3
"""Seat N01: with http_proxy in the environment, kama-completion-live.py
sends its graded POSTs to the proxy. This answers them itself and the tool
still records REQUEST_OK while the pinned child never serves a completion."""
import http.server
import json
import os
import subprocess
import sys
import threading

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
SCRATCH = '/fast/scratch/hyaku/kama-r62/w/N01CompletionSecurity/proxy-exploit'
TOOL = os.path.join(LANE, 'tools', 'kama-completion-live.py')
ALIAS = 'kama-completion-probe'
HITS = []


class Proxy(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n)
        try:
            req = json.loads(raw or b'{}')
        except ValueError:
            req = {}
        HITS.append({'path': self.path, 'prompt': req.get('prompt')})
        if 'prompt' not in req:
            body = json.dumps({'error': {'code': 400, 'message': 'no prompt',
                                         'type': 'invalid_request_error'}}).encode()
            self.send_response(400)
        else:
            body = json.dumps({
                'object': 'text_completion',
                'model': ALIAS,
                'system_fingerprint': 'b9999-cafebabefeed',
                'choices': [{'text': 'proxy-invented completion', 'index': 0,
                             'finish_reason': 'length'}],
                'usage': {'prompt_tokens': 5, 'completion_tokens': 8,
                          'total_tokens': 13},
                'timings': {'predicted_n': 8, 'predicted_ms': 12.0},
            }).encode()
            self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        HITS.append({'path': self.path, 'method': 'GET'})
        self.send_response(500)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def log_message(self, *a):
        pass


srv = http.server.HTTPServer(('127.0.0.1', 0), Proxy)
threading.Thread(target=srv.serve_forever, daemon=True).start()
proxy_port = srv.server_address[1]

os.makedirs(SCRATCH, exist_ok=True)
env = dict(os.environ)
env.update({'http_proxy': f'http://127.0.0.1:{proxy_port}',
            'HTTP_PROXY': f'http://127.0.0.1:{proxy_port}',
            'all_proxy': f'http://127.0.0.1:{proxy_port}',
            'ALL_PROXY': f'http://127.0.0.1:{proxy_port}'})
env.pop('no_proxy', None)
env.pop('NO_PROXY', None)
env['TMPDIR'] = SCRATCH
out = os.path.join(SCRATCH, 'receipt.json')
p = subprocess.run([sys.executable, TOOL, '--work',
                    os.path.join(SCRATCH, 'tool-work'),
                    '--alias', ALIAS, '--nonce', 'n01-proxy-receipt',
                    '--out', out],
                   capture_output=True, env=env)
print('tool_rc=', p.returncode)
print('stderr=', p.stderr.decode()[-400:])
try:
    r = json.load(open(out))
    print('verdict=', r['verdict'])
    print('failed_checks=', [k for k, v in r['checks'].items()
                             if v['passed'] is False])
    print('completion_text=', r['captures']['completion']['body'][:200])
except Exception as exc:
    print('no receipt:', exc)
print('proxy_hits=', json.dumps(HITS))
log = os.path.join(SCRATCH, 'tool-work', 'server.log')
try:
    text = open(log, errors='replace').read()
    print('child_log_mentions_completion_request=',
          ('/v1/completions' in text) or (' print_timing' in text))
    for line in text.splitlines():
        if 'completions' in line or 'print_timing' in line:
            print('  child:', line[:120])
except OSError as exc:
    print('no child log', exc)
srv.shutdown()
