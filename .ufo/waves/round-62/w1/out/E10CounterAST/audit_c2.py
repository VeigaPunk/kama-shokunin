#!/usr/bin/env python3
"""E10CounterAST row-level C2 audit harness (scratch-only, round 62).

Loads the tip-pinned round62-c2-counter.py as a module, runs its own main()
once under the arm env (so the printed counter line is the real CLI line),
then dumps the per-capability live facts out of the module's execution cache
plus the registry rows, so clean/hostile arms can be diffed row by row.

Usage: python3 audit_c2.py <arm:clean|hostile> <label>
"""
import contextlib
import io
import importlib.util
import json
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TIP = '65d7cad0fce90e34de37527cde22e97b63b118bf'
ARM = sys.argv[1]
LABEL = sys.argv[2]
WORK = os.path.join(S, 'work', LABEL)

HOSTILE = {
    'GIT_DIR': os.path.join(S, 'decoy', '.git'),
    'GIT_WORK_TREE': os.path.join(S, 'decoy'),
    'GIT_WORK_DIR': os.path.join(S, 'decoy'),
    'GIT_INDEX_FILE': os.path.join(S, 'decoy-index'),
}

# arm env: strip every inherited GIT_* var, then inject the hostile set.
os.environ.pop('TMPDIR', None)
for _k in [k for k in os.environ if k.startswith('GIT_')]:
    os.environ.pop(_k)
if ARM == 'hostile':
    os.environ.update(HOSTILE)

spec = importlib.util.spec_from_file_location('c2tip', os.path.join(S, 'bin', 'c2-tip.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

out = io.StringIO()
err = io.StringIO()
with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
    rc = mod.main(['--repo', LANE, '--tip', TIP, '--work', WORK])

tip_tree = os.path.join(WORK, 'tip')
env = dict(os.environ)
env['TMPDIR'] = os.path.join(WORK, 'run')
env.pop('PYTHONPATH', None)

reg_text = mod.blob(LANE, TIP, mod.REG)
rows, perr = mod.parse_registry(reg_text or '')
population = [(slug, mod.MANIFEST[slug][0]) for slug, _, _ in mod._MANIFEST]
facts = mod.score_registry(reg_text or '', tip_tree, os.path.join(WORK, 'run'),
                           LANE, TIP, env, population=population)
canon_n, canon_rows = mod.canonical_rows(mod.blob(LANE, TIP, 'SCORECARD.md'))

live = [{'cap': cap, 'verdict': v[0], 'sensitive': v[2], 'dead': v[3],
         'observed': v[1][:400]} for (t, cap), v in sorted(mod._EXEC_CACHE.items())]

detail = []
for row in rows:
    cap = row['cap']
    fact = next((x for x in live if x['cap'] == cap), None)
    detail.append({
        'cap': cap, 'stored_verdict': row['verdict'],
        'stored_observed': row['observed'],
        'live_verdict': None if fact is None else fact['verdict'],
        'sensitive': None if fact is None else fact['sensitive'],
        'dead': None if fact is None else fact['dead'],
        'observed_head': None if fact is None else fact['observed'],
    })

rec = {
    'arm': ARM, 'label': LABEL, 'rc': rc,
    'stdout': out.getvalue(), 'stderr': err.getvalue(),
    'env_git_vars': sorted(k for k in env if k.startswith('GIT_')),
    'env_git_values': {k: env[k] for k in sorted(env) if k.startswith('GIT_')},
    'facts': {k: v for k, v in facts.items() if k != 'err_list'},
    'err_list': facts['err_list'],
    'canonical': canon_n,
    'canonical_slugs': [s for s, _ in canon_rows],
    'registry_parse_errors': perr,
    'rows': detail,
    'live': live,
}
os.makedirs(os.path.join(S, 'receipts'), exist_ok=True)
p = os.path.join(S, 'receipts', f'c2-rows-{LABEL}.json')
json.dump(rec, open(p, 'w'), indent=1, sort_keys=True)
print(json.dumps({'arm': ARM, 'label': LABEL, 'rc': rc,
                  'stdout': out.getvalue().strip(),
                  'stderr': err.getvalue().strip()[:800]}))
print('receipt:', p)
