#!/usr/bin/env python3
"""MT14 replay harness: load a counter file by path, run its real main() once
(live tip run, real outside witness), and at the first score() call (the live
receipt) also re-score stored old receipts against the SAME witness and the
SAME run NONCE. Prints one REPLAY line per stored receipt. Does not edit anything.
Usage: replay-harness.py COUNTER_PATH REPO TIP WORK REPLAY_DIR
"""
import copy
import importlib.util
import json
import os
import sys

ctr, repo, tip, work, rdir = sys.argv[1:6]
spec = importlib.util.spec_from_file_location('ctr_under_test', ctr)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
orig = m.score
state = {'live_done': False}


def load(name):
    return json.load(open(os.path.join(rdir, name + '.json')))


def show(tag, rc, w):
    r = orig(rc, w)
    print(f'REPLAY {tag} schema={rc.get("schema")} nonce={rc.get("nonce")} '
          f'met={r["met"]} fails={sorted(r["fails"])}')


def wrapped(receipt, witness):
    res = orig(receipt, witness)
    if not state['live_done']:
        state['live_done'] = True
        print(f'HARNESS run_nonce={m.NONCE} live_met={res["met"]} '
              f'live_fails={sorted(res["fails"])} '
              f'child_pid={receipt.get("child_pid")} port={receipt.get("port")} '
              f'witness_pid={witness.get("pid")} witness_port={witness.get("port")}')
        for tag in ('r62-final-v1', 'r62-prewave-v1', 'v2-earlier-run'):
            show(tag, load(tag), witness)
        fb = load('v2-earlier-run')
        fb['child_pid'] = witness['pid']
        fb['port'] = witness['port']
        show('v2-earlier-run+rebound-pid-port', fb, witness)
        fn = copy.deepcopy(fb)
        fn['nonce'] = m.NONCE
        show('v2-earlier-run+rebound-pid-port+run-nonce', fn, witness)
    return res


m.score = wrapped
rc = m.main(['--repo', repo, '--tip', tip, '--work', work])
print(f'HARNESS main_exit={rc}')
