import os, subprocess, shutil, sys, importlib.util, py_compile
S = '/fast/scratch/hyaku/kama-r64/b/X04Regress3'
D = S + '/clone'
OUT = '/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-64/b/out/X04Regress3'
T = subprocess.check_output(['git', '-C', D, 'rev-parse', 'HEAD'], text=True).strip()
REG = {}
for l in open('/home/vgpnk/Projects/shokunin/kama-shokunin/registry/capability-claims-r63.tsv', encoding='utf-8'):
    c = l.rstrip('\n').split('\t')
    REG[c[0]] = c
shutil.rmtree(S + '/trees', ignore_errors=True)
os.makedirs(S + '/trees/U')
subprocess.run('git -C %s archive %s tools registry | tar -x -C %s/trees/U' % (D, T, S), shell=True, check=True)
env = {k: os.environ[k] for k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR') if k in os.environ}
env['TMPDIR'] = S + '/tmp'
os.makedirs(env['TMPDIR'], exist_ok=True)
rows = [l.rstrip('\n').split('\t') for l in open(OUT + '/capability-regress-r64.part3.tsv')]
log = []
for cap, path, find, repl in rows:
    run, pat = REG[cap][3], REG[cap][4]
    M = S + '/trees/M-' + cap
    shutil.rmtree(M, ignore_errors=True)
    shutil.copytree(S + '/trees/U', M)
    src = open(M + '/' + path, encoding='utf-8').read()
    cnt = src.count(find)
    assert '\t' not in find + repl
    mutsrc = src.replace(find, repl)
    open(M + '/' + path, 'w', encoding='utf-8').write(mutsrc)
    py_compile.compile(M + '/' + path, doraise=True, cfile=S + '/tmp/x.pyc')
    spec = importlib.util.spec_from_file_location('m_' + cap.replace('-', '_'), M + '/' + path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    res = {}
    for tag, tree in (('U', S + '/trees/U'), ('M', M)):
        sc = os.path.join(S, 'scratch-' + cap + '-' + tag)
        shutil.rmtree(sc, ignore_errors=True); os.makedirs(sc)
        cmd = run.replace('%T', tree).replace('%S', sc).replace('%R', D).replace('TIPREV', T)
        p = subprocess.run(cmd, shell=True, cwd=tree, env=env, capture_output=True, text=True, timeout=600)
        out = p.stdout + p.stderr
        res[tag] = (p.returncode, pat in p.stdout, p.stdout.strip().splitlines()[-1] if p.stdout.strip() else '')
        open(OUT + '/%s.%s.out' % (cap, tag), 'w').write(out)
    log.append((cap, path, cnt, res))
    print(cap, 'find_count=%d importable=yes' % cnt)
    print('  pattern=%r' % pat)
    for tag in 'UM':
        rc, has, last = res[tag]
        print('  %s: exit=%d pattern_present=%s last=%s' % (tag, rc, has, last))
    u, m = res['U'], res['M']
    print('  VERDICT unmutated=%s mutated=%s' % (u[0] == 0 and u[1], m[0] == 0 and m[1]))
