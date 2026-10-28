#!/usr/bin/env python3
"""Positive control: run the master completion-tool blob from a *copied* tip
tree shaped exactly like round62-c1-counter.py's <work>/tip (tools/ with both
master blobs + registry/endpoint-consumers.tsv). Proves all 12 imported dep
symbols resolve and work end-to-end when the tool is not run from the lane,
with a hold-window release so hold_for_witness/prepare_witness_dir are
exercised too.
"""
import json
import os
import subprocess
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
TIP = os.path.join(S, 'tip')
WORK = os.path.join(S, 'w', 'positive_copy')
HOLD = os.path.join(S, 'w', 'positive_copy_hold')
OUT = os.path.join(S, 'r', 'positive_copy.json')


def main():
    for d in (WORK, HOLD, os.path.dirname(OUT)):
        os.makedirs(d, exist_ok=True)
    env = {k: v for k, v in os.environ.items()
           if k in ('PATH', 'HOME', 'LANG', 'LC_ALL')}
    env['TMPDIR'] = os.path.join(S, 'tmpdir')
    os.makedirs(env['TMPDIR'], exist_ok=True)
    argv = [sys.executable, os.path.join(TIP, 'tools',
                                         'kama-completion-live.py'),
            '--work', WORK, '--hold-dir', HOLD, '--hold-timeout', '90',
            '--out', OUT, '--nonce', 'e08-deps-audit-positive',
            '--n-predict', '4']
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, text=True, env=env, cwd=S)
    released = False
    t0 = time.monotonic()
    while time.monotonic() - t0 < 120:
        if os.path.exists(os.path.join(HOLD, 'hold.json')):
            open(os.path.join(HOLD, 'release'), 'w').write('go\n')
            released = True
            break
        if p.poll() is not None:
            break
        time.sleep(0.25)
    if not released:
        open(os.path.join(HOLD, 'release'), 'w').write('go\n')
    try:
        _, err = p.communicate(timeout=180)
    except subprocess.TimeoutExpired:
        p.kill()
        _, err = p.communicate()
    rec = json.load(open(OUT)) if os.path.exists(OUT) else None
    res = {
        'rc': p.returncode,
        'hold_released_by_observer': released,
        'verdict': rec.get('verdict') if rec else None,
        'setup_error': rec.get('setup_error') if rec else None,
        'port': rec.get('port') if rec else None,
        'child_pid': rec.get('child_pid') if rec else None,
        'checks': {k: [v.get('passed'), v.get('evaluated')]
                   for k, v in (rec.get('checks') or {}).items()} if rec
        else None,
        'capture_keys': sorted((rec.get('captures') or {}).keys()) if rec
        else None,
        'teardown': rec.get('teardown') if rec else None,
        'schema': rec.get('schema') if rec else None,
        'stderr_last': (err or '').strip().splitlines()[-3:],
    }
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
