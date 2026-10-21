"""G: (1) a surrogate-escaped link key is the same bytes the kernel resolves;
(2) invisible / bidi / DEL / C1 names are accepted by the producer and are
escaped in the ensure_ascii receipt text (human-review exposure only)."""
import json
import os
import shutil

import common as C

P, G, W = C.P, C.G, C.WORK

print('== G1 surrogate-escaped link key maps back to the kernel name bytes')
d = os.path.join(W, 'd-kernel-surr')
shutil.rmtree(d, ignore_errors=True)
os.makedirs(d)
with open(os.path.join(d, 'llama-server'), 'wb') as fh:
    fh.write(b'stub\n')
with open(os.path.join(d, 'libllama.so.0.7.0'), 'wb') as fh:
    fh.write(b'lib\n')
os.symlink(b'libllama.so.0.7.0', os.path.join(os.fsencode(d), b'\xffsoname'))
links, _, probs = P.install_links(os.path.join(d, 'llama-server'))
key = next(iter(k for k in links if k.startswith('\udcff')))
print(' key repr:', ascii(key), '| fsencode(key) == original bytes:', os.fsencode(key) == b'\xffsoname')
print(' kernel resolves the key as a path:', os.path.exists(os.path.join(d, key)), '| problems:', probs)

print('== G2 invisible, bidi, DEL and C1 names: producer acceptance and receipt text')
d2 = os.path.join(W, 'd-invisible')
shutil.rmtree(d2, ignore_errors=True)
os.makedirs(d2)
with open(os.path.join(d2, 'llama-server'), 'wb') as fh:
    fh.write(b'stub\n')
with open(os.path.join(d2, 'libllama.so.0.7.0'), 'wb') as fh:
    fh.write(b'lib\n')
for n in ('libllama.so.0\u200b', 'libllama.so.0\u202e', 'libllama.so.0\x7f'):
    os.symlink('libllama.so.0.7.0', os.path.join(d2, n))
links2, _, probs2 = P.install_links(os.path.join(d2, 'llama-server'))
print(' producer problems:', probs2, '| recorded keys:', len(links2))
text = json.dumps(links2, sort_keys=True, ensure_ascii=True)
print(' receipt text:', text)
print(' all non-ASCII/DEL escaped (receipt is pure ASCII):', text.isascii())
print('done G', flush=True)
