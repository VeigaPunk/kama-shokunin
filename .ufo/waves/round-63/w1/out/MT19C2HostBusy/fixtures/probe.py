import os, re, subprocess, sys
S = '/fast/scratch/hyaku/kama-r63/w/MT19C2HostBusy'
mode = sys.argv[1]
tip_tree = S + '/work/iso-ns-fake/tip'
repo = S + '/v/iso-ns-fake'
tip = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
reg = open(tip_tree + '/registry/capability-claims-r63.tsv', encoding='utf-8').read().splitlines()
hdr = reg[0].split('\t')
env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'LANG', 'LC_ALL')}
for line in reg[1:]:
    if not line.strip() or line.startswith('#'):
        continue
    c = dict(zip(hdr, line.split('\t')))
    cap = c['cap']
    scratch = f'{S}/probe/{mode}/{cap}'
    os.makedirs(scratch, exist_ok=True)
    env['TMPDIR'] = scratch
    cmd = (c['run'].replace('%T', tip_tree).replace('%S', scratch)
           .replace('%R', repo).replace('TIPREV', tip))
    p = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True, timeout=900, cwd=tip_tree, env=env)
    out = p.stdout + p.stderr
    print(f'{cap:34s} rc={p.returncode} pat_in_out={c["pattern"] in out} tail={out.strip().splitlines()[-1][:120] if out.strip() else ""!r}')
