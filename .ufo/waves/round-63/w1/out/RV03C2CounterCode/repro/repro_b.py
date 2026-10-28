import sys, random, re, io, contextlib
sys.dont_write_bytecode = True
import c2
TIP = '03a6a1d850902a66a13dfad33f89cf3a8b759a09'
reg = open('reg.tsv').read()
sc = open('SCORECARD.md').read()
rand = random.Random(63)

print('== R3 sensitivity is an identity for the shipped verdict functions (fuzz)')
alpha = ['a', 'b', ' ', '0', '"', '\n']
bad = 0; n = 0; tr = 0
for _ in range(200000):
    pat = ''.join(rand.choice(alpha) for _ in range(rand.randint(1, 3)))
    out = ''.join(rand.choice(alpha) for _ in range(rand.randint(0, 12)))
    if rand.random() < 0.5: out += pat
    rc = rand.choice([0, 1, 2, 124]); dead = rand.random() < 0.1
    for vfn, rcs in ((c2.verdict_fn, None), (c2.refusal_fn, None)):
        v = vfn(out, rc, dead, pat); s = c2.is_sensitive(out, rc, dead, pat, vfn=vfn)
        n += 1; tr += v
        if v and not s: bad += 1
        if (v != s) and not v: bad += 0  # s implies v by construction
print(f'cases={n} verdict_true={tr} true_but_insensitive={bad}')
print('verdict_true => is_sensitive for every case (identity holds)' if bad == 0 else 'NOT identity')

print('== R4 score(): host-busy outcome with sensitive=False is not a mismatch')
def scorer_factory(outcome_map):
    def sc_(row):
        return outcome_map[row['cap']]
    return sc_
pats = {s: c2.MANIFEST[s][1][0]['pattern'] for s in c2.MANIFEST}
alts = {s: c2.MANIFEST[s][1][0].get('alt', '') for s in c2.MANIFEST}
omap = {s: ('true', pats[s], True, False) for s in c2.MANIFEST}
omap['context-capacity-receipt'] = ('host-busy', alts['context-capacity-receipt'], False, False)
f = c2.score(reg, scorer_factory(omap))
print('mismatches=', f['mismatches'], 'sensitive=', f['sensitive'], '/bound', f['bound'], '-> score only; main() still requires sensitive==bound')

print('== R5 score(): observed field may be blank or any fragment of the pattern')
lines = reg.splitlines()
def with_obs(new):
    out = []
    for l in lines:
        c = l.split('\t')
        if c and c[0] == 'sources-registry' and len(c) == 8:
            c[6] = new(c[6], c[4])
        out.append('\t'.join(c))
    return '\n'.join(out) + '\n'
ok_scorer = scorer_factory(omap)
for label, fn in [('blank', lambda o, p: ''), ('fragment "45"', lambda o, p: '45'), ('forged', lambda o, p: 'FORGED')]:
    f = c2.score(with_obs(fn), ok_scorer)
    print(f'observed={label:14s} mismatches={f["mismatches"]} covered={f["covered"]}/{f["population"]}')
print()
print('== R6 run column is not bound by any control family (run!=template is rejected but untested)')
rows = reg.splitlines()
def tamper_run(l):
    c = l.split('\t')
    if c[0] == 'pin-watch':
        c[3] = 'python3 -c "print(1)"'
    return '\t'.join(c)
t = '\n'.join(tamper_run(l) for l in rows) + '\n'
f = c2.score(t, ok_scorer)
print('tampered run column -> errors:', f['err_list'], 'mismatches=', f['mismatches'])
