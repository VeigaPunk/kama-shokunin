#!/usr/bin/env python3
"""MT40 third mutant round: isolate the field each survivor exploits.

Every tip is base + exactly one registry edit; the UNMUTATED counter scores it.
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


def g(*a):
    return subprocess.run(['git', '-C', CLONE, *a], capture_output=True,
                          text=True)


def read_reg():
    with open(os.path.join(CLONE, REG), 'rb') as fh:
        return fh.read()


def rows_of(data):
    lines = data.decode().split('\n')
    return lines[0].split('\t'), [ln for ln in lines[1:] if ln]


def emit(header, body):
    return ('\n'.join(['\t'.join(header)] + body) + '\n').encode()


def edit_ctx(body, **kw):
    """Apply cell edits to the context-capacity row (idx: cap,1 quote,
    2 binding,3 run,4 pattern,5 verdict,6 observed,7 outcomes,8 note)."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        if c[0] == 'context-capacity-receipt':
            for i, v in kw.items():
                c[int(i)] = v
    return r


def m23_ctx_verdict_true_observed_busy(header, body):
    """M23: ctx verdict=true but observed keeps the host-busy text."""
    r = edit_ctx(body, **{'5': 'true'})
    return emit(header, ['\t'.join(c) for c in r])


def m24_ctx_verdict_busy_observed_idle(header, body):
    """M24: ctx verdict=host-busy but observed carries the idle pattern."""
    r = edit_ctx(body, **{'6': '"all_ports_closed": true'})
    return emit(header, ['\t'.join(c) for c in r])


def m25_pinwatch_verdict_hostbusy(header, body):
    """M25: a single-outcome row claims the host-busy verdict."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        if c[0] == 'pin-watch':
            c[5] = 'host-busy'
    return emit(header, ['\t'.join(c) for c in r])


def m26_quote_other_capability(header, body):
    """M26: row 1 quotes another capability's canonical text."""
    r = [ln.split('\t') for ln in body]
    r[0][1] = 'Reconcile ca'
    return emit(header, ['\t'.join(c) for c in r])


def m27_quote_prefix_fragment(header, body):
    """M27: row 1 quotes a prefix fragment of its own canonical row."""
    r = [ln.split('\t') for ln in body]
    r[0][1] = '| sources-registry'
    return emit(header, ['\t'.join(c) for c in r])


def m28_row_order_shuffled(header, body):
    """M28: the 12 rows in reverse order (a reordering, not a change)."""
    return emit(header, list(reversed(body)))


def m29_note_every_row_rewritten(header, body):
    """M29: every row's note replaced with a false statement."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        c[8] = 'this capability was verified by printing a line, not by running it'
    return emit(header, ['\t'.join(c) for c in r])


def m30_ctx_note_empty(header, body):
    """M30: the ctx note emptied."""
    r = edit_ctx(body, **{'8': ''})
    return emit(header, ['\t'.join(c) for c in r])


MUTANTS3 = [
    ('M23-ctx-verdict-true-observed-busy', m23_ctx_verdict_true_observed_busy),
    ('M24-ctx-verdict-busy-observed-idle', m24_ctx_verdict_busy_observed_idle),
    ('M25-pinwatch-verdict-host-busy', m25_pinwatch_verdict_hostbusy),
    ('M26-quote-other-capability-text', m26_quote_other_capability),
    ('M27-quote-prefix-fragment', m27_quote_prefix_fragment),
    ('M28-rows-reversed-order', m28_row_order_shuffled),
    ('M29-all-notes-false-statement', m29_note_every_row_rewritten),
    ('M30-ctx-note-empty', m30_ctx_note_empty),
]


def commit_all():
    base = read_reg()
    header, body = rows_of(base)
    tips = []
    for name, fn in MUTANTS3:
        g('checkout', '-q', BASE, '--', REG)
        data = fn(header, body)
        assert data != base, name
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
    work = os.path.join(SCRATCH, 'work4-' + name)
    shutil.rmtree(work, ignore_errors=True)
    env = dict(os.environ, PATH=PATH)
    cmd = [sys.executable, 'tools/round64-c2-counter.py', '--repo', CLONE,
           '--tip', tip, '--work', work]
    t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=CLONE, capture_output=True, text=True,
                       env=env)
    for ext, data in (('.out', p.stdout), ('.err', p.stderr)):
        with open(os.path.join(OUT, name + ext), 'w') as fh:
            fh.write(data)
    shutil.rmtree(work, ignore_errors=True)
    return name, tip, p.returncode, p.stdout, p.stderr, round(
        time.monotonic() - t0, 1)


def report(res):
    name, tip, rc, out, err, secs = res
    print('== %-40s tip=%s rc=%s (%ss)' % (name, tip[:12], rc, secs),
          flush=True)
    print('   ' + out.strip().replace('\n', '\n   '), flush=True)
    for ln in err.splitlines():
        if ln.startswith(('registry:', 'problem:', 'gate-misses',
                          'control-escape', 'note:')):
            print('   | ' + ln, flush=True)


def main():
    tips = commit_all()
    with ThreadPoolExecutor(max_workers=3) as pool:
        for res in pool.map(lambda t: run_one(t[0], t[1]), tips):
            report(res)


if __name__ == '__main__':
    main()
