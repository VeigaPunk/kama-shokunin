#!/usr/bin/env python3
"""Bounded C2 mutation evidence runner; never edits tested source bytes."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import os
import signal
import subprocess
import sys

ROOT = Path('/tmp/kama-r21-C2ProducerGridMutants')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2ProducerGridMutants')
REV = 'a6617149722c73d90e142fbdc8154d6967055f7e'
TREE = '/home/vgpnk/.local/opt/llama-b11755'
PRODUCER = 'tools/kama-llamacpp-live.py'
GRID = 'tests/llamacpp-live/install-links-grid.py'
GATE = 'tests/llamacpp-live/check-receipt.py'
CASES = ('M1-drop-directory-problems', 'M2-drop-access-check',
         'M3-unsorted-json', 'M4-grid-ignore-problems', 'M5-null-expects-change')
WITNESS = """import runpy,sys
m=runpy.run_path(sys.argv[1])
a=m['links_digest']({'z':'target-z','a':'target-a'})
b=m['links_digest']({'a':'target-a','z':'target-z'})
print('reverse_sha256='+a)
print('sorted_sha256='+b)
print('insertion_order_invariant='+str(a==b))
sys.exit(0 if a==b else 1)
"""


def execute(argv, cwd, case, detector):
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['TMPDIR'] = str(ROOT / 'temporary')
    record = {'case': case, 'detector': detector, 'argv': [str(a) for a in argv],
              'cwd': str(cwd), 'timeout_seconds': 120}
    proc = subprocess.Popen(record['argv'], cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    try:
        stdout, stderr = proc.communicate(timeout=120)
        record['timed_out'] = False
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
        record['timed_out'] = True
    record.update(exit=proc.returncode, stdout=stdout, stderr=stderr)
    return record


def save(name, value):
    path = OUT / name
    with path.open('x', encoding='utf-8') as fh:
        json.dump(value, fh, indent=2, sort_keys=True)
        fh.write('\n')
    if path.stat().st_size > 1024 * 1024:
        raise RuntimeError(f'evidence exceeds 1 MiB: {path}')


def prepare_case(case):
    lane = ROOT / case
    records = [execute(['git', 'clone', '-q', '--shared', '--no-checkout',
                        ROOT / 'lane', lane], ROOT, case, 'clone')]
    if records[-1]['exit'] == 0:
        records.append(execute(['git', '-C', lane, 'checkout', '-q', REV],
                               ROOT, case, 'checkout'))
    return records


def hashes():
    return {case: {name: hashlib.sha256((ROOT / case / name).read_bytes()).hexdigest()
                   for name in (PRODUCER, GRID, GATE)} for case in CASES}


def main():
    phase = sys.argv[1]
    if phase == 'prepare':
        (ROOT / 'temporary').mkdir()
        with ThreadPoolExecutor(max_workers=5) as pool:
            records = [r for group in pool.map(prepare_case, CASES) for r in group]
        metadata = [execute(['git', '-C', ROOT / 'lane', 'rev-parse', 'HEAD'],
                            ROOT, 'environment', 'revision'),
                    execute(['python3', '--version'], ROOT, 'environment', 'python'),
                    execute(['id', '-u'], ROOT, 'environment', 'uid')]
        save('prepare.json', {'records': records + metadata})
        for r in records + metadata:
            print(r['case'], r['detector'], 'exit=' + str(r['exit']),
                  r['stdout'].strip(), r['stderr'].strip())
        return 0 if all(r['exit'] == 0 for r in records + metadata) else 1
    if phase not in ('baseline', 'mutated', 'restored'):
        raise SystemExit('expected prepare|baseline|mutated|restored')
    before = hashes()
    jobs = []
    for case in CASES:
        lane = ROOT / case
        jobs.extend((
            (['python3', '-B', lane / PRODUCER, '--selftest'], lane, case, 'producer-selftest'),
            (['python3', '-B', lane / GRID, '--selftest'], lane, case, 'grid-selftest'),
            (['python3', '-B', lane / GRID, '--tree', TREE, '--arm', 'current'],
             lane, case, 'grid-current'),
        ))
    case = CASES[2]
    lane = ROOT / case
    jobs.append((['python3', '-B', '-c', WITNESS, lane / PRODUCER],
                 lane, case, 'canonical-order-witness'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(execute, *job) for job in jobs]
        records = [future.result() for future in futures]
    after = hashes()
    payload = {'phase': phase, 'hashes_before': before, 'hashes_after': after,
               'source_bytes_unchanged_during_detectors': before == after,
               'records': records}
    if phase == 'restored':
        baseline = json.loads((OUT / 'baseline.json').read_text())
        payload['restoration_exact_all_sources'] = before == baseline['hashes_before']
    save(phase + '.json', payload)
    for r in records:
        lines = (r['stdout'] + r['stderr']).splitlines()
        significant = [line for line in lines if line.startswith((
            'FAIL', 'selftest:', 'selftest cases=', 'summary arm=',
            'could-not-evaluate:', 'kama-llamacpp-live selftest:',
            'insertion_order_invariant='))]
        print(r['case'], r['detector'], 'exit=' + str(r['exit']),
              ' | '.join(significant))
    print('source_bytes_unchanged_during_detectors=' + str(before == after))
    if phase == 'restored':
        print('restoration_exact_all_sources=' + str(payload['restoration_exact_all_sources']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
