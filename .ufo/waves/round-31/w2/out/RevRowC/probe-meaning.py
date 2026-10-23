#!/usr/bin/env python3
"""Live counterexamples for the two overbroad meaning clauses, on our own server."""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
CLONE = Path('/tmp/kama-r31w2/RevRowC/lane')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowC')
COUNTER = CLONE / '.ufo/waves/round-31/count-c1.py'
assert hashlib.sha256(COUNTER.read_bytes()).hexdigest() == 'd86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216'
spec = importlib.util.spec_from_file_location('r31_frozen_counter', COUNTER)
counter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(counter)
registry = json.loads((CLONE / 'registry/chat-param-outcomes-r31.json').read_text())
for path, key in ((counter.SERVER, 'server_sha256'), (counter.IMPL, 'library_sha256'), (counter.MODEL, 'model_sha256')):
    assert counter.sha256_file(path) == registry['build'][key], str(path)

cases = [
    ('base-user-string', registry['base_body']),
    ('user-null', {**registry['base_body'], 'messages': [{'role': 'user', 'content': None}]}),
    ('user-number', {**registry['base_body'], 'messages': [{'role': 'user', 'content': 42}]}),
    ('assistant-content-only', {**registry['base_body'], 'messages': [{'role': 'user', 'content': 'hi'}, {'role': 'assistant', 'content': 'hello'}]}),
    ('assistant-neither', {**registry['base_body'], 'messages': [{'role': 'assistant'}]}),
    ('assistant-tool-calls-only', {**registry['base_body'], 'messages': [{'role': 'user', 'content': 'hi'}, {'role': 'assistant', 'tool_calls': [{'id': 'call_1', 'type': 'function', 'function': {'name': 'f', 'arguments': '{}'}}]}]}),
]
srv = counter.Server.__new__(counter.Server)
results = []
try:
    counter.Server.__init__(srv)
    print(f'owned-server-port {srv.port}')
    for name, request in cases:
        status, body, headers = counter.http(srv.port, 'POST', '/v1/chat/completions', request)
        (OUT / f'probe-{name}-response.body').write_bytes(body)
        try:
            document = json.loads(body)
        except (ValueError, UnicodeError):
            document = None
        (OUT / f'probe-{name}-request.json').write_text(json.dumps(request, indent=2) + '\n')
        result = {'case': name, 'request': request, 'status': status, 'headers': headers, 'body': body.decode('utf-8', errors='replace'), 'parsed': document}
        results.append(result)
        print(f'{name} status={status} error={json.dumps((document or {}).get("error"), sort_keys=True)}')
    (OUT / 'meaning-probe.json').write_text(json.dumps({'port': srv.port, 'counter_sha256': hashlib.sha256(COUNTER.read_bytes()).hexdigest(), 'build': registry['build'], 'cases': results}, indent=2) + '\n')
finally:
    if hasattr(srv, 'proc'):
        srv.fh.flush()
        shutil.copyfile(srv.log, OUT / 'meaning-probe-server-before-shutdown.log')
        srv.close()
    elif hasattr(srv, 'tmp'):
        srv.tmp.cleanup()
