"""C: what check-receipt.py accepts that the producer (or the loader) would not.

Every receipt is derived from the round-21 live receipt (copied to /tmp) with
only the server block replaced by producer-shaped output for a /tmp tree.
Gate runs are real subprocess invocations of the attacked-commit gate."""
import json
import os
import shutil
import subprocess

import common as C

P, G, W = C.P, C.G, C.WORK
PIN_TREE = '6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c'
PIN_LINKS = '5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060'
LIVE = os.path.join(W, 'live-receipt.json')
REQ = ['--require-install-links']


def run(label, path, *flags):
    rc, out, err = C.gate(path, *flags)
    first = (out.splitlines() or [''])[0][:170]
    print(f'{label}: exit={rc} | {first}' + (f' | stderr: {err.splitlines()[-1][:140]}' if err else ''), flush=True)
    return rc


def load_text(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


print('== C0 baseline (unmodified round-21 live receipt, lane pins)')
run(' live receipt, pins', LIVE, *REQ, '--expect-install-tree-sha256', PIN_TREE,
    '--expect-install-links-sha256', PIN_LINKS)

print('== C1 tree member names not validated: merged name with \\n and space')
r = C.live_receipt()
tree = r['server']['install_tree']
names = sorted(tree)
pair = next((names[i], names[i + 1]) for i in range(len(names) - 1)
            if {names[i], names[i + 1]}.isdisjoint({'llama-server', 'libllama-server-impl.so'}))
n1, n2 = pair
h1, h2 = tree[n1], tree[n2]
merged = dict(tree)
del merged[n1], merged[n2]
merged[f'{n1} {h1}\n{n2}'] = h2
print(f' merged {n1!r} + {n2!r} -> one key; members {len(tree)} -> {len(merged)}')
print(' recomputed digest equal to pin:', G.install_tree_sha(merged) == PIN_TREE)
r['server']['install_tree'] = merged
p = C.write_receipt(os.path.join(W, 'c1-tree-merged.json'), r)
run(' merged-name receipt, tree pin', p, *REQ, '--expect-install-tree-sha256', PIN_TREE,
    '--expect-install-links-sha256', PIN_LINKS)

print('== C2 lone-surrogate-pair key: raw CESU bytes in the file vs escaped form')
text = C.write_receipt(os.path.join(W, 'c2-ref.json'), C.live_receipt())
txt = load_text(text)
anchor = '"libmtmd.so": "libmtmd.so.0"'
assert txt.count(anchor) == 1, txt.count(anchor)
raw = txt.replace(anchor, '"libmtmd\ud83d\ude00.so": "libmtmd.so.0"')   # str with surrogates
try:
    raw.encode('utf-8')
    print(' (unexpected) encodes')
except UnicodeEncodeError:
    pass
cesu = txt.replace(anchor, '"libmtmd\xed\xa0\xbd\xed\xb8\x80.so": "libmtmd.so.0"')
with open(os.path.join(W, 'c2-cesu.json'), 'wb') as fh:
    fh.write(cesu.encode('latin-1'))
run(' CESU bytes (raw surrogates in file)', os.path.join(W, 'c2-cesu.json'), *REQ)
esc = txt.replace(anchor, '"libmtmd\\ud83d\\ude00.so": "libmtmd.so.0"')
with open(os.path.join(W, 'c2-esc.json'), 'w', encoding='utf-8') as fh:
    fh.write(esc)
run(' escaped surrogate pair (json combines to astral)', os.path.join(W, 'c2-esc.json'), *REQ)

print('== C3 empty install_links + null digest satisfies --require-install-links')
r = C.live_receipt()
r['server']['install_links'] = {}
r['server']['install_links_sha256'] = None
p = C.write_receipt(os.path.join(W, 'c3-empty-links.json'), r)
run(' empty links, null digest, --require-install-links', p, *REQ, '--expect-install-tree-sha256', PIN_TREE)
run(' same, with links pin', p, *REQ, '--expect-install-tree-sha256', PIN_TREE,
    '--expect-install-links-sha256', PIN_LINKS)
r2 = C.live_receipt()
r2['server']['install_links'] = {}
print(' producer digest of {} would be', P.links_digest({}), '(producer never emits null)')

print('== C4 duplicate JSON keys: gate (last wins) vs first-wins reader')
txt = load_text(C.write_receipt(os.path.join(W, 'c4-ref.json'), C.live_receipt()))
anchor = '"libllama.so.0": "libllama.so.0.7.0"'
assert txt.count(anchor) == 1, txt.count(anchor)
dup = txt.replace(anchor, '"libllama.so.0": "libllama.so.0.7.1",\n      ' + anchor)
p = os.path.join(W, 'c4-dup.json')
with open(p, 'w', encoding='utf-8') as fh:
    fh.write(dup)
run(' duplicate key [first=invalid 0.7.1, last=valid 0.7.0]', p, *REQ,
    '--expect-install-tree-sha256', PIN_TREE, '--expect-install-links-sha256', PIN_LINKS)


def first_wins(pairs):
    out = {}
    for k, v in pairs:
        out.setdefault(k, v)
    return out


doc_first = json.loads(dup, object_pairs_hook=first_wins)
first_links = doc_first['server']['install_links']
print(' first-wins reader: libllama.so.0 ->', first_links['libllama.so.0'],
      '| digest', G.install_links_sha(first_links)[:16], 'vs pin', PIN_LINKS[:16])
print(' first-wins chain verdict:', G.link_chain_problem('libllama.so.0', first_links, C.live_receipt()['server']['install_tree']))

print('== C5 producer-shaped receipt for a 41-hop chain the loader cannot open')
d41 = os.path.join(W, 'hops-41')
srv41 = os.path.join(d41, 'stub-server')
r41, probs41 = C.receipt_for(srv41)
print(' producer problems:', probs41, '| recorded links:', len(r41['server']['install_links']))
p41 = C.write_receipt(os.path.join(W, 'c5-hops41.json'), r41)
run(' 41-hop receipt, its own digest pins', p41, *REQ,
    '--expect-install-tree-sha256', r41['server']['install_tree_sha256'],
    '--expect-install-links-sha256', r41['server']['install_links_sha256'])

print('== C6 non-UTF-8 symlink names/targets: gate verdicts on a receipt')
dsurr = os.path.join(W, 'd-surr')
bsurr = os.fsencode(dsurr)
os.unlink(os.path.join(bsurr, b'libdangle.so')) if os.path.lexists(os.path.join(bsurr, b'libdangle.so')) else None
r6, probs6 = C.receipt_for(os.path.join(dsurr, 'llama-server'))
print(' producer problems:', probs6, '| link keys (ascii):', [ascii(k) for k in r6['server']['install_links']])
p6 = C.write_receipt(os.path.join(W, 'c6-surr.json'), r6)
run(' non-UTF-8 link receipt', p6, *REQ, '--expect-install-tree-sha256', r6['server']['install_tree_sha256'],
    '--expect-install-links-sha256', r6['server']['install_links_sha256'])

print('== C7 gate on a tree member name with a lone surrogate (internal exception path)')
r7 = C.live_receipt()
r7['server']['install_tree']['\udcff-member'] = 'e' * 64
p7 = C.write_receipt(os.path.join(W, 'c7-surr-member.json'), r7)
run(' surrogate member name', p7, *REQ)

print('== C8 absolute-target soname link: producer records, gate rejects')
dabs = os.path.join(W, 'd-abs')
shutil.rmtree(dabs, ignore_errors=True)
os.makedirs(dabs)
shutil.copy(os.path.join(W, 'host-bin'), os.path.join(dabs, 'stub-server'))
shutil.copy(os.path.join(W, 'libllama-A.so.0.7.0'), os.path.join(dabs, 'libllama.so.0.7.0'))
os.symlink('/usr/lib/libz.so.1', os.path.join(dabs, 'libext.so.0'))
r8, probs8 = C.receipt_for(os.path.join(dabs, 'stub-server'))
print(' producer problems:', probs8, '| recorded:', r8['server']['install_links'])
p8 = C.write_receipt(os.path.join(W, 'c8-abs.json'), r8)
run(' absolute-target receipt', p8, *REQ, '--expect-install-tree-sha256', r8['server']['install_tree_sha256'],
    '--expect-install-links-sha256', r8['server']['install_links_sha256'])
print('done C', flush=True)
