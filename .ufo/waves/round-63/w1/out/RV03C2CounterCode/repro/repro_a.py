import os, sys, subprocess, shutil, random, importlib
sys.dont_write_bytecode = True
import c2
S = '/fast/scratch/hyaku/kama-r63/w/RV03C2CounterCode/h'
def sh(*a, cwd=None):
    return subprocess.run(list(a), capture_output=True, text=True, cwd=cwd, check=True).stdout.strip()

print('== R1 checkout_tip reuses a stale tree for a different tip')
fx = os.path.join(S, 'fx1'); shutil.rmtree(fx, ignore_errors=True); os.makedirs(fx)
G = ['git', '-C', fx, '-c', 'user.name=seat', '-c', 'user.email=seat@seat.invalid']
subprocess.run(['git', '-C', fx, 'init', '-q'], check=True)
os.makedirs(os.path.join(fx, 'tools'))
open(os.path.join(fx, 'tools', 'x.py'), 'w').write("print('A')\n")
subprocess.run(G + ['add', '-A'], check=True); subprocess.run(G + ['commit', '-q', '-m', 'A'], check=True)
A = sh('git', '-C', fx, 'rev-parse', 'HEAD')
open(os.path.join(fx, 'tools', 'x.py'), 'w').write("print('B')\n")
subprocess.run(G + ['commit', '-qam', 'B'], check=True)
B = sh('git', '-C', fx, 'rev-parse', 'HEAD')
work = os.path.join(S, 'w1'); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
t = c2.checkout_tip(fx, A, work)
t2 = c2.checkout_tip(fx, B, work)
print('tree for B says:', open(os.path.join(t2, 'tools', 'x.py')).read().strip(), '(expected B)')
w2 = os.path.join(S, 'w2'); shutil.rmtree(w2, ignore_errors=True); os.makedirs(os.path.join(w2, 'tip'))
print('empty pre-existing tip dir ->', c2.checkout_tip(fx, B, w2), 'contents:', os.listdir(os.path.join(w2, 'tip')))

print('== R2 host-busy branch: disjoint pid sets before/after accepted')
fake = os.path.join(S, 'tt'); os.makedirs(os.path.join(fake, 'tools'), exist_ok=True)
open(os.path.join(fake, 'tools', 'kama-context-capacity.py'), 'w').write(
    "import sys\nprint('host-not-idle-before-K1')\nsys.exit(2)\n")
row = {'cap': 'context-capacity-receipt', 'binding': 'cell', 'verdict': 'host-busy'}
tpls = c2.MANIFEST['context-capacity-receipt'][1]
seq = iter([[111], [222]])
c2.pgrep_foreign = lambda: next(seq)
print('before=[111] after=[222] ->', c2.run_bound(row, tpls, fake, S, fx, B, {'PATH': os.environ['PATH']})[:1])
seq = iter([[], [222]])
print('before=[]    after=[222] ->', c2.run_bound(row, tpls, fake, S, fx, B, {'PATH': os.environ['PATH']})[:1])
seq = iter([[111], []])
print('before=[111] after=[]    ->', c2.run_bound(row, tpls, fake, S, fx, B, {'PATH': os.environ['PATH']})[:1])
