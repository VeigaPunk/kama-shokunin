#!/usr/bin/env python3
"""Account the frozen audit population against committed, live register rows.

Round 77 owns the audit loader, bucket semantics and history/rotation reader.
This instrument adds population filtering and an explicit committed-row boundary.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
BASE = 'c62ffd3aea930b98375f805cc3dfb821a703148b'
PREDICATE = """> `python3 tools/round78-append-registers.py --repo <lane> --to c62ffd3aea930b98375f805cc3dfb821a703148b`
> prints one `APPEND_REGISTERS to=c62ffd3aea930b98375f805cc3dfb821a703148b events=248
> accepted=<a> exempt=<x> permitted=<p> out_of_region=<o> restored=<r> disclosed=<d>
> unaccounted=0 introductions=1/1 rotation_safe=1` line and exits 0 only when every deletion
> event the append-only audit reports at that revision sits in exactly one of the six buckets
> (their sum equals `events`), each bucket row is committed at the audited revision or earlier,
> register rows naming an event commit that is not ancestral to the audited revision are counted
> on a separate `APPEND_REGISTERS_OUT_OF_POPULATION rows=<n>` line and change no bucket, the two
> register files' sha256 prefixes are printed on a separate `APPEND_REGISTERS_REGISTERS
> exempt=<hex12> accepted=<hex12>` line, and rotation detection rejects a reintroduced path
> carrying new rows; it exits 1 naming `APPEND_REGISTERS_FINDING
> <missing-row|wrong-count|wrong-class|inside-region|out-of-population|rotation-reintroduced|uncommitted>
> <detail>` otherwise, and 2 on could-not-evaluate."""


def load_previous():
    path = Path(__file__).resolve().with_name('round77-append-registers.py')
    spec = importlib.util.spec_from_file_location('round77_append_registers', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


previous = load_previous()
ACCEPTED, EXEMPT = previous.ACCEPTED, previous.EXEMPT
BUCKETS = ('accepted', 'exempt', 'permitted', 'out_of_region', 'restored', 'disclosed')


def evaluate(repo, revision, audit, accepted_tool, exempt_tool, commit_at='master',
             expected_events=248):
    data = audit.audit(str(repo), to=revision)
    boundary = previous.git(repo, 'rev-parse', '--verify', commit_at + '^{commit}').strip()
    histories, rotations = previous.history(repo, boundary)
    sections = exempt_tool.exemption_sections(repo, data, audit)
    outside = previous.outside_regions(repo, data, audit)
    texts, filtered, hashes, findings = {}, {}, {}, []
    excluded = 0
    ancestry = {}

    def precedes(commit, target):
        key = commit, target
        if key not in ancestry:
            ancestry[key] = previous.ancestor(repo, commit, target)
        return ancestry[key]

    for path in (ACCEPTED, EXEMPT):
        raw = (repo / path).read_bytes()
        text = raw.decode('utf-8')
        texts[path] = text
        hashes[path] = hashlib.sha256(raw).hexdigest()[:12]
        committed = set(previous.git(repo, 'show', f'{boundary}:{path}').splitlines())
        lines = text.splitlines()
        keep = lines[:1]
        rows = set()
        for number, line in enumerate(lines[1:], 2):
            if not line.strip():
                continue
            if line not in committed:
                findings.append({'class': 'uncommitted', 'commit': '-', 'file': path,
                                 'detail': f'line {number} absent at {boundary}'})
            cells = line.split('\t')
            if len(cells) == 6 and re.fullmatch(r'[0-9a-f]{40}', cells[0]):
                rows.add(line)
                if not precedes(cells[0], data['to']):
                    excluded += 1
                    continue
            keep.append(line)
        # Bind each row to its first committed appearance, not merely today's
        # blob. A future or unrelated event cannot be blessed retroactively.
        pending = rows & committed
        for commit in previous.git(repo, 'log', '--reverse', '--topo-order',
                                   '--format=%H', boundary, '--', path).split():
            if not pending:
                break
            exists = subprocess.run(['git', '-C', str(repo), 'cat-file', '-e',
                                     f'{commit}:{path}'], capture_output=True, timeout=120)
            if exists.returncode:
                continue  # The path may have been deleted before reintroduction.
            blob = set(previous.git(repo, 'show', f'{commit}:{path}').splitlines())
            for line in pending & blob:
                event = line.split('\t', 1)[0]
                if not precedes(event, commit):
                    findings.append({'class': 'out-of-population', 'commit': event,
                                     'file': path, 'detail': f'row predates its event at {commit}'})
            pending -= blob
        filtered[path] = '\n'.join(keep) + '\n'
        if '\r' in text:
            findings.append({'class': 'wrong-class', 'commit': '-', 'file': path,
                             'detail': 'register requires LF rows'})
    result = previous.grade(data, filtered[ACCEPTED], filtered[EXEMPT], sections,
                            outside, histories, rotations,
                            lambda commit: precedes(commit, data['to']), accepted_tool)
    result['predicate'] = PREDICATE
    summary = result['summary']
    for key in ('accepted_cutoff', 'exempt_cutoff'):
        del summary[key]
    for finding in result['findings']:
        kind = finding['class']
        if kind == 'unaccounted':
            key = finding['commit'], finding['file']
            event = next((e for e in data['events'] if (e['commit'], e['file']) == key), None)
            finding['class'] = ('inside-region' if event and event['graded'] > 0
                                and event['status'] == 'unrestored' else 'missing-row')
        elif kind == 'rotation':
            finding['class'] = 'rotation-reintroduced'
        elif kind == 'duplicate':
            finding['class'] = 'wrong-class'
    result['findings'].extend(findings)
    if summary['events'] != expected_events:
        result['findings'].append({'class': 'out-of-population', 'commit': '-', 'file': '-',
                                  'detail': f"events={summary['events']} expected={expected_events}"})
    if sum(summary[key] for key in BUCKETS) != summary['events'] and not summary['unaccounted']:
        result['findings'].append({'class': 'wrong-count', 'commit': '-', 'file': '-',
                                  'detail': 'bucket sum differs from population'})
    if summary['introductions'] != '1/1' and summary['rotation_safe']:
        result['findings'].append({'class': 'rotation-reintroduced', 'commit': '-', 'file': '-',
                                  'detail': 'register introductions differ from 1/1'})
    result['registers'] = {'exempt': hashes[EXEMPT], 'accepted': hashes[ACCEPTED]}
    result['out_of_population'] = excluded
    return result


def verdict(result):
    return previous.verdict(result)


def render(result):
    lines = ['APPEND_REGISTERS ' + ' '.join(f'{k}={v}' for k, v in result['summary'].items()),
             'APPEND_REGISTERS_REGISTERS ' + ' '.join(f'{k}={v}' for k, v in result['registers'].items()),
             f"APPEND_REGISTERS_OUT_OF_POPULATION rows={result['out_of_population']}"]
    lines.extend(f"APPEND_REGISTERS_FINDING {f['class']} {f['commit']} {f['file']} {f['detail']}"
                 for f in result['findings'])
    return '\n'.join(lines)


def selftest(audit, accepted_tool, exempt_tool):
    """Reuse round 77's real-audit fixture scaffold, then attack new boundaries."""
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        legacy = previous.selftest(audit, accepted_tool, exempt_tool)
    if legacy:
        print(captured.getvalue(), end='')
    arms = ('missing-row', 'wrong-count', 'wrong-class', 'inside-region',
            'rotation-reintroduced', 'out-of-population-row', 'uncommitted')
    failures = 0
    scratch = Path(os.environ.get('TMPDIR') or tempfile.gettempdir()).resolve()
    for arm in arms:
        directory = Path(tempfile.mkdtemp(prefix='r78-registers-', dir=scratch))
        try:
            previous.git(directory, 'init', '-q')
            if Path(previous.git(directory, 'rev-parse', '--show-toplevel').strip()) != directory:
                raise previous.CouldNotEvaluate('fixture root mismatch')

            def put(path, text):
                target = directory / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)

            def commit(message):
                if Path(previous.git(directory, 'rev-parse', '--show-toplevel').strip()) != directory:
                    raise previous.CouldNotEvaluate('fixture root mismatch')
                previous.git(directory, 'add', '.')
                previous.git(directory, '-c', 'user.name=register-selftest', '-c',
                             'user.email=register-selftest@invalid', '-c', 'commit.gpgsign=false',
                             'commit', '-qm', message)
                return previous.git(directory, 'rev-parse', 'HEAD').strip()

            put('README.md', 'SCORECARD ## Head is re-derived, append-only\n')
            put(audit.CONTRACT, audit.HEADER + '\n' +
                'SCORECARD.md\tA\tREADME.md:1\texempt=## Head@README.md:1\tfixture\n')
            put('SCORECARD.md', '## Head\nold\n## Record\nheld\n')
            commit('base')
            put('SCORECARD.md', '## Head\nnew\n## Record\nheld\n')
            event = commit('head event')
            row = f'{event}\tSCORECARD.md\texempt-head\t1\t## Head\tfixture\n'
            put(ACCEPTED, accepted_tool.HEADER + '\n')
            put(EXEMPT, previous.HEADER + '\n' + row)
            frozen = commit('registers')
            green = evaluate(directory, frozen, audit, accepted_tool, exempt_tool,
                             commit_at='HEAD', expected_events=1)
            if verdict(green):
                raise ValueError('green fixture failed: ' + render(green))
            if arm == 'missing-row':
                put(EXEMPT, previous.HEADER + '\n')
            elif arm == 'wrong-count':
                put(EXEMPT, previous.HEADER + '\n' + row.replace('\t1\t', '\t2\t'))
            elif arm == 'wrong-class':
                put(EXEMPT, previous.HEADER + '\n' + row.replace('exempt-head', 'removal'))
            elif arm == 'inside-region':
                put('SCORECARD.md', '## Head\nnew\n## Record\nchanged\n')
            elif arm == 'rotation-reintroduced':
                (directory / EXEMPT).unlink()
                commit('remove register')
                put(EXEMPT, previous.HEADER + '\n' + row + row.replace('fixture', 'new fixture'))
            else:
                put('SCORECARD.md', '## Head\nlater\n## Record\nheld\n')
                later = commit('later head event')
                put(EXEMPT, previous.HEADER + '\n' + row + row.replace(event, later))
            if arm != 'uncommitted':
                commit('attack')
            target = 'HEAD' if arm == 'inside-region' else frozen
            result = evaluate(directory, target, audit, accepted_tool, exempt_tool,
                              commit_at='HEAD', expected_events=2 if arm == 'inside-region' else 1)
            if arm == 'out-of-population-row':
                # Exclusion itself is benign; assert unchanged buckets and make
                # the deliberately false inclusion expectation red-capable.
                ok = (verdict(result) == 0 and result['out_of_population'] == 1
                      and all(result['summary'][key] == green['summary'][key] for key in BUCKETS))
            else:
                ok = verdict(result) == 1 and any(f['class'] == arm for f in result['findings'])
        except (previous.CouldNotEvaluate, audit.AuditError, accepted_tool.CouldNotEvaluate,
                exempt_tool.CouldNotEvaluate, OSError, ValueError, KeyError, TypeError,
                subprocess.TimeoutExpired) as exc:
            print(f'APPEND_REGISTERS_SELFTEST_ERROR {arm} {exc}')
            ok = False
        finally:
            shutil.rmtree(directory)
        failures += not ok
        print(f"APPEND_REGISTERS_SELFTEST {arm} {'PASS' if ok else 'FAIL'}")
    if legacy:
        failures += 1
        print('APPEND_REGISTERS_SELFTEST_ERROR legacy-scaffolding failed')
    print(f'APPEND_REGISTERS_SELFTEST pass={len(arms) - min(failures, len(arms))} fail={failures}')
    return int(bool(failures))


def main(argv=None):
    parser = previous.Parser(description=__doc__)
    parser.add_argument('--repo', default='.')
    parser.add_argument('--to', default=BASE)
    parser.add_argument('--commit-at', default='master')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--selftest', action='store_true')
    errors = (previous.CouldNotEvaluate, OSError, ValueError, KeyError, TypeError,
              subprocess.TimeoutExpired, ImportError)
    try:
        args = parser.parse_args(argv)
        audit = previous.load('append-only-audit.py')
        accepted_tool = previous.load('round75-append-accepted.py')
        exempt_tool = previous.load('round76-append-exempt.py')
        errors += (audit.AuditError, accepted_tool.CouldNotEvaluate, exempt_tool.CouldNotEvaluate)
        if args.selftest:
            return selftest(audit, accepted_tool, exempt_tool)
        result = evaluate(Path(args.repo).resolve(), args.to, audit, accepted_tool,
                          exempt_tool, args.commit_at)
        print(json.dumps(result, indent=2) if args.json else render(result))
        return verdict(result)
    except errors as exc:
        print(f'APPEND_REGISTERS could-not-evaluate: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
