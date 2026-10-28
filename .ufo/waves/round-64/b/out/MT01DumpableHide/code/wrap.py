#!/usr/bin/env python3
"""Diagnostic wrapper (scratch only): loads a counter file by path, prints the
raw procfs snapshot the counter graded for the LIVE run (first score call),
including each holder's /proc state, then runs the counter's main().
Usage: wrap.py <counter.py> --repo R --tip T --work W"""
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location('c', sys.argv[1])
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
orig = c.score_run
_seen = []


def _state(pid):
    try:
        s = open(f'/proc/{pid}/stat').read()
        return s[s.rindex(')') + 2]
    except (OSError, ValueError):
        return None


def wrapped(receipt, witness, binding, probe_nonce):
    s = orig(receipt, witness, binding, probe_nonce)
    if _seen:
        return s
    _seen.append(1)
    raw = (binding or {}).get('raw_a') or {}
    snap = {
        'hold_pid': raw.get('hold_pid'),
        'tool_pid': raw.get('tool_pid'),
        'tool_start_ticks': raw.get('tool_start_ticks'),
        'holders': [{'pid': h.get('pid'), 'state': _state(h.get('pid')),
                     'start_ticks': h.get('start_ticks'),
                     'exe': h.get('exe'),
                     'argv0': (h.get('cmdline') or [None])[0]}
                    for h in raw.get('holders') or []],
        'unreadable_own': raw.get('unreadable_own'),
        'unreadable_old': raw.get('unreadable_old'),
        'listeners': raw.get('listeners'),
        'live_fails': sorted(s['fails']),
    }
    print('SNAP ' + json.dumps(snap), file=sys.stderr)
    return s


c.score_run = wrapped
sys.exit(c.main(sys.argv[2:]))
