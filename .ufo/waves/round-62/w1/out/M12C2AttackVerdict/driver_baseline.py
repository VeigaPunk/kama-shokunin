#!/usr/bin/env python3
"""V0 baseline: the counter's own main() on the pristine full-history clone,
then dump the module's execution cache for per-row ground truth.

Byte-pinned module: round62-c2-counter.py == git show master (sha256
15d11f1ce8f8cb85e002d83c50b40d2bd7e4dfa561d8dd2d453e2daa09c05929).
"""
import importlib.util
import json
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(S, 'fixture2')
TIP = '65d7cad0fce90e34de37527cde22e97b63b118bf'

spec = importlib.util.spec_from_file_location(
    'c2counter', os.path.join(S, 'round62-c2-counter.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

rc = mod.main(['--repo', FIX, '--tip', TIP,
               '--work', os.path.join(S, 'work-baseline2')])
print(f'baseline_exit={rc}', file=sys.stderr)
for (tip, cap), (v, obs, sens, dead) in sorted(
        mod._EXEC_CACHE.items(), key=lambda kv: kv[0][1]):
    print(json.dumps({'cap': cap, 'computed_verdict': v,
                      'observed_first_120': obs[:120],
                      'sensitive': sens, 'dead': dead}))
