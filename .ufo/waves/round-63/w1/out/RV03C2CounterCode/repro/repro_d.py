import sys, os, importlib.util
sys.dont_write_bytecode = True
TIP = '03a6a1d850902a66a13dfad33f89cf3a8b759a09'
S = '/fast/scratch/hyaku/kama-r63/w/RV03C2CounterCode/h'
exec(open(os.path.join(S, 'repro_c.py')).read().split('results = {}')[0])  # reuse load/mutate/MUTANTS
def seeded(m):
    m._EXEC_CACHE.clear()
    for slug, prefix, runs in m._MANIFEST:
        m._EXEC_CACHE[(TIP, slug)] = (('host-busy', runs[0]['alt'], True, False)
            if slug == 'context-capacity-receipt' else ('true', runs[0]['pattern'], True, False))
    return [(s, m.MANIFEST[s][0]) for s, _, _ in m._MANIFEST]
def baseline(m, regtext, sctext):
    pop = seeded(m)
    # canonical check is per call; use canon_problems for the sc text
    n, rows, probs = m.canon_problems(sctext)
    f = m.score_registry(regtext, '/nonexistent', S, S, TIP, {}, population=pop)
    return dict(reg_met=m.is_met(f), canon_probs=probs[:2], canon_round=n)

# M1: tampered run column on the registry
tampered = '\n'.join(('\t'.join(c[:3] + ['python3 -c "print(1)"'] + c[4:]) if (c := l.split('\t'))[0] == 'pin-watch' else l)
                     for l in reg.splitlines()) + '\n'
for name in ['M0-unmutated', 'M1-drop-run-equality']:
    m = load(name.replace('-', '_'), MUTANTS[name])
    print(f'{name:24s} tampered run column ->', baseline(m, tampered, sc)['reg_met'])

# M2: a frozen canonical row whose prefix is altered
alt_sc = sc.replace('| pin-watch | List upstream release tags', '| pin-watch | List every upstream tag', 1)
assert alt_sc != sc
for name in ['M0-unmutated', 'M2-drop-canon-prefix']:
    m = load(name.replace('-', '_'), MUTANTS[name])
    print(f'{name:24s} altered canonical prefix ->', baseline(m, reg, alt_sc)['canon_probs'])

# M3: the newest canonical list is round 62 (round-63 list removed)
cut = sc.split('**Capabilities — canonical list as of round 63')[0]
cut = cut.split('**Capabilities — canonical list as of round 62')[0] + '**Capabilities — canonical list as of round 62' + sc.split('**Capabilities — canonical list as of round 62')[1].split('**Capabilities — canonical list as of round 63')[0]
if '**Capabilities — canonical list as of round 63' in cut or 'round 63' not in sc.split('canonical list as of round 63')[0][-5:] and False: pass
no63 = sc.split('**Capabilities — canonical list as of round 63')[0]
for name in ['M0-unmutated', 'M3-drop-newest-round']:
    m = load(name.replace('-', '_'), MUTANTS[name])
    b = baseline(m, reg, no63)
    print(f'{name:24s} round-63 list absent (newest=round {b["canon_round"]}) -> reg_met={b["reg_met"]} canon_probs={b["canon_probs"]}')

# M5: sensitivity constant in run_bound (equivalent under the shipped verdict_fn)
import random
m0 = load('M0_unmutated', src0)
print('M5 equivalence: is_sensitive == verdict_fn on verdict-true outputs (checked in repro_b R3)')
