#!/usr/bin/env python3
"""M11C2AttackBinding — binding-family attack on the r62 C2 counter.

Loads the frozen master counter module from the exact scratch copy
(sha256-verified against `git show master:tools/round62-c2-counter.py`),
reproduces score()/parse_registry() exactly as the counter uses them, and
scores pristine + binding-mutated registry texts with a green-run stub
scorer (verdict True, sensitive True, dead False, observed == stored
observation). The stub isolates the binding check: any met_equivalent
change is attributable to binding acceptance alone.
"""
import hashlib
import importlib.util
import json
import os

SCRATCH = os.path.dirname(os.path.abspath(__file__))
COUNTER = os.path.join(SCRATCH, 'round62-c2-counter.py')
REG_PATH = os.path.join(SCRATCH, 'capability-claims-r62.tsv')

for label, path in (('counter', COUNTER), ('registry', REG_PATH)):
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    print(f'sha256[{label}] = {h}')

spec = importlib.util.spec_from_file_location('c2counter', COUNTER)
c2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2)

with open(REG_PATH, encoding='utf-8') as f:
    PRISTINE = f.read()


def green(row):
    return (True, row.get('observed', ''), True, False)


def met_eq(facts):
    return (facts['covered'] == facts['population']
            and facts['mismatches'] == 0 and facts['errors'] == 0
            and facts['dead'] == 0 and facts['bound'] >= facts['population'])


def set_binding(text, cap, new_binding):
    out, hit = [], 0
    for ln in text.splitlines():
        cells = ln.split('\t')
        if cells and cells[0] == cap:
            assert len(cells) == 8, ln
            cells[2] = new_binding          # COLS: cap quote binding run ...
            ln = '\t'.join(cells)
            hit += 1
        out.append(ln)
    assert hit == 1, (cap, hit)
    return '\n'.join(out) + '\n'


def pad_all_bindings(text, pad=' '):
    out = []
    for ln in text.splitlines():
        cells = ln.split('\t')
        if len(cells) == 8 and cells[0] != 'cap':
            cells[2] = pad + cells[2] + pad
            ln = '\t'.join(cells)
        out.append(ln)
    return '\n'.join(out) + '\n'


VARIANTS = [
    ('pristine',                  'live-ollama-lifecycle', 'live'),
    ('case-LIVE',                 'live-ollama-lifecycle', 'LIVE'),
    ('case-Live',                 'live-ollama-lifecycle', 'Live'),
    ('case-lIvE',                 'live-ollama-lifecycle', 'lIvE'),
    ('case-Selftest-pin-watch',   'pin-watch',             'Selftest'),
    ('case-Scan-digest-ledger',   'digest-ledger',         'Scan'),
    ('case-CENSUS-sources',       'sources-registry',      'CENSUS'),
    ('ws-both',                   'live-ollama-lifecycle', ' live '),
    ('ws-lead',                   'live-ollama-lifecycle', ' live'),
    ('ws-trail',                  'live-ollama-lifecycle', 'live '),
    ('ws-double',                 'live-ollama-lifecycle', '  live  '),
    ('ws-internal',               'live-ollama-lifecycle', 'li ve'),
    ('ws-nbsp',                   'live-ollama-lifecycle', 'live\xa0'),
    ('zwsp-trail',                'live-ollama-lifecycle', 'live\u200b'),
    ('ws-lead-digest-ledger',     'digest-ledger',         ' scan'),
    ('cross-selftest-on-sources', 'sources-registry',      'selftest'),
    ('cross-live-on-scan',        'digest-ledger',         'live'),
    ('unallowed-free',            'live-ollama-lifecycle', 'free'),
    ('unallowed-empty',           'live-ollama-lifecycle', ''),
    ('notobs-one-row',            'live-ollama-lifecycle', 'notobs'),
    ('ws-all-padded',             None,                    None),
]

results = []
for name, cap, binding in VARIANTS:
    if name == 'pristine':
        text = PRISTINE
    elif name == 'ws-all-padded':
        text = pad_all_bindings(PRISTINE)
    else:
        text = set_binding(PRISTINE, cap, binding)
    facts = c2.score(text, green)
    met = met_eq(facts)
    results.append({
        'variant': name, 'cap': cap, 'binding': repr(binding),
        'met_equivalent': met,
        'verdict': 'ACCEPTED' if met else 'REJECTED',
        'covered': facts['covered'], 'population': facts['population'],
        'bound': facts['bound'], 'errors': facts['errors'],
        'mismatches': facts['mismatches'], 'dead': facts['dead'],
        'err_list': facts['err_list'][:4],
        'mutated_row': next((l for l in text.splitlines()
                             if cap and l.split('\t')[0] == cap), None),
    })
    tail = f"  [{facts['err_list'][:2]}]" if facts['err_list'] else ''
    print(f"{name:28s} binding={binding!r:14s} -> "
          f"covered={facts['covered']}/{facts['population']} "
          f"bound={facts['bound']} errors={facts['errors']} "
          f"mismatches={facts['mismatches']} dead={facts['dead']} "
          f"{'ACCEPTED' if met else 'REJECTED'}{tail}")

# Fixture bytes for the end-to-end single-row whitespace mutant.
with open(os.path.join(SCRATCH, 'registry-ws-both.tsv'), 'w',
          encoding='utf-8') as f:
    f.write(set_binding(PRISTINE, 'live-ollama-lifecycle', ' live '))
# Aggregate padded registry (scoring-layer only).
with open(os.path.join(SCRATCH, 'registry-ws-all-padded.tsv'), 'w',
          encoding='utf-8') as f:
    f.write(pad_all_bindings(PRISTINE))
with open(os.path.join(SCRATCH, 'c2-matrix.json'), 'w',
          encoding='utf-8') as f:
    json.dump(results, f, indent=1, ensure_ascii=False)

print('\nsanity:')
rows, errs = c2.parse_registry(PRISTINE)
print('pristine parse: rows =', len(rows), 'errors =', errs)
print('pristine bindings =', sorted({r['binding'] for r in rows}))
print('population =', len(c2._MANIFEST), 'MIN_ROWS =', c2.MIN_ROWS)
for slug in c2.MANIFEST:
    print(f"allowed_ids[{slug}] = {sorted(c2.allowed_ids(slug))}")
