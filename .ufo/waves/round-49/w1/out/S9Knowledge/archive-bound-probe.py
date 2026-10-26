#!/usr/bin/env python3
"""S9Knowledge probe: verify_archive_member() refusals at HEAD, no server run.

usage: archive-bound-probe.py <scratch>
Builds each archive under <scratch>/cap, calls the lane function directly.
"""
import hashlib
import importlib.util
import io
import os
import sys
import tarfile
import time

S = sys.argv[1]
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
spec = importlib.util.spec_from_file_location(
    'kl', os.path.join(LANE, 'tools/kama-llamacpp-live.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

d = os.path.join(S, 'cap')
os.makedirs(d, exist_ok=True)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        h.update(fh.read())
    return h.hexdigest()


srv = os.path.join(d, 'llama-server')
with open(srv, 'wb') as fh:
    fh.write(b'#!/bin/sh\nexit 3\n')
os.chmod(srv, 0o755)
ssha, ssize = sha(srv), os.path.getsize(srv)

good = os.path.join(d, 'good.tar.gz')
with tarfile.open(good, 'w:gz') as tf:
    tf.add(srv, arcname='rel/llama-server')

bomb = os.path.join(d, 'bomb.tar.gz')
with tarfile.open(bomb, 'w:gz', format=tarfile.PAX_FORMAT) as tf:
    ti = tarfile.TarInfo('rel/llama-server')
    ti.size = 1
    ti.mode = 0o755
    ti.pax_headers = {'GNU.sparse.map': '0,1', 'GNU.sparse.major': '1',
                      'GNU.sparse.minor': '0',
                      'GNU.sparse.realsize': str(10 ** 15)}
    tf.addfile(ti, io.BytesIO(b'A'))

big = os.path.join(d, 'big.tar.gz')
with open(big, 'wb') as fh:
    fh.truncate((1 << 30) + 1)

many = os.path.join(d, 'many.tar.gz')
with tarfile.open(many, 'w:gz') as tf:
    for i in range(4100):
        ti = tarfile.TarInfo('f%d' % i)
        ti.size = 0
        tf.addfile(ti, io.BytesIO(b''))

dup = os.path.join(d, 'dup.tar.gz')
with open(srv, 'rb') as fh:
    server_bytes = fh.read()
with tarfile.open(dup, 'w:gz') as tf:
    for body in (b'old', server_bytes):
        ti = tarfile.TarInfo('rel/llama-server')
        ti.size = len(body)
        tf.addfile(ti, io.BytesIO(body))

cases = [
    ('good', (good, sha(good), 'rel/llama-server', ssha, ssize)),
    ('sparse-1e15', (bomb, sha(bomb), 'rel/llama-server', ssha, None)),
    ('size-mismatch', (good, sha(good), 'rel/llama-server', ssha, ssize + 1)),
    ('archive-too-large', (big, sha(big), 'rel/llama-server', ssha, ssize)),
    ('too-many-members', (many, sha(many), 'rel/llama-server', ssha, None)),
    ('not-regular', ('/dev/null', '0' * 64, 'rel/llama-server', ssha, None)),
    ('duplicate-last-wins', (dup, sha(dup), 'rel/llama-server', sha(srv), ssize)),
]
for name, args in cases:
    t0 = time.monotonic()
    try:
        arc_sha, member_sha = m.verify_archive_member(*args)
        out = 'ok member %s == server %s' % (member_sha[:12], ssha[:12])
    except m.SetupError as exc:
        out = 'SetupError %s' % exc.code
    print('%-20s %-48s %.3fs' % (name, out, time.monotonic() - t0))
print('sizes: bomb %d bytes (declares 10^15), big %d bytes allocated %d, many %d entries'
      % (os.path.getsize(bomb), os.path.getsize(big), os.stat(big).st_blocks * 512, 4100))
