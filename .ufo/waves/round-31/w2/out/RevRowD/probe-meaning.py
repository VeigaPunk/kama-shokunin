#!/usr/bin/python3
"""Probe only the two RevRowD meaning-cell counterexamples; never alter a counter."""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ap = argparse.ArgumentParser()
ap.add_argument('--clone', required=True)
ap.add_argument('--out', required=True)
a = ap.parse_args()
clone = Path(a.clone)
out = Path(a.out)
script = clone / '.ufo/waves/round-31/count-c1.py'
spec = importlib.util.spec_from_file_location('frozen_c1', script)
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)
reg = json.loads((clone / 'registry/chat-param-outcomes-r31.json').read_text())
for label, path, key in (
    ('server', frozen.SERVER, 'server_sha256'),
    ('library', frozen.IMPL, 'library_sha256'),
    ('model', frozen.MODEL, 'model_sha256'),
):
    actual = frozen.sha256_file(path)
    if actual != reg['build'][key]:
        raise RuntimeError(f'{label} pin mismatch: {actual}')

bodies = {}
for row in reg['rows']:
    if row['id'] not in ('K31-11', 'K31-12'):
        continue
    body = copy.deepcopy(reg['base_body'])
    body[row['param']] = copy.deepcopy(row['sent'])
    body.update(copy.deepcopy(row.get('also', {})))
    bodies[row['id']] = body

cases = [('base', copy.deepcopy(reg['base_body']))]
for rid, key, value in (
    ('K31-11', 'grammar', ''),
    ('K31-12', 'logprobs', False),
):
    cases.append((rid + '-registered', bodies[rid]))
    changed = copy.deepcopy(bodies[rid])
    changed[key] = value
    cases.append((rid + '-counterexample', changed))

server = frozen.Server()
receipt = {'port': server.port, 'pins': reg['build'], 'cases': []}
try:
    for name, body in cases:
        status, raw, headers = frozen.http(server.port, 'POST', '/v1/chat/completions', body)
        text = raw.decode('utf-8', errors='strict')
        frames = [line[6:] for line in text.splitlines() if line.startswith('data: ')]
        entry = {'name': name, 'request': body, 'status': status, 'headers': headers,
                 'body_utf8': text, 'body_hex': raw.hex(),
                 'sse_done': '[DONE]' in frames,
                 'non_done_frames': sum(frame != '[DONE]' for frame in frames)}
        receipt['cases'].append(entry)
        print(f'{name} status={status} sse_done={entry["sse_done"]} non_done_frames={entry["non_done_frames"]}')
        if status >= 400:
            print(text)
finally:
    server.fh.flush()
    (out.parent / 'meaning-server.log').write_bytes(server.log.read_bytes())
    server.close()
    out.write_text(json.dumps(receipt, indent=2) + '\n')
