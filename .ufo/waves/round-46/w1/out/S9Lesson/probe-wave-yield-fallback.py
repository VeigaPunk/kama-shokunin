#!/usr/bin/env python3
"""probe-wave-yield-fallback.py - round-46 seat S9Lesson, proposed fix for the
round-45 wave-stall defect (closure N-D): the yield counter could not see a wave
that never wrote a results JSON.

`tools/seat-yield.py` (round 45, considerthese/2026-10-25.md proposal 4) needs
`<wave>/<wave>-results.json` or `results.json`; it exits 2 on the round-45 and
round-46 wave directories, both of which carry only `dispatch.json`. So the tool
that is supposed to measure "did any seat work" cannot evaluate the one case it
exists for.

This probe takes its denominator from `dispatch.json` (the dispatched roster) and
its numerator from the wave's `out/` directory, and needs no results JSON:
  seats     `taskCall.tasks[].name`
  reports   `out/<seat>.md` or `out/<seat>/<seat>.md`
An extra report file for an undispatched name is reported, never counted.
Also prints `driver-log=<n>` for lines matching the wave name in
`.ufo/state/inline-dispatcher.log` (mutable, informational only).

Output: `wave=<name> seats=S reports=R missing=M driver-log=N` then
`missing: <seat>` per seat without a report.
Exit: 0 R == S; 1 R < S (a wave with 0 reports included); 2 could not evaluate
(no dispatch.json, no tasks, no out/).
Read-only.

Usage: probe-wave-yield-fallback.py --wave DIR [--expect-seats N]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--wave', required=True)
    ap.add_argument('--expect-seats', type=int, default=None)
    ap.add_argument('--lane', default='/home/vgpnk/Projects/shokunin/kama-shokunin')
    ap.add_argument('--driver-log', default=None,
                    help='mutating driver log; default <lane>/../.ufo/state/inline-dispatcher.log')
    args = ap.parse_args()
    dpath = os.path.join(args.wave, 'dispatch.json')
    out = os.path.join(args.wave, 'out')
    if not os.path.isfile(dpath):
        print('could-not-evaluate: no dispatch.json in %s' % args.wave)
        return 2
    try:
        with open(dpath, encoding='utf-8') as fh:
            d = json.load(fh)
    except (OSError, ValueError) as exc:
        print('could-not-evaluate: %s: %s' % (dpath, exc))
        return 2
    tasks = (d.get('taskCall') or {}).get('tasks') or []
    seats = [t.get('name') for t in tasks if t.get('name')]
    if not seats:
        print('could-not-evaluate: dispatch.json has no taskCall.tasks names')
        return 2
    if not os.path.isdir(out):
        print('could-not-evaluate: no out/ directory in %s' % args.wave)
        return 2
    have = []
    for seat in seats:
        if os.path.isfile(os.path.join(out, seat + '.md')) or \
                os.path.isfile(os.path.join(out, seat, seat + '.md')):
            have.append(seat)
    missing = [s for s in seats if s not in have]
    extra = []
    for name in sorted(os.listdir(out)):
        base = name[:-3] if name.endswith('.md') else name
        if base and base not in seats and (name.endswith('.md') or
                                           os.path.isfile(os.path.join(out, name, name + '.md'))):
            extra.append(base)
    logn = 0
    logp = args.driver_log or os.path.join(
        os.path.dirname(os.path.normpath(args.lane)), '.ufo', 'state',
        'inline-dispatcher.log')
    wave = d.get('wave') or ''
    needles = [wave]
    parts = wave.split('-')
    if len(parts) >= 2 and parts[1][:1] == 'r' and parts[1][1:].isdigit():
        needles.append('%s %s' % (parts[0], parts[1][1:]))
    try:
        with open(logp, encoding='utf-8', errors='replace') as fh:
            logn = sum(1 for ln in fh if any(n and n in ln for n in needles))
    except OSError:
        logn = -1
    print('wave=%s seats=%d reports=%d missing=%d driver-log=%d%s' % (
        d.get('wave') or os.path.basename(args.wave), len(seats), len(have),
        len(missing), logn,
        (' expected=%d MISMATCH' % args.expect_seats)
        if args.expect_seats is not None and args.expect_seats != len(seats) else ''))
    for s in missing:
        print('missing: %s' % s)
    for s in extra:
        print('undispatched-report: %s' % s)
    return 0 if not missing else 1


if __name__ == '__main__':
    sys.exit(main())
