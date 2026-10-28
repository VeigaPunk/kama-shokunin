#!/usr/bin/env python3
"""Supplementary probe (E06): a wholly synthetic receipt — no captured bytes
from the graded run — fed to round62 c1 score() with the AUTHENTIC witness
dict from the real lifecycle (saved by forge.py).

Purpose: the three required fixtures mutate a genuine receipt.  This probe
asks the complementary question: is the receipt's captured-body content bound
to the live answer at all?
"""
import importlib.util
import json
import os
import sys

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
W = '/fast/scratch/hyaku/kama-r62/w/E06FixtureForgery'
ALIAS = 'kama-completion-probe'
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'


def sha_b(s):
    return __import__('hashlib').sha256(s.encode()).hexdigest()


def load_counter():
    spec = importlib.util.spec_from_file_location(
        'r62c1', os.path.join(LANE, 'tools', 'round62-c1-counter.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cap(status, body):
    return {'status': status, 'error': None, 'body': body,
            'body_sha256': sha_b(body), 'body_truncated': False}


def main():
    mod = load_counter()
    wit = json.load(open(os.path.join(W, 'witness.json')))
    witness = wit['witness']
    mod.NONCE = wit['nonce']

    # invented completion bytes: shape-valid, text and fingerprint are NOT the
    # served answer recorded in the witness
    comp = json.dumps({
        'object': 'text_completion', 'model': ALIAS,
        'system_fingerprint': 'b11755-cafebabe01234567',
        'choices': [{'text': ' the mat', 'index': 0,
                     'finish_reason': 'length'}],
        'usage': {'prompt_tokens': 5, 'completion_tokens': 3,
                  'total_tokens': 8},
        'timings': {'predicted_n': 3, 'predicted_ms': 12.5},
    }, separators=(',', ':'))
    receipt = {
        'schema': 'kama-completion-live/v1',
        'nonce': wit['nonce'],
        'port': witness['port'],
        'child_pid': witness['pid'],
        'model': {'path': '/invented/models/stories260K.gguf',
                  'sha256': MODEL_SHA},
        'server': {'path': '/invented/llama-server', 'sha256': SERVER_SHA},
        'captures': {
            'health': cap(200, '{"status":"ok"}'),
            'models': cap(200, json.dumps(
                {'object': 'list',
                 'data': [{'id': ALIAS, 'object': 'model',
                           'owned_by': 'llamacpp'}]},
                separators=(',', ':'))),
            'props': cap(200, json.dumps({'model_alias': ALIAS},
                                         separators=(',', ':'))),
            'completion': cap(200, comp),
            'completion2': cap(200, comp),
            'bad_request': cap(400, json.dumps(
                {'error': {'code': 400, 'message': 'bad request'}},
                separators=(',', ':'))),
        },
        'teardown': {'child_pre_dead': False, 'returncode': 0,
                     'port_closed': True},
        'verdict': 'REQUEST_OK',
    }
    tmp = dict(receipt)
    tmp['checks'] = {}
    recomputed, _ = mod.grade(tmp)
    required = sorted(set(recomputed) - {'nonce_match'})
    receipt['checks'] = {n: {'passed': True, 'evaluated': True,
                             'reason': 'synthetic'} for n in required}
    json.dump(receipt, open(os.path.join(W, 'd_synthetic_receipt.json'), 'w'),
              indent=1, sort_keys=True)

    s = mod.score(receipt, witness)
    recomputed, inconsistent = mod.grade(receipt)
    out = {
        'accepted': s['met'],
        'score': s,
        'recomputed_false': sorted(k for k, v in recomputed.items()
                                   if v is not True),
        'inconsistent': inconsistent,
        'witness_text': witness['text'],
        'witness_fingerprint': witness['fingerprint'],
        'receipt_text': ' the mat',
        'receipt_fingerprint': 'b11755-cafebabe01234567',
    }
    json.dump(out, open(os.path.join(W, 'synthetic-results.json'), 'w'),
              indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
