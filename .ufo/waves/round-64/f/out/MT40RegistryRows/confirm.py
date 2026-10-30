#!/usr/bin/env python3
"""MT40 confirmation rerun: re-score the mutants whose verdict could be
confounded by a host-contention effect (the context-capacity row's idle
proof and the live rows), and record both outputs."""
import os
import shutil
import subprocess
import sys
import time

CLONE = '/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows/clone'
SCRATCH = '/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows'
OUT = os.path.join(SCRATCH, 'out')
PATH = '/home/vgpnk/.local/bin:/usr/local/bin:/usr/bin:/bin'

# (label, tip) pairs: the tip shas come from the committed mutant history.
TIPS = {
    'M10-ctx-verdict-vs-live-outcome': 'effa7691c9ec',
    'M11-ctx-note-false-statement': '2edabc836073',
    'M23-ctx-verdict-true-observed-busy': '56db69794c1c',
    'M17-quote-at-8-char-floor': '7d2c8c4a46c4',
    'M27-quote-prefix-fragment': '13f67ffaed0e',
}


def full(tip):
    p = subprocess.run(['git', '-C', CLONE, 'rev-parse', tip],
                       capture_output=True, text=True)
    return p.stdout.strip()


def run_one(label, tip):
    work = os.path.join(SCRATCH, 'work5-' + label)
    shutil.rmtree(work, ignore_errors=True)
    env = dict(os.environ, PATH=PATH)
    cmd = [sys.executable, 'tools/round64-c2-counter.py', '--repo', CLONE,
           '--tip', full(tip), '--work', work]
    t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=CLONE, capture_output=True, text=True,
                       env=env)
    with open(os.path.join(OUT, label + '.rerun.out'), 'w') as fh:
        fh.write(p.stdout)
    with open(os.path.join(OUT, label + '.rerun.err'), 'w') as fh:
        fh.write(p.stderr)
    shutil.rmtree(work, ignore_errors=True)
    print('== %-40s rc=%s (%ss)' % (label, p.returncode,
                                    round(time.monotonic() - t0, 1)),
          flush=True)
    print('   ' + p.stdout.strip(), flush=True)
    for ln in p.stderr.splitlines():
        if ln.startswith(('registry:', 'gate-misses', 'note:')):
            print('   | ' + ln, flush=True)
    print('   ctx row: ' + next(
        (ln for ln in p.stderr.splitlines()
         if ln.startswith('row context-capacity')), 'n/a'), flush=True)


def main():
    for label, tip in TIPS.items():
        run_one(label, tip)


if __name__ == '__main__':
    main()
