#!/usr/bin/env python3
"""ControlsCrash (kama round 20) runner: one controls.py run against a chosen
gate, inside an isolated TMPDIR under the seat scratch, then a sweep that
SIGKILLs and records every process still naming that TMPDIR (a leftover
fake/tool). Writes <label>.json (controls stdout), <label>.stderr.txt and
<label>.meta.json next to this file and prints a one-line-per-row summary.

  run_controls.py --lane LANE --label L --gate GATE [--only ID]
"""
import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def scan(marker):
    me, found = os.getpid(), []
    for d in os.listdir('/proc'):
        if not d.isdigit() or int(d) == me:
            continue
        try:
            with open(f'/proc/{d}/cmdline', 'rb') as fh:
                cmd = fh.read().replace(b'\0', b' ').decode('utf-8', 'replace')
        except OSError:
            continue
        if marker in cmd:
            found.append({'pid': int(d), 'cmdline': cmd.strip()[:300]})
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lane', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--gate', required=True)
    ap.add_argument('--only')
    a = ap.parse_args()
    lane = Path(a.lane)
    controls = lane / 'tests' / 'llamacpp-live' / 'controls.py'
    tool = lane / 'tools' / 'kama-llamacpp-live.py'
    gate = Path(a.gate).resolve()
    tmp = Path('/tmp/kama-r20-ControlsCrash') / f'tmp-{a.label}'
    tmp.mkdir(parents=True, exist_ok=False)
    marker = str(tmp) + '/'
    cmd = [sys.executable, str(controls), '--tool', str(tool),
           '--gate', str(gate), '--json']
    if a.only:
        cmd += ['--only', a.only]
    env = dict(os.environ)
    env['TMPDIR'] = str(tmp)
    before = scan(marker)
    t0 = time.monotonic()
    p = subprocess.run(cmd, capture_output=True, text=True, env=env,
                       cwd='/tmp/kama-r20-ControlsCrash', timeout=3000,
                       stdin=subprocess.DEVNULL)
    wall = round(time.monotonic() - t0, 1)
    after = scan(marker)
    killed = []
    for proc in after:
        try:
            os.kill(proc['pid'], signal.SIGKILL)
            killed.append(proc['pid'])
        except OSError as exc:
            proc['kill_error'] = repr(exc)
    time.sleep(0.5)
    after_kill = scan(marker)
    leftover_dirs = sorted(str(x) for x in tmp.iterdir())
    (OUT / f'{a.label}.json').write_text(p.stdout, encoding='utf-8')
    (OUT / f'{a.label}.stderr.txt').write_text(p.stderr, encoding='utf-8')
    meta = {
        'label': a.label, 'cmd': cmd, 'tmpdir': str(tmp),
        'controls_exit': p.returncode, 'wall_s': wall,
        'controls_sha256': sha(controls), 'tool_sha256': sha(tool),
        'gate_sha256': sha(gate), 'python': sys.version.split()[0],
        'procs_before': before, 'procs_after_controls_exit': after,
        'sigkilled_pids': killed, 'procs_after_sweep': after_kill,
        'tmpdir_entries_after': leftover_dirs,
    }
    (OUT / f'{a.label}.meta.json').write_text(
        json.dumps(meta, indent=2) + '\n', encoding='utf-8')
    print(f'== {a.label}: controls exit {p.returncode} wall {wall}s '
          f'leftover_after_exit={len(after)} killed={killed} '
          f'after_sweep={len(after_kill)} tmp_entries={len(leftover_dirs)}')
    try:
        res = json.loads(p.stdout)
    except ValueError:
        print('stdout not JSON; stderr tail:', p.stderr[-800:])
        return
    for r in res['controls']:
        gf = r.get('gate_flip')
        gfs = (f"flip(exit={gf['exit']} acc={gf['accepted']} "
               f"rej={gf['rejected']} tgt={gf['targeted']})" if gf else 'flip=-')
        print(f"{r['id']:<4} {r['kind']:<9} tool={r.get('tool_exit')!s:<4} "
              f"gate={r.get('gate_exit')!s:<4} {r['classification']:<19} "
              f"[{r['bucket']}] hit={r.get('targeted_hit')} "
              f"probs={len(r.get('gate_problems') or [])} "
              f"failed={r.get('failed_checks')} {gfs} :: {r['reason'][:150]}")
    keys = ('accepted_bad', 'good_rejected', 'misclassified', 'inconclusive',
            'gate_flip_bad', 'gate_flip_arms', 'good_ok')
    print('summary', {k: res.get(k) for k in keys})
    print('controlled_checks', res.get('controlled_checks'))
    print('uncontrolled_checks', res.get('uncontrolled_checks'))
    if p.stderr:
        print('controls stderr tail:', p.stderr[-600:])


if __name__ == '__main__':
    main()
