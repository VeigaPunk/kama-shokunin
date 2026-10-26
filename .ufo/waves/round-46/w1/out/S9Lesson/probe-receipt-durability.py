#!/usr/bin/env python3
"""probe-receipt-durability.py - round-46 seat S9Lesson, proposed fix for the
round-45 evidence-durability defect (closure N-E / routed D3) and for round 46's
own dead log pointers.

Question: can a fresh session re-obtain every artifact that the live receipts in
one directory name, using only what is in the lane tree?

For each `receipt-*.json` in --dir, three legs:
  model     receipt `model.path` + `model.sha256`
  server    receipt `server.realpath` (or `server.arg`) + `server.sha256`
  log       receipt `teardown.log_path`

A path leg passes when the artifact exists with the recorded sha256 AND a record
beside the receipts (any file in --dir other than the receipts) names both the
recorded sha256 and a locator for it (an http(s) URL, or `asset <name>` for a
release asset). A sha256 alone is not a locator: round 45 recorded the model
sha256 in receipt and row and still could not re-run (closure N-E).

The log leg passes when `log_path` is inside --tree, or a file with the log's
basename sits beside the receipts. A `/fast/scratch/...` or `/tmp/...` path that
is only on disk is a dead pointer for a later session (operator scratch
directive 2026-10-25: scratch is deleted; /tmp is never evidence).

Output: one `receipt <name> model=<pass|fail:reason> server=... log=...` line per
receipt, then `summary receipts=N fail=<n>`.
Exit: 0 every leg passes; 1 at least one leg fails; 2 could not evaluate (no
receipts, unreadable JSON).
Read-only.

Usage: probe-receipt-durability.py --dir DIR [--tree LANE]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import sys

URL = re.compile(r'https?://\S+')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def side_text(d, receipts):
    parts = []
    for p in sorted(glob.glob(os.path.join(d, '*'))):
        if not os.path.isfile(p) or p in receipts:
            continue
        try:
            with open(p, encoding='utf-8', errors='replace') as fh:
                parts.append(fh.read())
        except OSError:
            continue
    return '\n'.join(parts)


def artifact_leg(path, sha, text):
    if not path:
        return 'fail:no-recorded-path'
    if not os.path.exists(path):
        return 'fail:absent'
    try:
        got = sha256_file(path)
    except OSError as exc:
        return 'fail:unreadable:%s' % exc
    if sha and got != sha:
        return 'fail:sha-mismatch'
    if sha and sha not in text:
        return 'fail:no-side-record-of-sha'
    if not (URL.search(text) or re.search(r'asset\s+\S+', text)):
        return 'fail:no-side-locator'
    return 'pass'


_DIR = ['.']


def log_leg(path, tree):
    if not path:
        return 'pass:no-log-recorded'
    base = os.path.basename(path)
    if os.path.abspath(path).startswith(os.path.abspath(tree) + os.sep):
        return 'pass:in-tree'
    if os.path.exists(os.path.join(_DIR[0], base)):
        return 'pass:copied-beside-receipt'
    return 'fail:dead-pointer'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--tree', default='/home/vgpnk/Projects/shokunin/kama-shokunin')
    args = ap.parse_args()
    receipts = sorted(glob.glob(os.path.join(args.dir, 'receipt-*.json')))
    if not receipts:
        print('could-not-evaluate: no receipt-*.json in %s' % args.dir)
        return 2
    text = side_text(args.dir, set(receipts))
    _DIR[0] = args.dir
    fails = 0
    for p in receipts:
        try:
            with open(p, encoding='utf-8') as fh:
                r = json.load(fh)
        except (OSError, ValueError) as exc:
            print('could-not-evaluate: %s: %s' % (p, exc))
            return 2
        model = r.get('model') or {}
        server = r.get('server') or {}
        logp = (r.get('teardown') or {}).get('log_path')
        m = artifact_leg(model.get('path'), model.get('sha256'), text)
        s = artifact_leg(server.get('realpath') or server.get('arg'),
                         server.get('sha256'), text)
        g = log_leg(logp, args.tree)
        bad = [x for x in (m, s, g) if x.startswith('fail')]
        fails += bool(bad)
        print('receipt %s model=%s server=%s log=%s' % (
            os.path.basename(p), m, s, g))
    print('summary receipts=%d fail=%d' % (len(receipts), fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
