#!/usr/bin/env python3
"""Evidence driver: apply each row of capability-regress-r64.part1.tsv to a scratch copy of the
tip tree (tools/ tests/ registry/), prove find occurs exactly once, the mutant still imports
(compiles + loads as a module), then run the registry row's run template on the unmutated and
mutated copy. usage: verify_part1.py <tip-tree-dir> <scratch> <registry tsv> <part1 tsv> <repo>"""
import sys, os, shutil, shlex, subprocess, importlib.util, py_compile
tree0, S, reg, part, repo = sys.argv[1:6]
L = [l.rstrip('\n').split('\t') for l in open(reg)]
rows = {l[0]: dict(zip(L[0], l)) for l in L[1:]}
def run(cap, tree, tag):
    r = rows[cap]; w = f'{S}/work/{tag}'; os.makedirs(w, exist_ok=True)
    cmd = r['run'].replace('%T', tree).replace('%S', w).replace('%R', repo).replace('TIPREV', 'HEAD')
    p = subprocess.run(shlex.split(cmd), cwd=S, capture_output=True, text=True, timeout=300)
    out = p.stdout + p.stderr
    pat = r['pattern']; hit = [l.strip() for l in out.splitlines() if pat in l]
    fc = ''
    if cap == 'live-llamacpp-lifecycle':
        import json
        try:
            d = json.loads(p.stdout)
            fc = ' outcome=%s failed_checks=%s' % (d.get('outcome'), [c['id'] for c in d.get('checks', []) if c.get('passed') is False])
        except Exception as e:
            fc = ' (stdout not JSON: %s)' % type(e).__name__
    return p.returncode, pat in out, (hit[0][:110] if hit else '<absent> last=' + (out.strip().splitlines() or [''])[-1][:110]) + fc
for i, line in enumerate(open(part)):
    cap, tool, find, rep = line.rstrip('\n').split('\t')
    assert '\t' not in find + rep
    t = f'{S}/m{i}'
    if os.path.exists(t): shutil.rmtree(t)
    os.makedirs(t)
    for d in ('tools', 'tests', 'registry'): shutil.copytree(f'{tree0}/{d}', f'{t}/{d}', symlinks=True)
    f = f'{t}/{tool}'; src = open(f).read(); n = src.count(find)
    print(f'## {cap}\n  find={find!r}\n  replace={rep!r}\n  occurrences_of_find_in_{tool}={n}  (must be 1)')
    assert n == 1
    print('  differing_lines=', sum(1 for a, b in zip(src.splitlines(), src.replace(find, rep).splitlines()) if a != b), 'line_count_same=', len(src.splitlines()) == len(src.replace(find, rep).splitlines()))
    u = run(cap, tree0, f'u{i}')
    open(f, 'w').write(src.replace(find, rep))
    py_compile.compile(f, doraise=True)
    spec = importlib.util.spec_from_file_location(f'mut{i}', f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    print('  mutant_importable= True (py_compile + exec_module of the module body, __main__ guard not run)')
    mu = run(cap, t, f'm{i}')
    print(f'  unmutated: exit={u[0]} pattern_present={u[1]} line={u[2]}')
    print(f'  mutated  : exit={mu[0]} pattern_present={mu[1]} line={mu[2]}')
    print(f'  FLIPPED={(u[0]==0 and u[1]) and (mu[0]!=0 or not mu[1])}')
