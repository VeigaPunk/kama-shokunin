#!/usr/bin/env python3
"""S9Knowledge probe: run the lane live tool with --witness-dir against the host
b11909 install and observe from outside with the frozen counter's own observe().

usage: witness-probe.py <scratch> <out-dir>
Writes <out-dir>/witness-receipt.json; prints the observer's findings.
"""
import importlib.util
import json
import os
import subprocess
import sys
import time

S, OUT = sys.argv[1], sys.argv[2]
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
MODEL = '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf'
SERVER = '/home/vgpnk/.local/opt/llama-b11909/llama-server'

spec = importlib.util.spec_from_file_location(
    'c1', os.path.join(LANE, 'tools/round49-replay-witness-audit.py'))
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

assert c1.sha_file(MODEL) == c1.MODEL_SHA, 'host model is not the frozen model'
vocab = c1.gguf_tokens(MODEL)
wd = os.path.join(S, 'wd-live')
os.makedirs(wd)
out = os.path.join(OUT, 'witness-receipt.json')

argv = [sys.executable, os.path.join(LANE, 'tools/kama-llamacpp-live.py'),
        '--server', SERVER, '--model', MODEL, '--model-sha256', c1.MODEL_SHA,
        '--alias', 'kama-witness-s9k', '--witness-dir', wd,
        '--witness-timeout', '30', '--out', out]
t0 = time.monotonic()
p = subprocess.Popen(argv, cwd=LANE, stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT, text=True)
ready = None
while time.monotonic() - t0 < 60 and p.poll() is None:
    try:
        ready = json.load(open(os.path.join(wd, 'ready.json')))
    except (OSError, ValueError):
        ready = None
    if ready:
        break
    time.sleep(0.1)
print('ready.json: %r after %.2fs' % (ready, time.monotonic() - t0))
probs = []
if ready:
    nonce = c1.observe(ready['pid'], ready['port'], vocab, probs)
    print('observer nonce: %r' % nonce)
    print('observer problems: %r' % (probs or 'none'))
    print('readlink /proc/%d/exe -> %s' % (ready['pid'], os.readlink('/proc/%d/exe' % ready['pid'])))
    with open('/proc/%d/cmdline' % ready['pid'], 'rb') as fh:
        print('child argv: %r' % [a.decode() for a in fh.read().split(b'\0') if a][:16])
open(os.path.join(wd, 'release'), 'w').write('observed by S9Knowledge\n')
try:
    rc = p.wait(timeout=90)
except subprocess.TimeoutExpired:
    p.kill()
    rc = None
print('live exit: %r total %.2fs' % (rc, time.monotonic() - t0))
print('live stdout tail: %s' % p.stdout.read()[-200:].replace('\n', ' | '))
rec = json.load(open(out))
print('receipt schema: %s outcome: %s' % (rec.get('schema'), rec.get('outcome')))
print('receipt witness: %r' % (rec.get('witness'),))
print('checks: %r' % ({c['id']: c['passed'] for c in rec['checks']},))
print('pid alive after exit: %r port refuses: %r'
      % (c1.pid_alive(ready['pid']), c1.port_refuses(ready['port'])) if ready else 'no ready.json')
