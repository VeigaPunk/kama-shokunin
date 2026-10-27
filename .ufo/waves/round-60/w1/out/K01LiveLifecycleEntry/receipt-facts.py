#!/usr/bin/env python3
"""Read the committed round-60 live receipt and print every value the knowledge
entry quotes, so each quoted number has a counting command.

Usage: python3 .ufo/waves/round-60/w1/out/K01LiveLifecycleEntry/receipt-facts.py [RECEIPT]
Default RECEIPT is .ufo/waves/round-60/live/receipt.json (lane-root relative).
Read-only: opens the receipt, prints lines, writes nothing.
"""
import datetime
import json
import sys

p = sys.argv[1] if len(sys.argv) > 1 else '.ufo/waves/round-60/live/receipt.json'
d = json.load(open(p, encoding='utf-8'))

print('schema', d['schema'], 'verdict', d['verdict'])
print('checks', len(d['checks']),
      'evaluated_true', sum(1 for c in d['checks'] if c['evaluated'] and c['passed']),
      'failed', sum(1 for c in d['checks'] if c['evaluated'] and not c['passed']))
print('captures', len(d['captures']), sorted(d['captures']))
print('nonce', d['nonce'], 'port', d['port'], 'elapsed_s', d['elapsed_s'])
print('teardown returncode', d['teardown']['returncode'],
      'sigkill_needed', d['teardown']['sigkill_needed'],
      'port_closed', d['teardown']['port_closed'])
print('observations', json.dumps(d['observations'], sort_keys=True))
for k in ('root', 'version', 'tags-empty', 'ps-before', 'v1-models-empty',
          'v1-models', 'v1-model-single'):
    c = d['captures'][k]
    print(k, c['status'], c['sha256'], repr(c['body']))
gen = json.loads(d['captures']['generate']['body'])
ps = json.loads(d['captures']['ps-after']['body'])['models'][0]
tags = json.loads(d['captures']['tags']['body'])['models'][0]
show = json.loads(d['captures']['show']['body'])
print('generate_keys', sorted(gen))
print('generate_created_at', gen['created_at'], 'ps_expires_at', ps['expires_at'])
ct = datetime.datetime.fromisoformat(gen['created_at'].replace('Z', '+00:00'))
ex = datetime.datetime.fromisoformat(ps['expires_at'])
print('expires_minus_created_s', (ex - ct).total_seconds())
print('tags_size', tags['size'], 'ps_size', ps['size'], 'sizes_equal', tags['size'] == ps['size'])
print('tags_digest', tags['digest'])
print('ps_digest', ps['digest'], 'digests_equal', tags['digest'] == ps['digest'])
print('ps_size_vram', ps['size_vram'], 'ps_context_length', ps['context_length'], 'ps_runner', ps['runner'])
print('tags_details', json.dumps(tags['details'], sort_keys=True))
print('show_from', [l for l in show['modelfile'].split('\n') if l.startswith('FROM ')])
print('show_param_count', show['model_info']['general.parameter_count'],
      'show_context_length', show['model_info']['llama.context_length'])
print('v1_created', json.loads(d['captures']['v1-models']['body'])['data'][0]['created'],
      'owned_by', json.loads(d['captures']['v1-models']['body'])['data'][0]['owned_by'])
