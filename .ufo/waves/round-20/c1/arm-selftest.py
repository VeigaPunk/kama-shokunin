#!/usr/bin/env python3
"""Exercise the changed survivor classifiers only; never run the 42-run counter."""
import json
from pathlib import Path
import runpy

lane = Path(__file__).resolve().parents[4]
module = runpy.run_path(str(lane / '.ufo/waves/round-18/c2/survivors.py'))
checks = []

def check(name, passed, detail=''):
    checks.append({'name': name, 'passed': bool(passed), 'detail': str(detail)})

module['selftest_pure'](check)
failed = [row for row in checks if not row['passed']]
print(json.dumps({'scope': 'pure-classifiers-only', 'checks': checks,
                  'passed': len(checks) - len(failed), 'total': len(checks),
                  'failed': failed}, indent=1))
raise SystemExit(1 if failed else 0)
