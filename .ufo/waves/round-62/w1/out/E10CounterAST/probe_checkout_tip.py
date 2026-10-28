#!/usr/bin/env python3
"""Probe C2's checkout_tip() (tip-pinned module) under three envs.

Records whether the extracted tip tree is affected by (a) the three named
hostile GIT_* vars and (b) a hostile HOME carrying core.attributesFile with
export-ignore. Writes JSON to stdout.
"""
import importlib.util, json, os, subprocess, sys
SYS = os.path.dirname(os.path.abspath(__file__))
LANE, TIP = '/home/vgpnk/Projects/shokunin/kama-shokunin', sys.argv[1]
_moddir = os.path.join(SYS, 'work', 'module')
os.makedirs(_moddir, exist_ok=True)
BIN = os.path.join(_moddir, 'c2-tip.py')
_scrub = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
_got = subprocess.run(['git', '-C', LANE, 'show',
                       f'{TIP}:tools/round62-c2-counter.py'],
                      capture_output=True, env=_scrub)
assert _got.returncode == 0, _got.stderr
open(BIN, 'wb').write(_got.stdout)
spec = importlib.util.spec_from_file_location('c2', BIN)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def probe(label, home, gitvars):
    os.environ.pop('TMPDIR', None)
    for k in [k for k in os.environ if k.startswith('GIT_')]:
        os.environ.pop(k)
    os.environ['HOME'] = home
    os.environ.update(gitvars or {})
    work = os.path.join(SYS, 'work', 'ctip-' + label)
    subprocess.run(['rm', '-rf', work])
    tree = mod.checkout_tip(LANE, TIP, work)
    sc = os.path.join(tree, 'SCORECARD.md') if tree else ''
    can = mod.canonical_rows(open(sc).read()) if sc and os.path.exists(sc) else (None, [])
    py = [t for t in os.listdir(os.path.join(tree, 'tools')) if t.endswith('.py')] if tree else []
    n = sum(len(f) for _, _, f in os.walk(tree)) if tree else 0
    rec = {'label': label, 'tree_returned': bool(tree), 'files': n,
           'tools_py': len(py), 'scorecard': bool(sc and os.path.exists(sc)),
           'canonical_round': can[0], 'canonical_rows': len(can[1])}
    subprocess.run(['rm', '-rf', work])
    return rec

# hostile HOME fixture: a git config whose core.attributesFile marks every
# *.md and tools/*.py export-ignore, so `git archive` drops them.
HH = os.path.join(SYS, 'work', 'hostile-home')
os.makedirs(HH, exist_ok=True)
open(os.path.join(HH, 'attrs'), 'w').write('*.md export-ignore\ntools/*.py export-ignore\n')
open(os.path.join(HH, '.gitconfig'), 'w').write(
    '[core]\n\tattributesFile = ' + os.path.join(HH, 'attrs') + '\n')

out = [probe('clean', '/home/vgpnk', None),
       probe('git_vars', '/home/vgpnk', json.loads(sys.argv[2])),
       probe('hostile_home', HH, None)]
print(json.dumps(out, indent=1))
