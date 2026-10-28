import sys, os, importlib.util
sys.dont_write_bytecode = True
TIP = '03a6a1d850902a66a13dfad33f89cf3a8b759a09'
S = '/fast/scratch/hyaku/kama-r63/w/RV03C2CounterCode/h'
src0 = open(os.path.join(S, 'c2.py')).read()
reg = open(os.path.join(S, 'reg.tsv')).read()
sc = open(os.path.join(S, 'SCORECARD.md')).read()

def load(name, src):
    p = os.path.join(S, name + '.py'); open(p, 'w').write(src)
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m

def mutate(src, old, new=''):
    assert src.count(old) == 1, ('anchor count', src.count(old), old[:60])
    return src.replace(old, new)

MUTANTS = {
 'M0-unmutated': src0,
 'M1-drop-run-equality': mutate(src0,
   "        if row['run'] != tpl['run']:\n            errs.append(f'run:{cap}')\n            continue\n"),
 'M2-drop-canon-prefix': mutate(src0,
   "        if not row_text.startswith(prefix):\n            probs.append(f'prefix:{slug}')\n"),
 'M3-drop-newest-round': mutate(src0,
   "    if can_n != 63:\n        probs.append(f'newest canonical list is round {can_n}')\n"),
 'M4-drop-observed-check': mutate(src0,
   "        if row['observed'] and row['observed'] not in (want_obs or '') \\\n                and row['observed'] not in observed:\n            facts['mismatches'] += 1\n"),
 'M5-run_bound-sensitive-const': mutate(src0,
   "return ('true', pat, is_sensitive(out, rc, dead, pat), dead)", "return ('true', pat, True, dead)"),
}
results = {}
for name, src in MUTANTS.items():
    m = load(name.replace('-', '_'), src)
    # pre-seed execution results (what the real run produced at the tip)
    m._EXEC_CACHE.clear()
    for slug, prefix, runs in m._MANIFEST:
        pat = runs[0]['pattern']
        if slug == 'context-capacity-receipt':
            m._EXEC_CACHE[(TIP, slug)] = ('host-busy', runs[0]['alt'], True, False)
        else:
            m._EXEC_CACHE[(TIP, slug)] = ('true', pat, True, False)
    pop = [(s, m.MANIFEST[s][0]) for s, _, _ in m._MANIFEST]
    f = m.score_registry(reg, '/nonexistent', S, S, TIP, {}, population=pop)
    base = m.is_met(f)
    rej, tot, det = m.controls(reg, '/nonexistent', S, S, TIP, {}, pop, sc)
    escapes = sorted(k for k, v in det.items() if not v['hit'])
    results[name] = (base, rej, tot, escapes)
    print(f'{name:30s} baseline_met={base} controls_rejected={rej}/{tot} escapes={escapes}')
