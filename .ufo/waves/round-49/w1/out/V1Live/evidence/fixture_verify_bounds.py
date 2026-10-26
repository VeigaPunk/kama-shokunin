#!/usr/bin/env python3
"""V1Live fixture: verify_archive_member() bounds exercised against the lane tip
(kama-llamacpp-live.py at 74558c71c38ceaeace15fd4cf8aa9d84977584b1, imported via
importlib; loaded unmodified from the read-only lane clone)."""
import os, io, tarfile, tempfile, hashlib, importlib.util

SPEC = importlib.util.spec_from_file_location(
    'live', 'lane/tools/kama-llamacpp-live.py')
LIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LIVE)

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

d = tempfile.mkdtemp(prefix='v1live-fix-')

def mk_arc(n):
    p = os.path.join(d, f'arc{n}.tar')
    with tarfile.open(p, 'w') as tf:
        for i in range(n):
            ti = tarfile.TarInfo(f'f{i}'); ti.size = 1
            tf.addfile(ti, io.BytesIO(b'x'))
    return p

# 1) member-count cap boundary: 4096 entries pass, 4097 are refused
arc4096 = mk_arc(4096)
xfile = os.path.join(d, 'x'); open(xfile, 'wb').write(b'x')
try:
    LIVE.verify_archive_member(arc4096, sha(arc4096), 'f0', sha(xfile), 1)
    print('4096 index entries: PASS (no raise)')
except Exception as e:
    print('4096 index entries: unexpected', getattr(e, 'code', e))
arc4097 = mk_arc(4097)
try:
    LIVE.verify_archive_member(arc4097, sha(arc4097), 'f0', sha(xfile), 1)
    print('4097 index entries: NO RAISE (BUG)')
except LIVE.SetupError as e:
    print('4097 index entries ->', e.code)

# 2) duplicate member name: LAST occurrence wins (matches tarfile getmember/
#    extractfile on this interpreter, python 3.14.8)
dup = os.path.join(d, 'dup.tar')
with tarfile.open(dup, 'w') as tf:
    for body in (b'FIRST', b'LAST'):
        ti = tarfile.TarInfo('rel/llama-server'); ti.size = len(body)
        tf.addfile(ti, io.BytesIO(body))
srv_dup = os.path.join(d, 'srv_dup'); open(srv_dup, 'wb').write(b'LAST')
got = LIVE.verify_archive_member(dup, sha(dup), 'rel/llama-server',
                                 sha(srv_dup), 4)
print('duplicate member verified against LAST occurrence ->', got)

# 3) FIFO at the path is refused pre-open (S_ISREG guard)
fifo = os.path.join(d, 'fifo.tar')
os.mkfifo(fifo)
try:
    LIVE.verify_archive_member(fifo, '0' * 64, 'x', '0' * 64, 1)
    print('FIFO: NO RAISE (BUG)')
except LIVE.SetupError as e:
    print('FIFO ->', e.code)

# 4) truncated gzip archive: EOFError/TarError path maps to the stable token
gz = os.path.join(d, 'trunc.tar.gz')
with tarfile.open(gz, 'w:gz') as tf:
    ti = tarfile.TarInfo('rel/llama-server'); ti.size = 100; ti.mtime = 0
    tf.addfile(ti, io.BytesIO(b'A' * 100))
data = open(gz, 'rb').read()
open(gz, 'wb').write(data[:len(data) // 2])
try:
    LIVE.verify_archive_member(gz, sha(gz), 'rel/llama-server', '0' * 64, 100)
    print('truncated gzip member: NO RAISE')
except LIVE.SetupError as e:
    print('truncated gzip ->', e.code)
