#!/usr/bin/env python3
"""MT34RegressLogic: live timeout probe of the shipped C2 flip logic.

Question: when a REGRESSED run hangs past the runner's timeout, does the
shipped counter credit the row as a flipped regression?

Method (all shipped code, one fixture knob):
  - import the pristine counter module from the clone and set
    RUN_TIMEOUT=15 (feasibility knob only; shipped value is 900 s)
  - tip tree = pristine git archive of the tip
  - regressed overlay: tools/pin-watch.py with the row's shipped find
    line replaced by a `sleep(1200)` in front of it (single line, compiles)
  - run the counter's own Runner.run for both base and regressed, then the
    shipped classify() and flip_status()
Prints the shipped-code verdict for each condition.
"""
import importlib.util
import os
import sys

clone, tip = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location(
    'c2', os.path.join(clone, 'tools', 'round64-c2-counter.py'))
c2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2)

c2.RUN_TIMEOUT = 15            # fixture knob (shipped: 900)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

tip_tree = c2.checkout_tip(clone, tip, os.path.join(os.getcwd(), 'work'))
runner = c2.Runner(clone, tip, os.path.join(os.getcwd(), 'work'), tip_tree)

src = c2.blob_bytes(clone, tip, 'tools/pin-watch.py')
find = '    tags = release_tags(text, pin["rx"])'
assert src.decode().count(find) == 1
hang = ('    __import__("time").sleep(1200); '
        'tags = release_tags(text, pin["rx"])')
data, tag = c2.apply_regression(src, find, hang)
assert tag is None, tag

spec_s = c2.SPECS['pin-watch']
base = runner.run('pin-watch', 'base', tip_tree)
tree = runner.overlay('hang', {'tools/pin-watch.py': data})
reg = runner.run('pin-watch', 'hang', tree)

bc, _ = c2.classify(spec_s, base)
rc_, why = c2.classify(spec_s, reg)
print('base  : rc=%s outcome=%s' % (base['rc'], bc))
print('hang  : rc=%s out_marker=%s outcome=%s reason=%s' % (
    reg['rc'], 'TIMEOUT' in reg['out'], rc_, why))
print('flip_status(base=%r, reg=%r) -> %r' % (
    bc, rc_, c2.flip_status(spec_s, bc, rc_)))
print('=> row credited as flipped: %s' % (
    c2.flip_status(spec_s, bc, rc_) == 'flipped'))
