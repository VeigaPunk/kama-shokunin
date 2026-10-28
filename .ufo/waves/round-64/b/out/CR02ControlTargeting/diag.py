#!/usr/bin/env python3
"""Diagnostic driver: loads a round64-c1-counter.py module from a path, wraps
is_hit to log every credited/uncredited control's expect + full fail set, then
runs main(). Does not alter the counter source."""
import importlib.util
import json
import sys

counter_path, out_log = sys.argv[1], sys.argv[2]
rest = sys.argv[3:]
spec = importlib.util.spec_from_file_location('c1counter', counter_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
orig = m.is_hit
log = []


def logged(s, expect, cap=m.MAX_COLLATERAL):
    hit = orig(s, expect, cap)
    log.append({'expect': expect, 'cap': cap, 'hit': bool(hit),
                'met': bool(s['met']), 'fails': sorted(s['fails'])})
    return hit


m.is_hit = logged
rc = m.main(rest)
with open(out_log, 'w') as f:
    for row in log:
        f.write(json.dumps(row) + '\n')
sys.exit(rc)
