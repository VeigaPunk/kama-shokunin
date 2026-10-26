"""Decompression bombs via mode='r:*': walk must inflate the whole stream.
Each fixture: the target member first (named, right size), then one huge
zero member; the index walk still inflates everything to reach the end."""
import bz2, gzip, io, lzma, os, sys, tarfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

S = os.path.dirname(os.path.abspath(__file__))
m = lib.load()

class Zeros(io.RawIOBase):
    def __init__(self, n): self.n = n
    def read(self, k=-1):
        if self.n <= 0: return b''
        k = self.n if k is None or k < 0 else min(k, self.n)
        self.n -= k
        return b'\0' * k

def build(path, opener, bomb, target_bytes=b'S' * 4096):
    t0 = time.monotonic()
    with open(path, 'wb') as raw, opener(raw) as comp:
        with tarfile.open(fileobj=comp, mode='w|', format=tarfile.GNU_FORMAT) as tf:
            ti = tarfile.TarInfo('rel/llama-server'); ti.size = len(target_bytes); ti.mtime = 0
            tf.addfile(ti, io.BytesIO(target_bytes))
            ti = tarfile.TarInfo('filler'); ti.size = bomb; ti.mtime = 0
            tf.addfile(ti, Zeros(bomb))
    return round(time.monotonic() - t0, 3)

TARGET = b'S' * 4096
tsha = __import__('hashlib').sha256(TARGET).hexdigest()
cases = [
    ('gzip4g', lambda raw: gzip.GzipFile(fileobj=raw, mode='wb', compresslevel=1), 4 << 30),
    ('xz1g',   lambda raw: lzma.LZMAFile(raw, mode='wb', preset=0), 1 << 30),
    ('bz2_512m', lambda raw: bz2.BZ2File(raw, mode='wb', compresslevel=1), 512 << 20),
]
for label, opener, bomb in cases:
    p = os.path.join(S, label + '.tar.compressed')
    bt = build(p, opener, bomb)
    asha = lib.sha(p)
    r = lib.run(m, p, asha, 'rel/llama-server', tsha, len(TARGET))
    r['build_seconds'] = bt; r['declared_bomb_bytes'] = bomb
    lib.emit(label, r)
    os.unlink(p)
