#!/usr/bin/env python3
"""MT40 registry-row mutant sweep, corrected: PATH keeps the operator's
llama-server discoverable (the first sweep inherited a PATH=/usr/bin:/bin
shell and the live-llamacpp row failed for that reason alone).

Phase 1: commit one tip per mutant (each tip = base + exactly one registry
edit). Phase 2: score every tip with the UNMUTATED counter, 3 at a time,
each with its own fresh --work.
"""
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

CLONE = '/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows/clone'
SCRATCH = '/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows'
OUT = os.path.join(SCRATCH, 'out')
BASE = '23b3fdb1a925129a9961cf551f6d40bf251602cb'
REG = 'registry/capability-claims-r64.tsv'
PATH = '/home/vgpnk/.local/bin:/usr/local/bin:/usr/bin:/bin'

sys.path.insert(0, SCRATCH)
from mutants import MUTANTS, read_reg, rows_of, emit  # noqa: E402


def g(*a):
    return subprocess.run(['git', '-C', CLONE, *a], capture_output=True,
                          text=True)


def commit_mutants():
    base_bytes = read_reg()
    header, body = rows_of(base_bytes)
    tips = []
    for name, fn in MUTANTS:
        g('checkout', '-q', BASE, '--', REG)
        data = fn(header, body)
        assert data != base_bytes, name
        with open(os.path.join(CLONE, REG), 'wb') as fh:
            fh.write(data)
        g('add', '-A')
        c = subprocess.run(['git', '-C', CLONE, '-c', 'user.name=seat',
                            '-c', 'user.email=seat@seat.invalid', 'commit',
                            '-q', '-m', 'MT40 ' + name], capture_output=True,
                           text=True)
        assert c.returncode == 0, (name, c.stderr)
        tips.append((name, g('rev-parse', 'HEAD').stdout.strip()))
    g('checkout', '-q', BASE, '--', REG)
    return tips


def run_one(name, tip):
    work = os.path.join(SCRATCH, 'work2-' + name)
    shutil.rmtree(work, ignore_errors=True)
    env = dict(os.environ, PATH=PATH)
    cmd = [sys.executable, 'tools/round64-c2-counter.py', '--repo', CLONE,
           '--tip', tip, '--work', work]
    t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=CLONE, capture_output=True, text=True,
                       env=env)
    with open(os.path.join(OUT, name + '.out'), 'w') as fh:
        fh.write(p.stdout)
    with open(os.path.join(OUT, name + '.err'), 'w') as fh:
        fh.write(p.stderr)
    with open(os.path.join(OUT, name + '.cmd'), 'w') as fh:
        fh.write('PATH=%s ' % PATH + ' '.join(cmd) + '\n')
    shutil.rmtree(work, ignore_errors=True)
    return name, tip, p.returncode, p.stdout, p.stderr, round(
        time.monotonic() - t0, 1)


def report(res):
    name, tip, rc, out, err, secs = res
    print('== %-34s tip=%s rc=%s (%ss)' % (name, tip[:12], rc, secs),
          flush=True)
    print('   ' + out.strip().replace('\n', '\n   '), flush=True)
    for ln in err.splitlines():
        if ln.startswith(('registry:', 'problem:', 'gate-misses',
                          'control-escape', 'note:')):
            print('   | ' + ln, flush=True)
    print('   row live-llamacpp: ' + next(
        (ln for ln in err.splitlines()
         if ln.startswith('row live-llamacpp')), 'n/a'), flush=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    tips = commit_mutants()
    tips.append(('BASELINE-pristine-tip', BASE))
    with ThreadPoolExecutor(max_workers=3) as pool:
        for res in pool.map(lambda t: run_one(t[0], t[1]), tips):
            report(res)


if __name__ == '__main__':
    main()
