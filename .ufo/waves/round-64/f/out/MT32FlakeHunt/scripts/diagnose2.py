#!/usr/bin/env python3
"""Diagnostic wrapper #2: records the tool-start -> collect window length
and the unreadable_own population at each collect. Does NOT modify the
counter (it monkeypatches the imported module object only).

Usage: diagnose2.py <counter.py> <repo> <tip> <work> <dump.jsonl>
"""
import importlib.util
import json
import os
import sys

counter_path, repo, tip, work, dump = sys.argv[1:6]
spec = importlib.util.spec_from_file_location('r64c1', counter_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

HZ = os.sysconf('SC_CLK_TCK')
orig_collect = mod.collect
n = [0]


def now_ticks():
    return int(float(open('/proc/uptime').read().split()[0]) * HZ)


def collect(*a, **kw):
    raw = orig_collect(*a, **kw)
    n[0] += 1
    tt = raw.get('tool_start_ticks')
    age_ticks = (now_ticks() - tt) if tt else None
    try:
        with open(dump, 'a') as f:
            f.write(json.dumps({
                'n': n[0],
                'tool_age_s': round(age_ticks / HZ, 3) if age_ticks else None,
                'tool_start_ticks': tt,
                'holders': [h.get('pid') for h in (raw.get('holders') or [])],
                'hold_pid': raw.get('hold_pid'),
                'unreadable_own': raw.get('unreadable_own'),
                'unreadable_old': raw.get('unreadable_old'),
                'bind_holders': mod.grade_binding(raw).get('bind_holders'),
            }) + '\n')
    except Exception as e:
        sys.stderr.write(f'dump failed: {e}\n')
    return raw


mod.collect = collect
sys.exit(mod.main(['--repo', repo, '--tip', tip, '--work', work]))
