#!/usr/bin/env python3
"""E06 supplement: same two forgeries as fixtures (b) and (c), but with the
stored checks rewritten truthfully from grade() so the receipt is internally
self-consistent; only the verdict is fabricated.  This isolates "rejected by
recomputation" from "rejected by stored-vs-recomputed disagreement".
"""
import importlib.util
import json
import os
import sys

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
W = '/fast/scratch/hyaku/kama-r62/w/E06FixtureForgery'


def load_counter():
    spec = importlib.util.spec_from_file_location(
        'r62c1', os.path.join(LANE, 'tools', 'round62-c1-counter.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def consistent(mod, receipt):
    recomputed, _ = mod.grade(receipt)
    for name, v in receipt['checks'].items():
        if name in recomputed and recomputed[name] is not None:
            v['passed'] = recomputed[name]
    return receipt


def main():
    mod = load_counter()
    base = json.load(open(os.path.join(W, 'receipt.json')))
    wit = json.load(open(os.path.join(W, 'witness.json')))
    witness = wit['witness']
    mod.NONCE = wit['nonce']
    out = {}

    # b': bodies re-ordered across keys, checks truthful, verdict forged
    import copy
    b = copy.deepcopy(base)
    h, m = b['captures']['health'], b['captures']['models']
    h['body'], m['body'] = m['body'], h['body']
    for c in (h, m):
        c['body_sha256'] = __import__('hashlib').sha256(
            c['body'].encode()).hexdigest()
    b['verdict'] = 'REQUEST_OK'
    consistent(mod, b)
    json.dump(b, open(os.path.join(W, 'b2_reordered_consistent.json'), 'w'),
              indent=1, sort_keys=True)
    s = mod.score(b, witness)
    out['b2_capture_bodies_reordered_consistent_record'] = {
        'accepted': s['met'], 'score': s,
        'inconsistent': s['inconsistent']}

    # c': nonce matches, alias differs on every surface, checks truthful
    c = copy.deepcopy(base)
    other = 'kama-completion-other'
    import re
    for key in ('completion', 'completion2'):
        cap = c['captures'][key]
        cap['body'] = re.sub(r'"model"\s*:\s*"[^"]*"',
                             f'"model": "{other}"', cap['body'])
        cap['body_sha256'] = __import__('hashlib').sha256(
            cap['body'].encode()).hexdigest()
    mm = c['captures']['models']
    mm['body'] = json.dumps({'object': 'list', 'data': [
        {'id': other, 'object': 'model', 'owned_by': 'llamacpp'}]},
        separators=(',', ':'))
    mm['body_sha256'] = __import__('hashlib').sha256(
        mm['body'].encode()).hexdigest()
    pp = c['captures']['props']
    pp['body'] = json.dumps({'model_alias': other}, separators=(',', ':'))
    pp['body_sha256'] = __import__('hashlib').sha256(
        pp['body'].encode()).hexdigest()
    c['verdict'] = 'REQUEST_OK'
    consistent(mod, c)
    json.dump(c, open(os.path.join(W, 'c2_alias_differs_consistent.json'), 'w'),
              indent=1, sort_keys=True)
    s = mod.score(c, witness)
    out['c2_nonce_matches_alias_differs_consistent_record'] = {
        'accepted': s['met'], 'score': s,
        'inconsistent': s['inconsistent']}

    json.dump(out, open(os.path.join(W, 'consistent-results.json'), 'w'),
              indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
