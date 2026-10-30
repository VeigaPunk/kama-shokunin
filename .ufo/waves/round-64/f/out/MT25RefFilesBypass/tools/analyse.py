#!/usr/bin/env python3
"""MT25: summarise variant results and the (d) window against the counter's raw times."""
import json
import os

OUT = '/fast/scratch/hyaku/kama-r64/f/MT25RefFilesBypass/h/out/variants'
rows = []
for name in [d for d in sorted(os.listdir(OUT)) if d.startswith('V')]:
    d = os.path.join(OUT, name)
    hj = os.path.join(d, 'harness.json')
    if not os.path.exists(hj):
        continue
    r = (json.load(open(hj)) or [{}])[0]
    ev = {}
    if os.path.exists(os.path.join(d, 'evidence.json')):
        ev = json.load(open(os.path.join(d, 'evidence.json')))
    rows.append((name, r, ev))
    met = r.get('met')
    fails = r.get('fails')
    print('%-32s met=%s fails=%s err=%s' % (name, met, fails, r.get('error')))
    if 'after_hold' in ev and 'dlopen' in ev.get('after_hold', {}) or 'inject_lib' in ev.get('after_hold', {}):
        ah = ev['after_hold']
        raw_a = r.get('raw_a_ns')
        raw_b = r.get('raw_b_ns')
        t_hold = ah.get('hold_json_ns')
        t_inj = ah.get('inject_ns_before')
        t_inj_after = ah.get('inject_ns_after')
        pos = ('before raw_a' if t_inj < raw_a else
               'between raw_a and raw_b' if t_inj < raw_b else 'after raw_b')
        print('      hold.json->raw_a=%.0f ms  raw_a->raw_b=%.0f ms  inject@%s '
              '(%.0f ms after hold.json, handle=%s): %s' %
              ((raw_a - t_hold) / 1e6, (raw_b - raw_a) / 1e6, name,
               (t_inj - t_hold) / 1e6, ah.get('handle'), pos))
    if 'rewrite_pre' in ev:
        print('      pre-hold rewrite: restore=%s sha_in_hold=%s' %
              (ev['rewrite_pre']['restore'], ev['rewrite_pre']['sha_in_hold'][:12]))
    if 'rewrite_post' in ev:
        print('      post-release rewrite: restore=%s sha_in_post=%s' %
              (ev['rewrite_post']['restore'], ev['rewrite_post']['sha_in_post'][:12]))
    if 'wrap_argv' in ev:
        print('      wrap argv head: %s' % ev['wrap_argv'])
with open(os.path.join(OUT, 'analysis.json'), 'w') as f:
    json.dump([{'variant': n, 'met': r.get('met'), 'fails': r.get('fails'),
                'error': r.get('error'), 'evidence': e} for n, r, e in rows],
              f, indent=1)
