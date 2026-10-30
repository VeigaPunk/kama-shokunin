#!/usr/bin/env python3
"""MT34RegressLogic: test candidate SECOND regressions for a cap.

Usage: cand.py <clone> <tip> <work> <cap> <tool> <find> <replace>

Applies the candidate to a scratch overlay of the tip tree, runs the cap's
own run template on it, and reports the outcome plus the evidence lines.
The run template, environment and classifier are the counter's own.
"""
import importlib.util
import json
import os
import sys

clone, tip, work, cap, tool, find, repl = sys.argv[1:8]
spec = importlib.util.spec_from_file_location(
    'c2', os.path.join(clone, 'tools', 'round64-c2-counter.py'))
c2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2)

os.makedirs(work, exist_ok=True)
tip_tree = c2.checkout_tip(clone, tip, work)
runner = c2.Runner(clone, tip, work, tip_tree)
src = c2.blob_bytes(clone, tip, tool)
print('tool:', tool, 'find count in tool:', src.decode().count(find))
data, tag = c2.apply_regression(src, find, repl)
if data is None:
    print('apply_regression ->', tag, '(NOT applicable)')
    sys.exit(2)
sp = c2.SPECS[cap]
base = runner.run(cap, 'tip', tip_tree)
tree = runner.overlay('cand-' + cap, {tool: data})
r = runner.run(cap, 'cand', tree)
oc, why = c2.classify(sp, r)
bo, bwhy = c2.classify(sp, base)
print('base: rc=%s outcome=%s reason=%s pattern_present=%s' % (
    base['rc'], bo, bwhy, sp['pattern'] in base['out']))
print('reg : rc=%s outcome=%s reason=%s pattern_present=%s' % (
    r['rc'], oc, why, sp['pattern'] in r['out']))
print('flip_status:', c2.flip_status(sp, bo, oc))
print('--- regressed output (last 2200 chars) ---')
print(r['out'][-2200:])
