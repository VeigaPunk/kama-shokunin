#!/usr/bin/env python3
"""Diagnostic wrapper around the unmutated amended counter.

Runs the counter's own logic (nothing mutated) and additionally dumps every
collect() snapshot (listeners / holder pids / unreadable sets) to $MT22_DIAG.
Used for observation only; verdicts come from the unmodified counter file.
"""
import importlib.util
import json
import os
import sys

spec = importlib.util.spec_from_file_location('c1', sys.argv[1])
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

_orig_collect = c1.collect
OUT = os.environ.get('MT22_DIAG')


def collect(*a, **k):
    raw = _orig_collect(*a, **k)
    if OUT:
        rec = {'port': raw.get('port'),
               'listeners': raw.get('listeners'),
               'holder_pids': [h.get('pid') for h in raw.get('holders') or []],
               'holder_exes': [h.get('exe') for h in raw.get('holders') or []],
               'unreadable_own': raw.get('unreadable_own'),
               'unreadable_old': raw.get('unreadable_old')}
        with open(OUT, 'a') as f:
            f.write(json.dumps(rec) + '\n')
    return raw


c1.collect = collect
sys.exit(c1.main(sys.argv[2:]))
