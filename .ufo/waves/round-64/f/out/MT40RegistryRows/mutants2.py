#!/usr/bin/env python3
"""MT40 second mutant round: sharper registry-row edits that isolate which
field the counter grades.

Run from the same scratch clone; every tip is base + exactly one edit, and
the UNMUTATED counter (tools/round64-c2-counter.py at the base tip) scores it.
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


def m13_swap_patterns(header, body):
    """M13: swap the pattern cells of rows 1 and 2."""
    r = [ln.split('\t') for ln in body]
    r[0][4], r[1][4] = r[1][4], r[0][4]
    return emit(header, ['\t'.join(c) for c in r])


def m14_ctx_outcomes(header, body):
    """M14: drop host-busy from the context-capacity row's declared
    outcomes."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        if c[0] == 'context-capacity-receipt':
            c[7] = 'true'
    return emit(header, ['\t'.join(c) for c in r])


def m15_tab_in_observed(header, body):
    """M15: a TAB inside the observed cell."""
    r = [ln.split('\t') for ln in body]
    r[0][6] = '45/45 selftest\tcases passed'
    return emit(header, ['\t'.join(c) for c in r])


def m16_dup_conflict(header, body):
    """M16: a second row for the same cap with different content."""
    r = [ln.split('\t') for ln in body]
    c = list(r[0])
    c[4] = 'conflict'
    return emit(header, body + ['\t'.join(c)])


def m17_quote_8chars(header, body):
    """M17: a quote exactly at the 8-char floor."""
    r = [ln.split('\t') for ln in body]
    r[0][1] = 'Curate w'
    return emit(header, ['\t'.join(c) for c in r])


def m18_ctx_observed_busy_pattern(header, body):
    """M18: the context-capacity row keeps verdict=host-busy but records the
    idle pattern as observed."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        if c[0] == 'context-capacity-receipt':
            c[6] = '"all_ports_closed": true'
    return emit(header, ['\t'.join(c) for c in r])


def m19_verdict_false(header, body):
    """M19: verdict=false on row 1."""
    r = [ln.split('\t') for ln in body]
    r[0][5] = 'false'
    return emit(header, ['\t'.join(c) for c in r])


def m20_ctx_observed_other_row(header, body):
    """M20: the context-capacity row records another capability's observed
    text."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        if c[0] == 'context-capacity-receipt':
            c[6] = '45/45 selftest cases passed'
    return emit(header, ['\t'.join(c) for c in r])


def m21_ctx_note_true_claim(header, body):
    """M21: the context-capacity row's note claims the idle outcome was
    observed live on the measured host (a false statement about the run)."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        if c[0] == 'context-capacity-receipt':
            c[8] = ('the idle outcome was observed live on the measured host '
                    'with no copy of the tool')
    return emit(header, ['\t'.join(c) for c in r])


def m22_cap_renamed(header, body):
    """M22: rename row 1's cap to another bound cap (cross-binding)."""
    r = [ln.split('\t') for ln in body]
    r[0][0] = 'pin-watch'
    return emit(header, ['\t'.join(c) for c in r])


MUTANTS2 = [
    ('M13-swap-pattern-cells', m13_swap_patterns),
    ('M14-ctx-outcomes-drop-host-busy', m14_ctx_outcomes),
    ('M15-tab-inside-observed', m15_tab_in_observed),
    ('M16-duplicate-row-conflict', m16_dup_conflict),
    ('M17-quote-at-8-char-floor', m17_quote_8chars),
    ('M18-ctx-observed-idle-pattern', m18_ctx_observed_busy_pattern),
    ('M19-verdict-false', m19_verdict_false),
    ('M20-ctx-observed-other-row', m20_ctx_observed_other_row),
    ('M21-ctx-note-false-claim', m21_ctx_note_true_claim),
    ('M22-cap-renamed-cross-binding', m22_cap_renamed),
]


def commit_all():
    base = read_reg()
    header, body = rows_of(base)
    tips = []
    for name, fn in MUTANTS2:
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
    work = os.path.join(SCRATCH, 'work3-' + name)
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
    print('== %-38s tip=%s rc=%s (%ss)' % (name, tip[:12], rc, secs),
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
