#!/usr/bin/env python3
"""Attack (a), pairwise: over many draw_probes()-distributed prompts answered
by the pinned reference server (the counter's own reference_run), count the
probe PAIRS whose (n_predict, answer text, prompt tokens, completion tokens)
collide. A replay of one answer passes the reference checks for a pair only
if the pair collides on text AND usage; the counter's probe_fails also needs
the counter-owned n_predict to admit the replayed completion length.

Pairs are formed over all candidate pairs (i<j), i.e. the per-run collision
rate of two independently drawn probes under the counter's distribution.
"""
import collections
import concurrent.futures as cf
import importlib.util
import itertools
import json
import os
import random
import sys

CLONE, OUT = sys.argv[1], sys.argv[2]
N = int(sys.argv[3])
WORKERS = int(sys.argv[4]) if len(sys.argv) > 4 else 4

spec = importlib.util.spec_from_file_location(
    'c1', os.path.join(CLONE, 'tools', 'round64-c1-counter.py'))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
server = C.pick_server()
model = os.path.realpath(os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf'))
base = os.path.join(OUT, 'cand')
os.makedirs(base, exist_ok=True)


def one(i):
    rng = random.Random(10_000 + i)
    req = C.draw_probes(rng, f'r64q{i:05d}')[0]
    wd = os.path.join(base, f'c{i:05d}')
    os.makedirs(wd, exist_ok=True)
    ref = C.reference_run(server, model, [req], wd)
    if len(ref) != 1 or not isinstance(ref[0], dict):
        return None
    r = ref[0]
    return {'i': i, 'n': req['n_predict'], 'text': r.get('text'),
            'ptok': r.get('usage_prompt_tokens'),
            'ctok': r.get('usage_completion_tokens'),
            'finish': r.get('finish_reason'), 'prompt': req['prompt']}


with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
    cands = [c for c in ex.map(one, range(N)) if c]
with open(os.path.join(OUT, 'candidates.jsonl'), 'w') as fh:
    for c in cands:
        fh.write(json.dumps(c, ensure_ascii=False) + '\n')

pairs = list(itertools.combinations(cands, 2))
txt_eq = sum(1 for a, b in pairs if a['text'] == b['text'])
n_eq = sum(1 for a, b in pairs if a['n'] == b['n'])
joint = [(a, b) for a, b in pairs
         if a['text'] == b['text'] and a['ptok'] == b['ptok']
         and a['ctok'] == b['ctok']]
joint_same_n = [(a, b) for a, b in joint if a['n'] == b['n']]
ex_pairs = [{'a': {k: a[k] for k in ('i', 'n', 'text', 'ptok', 'ctok')},
             'b': {k: b[k] for k in ('i', 'n', 'text', 'ptok', 'ctok')}}
            for a, b in joint[:20]]
summ = {
    'candidates': len(cands), 'pairs': len(pairs),
    'pairs_text_equal': txt_eq,
    'pairs_n_equal': n_eq,
    'pairs_text_and_usage_equal': len(joint),
    'pairs_text_usage_and_n_equal': len(joint_same_n),
    'rate_text_and_usage_equal': len(joint) / len(pairs),
    'examples': ex_pairs,
}
with open(os.path.join(OUT, 'pair_summary.json'), 'w') as fh:
    json.dump(summ, fh, indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in summ.items() if k != 'examples'},
                 ensure_ascii=False))
print(json.dumps(ex_pairs[:3], ensure_ascii=False))
