#!/usr/bin/env python3
"""Read-only audit detectors; fixture writes are confined to the isolated scratch."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/tmp/kama-r21-C1CutoffErrataMutants')
LANE = ROOT / 'lane'
TARGET = LANE / 'tools/report-landing-audit.py'
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C1CutoffErrataMutants')
FLEET = ROOT / 'fleet-population'
PIN = 'a6617149722c73d90e142fbdc8154d6967055f7e'
ENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
           PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(ROOT / 'temp'))


def save(path, doc):
    with path.open('x', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
        fh.write('\n')


def command(argv):
    try:
        p = subprocess.run(list(map(str, argv)), cwd=ROOT, env=ENV,
                           capture_output=True, text=True, timeout=90)
        return {'argv': list(map(str, argv)), 'exit': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired as exc:
        return {'argv': list(map(str, argv)), 'exit': 'timeout',
                'stdout': (exc.stdout or b'').decode(errors='replace'),
                'stderr': (exc.stderr or b'').decode(errors='replace')}


def prepare():
    (ROOT / 'temp').mkdir()
    records = []

    def run(*argv, extra=None):
        env = dict(ENV)
        env.update(extra or {})
        p = subprocess.run(list(map(str, argv)), cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=90)
        records.append({'argv': list(map(str, argv)), 'exit': p.returncode,
                        'stdout': p.stdout, 'stderr': p.stderr,
                        'date_env': extra or {}})
        if p.returncode:
            raise RuntimeError(records[-1])
        return p.stdout.strip()

    run('git', '-c', 'core.hooksPath=/dev/null', 'clone', '-q', '--shared',
        '--no-checkout', '--single-branch',
        '/home/vgpnk/Projects/shokunin', FLEET)
    fleet_pin = run('git', '-C', FLEET, 'rev-parse', 'HEAD')
    reports = [f'.ufo/reports/round-{n}/kama.md' for n in range(10, 21)]
    run('git', '-C', FLEET, '-c', 'core.hooksPath=/dev/null',
        'checkout', 'HEAD', '--', *reports)
    lane, fleet = ROOT / 'boundary-lane', ROOT / 'boundary-fleet'
    for repo in (lane, fleet):
        repo.mkdir()
        run('git', '-C', repo, 'init', '-q', '-b', 'master')

    def commit(repo, subject, at, ct=None):
        dates = dict(GIT_AUTHOR_DATE=f'@{at} +0000',
                     GIT_COMMITTER_DATE=f'@{ct or at} +0000',
                     GIT_AUTHOR_NAME='kama-shokunin', GIT_COMMITTER_NAME='kama-shokunin',
                     GIT_AUTHOR_EMAIL='a@x', GIT_COMMITTER_EMAIL='a@x')
        run('git', '-C', repo, 'add', '--all')
        run('git', '-C', repo, '-c', 'core.hooksPath=/dev/null',
            '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', subject, extra=dates)
        return run('git', '-C', repo, 'rev-parse', 'HEAD')

    hashes = {}
    for label, subject, at, ct in (
            ('rebased', 'round-1: rebased work', 1100, 5000),
            ('equal', 'round-1: at report second', 1200, 1200),
            ('late', 'round-1: after report', 1300, 1300),
            ('between', 'round-2: between adds', 1400, 1400)):
        (lane / 'f').write_text(label + '\n', encoding='utf-8')
        hashes[label] = commit(lane, subject, at, ct)
    hashes['blob'] = run('git', '-C', lane, 'rev-parse', 'HEAD:f')
    r1 = fleet / '.ufo/reports/round-1/kama.md'
    r1.parent.mkdir(parents=True)
    r1.write_text('## Landed changes\n' + hashes['rebased'] + '\n', encoding='utf-8')
    commit(fleet, 'round-1: first report', 1200, 6000)
    r2 = fleet / '.ufo/reports/round-2/kama.md'
    r2.parent.mkdir(parents=True)
    r2.write_text('## Landed changes\nnone\n', encoding='utf-8')
    commit(fleet, 'round-2: first report', 1250)
    r2.unlink()
    commit(fleet, 'round-2: remove report', 1350)
    r2.write_text('## Landed changes\nnone\n', encoding='utf-8')
    commit(fleet, 'round-2: re-add report', 1500)
    save(ROOT / 'fixtures.json', hashes)
    doc = {'lane_commit': PIN, 'fleet_commit': fleet_pin,
           'source_sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
           'reports': {p: hashlib.sha256((FLEET / p).read_bytes()).hexdigest() for p in reports},
           'commands': records, 'fixtures': hashes,
           'python': sys.version, 'git': run('git', '--version')}
    save(OUT / 'setup.json', doc)
    print(json.dumps({k: doc[k] for k in ('lane_commit', 'fleet_commit', 'source_sha256', 'python', 'git')}, sort_keys=True))
    return 0


def boundaries():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('audit_under_probe', TARGET)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    h = json.loads((ROOT / 'fixtures.json').read_text())
    lane, fleet = ROOT / 'boundary-lane', ROOT / 'boundary-fleet'
    checks = []

    def check(name, observed, expected):
        checks.append({'case': name, 'ok': observed == expected,
                       'observed': observed, 'expected': expected})

    commits = audit.round_commits(lane, 'master', 'kama', 1)
    check('lane-author-time', next(c['atime'] for c in commits if c['sha'] == h['rebased']), 1100)
    check('fleet-author-time', audit.report_cutoff(fleet, '.ufo/reports/round-1/kama.md'), 1200)
    check('first-add-not-readd', audit.report_cutoff(fleet, '.ufo/reports/round-2/kama.md'), 1250)
    base = argparse.Namespace(lane_repo=str(lane), fleet_repo=str(fleet), branch='master',
                              lane='kama', rounds='1', report=None, errata=None, no_errata=True)
    rc, doc = audit.run(base)
    result = doc['results'][0]
    check('inclusive-required', [rc, result['required'], sorted(d['token'] for d in result['defects'])],
          [1, 2, [h['equal']]])
    check('post-split', result['post_report'], [h['late']])
    rc2, doc2 = audit.run(audit._ns(base, rounds='2'))
    check('first-add-post-split', [rc2, doc2['results'][0]['required'], doc2['results'][0]['post_report']],
          [0, 0, [h['between']]])

    def row(line, rnd, kind, token, correction):
        return dict(line=line, round=rnd, kind=kind, token=token, correction=correction, evidence='fixture')

    def result(kind, token):
        return [{'round': 1, 'defects': [{'kind': kind, 'token': token}]}]

    good = row(1, 1, 'landed-omitted', h['equal'], h['equal'])
    selected = row(2, 1, 'landed-omitted', h['late'], h['late'])
    unselected = row(3, 99, 'landed-omitted', h['late'], h['late'])
    unmatched, invalid = audit.apply_errata(result('landed-omitted', h['equal']),
                                           [good, selected, unselected], (lane, fleet))
    check('selected-unmatched-only', [[e['line'] for e in unmatched], [e['line'] for e in invalid]], [[2], []])
    wrong = row(1, 1, 'landed-omitted', h['equal'], h['rebased'])
    _, invalid = audit.apply_errata(result('landed-omitted', h['equal']), [wrong], (lane, fleet))
    check('omitted-correction-equals-token', [e['line'] for e in invalid], [1])
    blob = row(1, 1, 'unresolved-full-hash', '0' * 40, h['blob'])
    _, invalid = audit.apply_errata(result('unresolved-full-hash', '0' * 40), [blob], (lane, fleet))
    check('blob-rejected', [e['line'] for e in invalid], [1])
    for item in checks:
        print(json.dumps(item, sort_keys=True))
    failed = sum(not item['ok'] for item in checks)
    print(f'boundaries cases={len(checks)} failed={failed}')
    return int(bool(failed))


def phase(name):
    common = [sys.executable, str(TARGET), '--lane-repo', str(LANE),
              '--fleet-repo', str(FLEET), '--branch', PIN, '--rounds', '10-20']
    calls = {
        'selftest': [sys.executable, str(TARGET), '--selftest'],
        'population-raw': [*common, '--no-errata', '--json'],
        'population-ledger': [*common, '--json'],
        'boundaries': [sys.executable, str(OUT / 'probe.py'), 'boundaries'],
    }
    before = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = dict(zip(calls, pool.map(command, calls.values())))
    after = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    baseline_path = OUT / 'pristine.json'
    if name == 'pristine':
        baseline_ok = [records[k]['exit'] for k in calls] == [0, 1, 0, 0]
        raw = json.loads(records['population-raw']['stdout'])['summary']
        ledger = json.loads(records['population-ledger']['stdout'])['summary']
        baseline_ok = baseline_ok and 'selftest cases=32 failed=0' in records['selftest']['stdout']
        baseline_ok = baseline_ok and raw['defects'] == 9 and raw['required_commits'] == 42 and raw['post_report_commits'] == 4
        baseline_ok = baseline_ok and ledger['defects'] == ledger['corrected'] == 9
        baseline = records
    else:
        pristine = json.loads(baseline_path.read_text())
        baseline_ok, baseline = pristine['baseline_ok'], pristine['commands']
    changed = [k for k in calls if any(records[k][field] != baseline[k][field]
                                     for field in ('exit', 'stdout', 'stderr'))]
    brief = {}
    for key, record in records.items():
        if key.startswith('population-') and record['exit'] in (0, 1):
            summary = json.loads(record['stdout'])['summary']
            brief[key] = {'exit': record['exit'], 'summary': summary}
        else:
            brief[key] = {'exit': record['exit'],
                          'failures': [line for line in record['stdout'].splitlines()
                                       if line.startswith('FAIL ') or '"ok": false' in line],
                          'last_line': record['stdout'].splitlines()[-1:]}
    result = dict(phase=name, baseline_ok=baseline_ok, sha256_before=before, sha256_after=after,
                  commands=records, changed_detectors=changed,
                  claimed_detector_verdict=('inconclusive' if not baseline_ok else
                                            'killed' if any(k != 'boundaries' for k in changed) else 'survived'),
                  extended_detector_verdict=('inconclusive' if not baseline_ok else 'killed' if changed else 'survived'))
    save(OUT / f'{name}.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'commands'}, sort_keys=True))
    print(json.dumps(brief, sort_keys=True))
    return 0 if baseline_ok and before == after else 2


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'prepare':
        sys.exit(prepare())
    if action == 'boundaries':
        sys.exit(boundaries())
    if action == 'phase':
        sys.exit(phase(sys.argv[2]))
    raise SystemExit('prepare | boundaries | phase NAME')
