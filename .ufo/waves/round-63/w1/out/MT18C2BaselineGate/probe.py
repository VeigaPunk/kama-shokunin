import os, sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, os.environ['PROBE_DIR'])
import counter_t1 as C
repo, tip, work = os.environ['PROBE_REPO'], os.environ['PROBE_TIP'], os.environ['PROBE_WORK']
os.makedirs(work, exist_ok=True)
scratch = os.path.join(work, 'run'); os.makedirs(scratch, exist_ok=True)
env = {k: v for k, v in os.environ.items() if k in C.ENV_KEYS}; env['TMPDIR'] = scratch
tip_tree = C.checkout_tip(repo, tip, work)
sc = C.blob(repo, tip, 'SCORECARD.md')
can_n, can_rows, canon_mismatch = C.canon_problems(sc)
population = [(s, C.MANIFEST[s][0]) for s, _, _ in C._MANIFEST]
reg = C.blob(repo, tip, C.REG)
facts = C.score_registry(reg, tip_tree, scratch, repo, tip, env, population=population)
print('facts', {k: facts[k] for k in ('covered','bound','mismatches','errors','dead')}, 'baseline_met=', C.is_met(facts))
rej, total, det = C.controls(reg, tip_tree, scratch, repo, tip, env, population, sc)
print('controls_rejected', rej, '/', total)
for k, v in det.items():
    print('  ', k, 'met=%s hit=%s' % (v['met'], v['hit']), v['tags'])
# no-op control: identical registry bytes, no mutation at all
lines = [l for l in reg.splitlines() if l.strip()]
header = [l for l in lines if l.startswith('cap\t')][0]
data = [l for l in lines if '\t' in l and not l.startswith('cap\t') and not l.startswith('#')]
noop = header + '\n' + '\n'.join(data) + '\n'
f = C.score_registry(noop, tip_tree, scratch, repo, tip, env, population=population)
print('NOOP tags', sorted(f['tags']), 'mismatches', f['mismatches'], 'would hit observed-family (expect mismatch):', 'mismatch' in f['tags'] or f['mismatches']>0)
