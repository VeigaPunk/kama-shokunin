#!/usr/bin/env python3
"""S9Knowledge probe: a witness directory whose `release` already exists.

usage: stale-release-probe.py <scratch> <out-dir>
Writes <out-dir>/stale-release-receipt.json; prints exit, seconds, witness block.
"""
import json
import os
import subprocess
import sys
import time

S, OUT = sys.argv[1], sys.argv[2]
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
wd = os.path.join(S, 'wd-stale')
out = os.path.join(OUT, 'stale-release-receipt.json')
os.makedirs(wd)
with open(os.path.join(wd, 'release'), 'w') as fh:
    fh.write('pre-seeded by stale-release-probe\n')
t0 = time.monotonic()
p = subprocess.run([sys.executable, os.path.join(LANE, 'tools/kama-llamacpp-live.py'),
                    '--server', '/home/vgpnk/.local/opt/llama-b11909/llama-server',
                    '--model', '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf',
                    '--model-sha256', '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d',
                    '--alias', 'kama-witness-s9k', '--witness-dir', wd,
                    '--witness-timeout', '30', '--out', out],
                   cwd=LANE, capture_output=True, text=True)
r = json.load(open(out))
print('exit %r seconds %.2f' % (p.returncode, time.monotonic() - t0))
print('outcome %s witness %r' % (r['outcome'], r.get('witness')))
print('ready.json written: %r' % os.path.exists(os.path.join(wd, 'ready.json')))
