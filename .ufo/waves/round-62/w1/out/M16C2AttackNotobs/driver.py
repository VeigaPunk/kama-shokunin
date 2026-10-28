#!/usr/bin/env python3
"""M16C2AttackNotobs — notobs-family attack driver (stub layer).

Imports the byte-verified snapshot of tools/round62-c2-counter.py, builds the
four attack registries, and scores pristine + variants with the REAL score()
and REAL controls() mutant construction; only run_bound is stubbed
(green/sensitive) because notobs rows never execute and the bound rows are
byte-identical to pristine, whose live greenness the end-to-end baseline
establishes. Zero live execution here.
"""
import os
import sys

SC = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(SC, 'fix-base')
FIXREV = '2eeba5e523150076fb7c1b69b545b721b5a66b8a'
SNAP = os.path.join(SC, 'c2-counter-snapshot.py')

sys.dont_write_bytecode = True
import importlib.util
spec = importlib.util.spec_from_file_location('c2', SNAP)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

CAPS16 = {'sources-registry', 'ollama-offline-evidence-replay',
          'live-llamacpp-lifecycle', 'gguf-declared-identity-replay',
          'context-capacity-receipt', 'instrument-agreement'}


def notobs_row(line):
    c = line.split('\t')
    c[2] = 'notobs'
    return '\t'.join(c)


pristine = open(os.path.join(FIX, 'registry/capability-claims-r62.tsv'),
                encoding='utf-8').read()
lines = [l for l in pristine.splitlines() if l.strip()]
header = lines[0]
data = lines[1:]

variants = {}
variants['v1-all-notobs'] = header + '\n' + '\n'.join(
    notobs_row(l) for l in data) + '\n'
variants['v2-some-notobs'] = header + '\n' + '\n'.join(
    notobs_row(l) if l.split('\t')[0] in CAPS16 else l for l in data) + '\n'
variants['v3-some-notobs-plus-dup'] = pristine + '\n'.join(
    notobs_row(l) for l in data if l.split('\t')[0] in CAPS16) + '\n'
variants['v4-all-notobs-plus-dup'] = pristine + '\n'.join(
    notobs_row(l) for l in data) + '\n'

for name, text in variants.items():
    with open(os.path.join(SC, f'reg-{name}.tsv'), 'w', encoding='utf-8') as f:
        f.write(text)

# tip tree via the module's own checkout (fixture archive)
work = os.path.join(SC, 'drv')
tip_tree = m.checkout_tip(FIX, FIXREV, work)
assert tip_tree, 'checkout failed'
scratch = os.path.join(work, 'run')
os.makedirs(scratch, exist_ok=True)
env = dict(os.environ)
env['TMPDIR'] = scratch
env.pop('PYTHONPATH', None)

# canonical checks, replicated from main()
sc_text = open(os.path.join(tip_tree, 'SCORECARD.md'), encoding='utf-8').read()
can_n, can_rows = m.canonical_rows(sc_text)
canon_mismatch = []
population = None
if can_rows:
    slugs = [s for s, _ in can_rows]
    expected = [s for s, _, _ in m._MANIFEST]
    if len(slugs) != len(set(slugs)) or not set(expected).issubset(slugs):
        canon_mismatch.append('canonical dup/missing')
    population = [(slug, m.MANIFEST[slug][0]) for slug in expected]
    for slug, prefix, _ in m._MANIFEST:
        row_text = next((t for s, t in can_rows if s == slug), '')
        if not row_text.startswith(prefix):
            canon_mismatch.append(f'prefix:{slug}')
else:
    canon_mismatch.append('no canonical list section at tip')

# stub executor: green, observed=pattern, sensitive, alive
def stub(row):
    return (True, row['pattern'], True, False)

def stub_score_registry(reg_text, tip_tree, scratch, repo, tip, env,
                        population=None, manifest=m.MANIFEST):
    return m.score(reg_text, stub, manifest=manifest, population=population)

m.score_registry = stub_score_registry  # controls() now scores via stub

print(f'canonical={can_n} canon_mismatch={canon_mismatch} '
      f'population={len(population) if population else None}')
for name in ['pristine'] + list(variants):
    reg_text = pristine if name == 'pristine' else variants[name]
    facts = m.score(reg_text, stub, population=population)
    rejected, total, cdetail = m.controls(
        facts, reg_text, tip_tree, scratch, FIX, FIXREV, env, population)
    met = (bool(can_rows) and not canon_mismatch
           and facts['covered'] == facts['population']
           and facts['bound'] >= facts['population']
           and facts['dead'] == 0 and facts['mismatches'] == 0
           and facts['errors'] == 0 and rejected == total
           and population is not None
           and len(population) == m.MIN_ROWS)
    print(f'\n== {name} ==')
    print(f"population={facts['population']} rows={facts['rows']} "
          f"covered={facts['covered']}/{facts['population']} "
          f"bound={facts['bound']} eval_lines={facts['eval_lines']} "
          f"sensitive={facts['sensitive']}/{facts['bound']} "
          f"dead={facts['dead']} mismatches={facts['mismatches']} "
          f"canonical={can_n} controls_rejected={rejected}/{total} "
          f"errors={facts['errors'] + len(canon_mismatch)} met={met}")
    errs = facts['err_list']
    kinds = {}
    for e in errs:
        k = e.split(':')[0]
        kinds[k] = kinds.get(k, 0) + 1
    print(f"err_list ({len(errs)}): " +
          ', '.join(f'{k}x{n}' for k, n in kinds.items()))
    for k, v in cdetail.items():
        print(f"  family {k}: met={v['met']} covered={v['covered']} "
              f"mismatches={v['mismatches']} errors={v['errors']} "
              f"dead={v['dead']} err_list={v['err_list'][:2]}")
