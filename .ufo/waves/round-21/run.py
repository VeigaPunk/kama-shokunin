#!/usr/bin/env python3
"""Run the round-21 recipe once on a clean committed lane; preserve raw receipts."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

LANE = Path(__file__).resolve().parents[3]


def git(*args):
    return subprocess.check_output(['git', '-C', str(LANE), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipe', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    revision = git('rev-parse', 'refs/heads/master')
    if git('status', '--porcelain'):
        parser.error('measurement requires a clean committed working tree')
    recipe = json.loads(args.recipe.read_text())
    args.out.mkdir(parents=True, exist_ok=False)
    results = []
    for item in recipe:
        argv = [value.replace('{lane}', str(LANE)).replace('{python}', sys.executable)
                .replace('{revision}', revision).replace('{out}', str(args.out.resolve())) for value in item['argv']]
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        process = subprocess.Popen(argv, cwd=LANE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=item.get('timeout', 180))
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
        code = 124 if timed_out else process.returncode
        name = item['name']
        (args.out / f'{name}.stdout').write_bytes(stdout)
        (args.out / f'{name}.stderr').write_bytes(stderr)
        (args.out / f'{name}.exit').write_text(f'exit={code}\n')
        result = dict(name=name, argv=argv, started_utc=started, exit=code,
                      expected_exit=item.get('exit', 0), timed_out=timed_out,
                      stdout_sha256=hashlib.sha256(stdout).hexdigest(),
                      stderr_sha256=hashlib.sha256(stderr).hexdigest())
        result['as_expected'] = code == result['expected_exit']
        results.append(result)
        print(f'{name}: exit={code} expected={result["expected_exit"]}', flush=True)
    doc = dict(measured_commit=revision, recipe_sha256=hashlib.sha256(
        args.recipe.read_bytes()).hexdigest(), commands=results)
    (args.out / 'commands.json').write_text(json.dumps(doc, indent=1) + '\n')
    return 0 if all(row['as_expected'] for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
