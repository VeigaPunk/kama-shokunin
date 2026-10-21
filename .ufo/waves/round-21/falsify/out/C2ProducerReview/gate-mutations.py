#!/usr/bin/env python3
"""Gate mutation driver (FALSIFY evidence for C2ProducerReview).

Usage: python3 gate-mutations.py <lane_root> <live_receipt.json>

Reads the round-21 live v3 receipt (read-only), writes mutated copies under gate/
beside this file, and runs the lane's receipt gate CLI on each. Nothing else is written.
"""
import copy
import importlib.util
import json
import os
import subprocess
import sys

LANE, LIVE = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'gate')
GATE = os.path.join(LANE, 'tests/llamacpp-live/check-receipt.py')
os.makedirs(OUT, exist_ok=True)

spec = importlib.util.spec_from_file_location('gate_under_test', GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

with open(LIVE) as fh:
    base = json.load(fh)
base_tree_sha = base['server']['install_tree_sha256']
base_links_sha = base['server']['install_links_sha256']


def cli(name, receipt, flags=()):
    path = os.path.join(OUT, name + '.json')
    with open(path, 'w') as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    cp = subprocess.run(['python3', '-B', GATE, path, *flags],
                        capture_output=True, text=True, timeout=120)
    lines = cp.stdout.splitlines()
    head = lines[0] if lines else cp.stderr.strip()
    print(f'{name} flags={list(flags)} exit={cp.returncode} :: {head}')
    for ln in lines[1:2]:
        print('    ', ln)


def without(member):
    """Silently omit one install_tree member; recompute only the tree digest."""
    m = copy.deepcopy(base)
    tree = m['server']['install_tree']
    del tree[member]
    m['server']['install_tree_sha256'] = gate.install_tree_sha(tree)
    return m


REQ = ['--require-install-links']
cli('baseline-live', base, REQ)
cli('omit-nonchain-member', without('libggml-cpu-x64.so'), REQ)
cli('omit-nonchain-member-treepin', without('libggml-cpu-x64.so'),
    REQ + ['--expect-install-tree-sha256', base_tree_sha])
cli('omit-chain-target', without('libllama.so.0.7.0'), REQ)
empty = copy.deepcopy(base)
empty['server']['install_links'] = {}
empty['server']['install_links_sha256'] = None
cli('links-empty-null-digest', empty, REQ)
cli('links-empty-null-digest-linkspin', empty,
    REQ + ['--expect-install-links-sha256', base_links_sha])
nonempty = copy.deepcopy(base)
nonempty['server']['install_links_sha256'] = None
cli('links-nonempty-null-digest', nonempty, REQ)
