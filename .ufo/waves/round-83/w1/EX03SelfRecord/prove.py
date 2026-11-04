import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
OUT = ROOT / '.ufo/waves/round-83/w1/EX03SelfRecord'
S = Path('/fast/scratch/hyaku/kama-r83/EX03SelfRecord')
D = S / 'clone'
BASE = '30d8eac394a8714fad3dc792b74a45a25b4366a2'
SEALED = 'b1ba614b51255a3dcfe3e0946f32f8e31bd65c09'
records = []

def git(*args):
    assert subprocess.check_output(['git', '-C', str(D), 'rev-parse', '--show-toplevel'], text=True).strip() == str(D)
    return subprocess.check_output(['git', '-C', str(D), *args], text=True, stderr=subprocess.STDOUT)

def commit(label, paths):
    git('add', '--', *paths)
    git('-c', 'user.name=EX03 fixture', '-c', 'user.email=ex03@example.invalid', 'commit', '-qm', label)

def run(name, *flags):
    name = 'sealed-final-' + name
    cmd = ['python3', str(D / 'tools/round83-selfrecord-round82.py'), '--repo', str(D), *flags]
    proc = subprocess.run(cmd, cwd=D, capture_output=True, text=True)
    (OUT / (name + '.out')).write_text(proc.stdout)
    (OUT / (name + '.err')).write_text(proc.stderr)
    record = dict(name=name, command=cmd, exit=proc.returncode, stdout=str(OUT / (name + '.out')), stderr=str(OUT / (name + '.err')), revision=git('rev-parse', 'HEAD').strip())
    records.append(record)
    print(json.dumps(record), flush=True)
    print(proc.stdout, end='', flush=True)
    print(proc.stderr, end='', flush=True)

try:
    S.mkdir(parents=True, exist_ok=True)
    os.environ['TMPDIR'] = str(S)
    subprocess.run(['git', 'clone', '--shared', str(ROOT), str(D)], check=True, capture_output=True)
    git('checkout', '-B', 'master', BASE)
    shutil.copyfile(OUT / 'round83-selfrecord-round82.py', D / 'tools/round83-selfrecord-round82.py')
    commit('EX03 counter fixture', ['tools/round83-selfrecord-round82.py'])
    run('enumerate', '--enumerate')
    lesson = D / 'corpus/lessons/round-83.md'
    lesson.write_text('# Round 83 fixture\n\n## Corrections\n\n' + '\n'.join([
        f'corrected F1 old=log82-c1-selftest=18 new=log82-c1-selftest=23 at={SEALED} date=2026-11-04 fix=LOG.md',
        f'corrected F2 old=sc82c1-selftest=22 new=sc82c1-selftest=23 at={SEALED} date=2026-11-04 fix=SCORECARD.md',
        f'corrected F3 old=calib82-selftest=22 new=calib82-selftest=23 at={SEALED} date=2026-11-04 fix=SCORECARD.md',
    ]) + '\n')
    with (D / 'LOG.md').open('a') as stream:
        stream.write('\nLOG-CORRECTION round=82 field=c1-selftest old=pass=18 new=pass=23 log82-c1-selftest=23\n')
    with (D / 'SCORECARD.md').open('a') as stream:
        stream.write('\n#### round-83 correction\n\nSuperseded pass=22 twice; sc82c1-selftest=23 calib82-selftest=23\n')
    commit('EX03 requested correction records only', ['corpus/lessons/round-83.md', 'LOG.md', 'SCORECARD.md'])
    run('no-corrections', '--no-corrections')
    run('records-only')
    with (D / 'LOG.md').open('a') as stream:
        stream.write('\n## Round 83 witness binding\n\nRound-82 c1-selftest.out: SELFRECORD_R81_SELFTEST pass=23 fail=0; log82-c1-selftest=23\n')
    with (D / 'SCORECARD.md').open('a') as stream:
        stream.write('\n## Round 83 witness binding\n\nRound-82 c1-selftest.out: SELFRECORD_R81_SELFTEST pass=23 fail=0; sc82c1-selftest=23 calib82-selftest=23\n')
    commit('EX03 independent receipt binding outside restatements', ['LOG.md', 'SCORECARD.md'])
    run('honest')
    run('selftest', '--selftest')
finally:
    (OUT / 'EX03.json').write_text(json.dumps(dict(axis='calibration', base=BASE, sealed=SEALED, runs=records, scratch_removed=True, installs=[], lsp='unavailable: no mounted LSP tool'), indent=2) + '\n')
    shutil.rmtree(S, ignore_errors=True)
