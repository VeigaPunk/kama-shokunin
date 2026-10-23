#!/usr/bin/env python3
"""Isolated CriticNoop fixtures; does not mutate the lane or the counter."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import os
import shlex
import subprocess
import threading

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
OUT = LANE / '.ufo/waves/round-31/w2/out/CriticNoop'
SCRATCH = Path('/tmp/kama-r31w2/CriticNoop')
REPO = SCRATCH / 'fixtures.git'
TIP = '382d11b2107d335705875da1a4d889b074bd6fa6'
PIN = 'd86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216'
REGISTRY = 'registry/chat-param-outcomes-r31.json'
records = []
lock = threading.Lock()
env = dict(os.environ)
for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_OBJECT_DIRECTORY',
            'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_REPLACE_REF_BASE'):
    env.pop(key, None)
env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_INDEX_FILE=str(SCRATCH / 'fixture.index'),
           GIT_AUTHOR_NAME='CriticNoop isolated fixture',
           GIT_AUTHOR_EMAIL='critic-noop@fixture.local',
           GIT_COMMITTER_NAME='CriticNoop isolated fixture',
           GIT_COMMITTER_EMAIL='critic-noop@fixture.local', TMPDIR=str(SCRATCH))


def run(label, argv, *, allow_failure=False):
    p = subprocess.run([str(x) for x in argv], cwd=OUT, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, timeout=300)
    record = {'label': label, 'command': shlex.join([str(x) for x in argv]),
              'cwd': str(OUT), 'exit_code': p.returncode, 'output': p.stdout,
              'verbatim_tail': ''.join(p.stdout.splitlines(keepends=True)[-12:])}
    with lock:
        (OUT / (label + '.log')).write_text(p.stdout)
        records.append(record)
        (OUT / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
        with (OUT / 'execution.log').open('a') as log:
            log.write('$ ' + record['command'] + '\nexit ' + str(p.returncode) + '\n')
            log.write(p.stdout)
            if p.stdout and not p.stdout.endswith('\n'):
                log.write('\n')
        print('$ ' + record['command'], flush=True)
        print('exit ' + str(p.returncode), flush=True)
        print(record['verbatim_tail'], end='' if record['verbatim_tail'].endswith('\n') else '\n', flush=True)
    if p.returncode and not allow_failure:
        raise RuntimeError(f'{label} exited {p.returncode}')
    return p


def git(label, *args):
    return run(label, ['/usr/bin/git', '--no-replace-objects', '-C', REPO, *args]).stdout.strip()


counter = OUT / 'count-c1.py'
assert hashlib.sha256(counter.read_bytes()).hexdigest() == PIN
assert hashlib.sha256((LANE / '.ufo/waves/round-31/count-c1.py').read_bytes()).hexdigest() == PIN
registry = json.loads((OUT / 'noop-registry.json').read_text())
base = registry['base_body']
assert len(registry['rows']) == 12
assert len({row['id'] for row in registry['rows']}) == 12
for row in registry['rows']:
    req = dict(base)
    req[row['param']] = row['sent']
    req.update(row.get('also') or {})
    assert req == base, row['id']
    assert row['outcome'] == {'kind': 'slot', 'set': {'n_predict': 1}}
identity = {
    'counter_sha256': PIN,
    'base_body': base,
    'registry_rows': len(registry['rows']),
    'distinct_ids': len({row['id'] for row in registry['rows']}),
    'unique_effective_requests': 1,
    'each_effective_request_equals_base': True,
    'unique_outcome_assertions': 1,
    'source_rows': sorted({row['source']['row'] for row in registry['rows']}),
}
(OUT / 'request-identity.json').write_text(json.dumps(identity, indent=2) + '\n')
run('01-clone', ['/usr/bin/git', 'clone', '--quiet', '--shared', '--bare', LANE, REPO])
assert git('02-resolve-parent', 'rev-parse', '--verify', TIP + '^{commit}') == TIP
registry_blob = git('03-registry-blob', 'hash-object', '-w', OUT / 'noop-registry.json')
paired_skill_blob = git('04-paired-skill-blob', 'hash-object', '-w', OUT / 'paired-SKILL.md')
git('05-registry-parent-tree', 'read-tree', TIP)
git('06-registry-index', 'update-index', '--add', '--cacheinfo', '100644,' + registry_blob + ',' + REGISTRY)
registry_tree = git('07-registry-tree', 'write-tree')
registry_tip = git('08-registry-commit', 'commit-tree', registry_tree, '-p', TIP,
                   '-m', 'CriticNoop registry-only no-op test fixture; not landed')
git('09-registry-fixture-ref', 'update-ref', 'refs/heads/CriticNoop-registry-only', registry_tip)
git('10-paired-parent-tree', 'read-tree', TIP)
git('11-paired-index', 'update-index', '--add',
    '--cacheinfo', '100644,' + registry_blob + ',' + REGISTRY,
    '--cacheinfo', '100644,' + paired_skill_blob + ',SKILL.md')
paired_tree = git('12-paired-tree', 'write-tree')
paired_tip = git('13-paired-commit', 'commit-tree', paired_tree, '-p', TIP,
                 '-m', 'CriticNoop paired-table no-op test fixture; not landed')
git('14-paired-fixture-ref', 'update-ref', 'refs/heads/CriticNoop-paired', paired_tip)
git('15-bundle', 'bundle', 'create', OUT / 'fixtures.bundle',
    'refs/heads/CriticNoop-registry-only', 'refs/heads/CriticNoop-paired', '^' + TIP)
git('16-registry-scope', 'diff', '--name-status', TIP, registry_tip)
git('17-paired-scope', 'diff', '--name-status', TIP, paired_tip)
fixtures = {'parent': TIP, 'registry_only': registry_tip, 'paired_table': paired_tip,
            'repo': str(REPO), 'counter_sha256': PIN}
(OUT / 'fixtures.json').write_text(json.dumps(fixtures, indent=2) + '\n')


def measure(arm, tip):
    command = ['/usr/bin/python3', counter, '--lane', LANE, '--repo', REPO,
               '--tip', tip, '--out', OUT / ('c1-' + arm + '.json')]
    p = run('18-counter-' + arm, command, allow_failure=True)
    if p.returncode == 2 and any(token in p.stdout for token in
                                  ('port', 'server exited early', '/props model_path')):
        p = run('19-counter-' + arm + '-retry', command, allow_failure=True)
    if p.returncode:
        raise RuntimeError(f'{arm}: dead measurement (exit {p.returncode})')
    return p.stdout


with ThreadPoolExecutor(max_workers=2) as pool:
    pending = [pool.submit(measure, 'registry-only', registry_tip),
               pool.submit(measure, 'paired-table', paired_tip)]
    for future in pending:
        future.result()

print('REQUEST_IDENTITY ' + json.dumps(identity, sort_keys=True), flush=True)
(OUT / 'results.txt').write_text(''.join(
    '$ ' + r['command'] + '\nexit ' + str(r['exit_code']) + '\n' +
    (r['verbatim_tail'] if r['verbatim_tail'] else '(empty output)\n')
    for r in records))
