#!/usr/bin/env python3
"""C2 follow-up probes (critic seat; scratch only).

E5: a non-UTF-8 symlink target through install_links().
P1-CLI: replay the crafted-name collision through the real gate CLI with
the install-links pin, writing two receipt JSON files under scratch.
"""
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCR = Path('/tmp/kama-r21-LinksPolicyCritic')
LANE = SCR / 'lane'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load('prod', LANE / 'tools/kama-llamacpp-live.py')
gate = load('gate', LANE / 'tests/llamacpp-live/check-receipt.py')


def mkdir_with(files, links):
    d = Path(tempfile.mkdtemp(prefix='probe2-', dir=SCR))
    for name, data in files.items():
        (d / name).write_bytes(data)
    for name, target in links.items():
        os.symlink(target, d / name)
    return d


def identity(d):
    srv = str(d / 'llama-server')
    tree, tree_sha = prod.install_tree(srv)
    links, links_sha = prod.install_links(srv)
    return tree, tree_sha, links, links_sha


def receipt(d, tree, tree_sha, links, links_sha):
    r = copy.deepcopy(gate._selftest_receipt_v3())
    srv = str(d / 'llama-server')
    r['server'].update(arg=srv, realpath=srv, sha256=tree.get('llama-server'),
                       install_tree=tree, install_tree_sha256=tree_sha,
                       install_links=links, install_links_sha256=links_sha,
                       server_impl_sha256=None)
    r['argv'][0] = srv
    return r


print('## E5 non-UTF-8 symlink target')
E = mkdir_with({'llama-server': b'SRV', 'libllama.so.0.7.0': b'LIB'}, {})
os.symlink(b'\xff.so', E / 'libweird.so')
try:
    print('install_links ->', prod.install_links(str(E / 'llama-server')))
except Exception as exc:  # report, do not hide
    print('install_links raised:', type(exc).__name__, '-', exc)

print('\n## P1-CLI crafted-name collision through the gate CLI')
files = {'llama-server': b'SRV', 'libllama.so.0.7.0': b'LIB'}
G = mkdir_with(files, {'libllama.so.0': 'libllama.so.0.7.0',
                       'libllama.so': 'libllama.so.0'})
B = mkdir_with(files, {'libllama.so -> libllama.so.0\nlibllama.so.0':
                       'libllama.so.0.7.0'})
gt, gts, gl, gls = identity(G)
bt, bts, bl, bls = identity(B)
out = SCR / 'p1'
out.mkdir(exist_ok=True)
(out / 'G-receipt.json').write_text(json.dumps(receipt(G, gt, gts, gl, gls)))
(out / 'B-receipt.json').write_text(json.dumps(receipt(B, bt, bts, bl, bls)))
gate_py = str(LANE / 'tests/llamacpp-live/check-receipt.py')
runs = [
    ('G, pin=G links', ['p1/G-receipt.json', '--expect-install-links-sha256',
                        gls]),
    ('B, no pin', ['p1/B-receipt.json']),
    ('B, pin=G links', ['p1/B-receipt.json', '--expect-install-links-sha256',
                        gls]),
    ('B, pin=G tree', ['p1/B-receipt.json', '--expect-install-tree-sha256',
                       gts]),
]
for label, extra in runs:
    cp = subprocess.run([sys.executable, gate_py] + extra, cwd=SCR,
                        capture_output=True, text=True)
    first = (cp.stdout.splitlines() or [''])[0]
    print(f'{label:<16} exit={cp.returncode} :: {first}')
print('G links_sha =', gls)
print('B links_sha =', bls)
print('tree_sha (G==B) =', gts, '==', bts, gts == bts)
