#!/usr/bin/env python3
"""Diagnostic wrapper for the C1 counter: does NOT modify the counter.

It imports the committed counter module by path, monkeypatches only the
`collect` function to dump the raw procfs snapshot (holders,
unreadable_own/old, listeners) to a JSON file, and then calls the
counter's own main() unchanged. The verdict line and exit code are the
counter's own. Use this only to explain a met=False; the scored runs use
the unmodified counter directly.

Usage: diagnose.py <counter.py> <repo> <tip> <work> <dump.json>
"""
import importlib.util
import json
import os
import sys

counter_path, repo, tip, work, dump = sys.argv[1:6]
spec = importlib.util.spec_from_file_location('r64c1', counter_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

orig_collect = mod.collect
n = [0]


def collect(*a, **kw):
    raw = orig_collect(*a, **kw)
    n[0] += 1
    try:
        with open(dump, 'a') as f:
            f.write(json.dumps({
                'n': n[0],
                'holders': [{k: h.get(k) for k in ('pid', 'exe', 'state',
                                                    'tracer_pid',
                                                    'start_ticks', 'ppid',
                                                    'cmdline')}
                            for h in (raw.get('holders') or [])],
                'hold_pid': raw.get('hold_pid'),
                'hold_port': raw.get('hold_port'),
                'port': raw.get('port'),
                'listeners': raw.get('listeners'),
                'unreadable_own': raw.get('unreadable_own'),
                'unreadable_old': raw.get('unreadable_old'),
                'tool_start_ticks': raw.get('tool_start_ticks'),
            }) + '\n')
    except Exception as e:
        sys.stderr.write(f'diagnose dump failed: {e}\n')
    return raw


mod.collect = collect
sys.exit(mod.main(['--repo', repo, '--tip', tip, '--work', work]))
