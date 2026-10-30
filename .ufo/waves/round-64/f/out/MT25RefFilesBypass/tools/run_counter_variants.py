#!/usr/bin/env python3
"""MT25: score each forgery with the UNMUTATED counter at a committed forged tip."""
import json
import os
import shutil
import subprocess
import sys
from hashlib import sha256

S = '/fast/scratch/hyaku/kama-r64/f/MT25RefFilesBypass'
HOME = os.path.join(S, 'home')
MODEL = os.path.join(HOME, '.cache/kama-shokunin/models/stories260K.gguf')
PRISTINE = os.path.join(S, 'pristine/stories260K.gguf')
CLONE = os.path.join(S, 'clone')
COUNTER = os.path.join(CLONE, 'tools/round64-c1-counter.py')
OUT = os.path.join(S, 'h/out/counter')
HOOK_OFF = 14152
WEIGHT_OFF = 14176 + 2000

VARIANTS = [
    ('D_gap600', {'dlopen_lib': 'libllama-cli-impl.so', 'dlopen_delay_ms': 600}),
    ('C1_neutral_restore', {'rewrite_pre': {'off': HOOK_OFF,
                                            'hex': '01' * 24, 'restore': True}}),
    ('C2_neutral_persist', {'rewrite_pre': {'off': HOOK_OFF,
                                            'hex': '01' * 24, 'restore': False}}),
    ('C3_weight_hold_restore', {'rewrite_pre': {'off': WEIGHT_OFF,
                                                'hex': 'ff' * 4096,
                                                'restore': True}}),
    ('C4_native_reflink', {'native_swap': True}),
    ('C5_native_hardlink', {'native_hardlink': True}),
    ('C6_weight_post_release', {'rewrite_post': {'off': WEIGHT_OFF,
                                                 'hex': 'ff' * 4096,
                                                 'restore': True}}),
]


def reset_model():
    data = open(PRISTINE, 'rb').read()
    with open(MODEL, 'r+b') as f:
        f.seek(0)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    for extra in (MODEL + '.mt25swap', MODEL + '.mt25hl'):
        if os.path.exists(extra):
            os.remove(extra)


def commit_tip():
    subprocess.run(['git', '-C', CLONE, 'add', '-A'], check=True)
    subprocess.run(['git', '-C', CLONE, '-c', 'user.name=seat',
                    '-c', 'user.email=seat@seat.invalid', 'commit', '-q',
                    '-m', 'MT25 forged tool (scratch clone only)'], check=True)
    return subprocess.run(['git', '-C', CLONE, 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()


def run_one(name, mode, tip):
    d = os.path.join(OUT, name)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    reset_model()
    mp = os.path.join(HOME, 'mt25-mode.json')
    for p in (mp, os.path.join(HOME, 'mt25-evidence.json')):
        if os.path.exists(p):
            os.remove(p)
    with open(mp, 'w') as f:
        json.dump(mode, f)
    work = os.path.join(d, 'work')
    env = dict(os.environ, HOME=HOME)
    p = subprocess.run([sys.executable, COUNTER, '--repo', CLONE,
                        '--tip', tip, '--work', work],
                       capture_output=True, text=True, env=env)
    open(os.path.join(d, 'stdout.txt'), 'w').write(p.stdout)
    open(os.path.join(d, 'stderr.txt'), 'w').write(p.stderr)
    ev = os.path.join(HOME, 'mt25-evidence.json')
    if os.path.exists(ev):
        shutil.copy(ev, os.path.join(d, 'evidence.json'))
        os.remove(ev)
    line = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ''
    sha = sha256(open(MODEL, 'rb').read()).hexdigest()[:12]
    print('%-24s rc=%d sha_after=%s' % (name, p.returncode, sha), flush=True)
    print('   ', line, flush=True)
    for e in p.stderr.strip().splitlines()[:4]:
        print('    E:', e, flush=True)
    if os.path.exists(ev) or os.path.exists(os.path.join(d, 'evidence.json')):
        pass
    return {'name': name, 'rc': p.returncode, 'line': line,
            'stderr': p.stderr.strip().splitlines(),
            'model_sha_after': sha}


def main():
    only = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    tip = commit_tip()
    print('forged tip:', tip, flush=True)
    todo = [(n, m) for n, m in VARIANTS if not only or n in only]
    running = []
    results = []
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(run_one, n, m, tip): n for n, m in todo}
        for f in futs:
            results.append(f.result())
    reset_model()
    with open(os.path.join(OUT, 'summary.json'), 'w') as fh:
        json.dump({'tip': tip, 'results': results}, fh, indent=1)


if __name__ == '__main__':
    main()
