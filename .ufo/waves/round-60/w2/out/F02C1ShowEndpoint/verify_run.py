#!/usr/bin/env python3
"""F02C1ShowEndpoint: run the pristine lane counter's verify() read-only on a receipt."""
import importlib.util
import json
import pathlib
import sys

COUNTER = '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round60-c1-counter.py'
spec = importlib.util.spec_from_file_location('c1counter_pristine', COUNTER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

receipt_path, run_dir = sys.argv[1], sys.argv[2]
rec = json.loads(pathlib.Path(receipt_path).read_text())
nonce = rec['nonce']
bad = mod.verify(rec, run_dir, nonce)
show = rec['captures'].get('show', {})
checks = {c['id']: (c['passed'], c['evaluated']) for c in rec['checks']}
print(json.dumps({
    'receipt': receipt_path,
    'tool_verdict': rec['verdict'],
    'nonce': nonce,
    'port': rec['port'],
    'show_status': show.get('status'),
    'show_sha_ok': (lambda b: __import__('hashlib').sha256(b.encode()).hexdigest() == show.get('sha256'))(show.get('body', '')),
    'n_checks': len(rec['checks']),
    'failed_checks': [k for k, v in checks.items() if not v[0]],
    'teardown': rec['teardown'],
    'verify_bad': bad,
    'accepted': bad == [],
}, indent=1))
