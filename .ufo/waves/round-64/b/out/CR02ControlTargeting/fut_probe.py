#!/usr/bin/env python3
"""Capture the genuine live binding from one counter run, then re-grade
grade_binding() on the captured snapshot with the hold.json mtime moved
(a) just after t0 (genuine), (b) one hour in the future, (c) before t0.
Reads the counter; changes nothing in it."""
import importlib.util
import json
import sys

counter_path, work = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location('c1counter', counter_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
captured = {}
orig = m.witness_run


def cap(work_, label, *a, **k):
    res = orig(work_, label, *a, **k)
    if label == 'live':
        captured['binding'] = res[2]
    return res


m.witness_run = cap
m.main(['--repo', sys.argv[3], '--tip', sys.argv[4], '--work', work])
raw = captured['binding']['raw_a']
t0 = raw['t0_ns']
out = {}
for name, mt in [('genuine_mtime_after_t0', raw['hold_mtime_ns']),
                 ('future_mtime_plus_1h', t0 + 3600 * 10**9),
                 ('mtime_before_t0', t0 - 10**9)]:
    r = json.loads(json.dumps(raw))
    r['hold_mtime_ns'] = mt
    g = m.grade_binding(r)
    out[name] = {'hold_fresh': g['hold_fresh'], 'all_bind_true': all(g.values())}
print(json.dumps(out, indent=1))
print('raw hold_mtime_ns-t0_ns =', raw['hold_mtime_ns'] - t0,
      ' holder start_ticks>=tool:',
      all(h['start_ticks'] >= raw['tool_start_ticks'] for h in raw['holders']))
