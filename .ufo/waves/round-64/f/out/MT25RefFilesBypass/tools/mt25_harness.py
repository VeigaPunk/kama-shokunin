#!/usr/bin/env python3
"""MT25 harness v2: drive the round-64 C1 counter's own primitives by import.

Adds diagnostics: the full raw_a/raw_b snapshots (holders, unreadable pid
sets, maps) so a binding failure can be attributed.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import random
import subprocess
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument('mode', choices=['honest', 'forged'])
ap.add_argument('--repo', required=True)
ap.add_argument('--tip', required=True)
ap.add_argument('--counter', required=True)
ap.add_argument('--tool', default=None)
ap.add_argument('--n', type=int, default=5)
ap.add_argument('--load', type=int, default=0)
ap.add_argument('--second-server', action='store_true')
ap.add_argument('--label', default='live')
ap.add_argument('--dump-raw', action='store_true')
ap.add_argument('--out', required=True)
args = ap.parse_args()

spec = importlib.util.spec_from_file_location('c1r64', args.counter)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

server = c.pick_server()
model = os.path.realpath(os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf'))
assert server, 'no pinned server'
assert c.sha256_path(model) == c.MODEL_SHA, 'model digest mismatch'

burn = []
if args.load:
    for _ in range(args.load):
        burn.append(subprocess.Popen(
            [sys.executable, '-c', 'while True: pass'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
second = None
if args.second_server:
    port = c.free_port()
    log = open(os.path.join(os.path.dirname(os.path.abspath(args.out)),
                            'second-server.log'), 'wb')
    second = subprocess.Popen(
        [server, '--model', model, '--alias', 'mt25-second',
         '--port', str(port), '--host', '127.0.0.1', '-c', '512', '-t', '1'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
        env={k: v for k, v in os.environ.items()
             if k in c._TOOL_ENV_KEYS})
    time.sleep(3.0)

root = os.path.dirname(os.path.abspath(args.out))
os.makedirs(root, exist_ok=True)
tool_path = args.tool
if tool_path is None:
    tool_path, err = c.tool_files(args.repo, args.tip,
                                  os.path.join(root, 'tip-tool'))
    assert tool_path, 'tool_files: %s' % err

results = []
try:
    for i in range(args.n):
        work = os.path.join(root, 'w-%s-%d' % (args.label, i))
        os.makedirs(work, exist_ok=False)
        rng = random.Random(int.from_bytes(os.urandom(8), 'big'))
        nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
        ref_all = []
        reqs = tool_req = None
        for _ in range(8):
            reqs, tool_req = c.draw_requests(rng, nonce)
            ref_all = c.reference_run(server, model, reqs + [tool_req], work)
            texts = [(r or {}).get('text') for r in ref_all]
            if (len(ref_all) == 3 and all(isinstance(t, str) and t
                                          for t in texts)
                    and len(set(texts)) == 3):
                break
        c.TOOL_REQ.clear()
        c.TOOL_REQ.update(tool_req)
        receipt, witness, binding, tl_nonce, notes = c.witness_run(
            work, 'live', tool_path, server, model, reqs, tool_req)
        c.NONCE = tl_nonce
        rec = {'i': i, 'notes': notes}
        if receipt is None or witness is None or binding is None:
            rec['error'] = 'no receipt/witness: %s' % notes
            results.append(rec)
            continue
        witness['ref'] = ref_all[:2]
        witness['ref_tool'] = ref_all[2]
        witness['ref_files'] = [list(x) for x in c.REF_FILES]
        s = c.score_run(receipt, witness, binding, nonce)
        rec['met'] = s['met']
        rec['fails'] = sorted(s['fails'])
        rec['bind_ref_files_fail'] = 'bind_ref_files' in s['fails']
        raw_a = binding.get('raw_a') or {}
        raw_b = binding.get('raw_b') or {}
        refset = [list(x) for x in c.REF_FILES]
        hs = raw_a.get('holders') or []
        aset = [list(x) for x in c.file_set(hs[0].get('maps'))] if hs else []
        bset = [list(x) for x in c.file_set(
            (raw_b.get('holders') or [{}])[0].get('maps'))] if raw_b else []
        rec['ref_eq_a'] = (aset == refset)
        rec['ref_eq_b'] = (bset == refset)
        rec['a_eq_b'] = (aset == bset)
        rec['only_in_ref'] = sorted(
            set(map(tuple, refset)) - set(map(tuple, aset)))
        rec['only_in_a'] = sorted(
            set(map(tuple, aset)) - set(map(tuple, refset)))
        rec['only_in_b'] = sorted(
            set(map(tuple, bset)) - set(map(tuple, refset)))
        rec['b_minus_a'] = sorted(
            set(map(tuple, bset)) - set(map(tuple, aset)))
        rec['n_ref'] = len(refset)
        rec['n_a'] = len(aset)
        rec['n_b'] = len(bset)
        rec['holders_a'] = len(hs)
        rec['holder_pids_a'] = [h.get('pid') for h in hs]
        rec['hold_pid'] = raw_a.get('hold_pid')
        rec['unreadable_own_a'] = raw_a.get('unreadable_own')
        rec['unreadable_old_a'] = raw_a.get('unreadable_old')
        rec['unreadable_own_b'] = raw_b.get('unreadable_own')
        rec['raw_a_ns'] = raw_a.get('collected_ns')
        rec['raw_b_ns'] = raw_b.get('collected_ns')
        if args.dump_raw:
            rec['raw_a'] = raw_a
            rec['raw_b'] = raw_b
        results.append(rec)
        with open(args.out, 'w') as f:
            json.dump(results, f, indent=1)
        print('run %d met=%s fails=%s ref_eq_a=%s ref_eq_b=%s a_eq_b=%s '
              'only_ref=%d only_a=%d unown_a=%s' %
              (i, s['met'], sorted(s['fails'])[:6], rec['ref_eq_a'],
               rec['ref_eq_b'], rec['a_eq_b'], len(rec['only_in_ref']),
               len(rec['only_in_a']), rec['unreadable_own_a']), flush=True)
finally:
    for p in burn:
        p.kill()
    if second is not None:
        second.terminate()
        try:
            second.wait(timeout=15)
        except subprocess.TimeoutExpired:
            second.kill()
with open(args.out, 'w') as f:
    json.dump(results, f, indent=1)
n = len(results)
brf = sum(1 for r in results if r.get('bind_ref_files_fail'))
met = sum(1 for r in results if r.get('met'))
print('SUMMARY n=%d met=%d bind_ref_files_failures=%d' % (n, met, brf))
