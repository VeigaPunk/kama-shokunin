#!/usr/bin/env python3
"""MT25: run each forged variant once through the counter's own witness_run +
score_run (harness v2), sequentially, under a private HOME whose model copy is
reset in place (same inode) before every run."""
import json
import os
import shutil
import subprocess
import sys

S = '/fast/scratch/hyaku/kama-r64/f/MT25RefFilesBypass'
HOME = os.path.join(S, 'home')
MODEL = os.path.join(HOME, '.cache/kama-shokunin/models/stories260K.gguf')
PRISTINE = os.path.join(S, 'pristine/stories260K.gguf')
TIP = '23b3fdb1a925129a9961cf551f6d40bf251602cb'
CLONE = os.path.join(S, 'clone')
COUNTER = os.path.join(CLONE, 'tools/round64-c1-counter.py')
TOOL = os.path.join(S, 'forged/hooked/tools/kama-completion-live.py')
OUT = os.path.join(S, 'h/out/variants')
HOOK_OFF = 14152          # 24 zero alignment bytes after tensor info, never read
DATA0 = 14176             # tensor data start
WEIGHT_OFF = DATA0 + 2000  # inside token_embd.weight: changes answers

M = MODEL
VARIANTS = [
    ('V0_inert', {}, None),
    ('V1_c1_neutral_restore', {'rewrite_pre': {
        'off': HOOK_OFF, 'hex': '01' * 24, 'restore': True}}, None),
    ('V2_c1_neutral_persist', {'rewrite_pre': {
        'off': HOOK_OFF, 'hex': '01' * 24, 'restore': False}}, None),
    ('V3_weight_in_hold_restore', {'rewrite_pre': {
        'off': WEIGHT_OFF, 'hex': 'ff' * 4096, 'restore': True}}, None),
    ('V4_weight_post_release_restore', {'rewrite_post': {
        'off': WEIGHT_OFF, 'hex': 'ff' * 4096, 'restore': True}}, None),
    ('V5_dlopen_delay0', {'dlopen_lib': 'libllama-cli-impl.so',
                          'dlopen_delay_ms': 0}, None),
    ('V6_dlopen_delay300', {'dlopen_lib': 'libllama-cli-impl.so',
                            'dlopen_delay_ms': 300}, None),
    ('V7_dlopen_delay600', {'dlopen_lib': 'libllama-cli-impl.so',
                            'dlopen_delay_ms': 600}, None),
    ('V8_dlopen_delay1200', {'dlopen_lib': 'libllama-cli-impl.so',
                             'dlopen_delay_ms': 1200}, None),
    ('V9_bindself_in_mntns', {
        'wrap_prefix': ['/usr/bin/unshare', '-Urm', '/bin/sh', '-c'],
        'wrap_pre': f'mount --bind "{M}" "{M}"'}, None),
    ('V10_reflink_swap_pre_start', {
        'wrap_pre': f'cp --reflink=always "{M}" "{M}.r64" && mv -f "{M}.r64" "{M}"'},
     None),
    ('V11_hardlink_same_inode', {
        'wrap_pre': f'ln -f "{M}" "{M}.hl"'}, None),
]


def reset_model():
    with open(PRISTINE, 'rb') as f:
        data = f.read()
    with open(MODEL, 'r+b') as f:
        f.seek(0)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    for extra in (M + '.r64', M + '.hl'):
        if os.path.exists(extra):
            os.remove(extra)


def main():
    only = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for name, mode, _ in VARIANTS:
        if only and name not in only:
            continue
        d = os.path.join(OUT, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        reset_model()
        mode_path = os.path.join(HOME, 'mt25-mode.json')
        for p in (mode_path, os.path.join(HOME, 'mt25-evidence.json')):
            if os.path.exists(p):
                os.remove(p)
        if mode:
            with open(mode_path, 'w') as f:
                json.dump(mode, f)
        env = dict(os.environ, HOME=HOME)
        out = os.path.join(d, 'harness.json')
        log = os.path.join(d, 'harness.log')
        with open(log, 'w') as lf:
            rc = subprocess.run(
                [sys.executable, os.path.join(S, 'h/mt25_harness.py'),
                 'honest', '--repo', CLONE, '--tip', TIP,
                 '--counter', COUNTER, '--tool', TOOL, '--n', '1',
                 '--label', name, '--dump-raw', '--out', out],
                env=env, stdout=lf, stderr=subprocess.STDOUT).returncode
        ev = os.path.join(HOME, 'mt25-evidence.json')
        if os.path.exists(ev):
            shutil.copy(ev, os.path.join(d, 'evidence.json'))
            os.remove(ev)
        res = json.load(open(out)) if os.path.exists(out) else []
        r = res[0] if res else {}
        leftover = os.path.exists(mode_path)
        line = {'variant': name, 'rc': rc, 'met': r.get('met'),
                'fails': r.get('fails'), 'error': r.get('error'),
                'mode_unconsumed': leftover,
                'model_sha_after': None}
        from hashlib import sha256
        line['model_sha_after'] = sha256(open(MODEL, 'rb').read()).hexdigest()[:12]
        rows.append(line)
        print(json.dumps(line), flush=True)
    reset_model()
    with open(os.path.join(OUT, 'summary.json'), 'w') as f:
        json.dump(rows, f, indent=1)


if __name__ == '__main__':
    main()
