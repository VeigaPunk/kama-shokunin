#!/usr/bin/env python3
"""M15C2AttackWeak — weak-family falsification probes against the frozen
round-62 C2 counter (master 65d7cad0fce90e34de37527cde22e97b63b118bf).

Phases:
  A pristine  : real counter main() on the lane at master  (baseline)
  B registry mutations on warm cache: V1/V1b pattern shortened to a substring,
    V3a observed column emptied, V3b observed column replaced by 'a'
  C tip-tree tool mutated to emit the frozen pattern inside one deceptive
    line (stdout variant, then stderr-only variant); real counter main() again
  D bytes restored (sha256-verified); real counter main() again
All work under this scratch dir; the lane repo is only read (git show/archive).
"""
import hashlib
import os
import shutil
import subprocess
import sys

SW = os.path.dirname(os.path.abspath(__file__))
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TIP = '65d7cad0fce90e34de37527cde22e97b63b118bf'
sys.path.insert(0, os.path.join(SW, 'mod'))
import importlib.util as _ilu  # noqa: E402
_spec = _ilu.spec_from_file_location(
    'round62_c2_counter', os.path.join(SW, 'mod', 'round62-c2-counter.py'))
C = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(C)  # frozen instrument, unmodified bytes

WORK = os.path.join(SW, 'work')
SCRATCH = os.path.join(WORK, 'run')
TIP_TREE = os.path.join(WORK, 'tip')
os.makedirs(SCRATCH, exist_ok=True)
ENV = dict(os.environ)
ENV['TMPDIR'] = SCRATCH
ENV.pop('PYTHONPATH', None)

with open(os.path.join(SW, 'reg-pristine.tsv'), encoding='utf-8') as fh:
    PRISTINE = fh.read()

POP = [(slug, C.MANIFEST[slug][0]) for slug, _, _ in C._MANIFEST]


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def met_formula(f, canonical_ok=True):
    return bool(canonical_ok
                and f['covered'] == f['population']
                and f['bound'] >= f['population']
                and f['dead'] == 0 and f['mismatches'] == 0
                and f['errors'] == 0)


def facts_line(tag, f, met):
    print(f"[{tag}] population={f['population']} rows={f['rows']} "
          f"covered={f['covered']}/{f['population']} bound={f['bound']} "
          f"sensitive={f['sensitive']}/{f['bound']} dead={f['dead']} "
          f"mismatches={f['mismatches']} errors={f['errors']} met={met}")
    for e in f['err_list'][:6]:
        print(f"[{tag}] error: {e}")


def score(tag, reg_text, canonical_ok=True):
    f = C.score_registry(reg_text, TIP_TREE, SCRATCH, LANE, TIP, ENV,
                         population=POP)
    m = met_formula(f, canonical_ok)
    facts_line(tag, f, m)
    print(f"[{tag}] VERDICT: {'ACCEPTED' if m else 'REJECTED'}")
    return f, m


def drop_cache(cap):
    C._EXEC_CACHE.pop((TIP, cap), None)


def phase_a():
    print('=== Phase A: pristine (real counter main) ===', flush=True)
    rc = C.main(['--repo', LANE, '--tip', TIP, '--work', WORK])
    print(f'[A] counter exit={rc} (0 == met)')
    print('=== Phase A detail: cached run results per capability ===',
          flush=True)
    for (tip, cap), (v, obs, sens, dead) in sorted(
            C._EXEC_CACHE.items()):
        print(f'[A-detail] {cap}: verdict={v} sensitive={sens} dead={dead} '
              f'observed={obs[:300]!r}')


def phase_b():
    print('=== Phase B: registry mutations (warm cache) ===', flush=True)
    # V1: weak family — pattern shortened to a substring (sources-registry)
    v1 = PRISTINE.replace('\t45/45 selftest cases passed\t',
                          '\tpass\t', 1)
    assert v1 != PRISTINE
    score('V1 weak: pattern->substring (sources-registry)', v1)
    # V1b: same family, different row (instrument-agreement)
    v1b = PRISTINE.replace('\tIA_SELFTEST pass=\t', '\tpass=\t', 1)
    assert v1b != PRISTINE
    score('V1b weak: pattern->substring (instrument-agreement)', v1b)
    # V3a: observed column emptied on every row
    v3a = '\n'.join(
        (lambda c: '\t'.join(c[:6] + [''] + c[7:]))(ln.split('\t'))
        if not ln.startswith('#') and not ln.startswith('cap\t') and ln.strip()
        else ln
        for ln in PRISTINE.splitlines()) + '\n'
    score('V3a: observed column emptied (all rows)', v3a)
    # V3b: observed column replaced by a trivially-matching 'a' (one row)
    lines = PRISTINE.splitlines()
    for i, ln in enumerate(lines):
        c = ln.split('\t')
        if len(c) == 8 and c[0] == 'sources-registry':
            c[6] = 'a'
            lines[i] = '\t'.join(c)
            break
    score('V3b: observed column -> "a" (sources-registry)',
          '\n'.join(lines) + '\n')


def phase_c():
    print('=== Phase C: deceptive-line tool mutant (tip-tree copy in scratch)',
          flush=True)
    tool = os.path.join(TIP_TREE, 'tools', 'sources-append-only.py')
    orig = tool + '.orig-M15C2AttackWeak'
    shutil.copy2(tool, orig)
    before = sha(tool)
    print(f'[C] tool sha256 before mutation: {before}')
    MUTANT = (
        '#!/usr/bin/env python3\n'
        '"""[M15C2AttackWeak mutant] emits the frozen pattern as a substring\n'
        'of one deceptive line; runs no checks; exits 0."""\n'
        'import sys\n'
        'msg = ("45/45 selftest cases passed "\n'
        '       "(RETRACTED - 0/45 checks executed, verdict FAIL)")\n'
        'if "--stderr" in sys.argv:\n'
        '    print(msg, file=sys.stderr)\n'
        'else:\n'
        '    print(msg)\n'
        'sys.exit(0)\n'
    )
    with open(tool, 'w', encoding='utf-8') as fh:
        fh.write(MUTANT)
    after = sha(tool)
    print(f'[C] tool sha256 after mutation:  {after}')
    drop_cache('sources-registry')
    # C1: full scoring of the PRISTINE registry against the deceptive tool
    f, m = score('C-mutant: pristine registry, deceptive tool output',
                 PRISTINE)
    # C0: row-level acceptance of the lying row, direct run_bound
    row0 = dict(next(r for r in C.parse_registry(PRISTINE)[0]
                     if r['cap'] == 'sources-registry'))
    v0, obs0, sens0, dead0 = C.run_bound(
        row0, C.MANIFEST['sources-registry'][1], TIP_TREE, SCRATCH, LANE,
        TIP, ENV)
    print(f'[C-mutant] row sources-registry: verdict={v0} observed={obs0!r} '
          f'sensitive={sens0} dead={dead0} -> ROW ACCEPTED='
          f'{v0 and sens0 and not dead0}')
    # C2: full real-counter main() against the deceptive tool
    rc = C.main(['--repo', LANE, '--tip', TIP, '--work', WORK])
    print(f'[C-mutant] counter exit={rc} (0 == met)')
    # C3: stderr-only deceptive emission, direct run_bound
    row = next(r for r in C.parse_registry(PRISTINE)[0]
               if r['cap'] == 'sources-registry')
    row = dict(row)
    row['run'] = row['run'] + ' --stderr'
    tpl = dict(C.MANIFEST['sources-registry'][1][0])
    tpl['run'] = tpl['run'] + ' --stderr'
    v, obs, sens, dead = C.run_bound(row, [tpl], TIP_TREE, SCRATCH, LANE,
                                     TIP, ENV)
    print(f'[C-stderr-only] verdict={v} observed={obs!r} sensitive={sens} '
          f'dead={dead} -> ACCEPTED={v and sens and not dead}')
    # C4: do the 8 control families notice the lying row?
    rejected, total, detail = C.controls(
        f, PRISTINE, TIP_TREE, SCRATCH, LANE, TIP, ENV, POP)
    esc = {k: d for k, d in detail.items() if d['met']}
    print(f'[C-mutant] controls_rejected={rejected}/{total} escapes={esc}')
    return orig, before


def phase_d(orig, before):
    print('=== Phase D: restore exact bytes ===', flush=True)
    tool = os.path.join(TIP_TREE, 'tools', 'sources-append-only.py')
    shutil.copy2(orig, tool)
    restored = sha(tool)
    print(f'[D] tool sha256 restored: {restored}  matches-pristine='
          f'{restored == before}')
    os.remove(orig)
    drop_cache('sources-registry')
    rc = C.main(['--repo', LANE, '--tip', TIP, '--work', WORK])
    print(f'[D] counter exit={rc} (0 == met)')
    row = next(r for r in C.parse_registry(PRISTINE)[0]
               if r['cap'] == 'sources-registry')
    tpls = C.MANIFEST['sources-registry'][1]
    v, obs, sens, dead = C.run_bound(dict(row), tpls, TIP_TREE, SCRATCH,
                                     LANE, TIP, ENV)
    print(f'[D] direct run_bound: verdict={v} observed={obs!r} '
          f'sensitive={sens} dead={dead}')


if __name__ == '__main__':
    phase_a()
    phase_b()
    orig, before = phase_c()
    phase_d(orig, before)
    print('=== driver complete ===')
