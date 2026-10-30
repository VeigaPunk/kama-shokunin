#!/usr/bin/env python3
"""MT34RegressLogic probe: exercise the C2 counter's OWN flip accounting on
the three conditions the seat asks about, using the counter's own functions
(imported from the pristine clone), pristine vs each mutant.

Conditions:
  A. a regression whose mutated source does not compile
  B. a regression whose verdict is unchanged
  C. a regressed run that timed out (rc=124)

Usage: probe.py <clone> <tip>
"""
import hashlib
import importlib.util
import os
import sys

clone, tip = sys.argv[1], sys.argv[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pristine = load('c2p', os.path.join(clone, 'tools', 'round64-c2-counter.py'))
mut_dir = os.path.join(clone, 'tools', 'mutants')
mutants = {}
for m in ('m1', 'm2', 'm3'):
    p = os.path.join(mut_dir, m + '.py')
    if os.path.exists(p):
        mutants[m] = load('c2' + m, p)


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def probe(c2, label):
    out = {}
    # A: a regression that does not compile -> apply_regression tags it
    src = c2.blob_bytes(clone, tip, 'tools/pin-watch.py')
    data, tag = c2.apply_regression(src, 'def (', 'def (')
    # the counter's own accounting: plan tag -> flip
    st = tag if data is None else c2.flip_status(
        c2.SPECS['pin-watch'], 'true', 'false')
    out['A_tag'] = tag
    out['A_flip_credited'] = (st == 'flipped')
    # B: verdict unchanged
    out['B_flip_credited'] = (c2.flip_status(c2.SPECS['pin-watch'], 'true',
                                              'true') == 'flipped')
    # C: a regressed run that timed out
    run = {'out': 'partial output\nTIMEOUT', 'rc': 124, 'dead': False,
           'before': set(), 'after': set(), 'receipt': None,
           'secs': 900.0}
    oc, why = c2.classify(c2.SPECS['pin-watch'], run)
    out['C_outcome'] = oc
    out['C_reason'] = why
    out['C_flip_credited'] = (c2.flip_status(c2.SPECS['pin-watch'], 'true',
                                             oc) == 'flipped')
    # C-ctx (the row with a second declared outcome)
    run2 = dict(run, receipt=None)
    oc2, why2 = c2.classify(c2.SPECS[c2.CTX], run2)
    out['C_ctx_outcome'] = oc2
    out['C_ctx_flip_credited'] = (
        c2.flip_status(c2.SPECS[c2.CTX], 'host-busy', oc2) == 'flipped')
    print(label, out)
    return out


print('## pristine counter sha256:', sha(os.path.join(
    clone, 'tools', 'round64-c2-counter.py')))
for m, mod in mutants.items():
    print('## mutant %s sha256: %s' % (m, sha(os.path.join(mut_dir, m + '.py'))))
print()
res = {'pristine': probe(pristine, 'pristine')}
for m, mod in mutants.items():
    res[m] = probe(mod, m)
print()
print('SUMMARY')
for k, v in res.items():
    print('%-9s A_flip_credited=%-5s B_flip_credited=%-5s C_outcome=%-8s '
          'C_flip_credited=%-5s' % (k, v['A_flip_credited'],
                                     v['B_flip_credited'], v['C_outcome'],
                                     v['C_flip_credited']))
