#!/usr/bin/python3
"""Falsify global 'tools is ignored' without changing the frozen measurement."""
import importlib.util
import json
import shutil
from pathlib import Path

CLONE = Path('/tmp/kama-r31w2/RevRowE/clone')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowE')
spec = importlib.util.spec_from_file_location('frozen_c1', CLONE / '.ufo/waves/round-31/count-c1.py')
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)
reg = json.loads((CLONE / 'registry/chat-param-outcomes-r31.json').read_text())
row = next(r for r in reg['rows'] if r['id'] == 'K31-15')
base = {**reg['base_body'], 'grammar': 'root ::= "a"'}
probes = [('grammar-alone', base), ('same-grammar-with-K31-15-tools', {**base, 'tools': row['sent']})]
server = frozen.Server()
raw = {'server_port': server.port, 'server_pid': server.proc.pid, 'requests': []}
try:
    for label, request in probes:
        status, body, headers = frozen.http(server.port, 'POST', '/v1/chat/completions', request)
        text = body.decode('utf-8')
        raw['requests'].append({'label': label, 'request': request, 'status': status,
                                'headers': headers, 'body': text})
        doc = json.loads(text)
        print(json.dumps({'label': label, 'status': status, 'error': doc.get('error'),
                          'n_choices': len(doc.get('choices') or [])}, sort_keys=True))
finally:
    (OUT / 'tools-context-raw.json').write_text(json.dumps(raw, indent=2) + '\n')
    shutil.copyfile(server.log, OUT / 'tools-context-server.log')
    server.close()
