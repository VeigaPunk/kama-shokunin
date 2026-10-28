#!/usr/bin/env python3
"""Attack (a): how often do the two draw_probes() requests collide in the
reference server's answers, and does a replayed probe-1 answer pass as probe 2?

Uses the committed counter module's own draw_probes / reference_run /
probe_fails (imported from the scratch clone, read-only use). One fresh pinned
reference server per seed, as the counter does, so the numbers are the
counter's own behaviour, not a re-implementation.
"""
import concurrent.futures as cf
import importlib.util
import json
import os
import random
import sys

CLONE = sys.argv[1]
OUT = sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 200
WORKERS = int(sys.argv[4]) if len(sys.argv) > 4 else 4

spec = importlib.util.spec_from_file_location(
    'c1', os.path.join(CLONE, 'tools', 'round64-c1-counter.py'))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

server = C.pick_server()
model = os.path.realpath(os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf'))
assert server and C.sha256_path(model) == C.MODEL_SHA

base = os.path.join(OUT, 'per-seed')
os.makedirs(base, exist_ok=True)


def one(seed):
    rng = random.Random(seed)
    nonce = f'r64p{seed:04d}x'
    reqs = C.draw_probes(rng, nonce)
    wd = os.path.join(base, f's{seed:03d}')
    os.makedirs(wd, exist_ok=True)
    ref = C.reference_run(server, model, reqs, wd)
    rec = {'seed': seed, 'k': [len(r['prompt'].split()) - 1 for r in reqs],
           'n': [r['n_predict'] for r in reqs], 'ok': len(ref) == 2}
    if len(ref) != 2 or not all(isinstance(r, dict) for r in ref):
        return rec
    t0, t1 = ref[0].get('text'), ref[1].get('text')
    rec['text0'], rec['text1'] = t0, t1
    rec['text_equal'] = t0 == t1
    rec['usage'] = [[r.get('usage_prompt_tokens'),
                     r.get('usage_completion_tokens')] for r in ref]
    rec['usage_equal'] = rec['usage'][0] == rec['usage'][1]
    rec['joint_equal'] = rec['text_equal'] and rec['usage_equal']
    # replay: probe-1's full server answer, with the counter-owned fields
    # (sent_prompt, n_predict) of probe 2, scored against the reference of
    # probe 2 at index 1, exactly as the counter's probe_fails does.
    replay = dict(ref[0])
    replay['sent_prompt'] = json.loads(json.dumps(ref[1].get('sent_prompt')))
    replay['n_predict'] = reqs[1]['n_predict']
    f = C.probe_fails(replay, ref, 1)
    rec['replay_fails'] = sorted(f)
    rec['replay_passes'] = not (f & {'live_ref_text', 'live_ref_usage'})
    rec['replay_passes_all'] = not f
    return rec


rows = []
with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for r in ex.map(one, range(N)):
        rows.append(r)
with open(os.path.join(OUT, 'draw_probes_collisions.jsonl'), 'w') as fh:
    for r in rows:
        fh.write(json.dumps(r) + '\n')

ok = [r for r in rows if r['ok']]
summ = {
    'seeds': N, 'reference_ok': len(ok),
    'text_equal': sum(r['text_equal'] for r in ok),
    'usage_equal': sum(r['usage_equal'] for r in ok),
    'joint_text_and_usage_equal': sum(r['joint_equal'] for r in ok),
    'replay_passes_refchecks': sum(r['replay_passes'] for r in ok),
    'replay_passes_all_checks': sum(r['replay_passes_all'] for r in ok),
    'distinct_text0': len({r['text0'] for r in ok}),
    'distinct_text1': len({r['text1'] for r in ok}),
    'empty_text0': sum(1 for r in ok if not r['text0']),
    'top_texts': sorted(
        {t: sum(1 for r in ok if r['text0'] == t or r['text1'] == t)
         for t in {r['text0'] for r in ok} | {r['text1'] for r in ok}}.items(),
        key=lambda kv: -kv[1])[:8],
}
with open(os.path.join(OUT, 'summary.json'), 'w') as fh:
    json.dump(summ, fh, indent=1, ensure_ascii=False)
print(json.dumps(summ, ensure_ascii=False))
