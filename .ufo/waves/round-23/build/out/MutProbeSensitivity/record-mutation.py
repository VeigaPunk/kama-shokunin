#!/usr/bin/env python3
"""Run the unchanged probe interface and retain exact local observations."""
from __future__ import annotations

import hashlib
import json
import re
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path('/tmp/kama-r23/MutProbeSensitivity')
PROBE = ROOT / 'mutation-probe.sh'
AUDIT = ROOT / 'tools/report-landing-audit.py'
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/MutProbeSensitivity')
LABEL = sys.argv[1]
ENV = {
    'PATH': '/usr/bin:/bin',
    'HOME': str(ROOT),
    'LC_ALL': 'C.UTF-8',
    'LANG': 'C.UTF-8',
    'TZ': 'UTC',
    'GIT_CONFIG_GLOBAL': '/dev/null',
    'GIT_CONFIG_NOSYSTEM': '1',
    'GIT_AUTHOR_NAME': 'mutation-fixture',
    'GIT_COMMITTER_NAME': 'mutation-fixture',
    'GIT_AUTHOR_EMAIL': 'a@x',
    'GIT_COMMITTER_EMAIL': 'a@x',
    'GIT_AUTHOR_DATE': '@1500 +0000',
    'GIT_COMMITTER_DATE': '@1500 +0000',
    'AUDIT': str(AUDIT),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

probe_bytes = PROBE.read_bytes()
record = {
    'label': LABEL,
    'command': ['bash', str(PROBE)],
    'cwd': str(ROOT),
    'environment': ENV,
    'probe_sha256': sha(probe_bytes),
    'probe_text': probe_bytes.decode('utf-8'),
    'audit_sha256': sha(AUDIT.read_bytes()),
}
proc = subprocess.Popen(record['command'], cwd=ROOT, env=ENV,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        start_new_session=True)
try:
    stdout, stderr = proc.communicate(timeout=60)
    record['timed_out'] = False
except subprocess.TimeoutExpired:
    import os
    os.killpg(proc.pid, signal.SIGKILL)
    stdout, stderr = proc.communicate()
    record['timed_out'] = True
record.update(wrapper_exit=proc.returncode,
              stdout=stdout.decode('utf-8', errors='replace'),
              stderr=stderr.decode('utf-8', errors='replace'))
record['probe_sha256_after_run'] = sha(PROBE.read_bytes())
match = re.search(r'^T=(.+)$', record['stdout'], re.M)
record['fixtures'] = match.group(1) if match else None
record['cases'] = {}
if match:
    fixture_root = Path(match.group(1))
    for case, exit_code, stderr_tail in re.findall(
            r'^(\S+) exit=(\d+) stderr_tail=(.*)$', record['stdout'], re.M):
        output_bytes = (fixture_root / f'{case}.out').read_bytes()
        error_bytes = (fixture_root / f'{case}.err').read_bytes()
        result = {
            'audit_exit': int(exit_code), 'stderr_tail': stderr_tail,
            'stdout': output_bytes.decode('utf-8', errors='replace'),
            'stderr': error_bytes.decode('utf-8', errors='replace'),
        }
        try:
            document = json.loads(output_bytes)
            row = document['results'][0]
            result['observation'] = {
                'audit_exit': int(exit_code),
                'status': document['summary']['status'],
                'defects': row['defects'],
                'required': row['required'], 'cutoff': row['cutoff'],
                'round_commits': row['round_commits'],
            }
        except (ValueError, KeyError, IndexError):
            result['observation'] = {
                'audit_exit': int(exit_code), 'json': False,
                'stderr_tail': stderr_tail,
            }
        record['cases'][case] = result
    record['actual_marker'] = (fixture_root / 'f5/marker').exists()
    record['wrong_marker'] = (fixture_root / 'f5/marker.wrong').exists()
    record['printed_marker'] = '   MARKER CREATED (command executed)' in record['stdout']
with (OUT / 'runs.jsonl').open('a', encoding='utf-8') as handle:
    handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + '\n')
print(json.dumps({key: record[key] for key in (
    'label', 'probe_sha256', 'probe_sha256_after_run', 'audit_sha256',
    'wrapper_exit', 'timed_out', 'fixtures', 'actual_marker', 'wrong_marker', 'printed_marker')},
    indent=2))
print(record['stdout'], end='')
if record['stderr']:
    print('WRAPPER STDERR:', record['stderr'], file=sys.stderr)
