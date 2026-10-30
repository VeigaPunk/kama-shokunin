#!/usr/bin/env python3
"""MT34RegressLogic: per-row driver for registry/capability-regress-r64.tsv.

For each of the 12 rows: build a scratch copy of the tip tree with the
row's one-line regression applied, run the row's OWN run template on it
and on the unmutated tip tree, and record rc + stdout so the flip can be
attributed to a reason (not an interpreter break).

The run templates, the placeholder expansion, the environment allowlist
and the verdict classifier are the counter's own (imported from the
clone's tools/round64-c2-counter.py), so what is measured here is what
the counter measures.

Usage: driver.py <clone> <tip> <work> <out.json>
"""
import importlib.util
import json
import os
import sys

clone, tip, work, outp = sys.argv[1:5]

spec = importlib.util.spec_from_file_location(
    'c2', os.path.join(clone, 'tools', 'round64-c2-counter.py'))
c2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2)

os.makedirs(work, exist_ok=True)
tip_tree = c2.checkout_tip(clone, tip, work)
if not tip_tree:
    print('tip checkout failed', file=sys.stderr)
    sys.exit(1)

runner = c2.Runner(clone, tip, work, tip_tree)
rtext = c2.blob(clone, tip, c2.REGRESS)
rows, rerrs = c2.parse_regress(rtext)
by_cap = {r['cap']: r for r in rows}


def run_one(cap):
    spec_s = c2.SPECS[cap]
    row = by_cap.get(cap)
    rec = {'cap': cap, 'tool': spec_s['tool'], 'pattern': spec_s['pattern'],
           'eol': spec_s['eol'], 'find': row['find'] if row else None,
           'replace': row['replace'] if row else None}
    # unmutated
    base = runner.run(cap, 'tip', tip_tree)
    rec['base'] = {'rc': base['rc'], 'secs': base['secs'],
                   'outcome': c2.classify(spec_s, base)[0],
                   'reason': c2.classify(spec_s, base)[1],
                   'out': base['out'][-4000:]}
    # regressed
    data, tag = c2.apply_regression(c2.blob_bytes(clone, tip, spec_s['tool']),
                                    row['find'], row['replace'])
    rec['apply_tag'] = tag
    if data is None:
        rec['reg'] = {'rc': None, 'outcome': None, 'reason': tag,
                      'out': ''}
        return rec
    tree = runner.overlay('reg-' + cap, {spec_s['tool']: data})
    r = runner.run(cap, 'reg', tree)
    oc, why = c2.classify(spec_s, r)
    rec['reg'] = {'rc': r['rc'], 'secs': r['secs'], 'outcome': oc,
                  'reason': why, 'out': r['out'][-4000:]}
    rec['flip_status'] = c2.flip_status(spec_s, rec['base']['outcome'], oc)
    return rec


out = []
with c2.ThreadPoolExecutor(max_workers=4) as pool:
    futs = [pool.submit(run_one, cap) for cap in c2.SLUGS]
    for f in futs:
        out.append(f.result())

with open(outp, 'w') as fh:
    json.dump({'rows': out, 'rerrs': rerrs}, fh, indent=1)
print('wrote', outp)
for rec in out:
    print(rec['cap'], 'base=', rec['base']['outcome'], 'reg=',
          rec['reg']['outcome'], 'flip=', rec.get('flip_status'),
          'rc=', rec['reg']['rc'])
