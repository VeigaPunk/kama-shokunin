#!/usr/bin/env python3
"""MT40 registry-row mutants for the round-64 C2 counter.

Each mutant rewrites registry/capability-claims-r64.tsv in the scratch clone,
is committed, and is scored by the UNMUTATED counter run from the clone's
tools/ directory against the committed tip.
"""
import os
import subprocess
import sys

CLONE = '/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows/clone'
BASE = '23b3fdb1a925129a9961cf551f6d40bf251602cb'
REG = 'registry/capability-claims-r64.tsv'
OUT = '/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows/out'
SCRATCH = '/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows'


def g(*a, **kw):
    return subprocess.run(['git', '-C', CLONE, *a], capture_output=True,
                          text=True, **kw)


def read_reg():
    with open(os.path.join(CLONE, REG), 'rb') as fh:
        return fh.read()


def write_reg(data):
    with open(os.path.join(CLONE, REG), 'wb') as fh:
        fh.write(data)


def rows_of(data):
    txt = data.decode()
    lines = txt.split('\n')
    header = lines[0].split('\t')
    body = [ln for ln in lines[1:] if ln]
    return header, body


def emit(header, body):
    return ('\n'.join(['\t'.join(header)] + body) + '\n').encode()


def m_swap_run(header, body):
    """M1: swap the run templates of rows 1 and 2."""
    r = [ln.split('\t') for ln in body]
    r[0][3], r[1][3] = r[1][3], r[0][3]
    return emit(header, ['\t'.join(c) for c in r])


def m_quote_short(header, body):
    """M2: shorten the quote below the 8-char floor."""
    r = [ln.split('\t') for ln in body]
    r[0][1] = 'Curate'
    return emit(header, ['\t'.join(c) for c in r])


def m_observed(header, body):
    """M3: change the observed column of row 1."""
    r = [ln.split('\t') for ln in body]
    r[0][6] = 'FORGED-OBSERVED'
    return emit(header, ['\t'.join(c) for c in r])


def m_dup_row(header, body):
    """M4: add a duplicate of row 1."""
    return emit(header, body + [body[0]])


def m_pattern_usage(header, body):
    """M5: point the pattern at a usage line the tool prints regardless."""
    r = [ln.split('\t') for ln in body]
    r[0][4] = 'usage:'
    return emit(header, ['\t'.join(c) for c in r])


def m_extra_cap(header, body):
    """M6: add a 13th capability row."""
    extra = ['extra-capability', 'Extra binding row', 'selftest',
             'python3 %T/tools/pin-watch.py selftest',
             'selftest pass=9 fail=0', 'true', 'selftest pass=9 fail=0',
             'true', 'added by MT40 as a thirteenth capability']
    return emit(header, body + ['\t'.join(extra)])


def m_drop_outcomes(header, body):
    """M7: remove the outcomes column entirely."""
    i = header.index('outcomes')
    h2 = header[:i] + header[i + 1:]
    b2 = []
    for ln in body:
        c = ln.split('\t')
        b2.append('\t'.join(c[:i] + c[i + 1:]))
    return emit(h2, b2)


def m_binding(header, body):
    """M8: change the binding word of row 1."""
    r = [ln.split('\t') for ln in body]
    r[0][2] = 'scan'
    return emit(header, ['\t'.join(c) for c in r])


def m_tab_in_cell(header, body):
    """M9: put a TAB inside a cell."""
    r = [ln.split('\t') for ln in body]
    r[0][1] = 'Curate\twhere'
    return emit(header, ['\t'.join(c) for c in r])


def m_verdict_ctx(header, body):
    """M10: the context-capacity row claims the idle outcome while the
    measured host was busy."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        if c[0] == 'context-capacity-receipt':
            c[5] = 'true'
            c[6] = '"all_ports_closed": true'
    return emit(header, ['\t'.join(c) for c in r])


def m_note_ctx(header, body):
    """M11: rewrite the note of the context-capacity row with a false
    statement about how the idle outcome was proved."""
    r = [ln.split('\t') for ln in body]
    for c in r:
        if c[0] == 'context-capacity-receipt':
            c[8] = ('the idle outcome was observed live on the measured host; '
                    'no copy of the tool was run')
    return emit(header, ['\t'.join(c) for c in r])


def m_quote_other(header, body):
    """M12: replace the quote with a different substring of the canonical
    row prefix (still 8+ chars)."""
    r = [ln.split('\t') for ln in body]
    r[0][1] = 'Curate where kama learns'
    return emit(header, ['\t'.join(c) for c in r])


MUTANTS = [
    ('M01-swap-run-templates', m_swap_run),
    ('M02-quote-below-floor', m_quote_short),
    ('M03-change-observed', m_observed),
    ('M04-duplicate-row', m_dup_row),
    ('M05-pattern-usage-line', m_pattern_usage),
    ('M06-thirteenth-capability', m_extra_cap),
    ('M07-drop-outcomes-column', m_drop_outcomes),
    ('M08-change-binding-word', m_binding),
    ('M09-tab-inside-cell', m_tab_in_cell),
    ('M10-ctx-verdict-vs-live-outcome', m_verdict_ctx),
    ('M11-ctx-note-false-statement', m_note_ctx),
    ('M12-quote-other-substring', m_quote_other),
]


def main():
    only = sys.argv[1:] or None
    os.makedirs(OUT, exist_ok=True)
    base_bytes = None
    for name, fn in MUTANTS:
        if only and name not in only:
            continue
        # reset the registry to the base blob, then apply the mutation
        g('checkout', '-q', BASE, '--', REG)
        if base_bytes is None:
            base_bytes = read_reg()
        header, body = rows_of(base_bytes)
        data = fn(header, body)
        assert data != base_bytes, name
        write_reg(data)
        g('add', '-A')
        c = subprocess.run(['git', '-C', CLONE, '-c', 'user.name=seat',
                            '-c', 'user.email=seat@seat.invalid', 'commit',
                            '-q', '-m', 'MT40 ' + name], capture_output=True,
                           text=True)
        if c.returncode != 0:
            print(name, 'COMMIT FAILED', c.stderr, flush=True)
            continue
        tip = g('rev-parse', 'HEAD').stdout.strip()
        work = os.path.join(SCRATCH, 'work-' + name)
        cmd = [sys.executable, 'tools/round64-c2-counter.py', '--repo', CLONE,
               '--tip', tip, '--work', work]
        p = subprocess.run(cmd, cwd=CLONE, capture_output=True, text=True)
        with open(os.path.join(OUT, name + '.out'), 'w') as fh:
            fh.write(p.stdout)
        with open(os.path.join(OUT, name + '.err'), 'w') as fh:
            fh.write(p.stderr)
        with open(os.path.join(OUT, name + '.cmd'), 'w') as fh:
            fh.write(' '.join(cmd) + '\n')
        print('== %s tip=%s rc=%s' % (name, tip[:12], p.returncode),
              flush=True)
        print('   ' + p.stdout.strip().replace('\n', '\n   '), flush=True)
        reg_lines = [ln for ln in p.stderr.splitlines()
                     if ln.startswith('registry:') or ln.startswith('problem:')
                     or ln.startswith('gate-misses')
                     or ln.startswith('control-escape')
                     or ln.startswith('note:')]
        for ln in reg_lines[:14]:
            print('   | ' + ln, flush=True)
        # keep the counter's scratch for inspection, then drop the tip tree
        subprocess.run(['rm', '-rf', work], check=False)
    g('checkout', '-q', BASE, '--', REG)


if __name__ == '__main__':
    main()
