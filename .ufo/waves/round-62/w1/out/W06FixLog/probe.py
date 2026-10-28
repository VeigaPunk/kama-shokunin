#!/usr/bin/env python3
"""Red-before / green-after probe for the two post-freeze C1 counter repairs.
No live server, no git writes; imports the committed tip counter and the
working-tree counter and feeds both the same captured receipt bytes."""
import copy
import importlib.util
import json
import sys

HEAD = '/fast/scratch/hyaku/kama-r62/w/W06FixLog/head-counter.py'
WT = '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round62-c1-counter.py'
RECEIPT = ('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-62/'
           'w1/out/A02C1HoldTamper/c1-hold-tamper-counter-live-receipt.json')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def show(label, fn, receipt):
    try:
        out, inconsistent = fn(receipt)
        print(f'{label}: checks={len(out)} inconsistent={inconsistent}')
    except Exception as exc:  # noqa: BLE001 - the defect under test is a crash
        print(f'{label}: CRASH {type(exc).__name__}: {exc}')


head = load(HEAD, 'c1_head')
wt = load(WT, 'c1_wt')
base = json.load(open(RECEIPT))
tampered = copy.deepcopy(base)
tampered['captures']['completion']['body'] = '__kama_mut__'

print('receipt:', RECEIPT)
print('stored check names:', sorted((base.get('checks') or {}).keys()))
show('tip   pristine', head.grade, base)
show('tip   tampered', head.grade, tampered)
show('tree  pristine', wt.grade, base)
show('tree  tampered', wt.grade, tampered)
