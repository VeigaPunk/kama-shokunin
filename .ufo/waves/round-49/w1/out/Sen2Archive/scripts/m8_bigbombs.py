"""Bigger bombs: bytes of archive in vs seconds of record time out.
Each archive holds the tiny target member plus one huge zero member; the walk
must inflate everything to reach the end of the catalogue."""
import bz2, gzip, hashlib, io, lzma, os, sys, tarfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

S = os.path.dirname(os.path.abspath(__file__))
m = lib.load()
TARGET = b'S' * 4096
tsha = hashlib.sha256(TARGET).hexdigest()
WRONG = '0' * 64

class Zeros(io.RawIOBase):
    def __init__(self, n): self.n = n
    def read(self, k=-1):
        if self.n <= 0: return b''
        k = self.n if k is None or k < 0 else min(k, self.n)
        self.n -= k
        return b'\0' * k

def build(path, opener, bomb):
    t0 = time.monotonic()
    with open(path, 'wb') as raw, opener(raw) as comp:
        with tarfile.open(fileobj=comp, mode='w|', format=tarfile.GNU_FORMAT) as tf:
            ti = tarfile.TarInfo('rel/llama-server'); ti.size = len(TARGET); ti.mtime = 0
            tf.addfile(ti, io.BytesIO(TARGET))
            ti = tarfile.TarInfo('filler'); ti.size = bomb; ti.mtime = 0
            tf.addfile(ti, Zeros(bomb))
    return round(time.monotonic() - t0, 3)

cases = [
    ('gzip_64GiB', lambda f: gzip.GzipFile(fileobj=f, mode='wb', compresslevel=1), 64 << 30),
    ('xz_32GiB',   lambda f: lzma.LZMAFile(f, mode='wb', preset=0), 32 << 30),
    ('bz2_32GiB',  lambda f: bz2.BZ2File(f, mode='wb', compresslevel=1), 32 << 30),
]
for label, opener, bomb in cases:
    p = os.path.join(S, label + '.tar.bin')
    bt = build(p, opener, bomb)
    size = os.path.getsize(p)
    r = lib.run(m, p, lib.sha(p), 'rel/llama-server', WRONG, len(TARGET))
    r.update({'archive_bytes': size, 'inflated_bytes': bomb, 'build_seconds': bt,
              'ratio': round(bomb / size, 1),
              'mb_per_s': round(bomb / (1 << 20) / max(r['seconds'], 1e-9), 1)})
    r['projected_cap_seconds'] = round((1 << 30) * (bomb / size) / (bomb / r['seconds']), 1)
    lib.emit(label, r)
    os.unlink(p)
