#!/usr/bin/python3
"""Bounded, scratch-only lookup/checkable-abbrev mutation probe; never edits source."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

SCRATCH = Path('/tmp/kama-r21-C1LookupMutants')
LANE = SCRATCH / 'lane'
TARGET = LANE / 'tools/report-landing-audit.py'
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C1LookupMutants')
FLEET = Path('/home/vgpnk/Projects/shokunin')
REV = 'a6617149722c73d90e142fbdc8154d6967055f7e'
PYTHON = '/usr/bin/python3'
BASE_ENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
BASE_ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(SCRATCH))
sys.dont_write_bytecode = True


def run(argv, *, stdin=None, env=None):
    proc = subprocess.run(list(map(str, argv)), input=stdin, text=True,
                          capture_output=True, cwd=LANE, env=env or BASE_ENV,
                          timeout=25)
    return {'argv': list(map(str, argv)), 'exit': proc.returncode,
            'stdout': proc.stdout, 'stderr': proc.stderr}


def prepare():
    records = []
    fixtures = SCRATCH / 'fixtures'
    fixtures.mkdir()

    def git(repo, *args, stdin=None):
        rec = run(['/usr/bin/git', '-C', repo, *args], stdin=stdin)
        records.append(rec)
        if rec['exit'] != 0:
            raise RuntimeError(rec)
        return rec['stdout'].strip()

    lane, fleet = fixtures / 'lane', fixtures / 'fleet'
    for repo in (lane, fleet):
        repo.mkdir()
        git(repo, 'init', '-q', '-b', 'master')
    tree = git(lane, 'mktree', stdin='')
    header = (f'tree {tree}\nauthor fixture <fixture@local> 1000 +0000\n'
              'committer fixture <fixture@local> 1000 +0000\n\n')
    root_body = header + 'fixture root\n'
    root = git(lane, 'hash-object', '-t', 'commit', '-w', '--stdin', stdin=root_body)
    git(lane, 'update-ref', 'refs/heads/master', root)
    git(fleet, 'mktree', stdin='')
    fleet_root = git(fleet, 'hash-object', '-t', 'commit', '-w', '--stdin', stdin=root_body)
    git(fleet, 'update-ref', 'refs/heads/master', fleet_root)
    blob = git(lane, 'hash-object', '-w', '--stdin', stdin='not a landed commit\n')
    seen = {}
    for index in range(100000):
        body = header + f'collision candidate {index}\n'
        payload = body.encode()
        digest = hashlib.sha1(f'commit {len(payload)}\0'.encode() + payload).hexdigest()
        prefix = digest[:7]
        if not (any(c.isdigit() for c in prefix) and any(c in 'abcdef' for c in prefix)):
            continue
        if prefix in seen:
            previous, previous_digest = seen[prefix]
            first = git(lane, 'hash-object', '-t', 'commit', '-w', '--stdin', stdin=previous)
            second = git(lane, 'hash-object', '-t', 'commit', '-w', '--stdin', stdin=body)
            if (first, second) != (previous_digest, digest):
                raise RuntimeError('Git/hashlib object identity mismatch')
            collision = {'prefix': prefix, 'objects': [first, second], 'candidates': index + 1}
            break
        seen[prefix] = (body, digest)
    else:
        raise RuntimeError('bounded collision search exhausted')
    reports = {
        'ambiguous': prefix,
        'batch_rc': root,
        'peel': blob,
        'digitletter': 'defaced 1234567 deadbee1',
        'exemption': 'f' * 40 + ' ' + '1' * 40,
    }
    for name, tokens in reports.items():
        (fixtures / f'{name}.md').write_text(f'## Landed changes\n{tokens}\n', encoding='utf-8')
    shim = fixtures / 'shim'
    shim.mkdir()
    wrapper = shim / 'git'
    wrapper.write_text(
        '#!/usr/bin/python3\nimport subprocess, sys\n'
        'p = subprocess.run(["/usr/bin/git", *sys.argv[1:]])\n'
        'if "cat-file" in sys.argv and "--batch-check" in sys.argv and p.returncode == 0:\n'
        '    print("injected batch-check failure after valid stdout", file=sys.stderr)\n'
        '    sys.exit(70)\nsys.exit(p.returncode)\n', encoding='utf-8')
    wrapper.chmod(0o755)
    meta = {'root': root, 'blob': blob, 'collision': collision}
    (fixtures / 'meta.json').write_text(json.dumps(meta, indent=2) + '\n')
    artifact = {'phase': 'prepare', 'exit': 0, 'fixtures': meta, 'commands': records}
    (OUT / 'prepare.json').write_text(json.dumps(artifact, indent=2) + '\n')
    print(json.dumps(meta, sort_keys=True))
    return 0


def focused():
    spec = importlib.util.spec_from_file_location('landing_audit', TARGET)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    fixtures = SCRATCH / 'fixtures'
    meta = json.loads((fixtures / 'meta.json').read_text())
    repos = [fixtures / 'lane', fixtures / 'fleet']
    prefix = meta['collision']['prefix']
    checks = []

    def check(name, actual, expected):
        checks.append({'case': name, 'actual': actual, 'expected': expected,
                       'pass': actual == expected})

    check('lookup-ambiguous-not-found', audit.lookup(repos, [prefix]), {prefix: 'ambiguous'})
    saved_path = os.environ['PATH']
    os.environ['PATH'] = str(fixtures / 'shim') + os.pathsep + saved_path
    try:
        try:
            result = audit.lookup(repos, [meta['root']], '^{commit}')
            outcome = {'error': False, 'result': result}
        except audit.EvalError as exc:
            outcome = {'error': True, 'message': str(exc)}
    finally:
        os.environ['PATH'] = saved_path
    check('batch-check-nonzero-is-evaluation-error', outcome['error'], True)
    checks[-1]['observation'] = outcome
    check('blob-cannot-peel-to-commit', audit.lookup(repos, [meta['blob']], '^{commit}'),
          {meta['blob']: 'missing'})
    check('mixed-only-short-citations',
          [audit.checkable_abbrev(t) for t in ('defaced', '1234567', 'deadbee1')],
          [False, False, True])
    check('forty-hex-always-checked',
          [audit.checkable_abbrev(t) for t in ('f' * 40, '1' * 40)], [True, True])
    cli = []
    expected = {
        'batch_rc': None,
        'peel': [('landed-unresolved', meta['blob'])],
        'digitletter': [('landed-unresolved', 'deadbee1')],
        'exemption': [(kind, token) for kind in ('unresolved-full-hash', 'landed-unresolved')
                      for token in ('f' * 40, '1' * 40)],
    }
    for name, defects in expected.items():
        argv = [PYTHON, TARGET, '--lane-repo', repos[0], '--fleet-repo', repos[1],
                '--branch', 'master', '--rounds', '901', '--no-errata', '--json',
                '--report', f'901={fixtures / (name + ".md")}']
        env = dict(BASE_ENV)
        if name == 'batch_rc':
            env['PATH'] = str(fixtures / 'shim') + os.pathsep + saved_path
        rec = run(argv, env=env)
        rec['case'] = name
        if defects is None:
            check('cli-batch-check-nonzero-is-exit-2', rec['exit'], 2)
        else:
            doc = json.loads(rec['stdout'])
            actual = sorted((d['kind'], d['token']) for d in doc['results'][0]['defects'])
            check('cli-' + name + '-exact-defects', actual, sorted(defects))
            check('cli-' + name + '-exit', rec['exit'], 1)
        cli.append(rec)
    print(json.dumps({'checks': checks, 'commands': cli}, indent=2))
    return 0 if all(c['pass'] for c in checks) else 1


def suite(phase):
    source_before = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    commands = {
        'selftest': [PYTHON, TARGET, '--selftest'],
        'raw': [PYTHON, TARGET, '--lane-repo', LANE, '--fleet-repo', FLEET,
                '--branch', REV, '--rounds', '10-20', '--no-errata', '--json'],
        'focused': [PYTHON, Path(__file__), 'focused'],
    }
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = dict(zip(commands, pool.map(run, commands.values())))
    for name, rec in results.items():
        for stream in ('stdout', 'stderr'):
            (OUT / f'{phase}.{name}.{stream}').write_text(rec[stream], encoding='utf-8')
    source_after = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    record = {'phase': phase, 'source_before': source_before, 'source_after': source_after,
              'commands': results}
    (OUT / f'{phase}.json').write_text(json.dumps(record, indent=2) + '\n')
    summary = {'phase': phase, 'source_before': source_before, 'source_after': source_after,
               'exits': {n: r['exit'] for n, r in results.items()}}
    summary['selftest'] = results['selftest']['stdout'].splitlines()[-1:]
    summary['failed_selftest'] = [l for l in results['selftest']['stdout'].splitlines()
                                  if l.startswith('FAIL ')]
    try:
        summary['raw'] = json.loads(results['raw']['stdout'])['summary']
        focus = json.loads(results['focused']['stdout'])
        summary['failed_focused'] = [c for c in focus['checks'] if not c['pass']]
    except (ValueError, KeyError):
        summary['parse_error'] = True
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('prepare', 'focused', 'suite'))
    parser.add_argument('phase', nargs='?')
    args = parser.parse_args()
    if args.mode == 'prepare':
        sys.exit(prepare())
    if args.mode == 'focused':
        sys.exit(focused())
    if args.phase is None:
        parser.error('suite requires a phase')
    sys.exit(suite(args.phase))
