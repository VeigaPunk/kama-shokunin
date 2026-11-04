#!/usr/bin/env python3
"""Parent-owned EX01 proof; not executed by the editing seat."""
import json
import os
from pathlib import Path
import shutil
import subprocess

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
SEAT = Path(__file__).resolve().parent
S = Path('/fast/scratch/hyaku/kama-r83/EX01LateBinding')
BASE = '30d8eac394a8714fad3dc792b74a45a25b4366a2'


def run(name, command, *, check=False):
    result = subprocess.run(command, cwd=S, capture_output=True, text=True)
    (SEAT / f'{name}.stdout').write_text(result.stdout)
    (SEAT / f'{name}.stderr').write_text(result.stderr)
    (SEAT / f'{name}.receipt.json').write_text(json.dumps({
        'command': command, 'exit_code': result.returncode,
        'stdout': result.stdout, 'stderr': result.stderr, 'status': 'executed'
    }, indent=2) + '\n')
    if check and result.returncode:
        raise RuntimeError(f'{name} exit={result.returncode}: {result.stderr}')
    return result


if __name__ == '__main__':
    S.mkdir(parents=True, exist_ok=True)
    os.environ['TMPDIR'] = str(S)
    clone = S / 'clone'
    try:
        run('clone', ['git', 'clone', '--shared', str(LANE), str(clone)], check=True)

        def fixture_git(name, *args):
            root = subprocess.run(['git', '-C', str(clone), 'rev-parse', '--show-toplevel'],
                                  capture_output=True, text=True, check=True).stdout.strip()
            if Path(root) != clone:
                raise RuntimeError(f'fixture root mismatch: {root}')
            return run(name, ['git', '-C', str(clone), *args], check=True)

        fixture_git('checkout', 'checkout', '-q', BASE)
        shutil.copyfile(SEAT / 'round81-append-debt.py', clone / 'tools/round81-append-debt.py')
        fixture_git('commit', '-c', 'user.name=probe', '-c', 'user.email=p@p',
                    'commit', '-qm', 'probe', '--', 'tools/round81-append-debt.py')
        tool = ['python3', str(clone / 'tools/round81-append-debt.py')]
        common = [*tool, '--repo', str(clone), '--round', '83']
        run('legA', common)
        run('legB', [*common, '--late', 'registry/append-only-late.tsv'])
        run('selftest', [*tool, '--selftest'])
        outside = S / 'outside.tsv'
        shutil.copyfile(clone / 'registry/append-only-late.tsv', outside)
        shutil.copyfile(outside, clone / 'untracked.tsv')
        run('outside-repo', [*common, '--late', str(outside)])
        run('untracked-path', [*common, '--late', 'untracked.tsv'])
    finally:
        shutil.rmtree(S)
