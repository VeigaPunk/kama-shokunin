#!/usr/bin/env python3
"""Round85 author-side calibration controls; never edits the source checkout.

Axes: calibration and operability. Uses only stdlib and git. Each case checks
exact cells, imported calibration(), and the frozen CLI on a committed fixture.
Run with --repo KAMA_ROOT --work OWN_SCRATCH. Fixtures are removed on exit.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
FREEZE = '7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd'
BASE = '4401b72f64a2202fd30f26479c463e9b9d9cabad'
GATE = 'b53cd336e0cb204cf71246e95fdf7494babeafa4'
COUNTER = '.ufo/waves/round-85/count.py'
TOKEN = 'PRE_REPORT round=84 arms=13 failed=0 uncommitted=0'


def run(argv, env):
    result = subprocess.run([str(v) for v in argv], capture_output=True,
                            text=True, env=env)
    print(f'COMMAND {shlex.join([str(v) for v in argv])} exit={result.returncode}')
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    return result


def require(result):
    if result.returncode:
        raise RuntimeError(f'command failed: exit={result.returncode}')
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    args.work.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, 'TMPDIR': str(args.work.resolve()),
           'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_COUNT': '0'}
    counter = repo / COUNTER
    frozen = subprocess.run(['git', '-C', str(repo), 'show', f'{FREEZE}:{COUNTER}'],
                            capture_output=True, check=True, env=env).stdout
    if counter.read_bytes() != frozen:
        raise RuntimeError('working counter differs from frozen commit')
    print(f'FREEZE revision={FREEZE} counter_sha256={hashlib.sha256(frozen).hexdigest()}')
    spec = importlib.util.spec_from_file_location('round85_frozen', counter)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    score = subprocess.run(['git', '-C', str(repo), 'show', f'{BASE}:SCORECARD.md'],
                           capture_output=True, text=True, check=True, env=env).stdout
    # Independent oracle: take the literal first live lines from the base blob,
    # not cells(), so a selector regression cannot redefine its own expectation.
    stale_authority = next(line for line in score.splitlines()
                           if line.startswith('**Current authority'))
    first_axes = score.split('\n## Axes\n', 1)[1].split('\n## ', 1)[0]
    stale_row = next(line for line in first_axes.splitlines()
                     if line.startswith('| calibration |'))
    if 'under terminal measurement' not in stale_authority:
        raise RuntimeError('base authority is not the actual stale cell')
    old_path = 'latest outside closure `corpus/lessons/round-83-verifier-spotcheck.md`'
    new_path = old_path.replace('round-83', 'round-84')
    if old_path not in stale_row:
        raise RuntimeError('base calibration row is not the actual stale cell')
    print(f'BASE_CELLS revision={BASE}')
    print(stale_authority)
    print(stale_row)
    repaired_authority = (f'**Current authority (round 84):** terminal `{TOKEN}`; '
                          f'measured revision `{GATE}`; receipt '
                          '`.ufo/waves/round-84/measured/final/c1.out`; '
                          'not retrospective admission.')
    repaired_row = stale_row.replace(old_path, new_path)

    def document(authority, row):
        return f'# Fixture\n\n{authority}\n\n## Axes\n\n{row}\n\n## Notes\n'

    cases = []

    def add(name, text, authority, row, gate, closure):
        cases.append((name, text, (authority, row), gate, closure))

    stale = document(stale_authority, stale_row)
    repaired = document(repaired_authority, repaired_row)
    add('actual-stale', stale, stale_authority, stale_row, 0, 0)
    add('repaired-positive', repaired, repaired_authority, repaired_row, 1, 1)
    witnesses = f'Unrelated witness: {TOKEN}; {GATE}; {new_path}.\n'
    add('unrelated-witnesses', stale + witnesses + repaired_authority + '\n' + repaired_row,
        stale_authority, stale_row, 0, 0)
    for indent in range(4):
        heading = ' ' * indent + '### round-85 correction\n'
        block = heading + repaired_authority + '\n' + repaired_row + '\n## Resume\n'
        add(f'correction-after-stale-indent-{indent}', stale + block,
            stale_authority, stale_row, 0, 0)
        # The fake authority is FIRST in raw text; only heading exclusion can
        # prevent it from replacing the later actual stale authority.
        add(f'fake-first-indent-{indent}', '# Fixture\n' + block + stale,
            stale_authority, stale_row, 0, 0)
        add(f'missing-live-indent-{indent}', '# Fixture\n' + block + document('', repaired_row),
            '', repaired_row, 0, 1)
        # Corrected cells remain live after the closing heading.
        add(f'repaired-after-block-indent-{indent}', '# Fixture\n' + block + repaired,
            repaired_authority, repaired_row, 1, 1)
    # Four spaces is not an ATX heading: it must NOT open an exclusion block.
    add('four-space-not-heading', '    ### round-85 correction\n' + repaired,
        repaired_authority, repaired_row, 1, 1)
    add('missing-authority', document('', repaired_row), '', repaired_row, 0, 1)
    add('missing-calibration', document(repaired_authority, ''), repaired_authority, '', 1, 0)
    for name, bad in [('wrong-arms', repaired_authority.replace('arms=13', 'arms=14')),
                      ('wrong-revision', repaired_authority.replace(GATE, GATE[:-1] + '5')),
                      ('wrong-failure', repaired_authority.replace('failed=0', 'failed=1')),
                      ('stale-phrase', repaired_authority + ' under terminal measurement')]:
        add(name, document(bad, repaired_row), bad, repaired_row, 0, 1)
    add('wrong-closure', document(repaired_authority, stale_row), repaired_authority, stale_row, 1, 0)
    failures = 0
    with tempfile.TemporaryDirectory(prefix='authority-controls-', dir=args.work) as directory:
        root = Path(directory)
        fixture = root / 'repo'
        fixture.mkdir()
        require(run(['git', '-C', fixture, 'init', '-b', 'fixture'], env))
        # No source mutation. Assert the exact owning root before each add/commit.
        for name, text, expected_cells, gate, closure in cases:
            observed_cells = module.cells(text)
            (fixture / 'SCORECARD.md').write_text(text)
            lessons = fixture / 'corpus/lessons'
            lessons.mkdir(parents=True, exist_ok=True)
            for round_number in (83, 84):
                (lessons / f'round-{round_number}-verifier-spotcheck.md').write_text('# Fixture\n')
            top = require(run(['git', '-C', fixture, 'rev-parse', '--show-toplevel'], env)).strip()
            if Path(top).resolve() != fixture.resolve():
                raise RuntimeError('fixture root guard failed')
            require(run(['git', '-C', fixture, 'add', '--', 'SCORECARD.md', 'corpus/lessons'], env))
            require(run(['git', '-C', fixture, '-c', 'user.name=Authority Controls',
                         '-c', 'user.email=authority-controls@example.invalid',
                         '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                         'commit', '--allow-empty', '-m', name], env))
            revision = require(run(['git', '-C', fixture, 'rev-parse', 'HEAD'], env)).strip()
            expected = (f'AUTHORITY_CELLS facts=2 mismatches={2-gate-closure} '
                        f'gate={gate} closure={closure} newest=round-84-verifier-spotcheck.md\n')
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                status = module.calibration(fixture, revision)
            cli = run([sys.executable, counter, 'c1', '--repo', fixture,
                       '--rev', revision, '--work', root / 'work'], env)
            expected_exit = int(not (gate and closure))
            checks = (observed_cells == expected_cells,
                      (status, captured.getvalue()) == (expected_exit, expected),
                      (cli.returncode, cli.stdout, cli.stderr) == (expected_exit, expected, ''))
            passed = all(checks)
            failures += not passed
            print(f'CONTROL {name} cells={int(checks[0])} calibration={int(checks[1])} '
                  f'cli={int(checks[2])} fixture_rev={revision} verdict={"PASS" if passed else "FAIL"}')
            if not passed:
                print(f'DEFECT expected_cells={expected_cells!r} actual_cells={observed_cells!r} '
                      f'expected_cli={(expected_exit, expected)!r} '
                      f'actual_calibration={(status, captured.getvalue())!r}')
    print(f'AUTHORITY_CONTROLS pass={len(cases)-failures} fail={failures}')
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
