#!/usr/bin/env python3
"""Build the 'receipt omits the holder bookkeeping' forgery (the case the
AMENDMENT 1 kill rule names).

The tool performs its real, genuine request plane against the real pinned
child -- every procfs observation the counter makes stays true -- but it
omits the holder bookkeeping from the receipt and from hold.json:
  - receipt['listener_holders'] is not written at all
  - hold.json carries no 'holders' key
  - the tool-side check 'listener_holders_pinned' is still evaluated
    (against the local enumeration) so the receipt's check set stays
    complete; only the bookkeeping the counter reads is absent.

Usage: build_noholders.py <tool.py> <out.py>
"""
import sys

tool, out = sys.argv[1:3]
base = open(tool).read()

OLD_REC = ("        holders = _proc_holders(port)\n"
           "        receipt['listener_holders'] = holders\n")
NEW_REC = ("        holders = _proc_holders(port)\n"
           "        # receipt omits the holder bookkeeping entirely\n")

OLD_HOLD = "               'holders': holders,\n"
NEW_HOLD = ""

assert base.count(OLD_REC) == 1, 'receipt anchor not found exactly once'
assert base.count(OLD_HOLD) == 1, 'hold anchor not found exactly once'
new = base.replace(OLD_REC, NEW_REC).replace(OLD_HOLD, NEW_HOLD)
open(out, 'w').write(new)
print(f'no-holders forgery written: {out}')
