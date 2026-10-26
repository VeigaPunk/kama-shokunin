"""Cap-case: archive at ARCHIVE_MAX_BYTES (1 GiB) - hash and walk cost."""
import hashlib, io, os, sys, tarfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

S = os.path.dirname(os.path.abspath(__file__))
m = lib.load()
FULL = (1 << 30) - 10240 - 512   # tar total (header+payload+trailer, rounded) <= 1 GiB

class Zeros(io.RawIOBase):
    def __init__(self, n): self.n = n
    def read(self, k=-1):
        if self.n <= 0: return b''
        k = self.n if k is None or k < 0 else min(k, self.n)
        self.n -= k
        return b'\0' * k

def build(path, members):
    t0 = time.monotonic()
    with tarfile.open(path, 'w', format=tarfile.GNU_FORMAT) as tf:
        for name, size in members:
            ti = tarfile.TarInfo(name); ti.size = size; ti.mtime = 0
            tf.addfile(ti, Zeros(size))
    return round(time.monotonic() - t0, 3)

def sha_zeros(n):
    h = hashlib.sha256()
    while n > 0:
        k = min(n, 1 << 20); h.update(b'\0' * k); n -= k
    return h.hexdigest()

a = os.path.join(S, 'cap_full.tar')
bt = build(a, [('rel/llama-server', FULL)])
sz = os.path.getsize(a)
print('cap_full_built', sz, 'build_s', bt, 'under_cap', sz <= (1 << 30), flush=True)
lib.emit('cap_full', lib.run(m, a, lib.sha(a), 'rel/llama-server', sha_zeros(FULL), FULL))

c = os.path.join(S, 'cap_smallmem.tar')
build(c, [('filler', FULL - 4608), ('rel/llama-server', 4096)])
print('cap_smallmem_built', os.path.getsize(c), flush=True)
lib.emit('cap_smallmem', lib.run(m, c, lib.sha(c), 'rel/llama-server',
                                 hashlib.sha256(b'\0' * 4096).hexdigest(), 4096))

t0 = time.monotonic(); lib.sha(a)
print('sha_1GiB_seconds', round(time.monotonic() - t0, 3), flush=True)

# the same archive one byte over the cap is refused before any read
d = os.path.join(S, 'cap_over.tar')
build(d, [('rel/llama-server', FULL)])
with open(d, 'r+b') as fh:
    fh.truncate(0)
build(d, [('rel/llama-server', (1 << 30) - 10240)])
print('cap_over_size', os.path.getsize(d), flush=True)
lib.emit('cap_over', lib.run(m, d, '0' * 64, 'rel/llama-server', '0' * 64, 1 << 30))
for f in (a, c, d):
    os.unlink(f)
