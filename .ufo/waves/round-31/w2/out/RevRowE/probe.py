#!/usr/bin/python3
"""Read-only row-meaning probe; unmodified frozen counter owns server lifecycle only."""
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
base = reg['base_body']
rows = [r for r in reg['rows'] if r['id'] in {f'K31-{n}' for n in range(13, 19)}]
probes = [('base', base)]
for row in rows:
    request = {**base, row['param']: row['sent'], **row.get('also', {})}
    probes.append((row['id'], request))
probes += [
    ('include-usage-without-stream', {**base, 'stream_options': {'include_usage': True}}),
    ('stream-with-usage-false', {**base, 'stream': True, 'stream_options': {'include_usage': False}}),
]

def shape(doc):
    choices = doc.get('choices') or []
    return {
        'top_keys': sorted(doc.keys()),
        'n_choices': len(choices),
        'choice_keys': [sorted(c.keys()) for c in choices if isinstance(c, dict)],
        'has_logprobs': bool(choices) and choices[0].get('logprobs') is not None,
        'usage_keys': sorted((doc.get('usage') or {}).keys()),
        'prompt_tokens': (doc.get('usage') or {}).get('prompt_tokens'),
    }

server = frozen.Server()
raw = {'server_port': server.port, 'server_pid': server.proc.pid, 'requests': []}
try:
    status, props, _ = frozen.http(server.port, 'GET', '/props', None)
    raw['props_status'] = status
    raw['props'] = json.loads(props)
    for label, request in probes:
        status, body, headers = frozen.http(server.port, 'POST', '/v1/chat/completions', request)
        (OUT / (label + '-body.txt')).write_bytes(body)
        newest = server.newest()
        text = body.decode('utf-8')
        data_lines = [line[6:] for line in text.splitlines() if line.startswith('data: ')]
        frames = [json.loads(line) for line in data_lines if line.strip() != '[DONE]']
        doc = json.loads(text) if not data_lines else None
        summary = {
            'label': label, 'status': status,
            'content_type': headers.get('Content-Type'),
            'slot_task': newest.get('id_task'),
            'user_in_slot_params': 'user' in newest.get('params', {}),
            'sse': bool(frames) and any(line.strip() == '[DONE]' for line in data_lines),
            'usage_frames': sum(1 for fr in frames if isinstance(fr, dict) and fr.get('usage')),
            'n_choices': len(doc.get('choices') or []) if doc else None,
        }
        raw['requests'].append({
            'label': label, 'request': request, 'status': status,
            'headers': headers, 'body': text, 'slot': newest,
            'summary': summary, 'normalized': shape(doc) if doc else None,
        })
        print(json.dumps(summary, sort_keys=True))
    base_record = raw['requests'][0]
    for record in raw['requests'][1:4]:
        b = base_record['slot']['params']
        r = record['slot']['params']
        delta = sorted(k for k in set(b) | set(r) if k not in b or k not in r or b[k] != r[k])
        record['slot_delta_keys_exact'] = delta
        record['normalized_equal_base'] = record['normalized'] == base_record['normalized']
        record['messages_equal_base'] = [c.get('message') for c in record['body'] and json.loads(record['body']).get('choices', [])] == [c.get('message') for c in json.loads(base_record['body']).get('choices', [])]
        print(json.dumps({'label': record['label'], 'slot_delta_keys_exact': delta,
                          'normalized_equal_base': record['normalized_equal_base'],
                          'messages_equal_base': record['messages_equal_base']}, sort_keys=True))
finally:
    (OUT / 'probe-raw.json').write_text(json.dumps(raw, indent=2) + '\n')
    shutil.copyfile(server.log, OUT / 'probe-server.log')
    server.close()
