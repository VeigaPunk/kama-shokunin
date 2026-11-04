#!/usr/bin/env python3
"""Account for append-only history with independent register introductions.

Registers are read from the working tree so a new append can account for the
explicit historical --to revision. Scope ruling (a) admits row commits ancestral
to that revision; introductions remain independent provenance and rotation guards.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
PREDICATE = """> `python3 tools/round77-append-registers.py --repo <lane> --to <40-hex>` prints one
> `APPEND_REGISTERS to=<40-hex> events=<n> accepted=<n> exempt=<n> permitted=<n>
> out_of_region=<n> restored=<n> disclosed=<n> unaccounted=0 accepted_cutoff=<40-hex>
> exempt_cutoff=<40-hex> introductions=<a>/<e> rotation_safe=1` line and exits 0 only when every
> event the append-only audit reports at that revision is accounted for exactly once — by a
> line-bound row of `registry/append-only-accepted.tsv` under that register's own introduction
> cutoff, by a class-bound `exempt-head` row of `registry/append-only-exempt.tsv` under that
> register's own introduction cutoff whose count equals the event's ungraded deleted lines and
> whose section list equals the parents those lines sit in, by the audit's own `permitted`
> carriage class when every deleted line of the event is permitted and none is graded or
> ungraded, by the declared `out_of_region` class when the event's file declares an `only=`
> contract region and every deleted line lies outside every declared region, by restoration
> held at the audit revision, or by a disclosure row — and no register path is re-introduced
> after its first introduction with rows its previous version did not carry; it exits 1 naming
> each `APPEND_REGISTERS_FINDING <unaccounted|wrong-class|wrong-count|duplicate|rotation> …`,
> and 2 on could-not-evaluate (audit failure, missing register, CLI misuse)."""
ACCEPTED = "registry/append-only-accepted.tsv"
EXEMPT = "registry/append-only-exempt.tsv"
HEADER = "commit\tfile\tclass\tcount\tsections\tnote"


class CouldNotEvaluate(Exception):
    pass


def load(name):
    path = Path(__file__).resolve().parent / name
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                            text=True, timeout=120)
    if result.returncode:
        raise CouldNotEvaluate(result.stderr.strip())
    return result.stdout


def ancestor(repo, commit, revision):
    result = subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor',
                             commit, revision], capture_output=True, timeout=120)
    if result.returncode not in (0, 1):
        raise CouldNotEvaluate(f'cannot resolve row ancestry: {commit}')
    return result.returncode == 0


def history(repo, revision):
    """Inspect each path separately, in graph order rather than author-date order."""
    ordered = git(repo, 'rev-list', '--topo-order', '--reverse', revision).split()
    histories, rotations = {}, []
    for path in (ACCEPTED, EXEMPT):
        additions = set(git(repo, 'log', '--diff-filter=A', '--format=%H',
                            revision, '--', path).split())
        introductions = [commit for commit in ordered if commit in additions]
        if not introductions:
            raise CouldNotEvaluate(f'no introduction: {path}')
        histories[path] = introductions
        for commit in introductions[1:]:
            # The immediately preceding version of a deleted path is the last
            # extant version, not the absent blob at the re-add's parent.
            previous = git(repo, 'log', '-1', '--format=%H', '--diff-filter=AM',
                           commit + '^1', '--', path).strip()
            if not previous:
                raise CouldNotEvaluate(f'no preceding version: {commit} {path}')
            before = set(git(repo, 'show', f'{previous}:{path}').splitlines()[1:])
            after = set(git(repo, 'show', f'{commit}:{path}').splitlines()[1:])
            if not after <= before:
                rotations.append({'class': 'rotation', 'commit': commit, 'file': path,
                                  'detail': 're-introduction carries new rows'})
    return histories, rotations


def outside_regions(repo, data, audit):
    contract = audit.parse_contract(git(repo, 'show', f"{data['to']}:{audit.CONTRACT}"))
    outside = set()
    for event in data['events']:
        commit, path = event['commit'], event['file']
        _, prefixes = audit.file_regions(contract, path)
        if not prefixes:
            continue
        parent = git(repo, 'rev-parse', commit + '^1').strip()
        body = audit._git(str(repo), 'show', f'{parent}:{path}')
        parents = audit.sections(audit.split_lines(body))
        deleted = audit.deleted_lines(str(repo), parent, commit, path)
        if deleted and all(not any(parents[pos - 1] is not None and
                                  parents[pos - 1].startswith(prefix)
                                  for prefix in prefixes) for pos, _, _ in deleted):
            outside.add((commit, path))
    return outside


def grade(data, accepted, exempt, sections, outside, histories, rotations, precedes, tool):
    tool.validate_audit(data)
    findings = list(rotations)

    def bad(kind, key, detail):
        findings.append({'class': kind, 'commit': key[0], 'file': key[1], 'detail': detail})

    events = {(event['commit'], event['file']): event for event in data['events']}
    # Reuse the line-bound grader on each candidate, retaining its exact row,
    # hash, class, count, and note checks without confusing missing rows with
    # events that belong to other accounting buckets.
    accepted_keys = set()
    accepted_rows = {}
    for line in accepted.splitlines()[1:]:
        cells = line.split('\t')
        if len(cells) == 6:
            accepted_rows.setdefault((cells[0], cells[1]), []).append(line)
    validation = tool.grade(data, accepted, precedes)
    for finding in validation['findings']:
        detail = finding['detail']
        if finding['class'] == 'count-short' and ': missing ' in detail:
            continue
        match = re.search(r'([0-9a-f]{40}) (\S+)', detail)
        key = match.groups() if match else ('-', ACCEPTED)
        kind = {'duplicate': 'duplicate', 'class-mismatch': 'wrong-class',
                'unknown-event': 'wrong-class', 'restored-event': 'wrong-class',
                'post-introduction': 'wrong-class'}.get(finding['class'], 'wrong-count')
        bad(kind, key, detail)
    for key, lines in accepted_rows.items():
        if key not in events:
            continue
        one = {**data, 'events': [events[key]]}
        result = tool.grade(one, tool.HEADER + '\n' + '\n'.join(lines) + '\n', precedes)
        if result['summary']['accepted'] == 1 and not result['summary']['bad_rows']:
            accepted_keys.add(key)
    valid, seen, invalid = set(), set(), set()
    lines = exempt.splitlines()
    if not lines or lines[0] != HEADER or '\r' in exempt:
        bad('wrong-class', ('-', EXEMPT), 'requires six-column LF TSV header')
    for line in lines[1:] if lines and lines[0] == HEADER else lines:
        if not line.strip():
            continue
        cells = line.split('\t')
        if len(cells) != 6:
            bad('wrong-class', ('-', EXEMPT), 'expected six columns')
            continue
        commit, path, klass, count, titles, note = cells
        key = (commit, path)
        if key in seen:
            invalid.add(key)
            bad('duplicate', key, 'duplicate exempt row')
            continue
        seen.add(key)
        event = events.get(key)
        parents, eligible = sections.get(key, ([], False))
        if (event is None or event['status'] != 'ungraded' or event['graded'] != 0
                or event['ungraded'] != event['deleted'] or not eligible
                or klass != 'exempt-head' or titles != '|'.join(parents)
                or not note.strip() or not precedes(commit)):
            bad('wrong-class', key, 'not a class-bound exempt-head event')
            continue
        if not re.fullmatch(r'[1-9][0-9]*', count) or int(count) != event['ungraded']:
            bad('wrong-count', key, f"count={count} expected={event['ungraded']}")
            continue
        valid.add(key)
    valid -= invalid
    buckets = dict.fromkeys(('accepted', 'exempt', 'permitted', 'out_of_region',
                             'restored', 'disclosed'), 0)
    unaccounted = 0
    for key, event in events.items():
        classes = []
        if key in accepted_keys:
            classes.append('accepted')
        if key in valid:
            classes.append('exempt')
        if event['permitted'] == event['deleted'] and event['graded'] == event['ungraded'] == 0:
            classes.append('permitted')
        if key in outside:
            classes.append('out_of_region')
        if event['status'] == 'restored' and event['held_at_to'] == event['graded']:
            classes.append('restored')
        if event['status'] == 'disclosed':
            classes.append('disclosed')
        if len(classes) == 1:
            buckets[classes[0]] += 1
        else:
            unaccounted += 1
            bad('duplicate' if classes else 'unaccounted', key,
                'buckets=' + '|'.join(classes) if classes else 'no valid accounting bucket')
    for name in ('bad_declarations', 'bad_disclosures', 'binary', 'vanished', 'unmatched'):
        if data['summary'].get(name, 0):
            bad('unaccounted', ('-', '-'), f"audit {name}={data['summary'][name]}")
    return {'schema': 'append-registers/v1', 'predicate': PREDICATE,
            'summary': {'to': data['to'], 'events': len(events), **buckets,
                        'unaccounted': unaccounted,
                        'accepted_cutoff': histories[ACCEPTED][0],
                        'exempt_cutoff': histories[EXEMPT][0],
                        'introductions': f'{len(histories[ACCEPTED])}/{len(histories[EXEMPT])}',
                        'rotation_safe': int(not rotations)}, 'findings': findings}


def verdict(result):
    return int(bool(result['findings'] or result['summary']['unaccounted']))


def render(result):
    lines = ['APPEND_REGISTERS ' + ' '.join(f'{key}={value}' for key, value in result['summary'].items())]
    lines.extend(f"APPEND_REGISTERS_FINDING {f['class']} {f['commit']} {f['file']} {f['detail']}"
                 for f in result['findings'])
    return '\n'.join(lines)


def evaluate(repo, revision, audit, accepted_tool, exempt_tool):
    data = audit.audit(str(repo), to=revision)
    histories, rotations = history(repo, data['to'])
    sections = exempt_tool.exemption_sections(repo, data, audit)
    outside = outside_regions(repo, data, audit)
    accepted = (repo / ACCEPTED).read_bytes().decode('utf-8')
    exempt = (repo / EXEMPT).read_bytes().decode('utf-8')
    # A row must live in a committed register blob: an uncommitted worktree row
    # would let the tip bless its own damage without any commit (round-77 critic
    # F2). The register may grow after the audited revision, so the comparison
    # revision is the working tip, not --to.
    try:
        head = git(repo, 'rev-parse', '--verify', 'master^{commit}').strip()
    except (CouldNotEvaluate, subprocess.CalledProcessError):
        head = data['to']
    for path, text in ((ACCEPTED, accepted), (EXEMPT, exempt)):
        try:
            committed = set(git(repo, 'show', f'{head}:{path}').splitlines())
        except (CouldNotEvaluate, subprocess.CalledProcessError):
            committed = set()
        for number, line in enumerate(text.splitlines()[1:], 2):
            if line.strip() and line not in committed:
                rotations.append({'class': 'uncommitted', 'commit': '-', 'file': path,
                                  'detail': f'line {number} is not in the committed register at {head[:12]}'})
    return grade(data, accepted, exempt, sections, outside, histories, rotations,
                 lambda commit: ancestor(repo, commit, data['to']), accepted_tool)


def selftest(audit, accepted_tool, exempt_tool):
    """Exercise the real audit and register history in isolated fixture repos."""
    scratch = Path(os.environ['TMPDIR']).resolve()
    fails = 0
    arms = ('audit-fixture-green', 'missing-row', 'wrong-count', 'wrong-class',
            'inside-region', 'rotation-reintroduced', 'permitted-overclaim')
    for arm in arms:
        directory = Path(tempfile.mkdtemp(prefix='registers-', dir=scratch))
        try:
            git(directory, 'init', '-q')
            if Path(git(directory, 'rev-parse', '--show-toplevel').strip()) != directory:
                raise CouldNotEvaluate('fixture git root mismatch')
            def put(path, text):
                target = directory / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)
            def commit(message):
                git(directory, 'add', '.')
                git(directory, '-c', 'user.name=register-selftest', '-c',
                    'user.email=register-selftest@invalid', '-c', 'commit.gpgsign=false',
                    'commit', '-qm', message)
                return git(directory, 'rev-parse', 'HEAD').strip()
            # The audit binds a declaration line to its region: an exempt pointer must say the
            # titles are re-derived, an only pointer must say the region is append-only.
            put('README.md', 'SCORECARD ## Head is re-derived, append-only\n'
                             'consumer-registry is append-only; only ## Errata is graded\n')
            put(audit.CONTRACT, audit.HEADER + '\n' +
                'SCORECARD.md\tA\tREADME.md:1\texempt=## Head@README.md:1\tfixture\n' +
                'consumer-registry.md\tA\tREADME.md:2\tonly=## Errata@README.md:2\tfixture\n')
            put('SCORECARD.md', '## Head\nold\n')
            put('consumer-registry.md', '## Errata\ninside\n')
            commit('fixture base')
            put('SCORECARD.md', '## Head\nnew\n')
            event = commit('head re-derivation')
            put(ACCEPTED, accepted_tool.HEADER + '\n')
            row = f'{event}\tSCORECARD.md\texempt-head\t1\t## Head\tfixture head re-derivation\n'
            put(EXEMPT, HEADER + '\n' + row)
            commit('introduce registers')
            if arm == 'missing-row':
                put(EXEMPT, HEADER + '\n')
            elif arm == 'wrong-count':
                put(EXEMPT, HEADER + '\n' + row.replace('\t1\t', '\t2\t'))
            elif arm == 'wrong-class':
                put(EXEMPT, HEADER + '\n' + row.replace('exempt-head', 'removal'))
            elif arm == 'inside-region':
                put('consumer-registry.md', '## Errata\nchanged\n')
                commit('inside region deletion')
            elif arm == 'rotation-reintroduced':
                (directory / EXEMPT).unlink()
                commit('remove register')
                put(EXEMPT, HEADER + '\n' + row + row.replace('fixture head', 'new fixture head'))
                commit('reintroduce register with new row')
            result = evaluate(directory, 'HEAD', audit, accepted_tool, exempt_tool)
            if arm == 'permitted-overclaim':
                # Real audit event, with a deliberately inconsistent permitted
                # overclaim: a graded line must defeat the carriage shortcut.
                data = audit.audit(str(directory), to='HEAD')
                data = copy.deepcopy(data)
                target = data['events'][0]
                target.update(permitted=target['deleted'], graded=1, ungraded=0,
                              status='unrestored', undisclosed=[])
                histories, rotations = history(directory, data['to'])
                result = grade(data, accepted_tool.HEADER + '\n', HEADER + '\n', {}, set(),
                               histories, rotations, lambda c: True, accepted_tool)
            expected = 0 if arm == 'audit-fixture-green' else 1
            kind = {'wrong-count': 'wrong-count', 'wrong-class': 'wrong-class',
                    'rotation-reintroduced': 'rotation'}.get(arm, 'unaccounted')
            ok = verdict(result) == expected and (expected == 0 or
                 any(f['class'] == kind for f in result['findings']))
        except (CouldNotEvaluate, audit.AuditError, accepted_tool.CouldNotEvaluate,
                OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
            print(f'APPEND_REGISTERS_SELFTEST_ERROR {arm} {exc}')
            ok = False
        finally:
            shutil.rmtree(directory)
        fails += not ok
        print(f"APPEND_REGISTERS_SELFTEST {arm} {'PASS' if ok else 'FAIL'}")
    print(f'APPEND_REGISTERS_SELFTEST pass={len(arms) - fails} fail={fails}')
    return int(bool(fails))


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CouldNotEvaluate(message)


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('--repo', default='.')
    parser.add_argument('--to', default='HEAD')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--selftest', action='store_true')
    errors = (CouldNotEvaluate, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired)
    try:
        args = parser.parse_args(argv)
        audit = load('append-only-audit.py')
        accepted_tool = load('round75-append-accepted.py')
        exempt_tool = load('round76-append-exempt.py')
        errors += (audit.AuditError, accepted_tool.CouldNotEvaluate, exempt_tool.CouldNotEvaluate)
        if args.selftest:
            return selftest(audit, accepted_tool, exempt_tool)
        result = evaluate(Path(args.repo).resolve(), args.to, audit, accepted_tool, exempt_tool)
        print(json.dumps(result, indent=2) if args.json else render(result))
        return verdict(result)
    except errors as exc:
        print(f'APPEND_REGISTERS could-not-evaluate: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
