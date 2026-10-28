#!/usr/bin/env python3
"""E07 driver: run kama-completion-live.py at edge args with an outside
observer during the hold window. Writes receipts into this scratch dir."""
import json
import os
import subprocess
import sys
import time
import urllib.request

SCRATCH = os.path.dirname(os.path.abspath(__file__))
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TOOL = os.path.join(LANE, 'tools', 'kama-completion-live.py')
PROMPT = 'Grüße aus Zürich — 日本語 café ① naïve façade ☕🚀'


def post(port, payload, timeout=10.0):
    req = urllib.request.Request(
        f'http://127.0.0.1:{port}/v1/completions',
        data=json.dumps(payload).encode(),
        method='POST', headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'


def run(name, extra, hold=None, observe=None):
    work = os.path.join(SCRATCH, 'work-' + name)
    os.makedirs(work, exist_ok=True)
    out = os.path.join(SCRATCH, name + '.json')
    argv = [sys.executable, TOOL, '--work', os.path.join(work, 'server'),
            '--out', out, '--prompt', PROMPT] + extra
    if hold:
        hd = os.path.join(SCRATCH, 'hold-' + name)
        os.makedirs(hd, exist_ok=True)
        argv += ['--hold-dir', hd, '--hold-timeout', '60']
    env = dict(os.environ)
    env['TMPDIR'] = SCRATCH
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, cwd=SCRATCH, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True)
    obs = None
    if hold and observe:
        rp = os.path.join(hd, 'ready.json')
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline and proc.poll() is None:
            if os.path.exists(rp):
                doc = json.load(open(rp))
                obs = {'ready_json': doc,
                       'observed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
                payload = {'prompt': PROMPT, 'n_predict': 1,
                           'temperature': 0.5, 'seed': 7,
                           'timings_per_token': False}
                st, body = post(doc['port'], payload)
                obs['outside_status'] = st
                obs['outside_body'] = body[:1500]
                open(os.path.join(hd, 'release'), 'w').close()
                break
            time.sleep(0.05)
    stdout, _ = proc.communicate(timeout=300)
    rec = json.load(open(out)) if os.path.exists(out) else None
    return {'name': name, 'argv_tail': argv[1:], 'rc': proc.returncode,
            'wall_s': round(time.monotonic() - t0, 2),
            'stdout': stdout[-2000:], 'observer': obs,
            'receipt_path': out, 'receipt': rec}


if __name__ == '__main__':
    results = []
    # A: required edge run (temperature 0.5, n_predict 1, unicode prompt)
    results.append(run('A-edge-t05-np1', ['--temperature', '0.5',
                                          '--n-predict', '1',
                                          '--nonce', 'e07A'],
                       hold=True, observe=True))
    # B: contrast baseline (temperature 0 -> determinism evaluated)
    results.append(run('B-base-t00-np1', ['--temperature', '0.0',
                                          '--n-predict', '1',
                                          '--nonce', 'e07B'],
                       hold=True, observe=True))
    # C: same edge args, no hold dir (check-absence shape)
    results.append(run('C-edge-nohold', ['--temperature', '0.5',
                                         '--n-predict', '1',
                                         '--nonce', 'e07C']))
    with open(os.path.join(SCRATCH, 'summary.json'), 'w') as f:
        json.dump(results, f, indent=1)
    for r in results:
        rec = r['receipt'] or {}
        checks = rec.get('checks') or {}
        ne = sorted(k for k, v in checks.items() if v.get('evaluated') is False)
        print(json.dumps({
            'run': r['name'], 'rc': r['rc'], 'verdict': rec.get('verdict'),
            'setup_error': rec.get('setup_error'),
            'not_evaluated': ne,
            'absent_checks': sorted(set(['completion_deterministic',
                                         'hold_released']) - set(checks)),
            'failed': sorted(k for k, v in checks.items()
                             if v.get('evaluated') and not v.get('passed')),
            'n_checks': len(checks),
            'hold_released': (rec.get('hold') or {}).get('released'),
            'outside_status': (r['observer'] or {}).get('outside_status'),
        }))
