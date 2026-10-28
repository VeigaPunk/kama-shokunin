#!/usr/bin/env python3
"""E06 supplement: re-score every saved fixture against the BYTE-PINNED tip
counter (git show <tip>:tools/round62-c1-counter.py) and against the live
worktree copy, so the report states which instrument produced which verdict.
Also probes a non-JSON completion body (fixture e).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import traceback

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TIP = '65d7cad0fce90e34de37527cde22e97b63b118bf'
W = '/fast/scratch/hyaku/kama-r62/w/E06FixtureForgery'
ALIAS = 'kama-completion-probe'


def sha_b(s):
    return hashlib.sha256(s.encode()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    blob = subprocess.run(['git', '-C', LANE, 'show',
                           f'{TIP}:tools/round62-c1-counter.py'],
                          capture_output=True, check=True).stdout
    tippath = os.path.join(W, 'tipcounter', 'round62-c1-counter.py')
    os.makedirs(os.path.dirname(tippath), exist_ok=True)
    with open(tippath, 'wb') as f:
        f.write(blob)
    wtpath = os.path.join(LANE, 'tools', 'round62-c1-counter.py')
    versions = {
        'tip_blob': (load(tippath, 'r62tip'), hashlib.sha256(blob).hexdigest()),
        'worktree': (load(wtpath, 'r62wt'),
                     hashlib.sha256(open(wtpath, 'rb').read()).hexdigest()),
    }
    wit = json.load(open(os.path.join(W, 'witness.json')))
    witness = wit['witness']
    fixtures = ['receipt.json',
                'a_verdict_fabricated_real_failing_body.json',
                'a2_verdict_and_check_fabricated.json',
                'b_capture_bodies_reordered_across_keys.json',
                'b2_reordered_consistent.json',
                'c_nonce_matches_alias_differs.json',
                'c2_alias_differs_consistent.json',
                'd_synthetic_receipt.json']
    # fixture e: hand-edited authentic receipt whose completion body is not JSON
    base = json.load(open(os.path.join(W, 'receipt.json')))
    e = json.loads(json.dumps(base))
    cap = e['captures']['completion']
    cap['body'] = '<html>502 Bad Gateway</html>'
    cap['body_sha256'] = sha_b(cap['body'])
    e['verdict'] = 'REQUEST_OK'
    json.dump(e, open(os.path.join(W, 'e_nonjson_completion_body.json'), 'w'),
              indent=1, sort_keys=True)
    fixtures.append('e_nonjson_completion_body.json')

    out = {}
    for label, (mod, digest) in versions.items():
        mod.NONCE = wit['nonce']
        res = {'counter_sha256': digest}
        for fx in fixtures:
            receipt = json.load(open(os.path.join(W, fx)))
            try:
                s = mod.score(receipt, witness)
                res[fx] = {'accepted': s['met'], 'score': s}
            except Exception as exc:  # noqa: BLE001 - recording the instrument
                res[fx] = {'accepted': None, 'exception': type(exc).__name__,
                           'message': str(exc),
                           'traceback_tail': traceback.format_exc()
                           .strip().splitlines()[-3:]}
        out[label] = res
    json.dump(out, open(os.path.join(W, 'version-matrix-results.json'), 'w'),
              indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
