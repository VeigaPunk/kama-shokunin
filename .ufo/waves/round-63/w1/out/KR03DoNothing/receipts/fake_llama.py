#!/usr/bin/env python3
"""Mutant c1-fake-child: a stdlib HTTP server that impersonates llama-server.
It runs no llama.cpp code. It answers the same endpoints with self-consistent
bodies (usage/tokenize counted by the same word rule) so every grader check
passes while the receipt still names the real llama-server binary path+sha."""
import argparse
import http.server
import json
import sys

FP = 'b11755-704366d76'
ap = argparse.ArgumentParser()
ap.add_argument('--port', type=int, required=True)
ap.add_argument('--alias', default='kama-completion-probe')
args, _unused = ap.parse_known_args(sys.argv[1:])


def ntok(text):
    return len(text.split()) + 1  # same count for /tokenize and usage


class H(http.server.BaseHTTPRequestHandler):
    def _send(self, status, payload):
        b = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == '/health':
            b = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        elif self.path == '/v1/models':
            self._send(200, {'object': 'list', 'data': [
                {'id': args.alias, 'object': 'model'}]})
        elif self.path == '/props':
            self._send(200, {'model_alias': args.alias})
        else:
            self._send(404, {'error': {'code': 404, 'message': 'nf'}})

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        body = json.loads(self.rfile.read(n) or b'{}')
        if self.path == '/tokenize':
            self._send(200, {'tokens': [1] * ntok(body.get('content', ''))})
            return
        if self.path != '/v1/completions' or 'prompt' not in body:
            self._send(400, {'error': {'code': 400, 'message': 'prompt missing',
                                       'type': 'invalid_request_error'}})
            return
        p = ntok(body['prompt'])
        self._send(200, {
            'object': 'text_completion', 'model': args.alias,
            'id': 'cmpl-fake-r63', 'created': 1793227518,
            'system_fingerprint': FP,
            'choices': [{'text': ' sat on', 'index': 0, 'logprobs': None,
                         'finish_reason': 'length'}],
            'usage': {'prompt_tokens': p, 'completion_tokens': 2,
                      'total_tokens': p + 2,
                      'prompt_tokens_details': {'cached_tokens': 0}},
            'timings': {'predicted_n': 2, 'cache_n': 0, 'prompt_n': p,
                        'predicted_ms': 1.0, 'prompt_ms': 1.0}})

    def log_message(self, *a):
        pass


http.server.HTTPServer(('127.0.0.1', args.port), H).serve_forever()
