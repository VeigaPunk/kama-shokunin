#!/usr/bin/env python3
"""Bounded, isolated artifact runner for MutateTimeCheck; mutations are external edits."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
OUT = LANE / '.ufo/waves/round-29/w1/out/MutateTimeCheck'
SCRATCH = Path('/fast/scratch/hyaku/kama-r29/w1/MutateTimeCheck')
SOURCE = LANE / 'tools/prereg-time-check.py'
EXPECTED_SOURCE = 'ca72edf2a210a763c1d8cbc7a57aa70445a2794c195fc288e82d6dfe7d473dd4'
REV = '75b78bb4900aae1edcdb6b229bb8c572c20fcbce'
PATH = '.ufo/waves/round-28/preregistration.json'
IDS = [f'M{i:02d}' for i in range(1, 9)]
MAX_BYTES = 1024 * 1024 - 1
ENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
ENV.update({'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_TERMINAL_PROMPT': '0', 'PYTHONDONTWRITEBYTECODE': '1',
            'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'})


def save(path: Path, value: str | bytes) -> None:
    data = value.encode() if isinstance(value, str) else value
    if len(data) > MAX_BYTES:
        raise RuntimeError(f'output exceeds bound: {path}: {len(data)}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def save_json(path: Path, obj: object) -> None:
    save(path, json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv: list[str], seconds: int = 30) -> dict:
    cmd = ['/usr/bin/timeout', '--signal=TERM', '--kill-after=2s', f'{seconds}s',
           '/usr/bin/prlimit', '--as=536870912', '--cpu=25', '--nofile=128', '--', *argv]
    p = subprocess.run(cmd, cwd=str(SCRATCH), env=ENV, capture_output=True,
                       timeout=seconds + 5)
    if len(p.stdout) + len(p.stderr) > MAX_BYTES:
        raise RuntimeError(f'command output exceeds bound: {argv}')
    return {'argv': cmd, 'rc': p.returncode,
            'stdout': p.stdout.decode(errors='replace'),
            'stderr': p.stderr.decode(errors='replace')}


def git(*args: str) -> dict:
    return run(['/usr/bin/git', '--no-replace-objects', '-C', str(LANE), *args])


def detector(mid: str, phase: str, tool: Path | None = None) -> dict:
    tool = tool or SCRATCH / f'{mid}.py'
    phase_out = OUT / 'receipts' / mid / phase
    before = sha(tool)
    results = {}
    for label, args in (
        ('selftest', ['--selftest', '--scratch', str(SCRATCH / 'selftests' / mid / phase)]),
        ('75b78bb4', ['--repo', str(LANE), '--path', PATH, '--rev', REV, '--strict']),
    ):
        result = run(['/usr/bin/python3', str(tool), *args])
        save(phase_out / f'{label}.out', result['stdout'])
        save(phase_out / f'{label}.err', result['stderr'])
        result['stdout_sha256'] = hashlib.sha256(result['stdout'].encode()).hexdigest()
        if label == 'selftest':
            result['meets_expected'] = (result['rc'] == 0 and 'SELFTEST PASS' in result['stdout']
                                        and '[FAIL]' not in result['stdout'])
        else:
            result['meets_expected'] = (result['rc'] == 1 and
                'FLAG line 41: 2026-10-23 ~08:45Z (later than commit by 404s)' in result['stdout']
                and 'RESULT fail: 1 timestamp(s) later than the committer time' in result['stdout'])
        save_json(phase_out / f'{label}.json', result)
        results[label] = result
    record = {'id': mid, 'phase': phase, 'tool': str(tool), 'before_sha256': before,
              'after_sha256': sha(tool), 'detectors': results,
              'meets_expected': all(r['meets_expected'] for r in results.values())}
    save_json(phase_out / 'result.json', record)
    return record


def batch(phase: str) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(lambda mid: detector(mid, phase), IDS))
    save_json(OUT / f'{phase}.json', records)
    for r in records:
        print(r['id'], phase, 'expected=' + str(r['meets_expected']),
              'rcs=' + ','.join(str(d['rc']) for d in r['detectors'].values()),
              'sha=' + r['after_sha256'])


def prepare() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if sha(SOURCE) != EXPECTED_SOURCE:
        raise RuntimeError('the assigned lane patch changed before the snapshot')
    for dest in [SCRATCH / 'pristine.py', *(SCRATCH / f'{mid}.py' for mid in IDS)]:
        p = run(['/usr/bin/cp', '--', str(SOURCE), str(dest)])
        if p['rc'] or sha(dest) != EXPECTED_SOURCE:
            raise RuntimeError(f'copy failed: {p}')
    head = git('rev-parse', 'HEAD')
    if head['rc']:
        raise RuntimeError(head)
    diff = git('diff', '35b90184', '513eba3b', '--', 'tools/prereg-time-check.py')
    save(OUT / 'source.diff', diff['stdout'])
    save_json(OUT / 'snapshot.json', {'source': str(SOURCE), 'source_sha256': sha(SOURCE),
               'pristine': str(SCRATCH / 'pristine.py'), 'head': head['stdout'].strip(),
               'source_diff': diff, 'ids': IDS, 'concurrency': 2,
               'bounds': 'timeout 30s + kill 2s; AS 512MiB; CPU 25s; nofile 128; outputs <1MiB',
               'axes': ['timestamp-form recall', 'detector sensitivity', 'exact restoration'],
               'detector': 'selftest exit 0/PASS plus historical --strict exit 1 and exact A1 404s FLAG'})
    batch('pristine')


def restore() -> None:
    # Whole-file restoration, never a text edit; restore every specimen even if one fails.
    records = []
    for mid in IDS:
        target = SCRATCH / f'{mid}.py'
        before = sha(target)
        result = run(['/usr/bin/cp', '--', str(SCRATCH / 'pristine.py'), str(target)])
        after = sha(target)
        records.append({'id': mid, 'before_sha256': before, 'after_sha256': after,
                        'exact': after == EXPECTED_SOURCE, 'copy': result})
    save_json(OUT / 'restoration.json', records)
    batch('restored')
    save_json(OUT / 'final-source.json', {'path': str(SOURCE), 'sha256': sha(SOURCE),
               'same_as_snapshot': sha(SOURCE) == EXPECTED_SOURCE,
               'pristine_sha256': sha(SCRATCH / 'pristine.py')})
    if not all(r['exact'] and r['copy']['rc'] == 0 for r in records):
        raise RuntimeError('not all copies restored exactly')


def history() -> None:
    snapshot = json.loads((OUT / 'snapshot.json').read_text())
    result = git('log', snapshot['head'], '--format=commit %H %cI', '--name-status', '--',
                 '.ufo/waves/*/preregistration.json')
    save(OUT / 'history-log.out', result['stdout'])
    if result['rc']:
        raise RuntimeError(result)
    versions = []
    current = None
    for line in result['stdout'].splitlines():
        if line.startswith('commit '):
            _, rev, ctime = line.split()
            current = (rev, ctime)
        elif line and '\t' in line:
            status, path = line.split('\t', 1)
            if status == 'D':
                continue
            if current is None:
                raise RuntimeError('history parse error')
            rev, ctime = current
            versions.append({'rev': rev, 'commit_time': ctime, 'path': path, 'status': status})

    def one(v: dict) -> dict:
        stem = v['rev'][:12]
        blob = git('show', f"{v['rev']}:{v['path']}")
        save(OUT / 'history' / f'{stem}.source.json', blob['stdout'])
        v['blob_sha256'] = hashlib.sha256(blob['stdout'].encode()).hexdigest()
        v['blob_rc'] = blob['rc']
        v['source_file'] = str(OUT / 'history' / f'{stem}.source.json')
        v['modes'] = {}
        for mode, args in (('default', []), ('strict', ['--strict'])):
            r = run(['/usr/bin/python3', str(SCRATCH / 'pristine.py'), '--repo', str(LANE),
                     '--path', v['path'], '--rev', v['rev'], *args])
            save(OUT / 'history' / f'{stem}.{mode}.out', r['stdout'])
            save(OUT / 'history' / f'{stem}.{mode}.err', r['stderr'])
            r['flags'] = [line.strip() for line in r['stdout'].splitlines() if 'FLAG line ' in line]
            v['modes'][mode] = r
        return v

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(one, versions))
    save_json(OUT / 'history.json', records)
    for v in records:
        print(v['rev'][:12], v['path'], 'default=' + str(v['modes']['default']['rc']),
              'strict=' + str(v['modes']['strict']['rc']))
        for mode in ('default', 'strict'):
            for line in v['modes'][mode]['flags']:
                print(' ', mode, line)


def main() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (768 * 1024 * 1024, 768 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    OUT.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1]
    if mode == 'prepare':
        prepare()
    elif mode == 'mutated':
        try:
            batch('mutated')
        finally:
            restore()
    elif mode == 'restore':
        restore()
    elif mode == 'history':
        history()
    else:
        raise SystemExit('unknown phase')


if __name__ == '__main__':
    main()
