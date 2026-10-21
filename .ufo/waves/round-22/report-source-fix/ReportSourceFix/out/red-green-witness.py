#!/usr/bin/env python3
"""Compare pinned cc9f8d3 and current auditors on one synthetic census report.

All Git writes are in removed temporary repositories. Fixed fixture commit
clocks are synthetic test data, not observation timestamps. Actual lane/fleet
Git state is read-only. 0 red-green-match, 1 red-green-mismatch, 2 unavailable
or snapshot_tampered. --selftest runs this CLI on positive/tamper controls.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

OUT = Path(__file__).resolve().parent
LANE = OUT.parents[5]
MANIFEST_SHA = '499442f137f69e0af93aa8d76e706e15e61d2cb6e632df98992d281cd0794d6b'
GIT_ENV = {'PATH': os.defpath, 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
           'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_NO_REPLACE_OBJECTS': '1'}


class SnapshotError(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def command(argv, env):
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=env, check=False, timeout=60)
    if proc.returncode:
        raise RuntimeError(f'command failed ({proc.returncode}): {argv!r}: '
                           + proc.stderr.decode('utf-8', 'replace'))
    return proc.stdout


def git(repo, *args, env=None):
    return command(['git', '-C', str(repo), *args], env or GIT_ENV)


def pinned_blob(lane, base, expected):
    path = expected['path']
    oid = git(lane, 'rev-parse', f'{base}:{path}').decode('ascii').strip()
    data = git(lane, 'show', f'{base}:{path}')
    if oid != expected['blob'] or digest(data) != expected['sha256']:
        raise SnapshotError('snapshot_tampered:' + path)
    return data


def commit_env(epoch):
    env = dict(GIT_ENV)
    env.update(GIT_AUTHOR_NAME='fixture', GIT_COMMITTER_NAME='fixture',
               GIT_AUTHOR_EMAIL='fixture@example.invalid',
               GIT_COMMITTER_EMAIL='fixture@example.invalid',
               GIT_AUTHOR_DATE=f'@{epoch} +0000',
               GIT_COMMITTER_DATE=f'@{epoch} +0000')
    return env


def cli_result(script, lane, fleet):
    argv = [sys.executable, str(script), '--lane-repo', str(lane),
            '--fleet-repo', str(fleet), '--branch', 'master', '--rounds', '22',
            '--no-errata', '--json']
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=GIT_ENV, check=False, timeout=60)
    if proc.returncode not in (0, 1):
        raise RuntimeError(f'auditor did not emit a completed verdict: exit={proc.returncode}')
    doc = json.loads(proc.stdout)
    return {'exit': proc.returncode,
            'defects': sorted([d['kind'], d['token']]
                              for d in doc['results'][0]['defects']),
            'source_url_hashes': doc['results'][0].get('source_url_hashes', []),
            'status': doc['summary']['status'],
            'stderr': proc.stderr.decode('utf-8', 'replace')}


def measure(args):
    raw = args.manifest.read_bytes()
    if digest(raw) != MANIFEST_SHA:
        raise SnapshotError('snapshot_tampered:manifest')
    manifest = json.loads(raw)
    base = manifest['base_commit']
    old_bytes = pinned_blob(args.lane_repo, base, manifest['old_script'])
    registry = pinned_blob(args.lane_repo, base, manifest['source_registry'])
    census = pinned_blob(args.lane_repo, base, manifest['census_stdout'])
    fixture_path = args.fixture or args.manifest.parent / manifest['report_fixture']['path']
    fixture = fixture_path.read_bytes()
    if digest(fixture) != manifest['report_fixture']['sha256']:
        raise SnapshotError('snapshot_tampered:report')
    if fixture.count(census) != 1:
        raise SnapshotError('snapshot_tampered:census-embedding')
    candidate_sha = digest(args.candidate.read_bytes())
    with tempfile.TemporaryDirectory(prefix='report-source-witness-') as temp:
        root = Path(temp)
        lane, fleet = root / 'lane', root / 'fleet'
        for repo in (lane, fleet):
            repo.mkdir()
            git(repo, 'init', '-q', '-b', 'master')
        target = lane / manifest['source_registry']['path']
        target.parent.mkdir(parents=True)
        target.write_bytes(registry)
        git(lane, 'add', '--', manifest['source_registry']['path'])
        git(lane, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m',
            'fixture registry', env=commit_env(1_797_000_000))
        git(fleet, '-c', 'commit.gpgsign=false', 'commit', '--allow-empty',
            '-q', '-m', 'fixture fleet', env=commit_env(1_797_000_001))
        report = fleet / '.ufo/reports/round-22/kama.md'
        report.parent.mkdir(parents=True)
        report.write_bytes(fixture)
        git(fleet, 'add', '--', '.ufo/reports/round-22/kama.md')
        git(fleet, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m',
            'fixture report', env=commit_env(1_797_000_002))
        old_script = root / 'old-audit.py'
        old_script.write_bytes(old_bytes)
        observed = {'old': cli_result(old_script, lane, fleet),
                    'candidate': cli_result(args.candidate, lane, fleet)}
    failures = [label for label, expected in manifest['expected'].items()
                if any(observed[label][key] != value for key, value in expected.items())]
    result = {'finding_id': 'red-green-mismatch' if failures else 'red-green-match',
              'base_commit': base, 'manifest_sha256': MANIFEST_SHA,
              'old_script_sha256': manifest['old_script']['sha256'],
              'source_registry_sha256': manifest['source_registry']['sha256'],
              'census_stdout_sha256': manifest['census_stdout']['sha256'],
              'report_fixture_sha256': manifest['report_fixture']['sha256'],
              'candidate_sha256': candidate_sha, 'results': observed,
              'same_synthetic_repositories_and_report': True,
              'actual_lane_or_fleet_git_writes': False, 'failures': failures}
    return int(bool(failures)), result


def selftest(args):
    raw = args.manifest.read_bytes()
    if digest(raw) != MANIFEST_SHA:
        raise SnapshotError('snapshot_tampered:manifest')
    with tempfile.TemporaryDirectory(prefix='report-source-witness-selftest-') as temp:
        temp = Path(temp)
        bad_manifest = temp / 'manifest.json'
        bad_manifest.write_bytes(raw + b' ')
        bad_report = temp / 'report.md'
        bad_report.write_bytes(b'tampered report')
        old_script = temp / 'old.py'
        manifest = json.loads(raw)
        old_script.write_bytes(pinned_blob(args.lane_repo,
                               manifest['base_commit'], manifest['old_script']))
        error_script = temp / 'error.py'
        error_script.write_text(
            'import json\nprint(json.dumps({"results": [{"defects": [], '
            '"source_url_hashes": []}], "summary": {"status": "clean"}}))\n'
            'raise SystemExit(2)\n')
        cases = [('positive', [], 0, 'red-green-match'),
                 ('manifest-tamper', ['--manifest', str(bad_manifest)], 2, 'snapshot_tampered'),
                 ('report-tamper', ['--fixture', str(bad_report)], 2, 'snapshot_tampered'),
                 ('missing-candidate', ['--candidate', str(temp / 'missing.py')], 2, 'could-not-evaluate'),
                 ('old-as-current', ['--candidate', str(old_script)], 1, 'red-green-mismatch'),
                 ('child-error-not-a-verdict', ['--candidate', str(error_script)], 2, 'could-not-evaluate')]
        results = []
        for name, extra, code, finding in cases:
            proc = subprocess.run([sys.executable, __file__, '--lane-repo',
                                   str(args.lane_repo), '--candidate', str(args.candidate),
                                   '--manifest', str(args.manifest), *extra],
                                  capture_output=True, text=True, timeout=180)
            doc = json.loads(proc.stdout)
            passed = proc.returncode == code and doc['finding_id'] == finding
            results.append({'case': name, 'exit': proc.returncode,
                            'finding_id': doc['finding_id'], 'passed': passed})
        failures = sum(not r['passed'] for r in results)
        return int(bool(failures)), {'finding_id': 'selftest-failed' if failures else 'selftest-clean',
                                    'cases': len(results), 'failures': failures, 'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lane-repo', type=Path, default=LANE)
    parser.add_argument('--candidate', type=Path, default=LANE / 'tools/report-landing-audit.py')
    parser.add_argument('--manifest', type=Path, default=OUT / 'red-green-fixture.json')
    parser.add_argument('--fixture', type=Path)
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    try:
        code, result = selftest(args) if args.selftest else measure(args)
    except SnapshotError as exc:
        code, result = 2, {'finding_id': 'snapshot_tampered', 'reason': str(exc)}
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        code, result = 2, {'finding_id': 'could-not-evaluate', 'reason': str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
