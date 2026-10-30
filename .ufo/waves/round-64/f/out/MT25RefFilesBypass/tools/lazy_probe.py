#!/usr/bin/env python3
"""MT25 (b): which file-backed mappings appear only after which request?

Starts the pinned server with the counter's own flags/env, snapshots
/proc/<pid>/maps (parsed by the counter's own read_maps/file_set) after
each request in the tool's own request order and after the counter's
reference-probe order, then diffs the sets.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument('--counter', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--rounds', type=int, default=3)
args = ap.parse_args()

spec = importlib.util.spec_from_file_location('c1r64', args.counter)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

server = c.pick_server()
model = os.path.realpath(os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf'))
sdir = os.path.dirname(server)
results = []

for rnd in range(args.rounds):
    port = c.free_port()
    log = open('/tmp/zz-lazy-%d.log' % rnd, 'wb')
    proc = subprocess.Popen(
        [server, '--model', model, '--alias', 'kama-completion-probe',
         '--port', str(port), '--host', '127.0.0.1', '-c', '512', '-t', '1'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
        env={k: v for k, v in os.environ.items() if k in c._TOOL_ENV_KEYS})
    rec = {'round': rnd}
    try:
        t0 = time.monotonic()
        while time.monotonic() - t0 < 60:
            st, _, body, _ = c.http(port, '/health', timeout=2.0)
            if st == 200 and body == '{"status":"ok"}':
                break
            time.sleep(0.2)
        snaps = []

        def snap(tag):
            s = c.file_set(c.read_maps(proc.pid, sdir))
            snaps.append((tag, s))
            return s

        base = snap('after-start')
        # the tool's own request order (tools/kama-completion-live.py)
        c.http(port, '/health', timeout=5.0)
        s1 = snap('after-health')
        c.http(port, '/v1/models', timeout=5.0)
        s2 = snap('after-models')
        c.http(port, '/props', timeout=5.0)
        s3 = snap('after-props')
        payload = {'prompt': 'lazy mapping probe prompt', 'n_predict': 4,
                   'temperature': 0.0, 'seed': 1, 'timings_per_token': False}
        c.http(port, '/v1/completions', payload, timeout=30.0)
        s4 = snap('after-completion')
        c.http(port, '/tokenize', {'content': 'x', 'add_special': True},
               timeout=10.0)
        s5 = snap('after-tokenize')
        c.http(port, '/v1/completions', payload, timeout=30.0)
        s6 = snap('after-completion2')
        bad = dict(payload)
        bad.pop('prompt')
        c.http(port, '/v1/completions', bad, timeout=10.0)
        s7 = snap('after-bad-request')
        # the counter's reference-probe order (3 probes)
        for i in range(3):
            c.probe(port, {'prompt': 'ref probe %d' % i, 'n_predict': 3,
                           'seed': 10 + i})
            snaps.append(('after-ref-probe-%d' % i,
                          c.file_set(c.read_maps(proc.pid, sdir))))
        final = snaps[-1][1]
        rec['steps'] = [(t, len(s)) for t, s in snaps]
        rec['diffs'] = []
        for i in range(1, len(snaps)):
            tag, s = snaps[i]
            prev = snaps[i - 1][1]
            added = sorted(set(map(tuple, s)) - set(map(tuple, prev)))
            removed = sorted(set(map(tuple, prev)) - set(map(tuple, s)))
            if added or removed:
                rec['diffs'].append({'step': tag, 'added': added,
                                     'removed': removed})
        # the tool's final set vs the counter's reference set shape
        tool_set = [list(x) for x in s7]
        rec['tool_set_n'] = len(tool_set)
        rec['tool_set'] = tool_set
        rec['final_set_n'] = len(final)
        rec['final_set'] = [list(x) for x in final]
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
        log.close()
    results.append(rec)
    print('round %d steps=%s diffs=%d' %
          (rnd, rec['steps'], len(rec['diffs'])), flush=True)
    for d in rec['diffs']:
        print('   %s added=%s removed=%s' %
              (d['step'], [a[0] for a in d['added']],
               [r[0] for r in d['removed']]), flush=True)

with open(args.out, 'w') as f:
    json.dump(results, f, indent=1)
print('wrote', args.out)
