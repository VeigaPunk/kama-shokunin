"""Index walk cost with many tiny members and long names / PAX headers."""
import hashlib, io, os, sys, tarfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

S = os.path.dirname(os.path.abspath(__file__))
m = lib.load()
TARGET = b'S' * 4096
tsha = hashlib.sha256(TARGET).hexdigest()

def build(path, n, name_len, fmt, target_last=True):
    t0 = time.monotonic()
    with tarfile.open(path, 'w|' + ('gz' if path.endswith('.gz') else ''), format=fmt) as tf:
        if not target_last:
            ti = tarfile.TarInfo('rel/llama-server'); ti.size = len(TARGET); ti.mtime = 0
            tf.addfile(ti, io.BytesIO(TARGET))
        for i in range(n):
            ti = tarfile.TarInfo('d%04d/%s' % (i, 'x' * name_len))
            ti.size = 1; ti.mtime = 0
            tf.addfile(ti, io.BytesIO(b'z'))
        if target_last:
            ti = tarfile.TarInfo('rel/llama-server'); ti.size = len(TARGET); ti.mtime = 0
            tf.addfile(ti, io.BytesIO(TARGET))
    return round(time.monotonic() - t0, 3)

cases = [
    ('many_4096_pax_long', 4095, 3000, tarfile.PAX_FORMAT, 'many4096.tar.gz'),
    ('many_4096_short', 4095, 40, tarfile.PAX_FORMAT, 'many4096short.tar.gz'),
    ('many_over_4097', 4097, 40, tarfile.PAX_FORMAT, 'many4098.tar.gz'),
    ('many_4096_uncompressed', 4095, 40, tarfile.GNU_FORMAT, 'many4096.tar'),
]
for label, n, nlen, fmt, fname in cases:
    p = os.path.join(S, fname)
    bt = build(p, n, nlen, fmt)
    r = lib.run(m, p, lib.sha(p), 'rel/llama-server', tsha, len(TARGET))
    r['build_seconds'] = bt; r['members'] = n + 1; r['name_len'] = nlen
    lib.emit(label, r)
    os.unlink(p)
