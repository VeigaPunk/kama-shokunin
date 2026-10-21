#!/usr/bin/env python3
"""C2 proposed-encoding check (critic seat; scratch only, nothing applied to the lane).

Tests whether a canonical JSON encoding of the link map removes the P1
collision and the E5 UnicodeEncodeError, using the producer's current
rendering as the baseline. Also names the grid's second-arm retarget
target for the real tree (read-only listing).
"""
import hashlib
import json
import os
from pathlib import Path

REAL = Path.home() / '.local/opt/llama-b11755'


def current(m):
    return hashlib.sha256(''.join(f'{n} -> {m[n]}\n' for n in sorted(m))
                          .encode()).hexdigest()


def canonical(m):
    return hashlib.sha256(json.dumps(sorted(m.items()), ensure_ascii=True,
                                     separators=(',', ':')).encode('ascii')
                          ).hexdigest()


G = {'libllama.so': 'libllama.so.0', 'libllama.so.0': 'libllama.so.0.7.0'}
B = {'libllama.so -> libllama.so.0\nlibllama.so.0': 'libllama.so.0.7.0'}
print('current(G) == probe-output digest a49818c8:',
      current(G).startswith('a49818c8'))
print('current(G) == current(B):', current(G) == current(B))
print('canonical(G) == canonical(B):', canonical(G) == canonical(B))
W = {'libweird.so': '\udcff.so'}
try:
    current(W)
    print('current(W): encoded')
except UnicodeEncodeError as exc:
    print('current(W): UnicodeEncodeError (E5)')
print('canonical(W) ascii digest:', canonical(W))
regular = sorted(e for e in os.listdir(REAL)
                 if (REAL / e).is_file() and not (REAL / e).is_symlink())
print('grid other_member (first sorted regular, not the real target):',
      regular[0])
