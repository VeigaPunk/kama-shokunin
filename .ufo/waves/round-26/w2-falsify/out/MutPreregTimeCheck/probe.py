#!/usr/bin/env python3
"""Fixed behavioral detector for the four assigned prereg-time-check mutants.

Does not modify checker bytes. Each invocation runs the same cases, including
shipped selftest, historical files, and two explicitly supplemental boundaries.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path('/fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/MutPreregTimeCheck')
CHECKER = ROOT / 'work/tools/prereg-time-check.py'
HISTORY = ROOT / 'history.git'
TIP = 'f4066979096e3452ae731c0e09e50155c6d8258a'
ENV = dict(os.environ)
for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
    ENV.pop(key, None)
ENV.update({'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null',
            'GIT_TERMINAL_PROMPT': '0', 'PYTHONDONTWRITEBYTECODE': '1',
            'GIT_AUTHOR_NAME': 'mutation-probe', 'GIT_AUTHOR_EMAIL': 'probe@local',
            'GIT_COMMITTER_NAME': 'mutation-probe', 'GIT_COMMITTER_EMAIL': 'probe@local'})


def run(command, *, extra_env=None):
    env = dict(ENV)
    env.update(extra_env or {})
    bounded = ['timeout', '--kill-after=2', '45', *map(str, command)]
    p = subprocess.run(bounded, cwd=ROOT, env=env, capture_output=True, text=True, timeout=50)
    return {'command': shlex.join(bounded), 'exit_code': p.returncode,
            'stdout': p.stdout, 'stderr': p.stderr}


def prepare_fixtures():
    repo = ROOT / 'boundary-fixtures'
    metadata = ROOT / 'boundary-fixtures.json'
    if metadata.exists():
        return json.loads(metadata.read_text())
    repo.mkdir()
    setup = []
    setup.append(run(['git', '-C', repo, 'init', '-q']))
    fixtures = []
    for name, stamp, author, expected in (
        ('supplement-author-skew', '2026-10-23T03:18:51Z', '2026-10-23T03:00:00+00:00', 0),
        ('supplement-subminute-future', '2026-10-23T03:19:59Z', '2026-10-23T03:19:43+00:00', 1),
    ):
        commit_time = '2026-10-23T03:19:43+00:00'
        (repo / 'f.json').write_text(json.dumps({'written_utc': stamp}) + '\n')
        dates = {'GIT_AUTHOR_DATE': author, 'GIT_COMMITTER_DATE': commit_time}
        setup.append(run(['git', '-C', repo, 'add', 'f.json']))
        setup.append(run(['git', '-C', repo, 'commit', '-q', '-m', name], extra_env=dates))
        revision = run(['git', '-C', repo, 'rev-parse', 'HEAD'])
        setup.append(revision)
        fixtures.append({'name': name, 'repo': str(repo), 'path': 'f.json',
                         'rev': revision['stdout'].strip(), 'expected': expected,
                         'content': {'written_utc': stamp}, 'author_time': author,
                         'committer_time': commit_time})
    for result in setup:
        if result['exit_code']:
            raise RuntimeError(json.dumps(result))
    payload = {'setup': setup, 'fixtures': fixtures}
    metadata.write_text(json.dumps(payload, indent=2) + '\n')
    return payload


def main():
    phase = sys.argv[1]
    if not phase.replace('-', '').isalnum():
        raise SystemExit('phase must be alphanumeric/hyphen')
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / f'{phase}.json').exists():
        raise SystemExit('refusing to overwrite phase evidence')
    fixtures = prepare_fixtures()
    records = []

    def case(name, argv, expected, required=()):
        record = {'name': name, 'expected_exit': expected, 'required_output': list(required),
                  **run(['python3', CHECKER, *argv])}
        record['detector_pass'] = (record['exit_code'] == expected and
                                   all(s in record['stdout'] for s in required))
        records.append(record)

    case('shipped-selftest', ['--selftest', '--scratch', ROOT / 'selftests'], 0,
         ('SELFTEST PASS',))
    r26 = '.ufo/waves/round-26/preregistration.json'
    real_cases = [
        ('r26-freeze', r26, 'a4a159c39967e88a89b0808dcd201c79c474efd1', 1,
         ('committer_time=2026-10-23T00:18:51-03:00 max_future=86400',
          '2026-10-23T03:45Z (later than commit by 1569s)')),
        ('r26-A0', r26, 'a12850c5cbc1013e60cc5bba2d6800d1cd634499', 1,
         ('2026-10-23T03:45Z (later than commit by 1517s)',
          '2026-10-23T03:55Z (later than commit by 2117s)')),
        ('r26-corrected', r26, 'f071209a0f956680b5722e09242e784a1644e216', 0, ()),
        ('r26-tip', r26, TIP, 0, ('future beyond horizon',)),
        ('r25-original', '.ufo/waves/round-25/preregistration.json',
         'efe58e96e6cfbef88a0fba9d64505e18b7ad7356', 1, ('later than commit by 76s',)),
        ('r25-amendment-1', '.ufo/waves/round-25/preregistration-amendment-1.json',
         'efe58e96e6cfbef88a0fba9d64505e18b7ad7356', 1,
         ('later than commit by 16s', 'later than commit by 76s')),
        ('r25-amendment-2', '.ufo/waves/round-25/preregistration-amendment-2.json',
         '5388b7cf1d5bad9c228da6f95c40f323414be2f1', 1, ('later than commit by 76s',)),
        ('r25-amendment-3', '.ufo/waves/round-25/preregistration-amendment-3.json',
         'c808ba07f09c4be55413d3d6516c542ab69b64f8', 1, ('later than commit by 75s',)),
        ('r25-amendment-4', '.ufo/waves/round-25/preregistration-amendment-4.json',
         '46fb04bd54978a2a3c47b3da098a2526804014e0', 0, ()),
    ]
    for name, path, rev, expected, required in real_cases:
        case(name, ['--repo', HISTORY, '--path', path, '--rev', rev], expected, required)
    for fixture in fixtures['fixtures']:
        case(fixture['name'], ['--repo', fixture['repo'], '--path', fixture['path'],
                               '--rev', fixture['rev']], fixture['expected'])
    byte_hash = hashlib.sha256(CHECKER.read_bytes()).hexdigest()
    detector_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    failed = [record['name'] for record in records if not record['detector_pass']]
    payload = {'phase': phase, 'checker_sha256': byte_hash, 'detector_sha256': detector_hash,
               'environment': {key: ENV.get(key) for key in
                               ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
                                'GIT_CONFIG_GLOBAL', 'GIT_CONFIG_SYSTEM')},
               'records': records, 'failed_cases': failed,
               'detector_exit': int(bool(failed))}
    (OUT / f'{phase}.json').write_text(json.dumps(payload, indent=2) + '\n')
    text = [f'phase={phase}', f'checker_sha256={byte_hash}', f'detector_sha256={detector_hash}']
    for record in records:
        text.extend(('', f"== {record['name']} ==", f"$ {record['command']}",
                     f"expected_exit={record['expected_exit']} exit={record['exit_code']} detector_pass={record['detector_pass']}",
                     record['stdout'].rstrip(), 'stderr: ' + record['stderr'].rstrip()))
    text.extend(('', 'failed_cases=' + repr(failed), f'detector_exit={int(bool(failed))}'))
    (OUT / f'{phase}.txt').write_text('\n'.join(text) + '\n')
    print(f'phase={phase} checker_sha256={byte_hash} detector_sha256={detector_hash}')
    for record in records:
        print(f"{record['name']}: expected={record['expected_exit']} got={record['exit_code']} detector_pass={record['detector_pass']}")
    print('failed_cases=' + repr(failed))
    return int(bool(failed))


if __name__ == '__main__':
    sys.exit(main())
