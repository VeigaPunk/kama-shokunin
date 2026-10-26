"""Validate the proposed fix in scratch: bounded *inflated* bytes, bounded hash
read (fstat size), RecursionError mapped to a provenance token.
Patched copy only; the lane file is untouched."""
import gzip, hashlib, io, os, stat as statmod, sys, tarfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawtar

S = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(S, 'build74558', 'tools', 'kama-llamacpp-live.py')
DST = os.path.join(S, 'patched', 'kama-llamacpp-live.py')
os.makedirs(os.path.dirname(DST), exist_ok=True)

NEW = '''ARCHIVE_MAX_BYTES = 1 << 30      # release assets are ~70 MB; 1 GiB is generous
MEMBER_MAX_COUNT = 4096          # archive index entries; the b11909 asset has ~60
ARCHIVE_MAX_INFLATED_BYTES = 1 << 30   # decompressed stream (b11909 asset: ~70 MB)


class _BoundedReader:
    """Counts the bytes tarfile pulls from the *decompressed* stream and refuses
    past `limit`: a 1 GiB gzip/bz2/xz file can inflate to terabytes, and the
    index walk must inflate all of it to reach the end of the catalogue."""

    def __init__(self, inner, limit, token):
        self.inner, self.limit, self.token, self.seen = inner, limit, token, 0

    def read(self, n=-1):
        data = self.inner.read(n)
        self.seen += len(data)
        if self.seen > self.limit:
            raise SetupError(self.token)
        return data

    def tell(self):
        return self.inner.tell()

    def seek(self, pos, whence=0):
        return self.inner.seek(pos, whence)

    def close(self):
        return None


def verify_archive_member(archive, asset_sha256, member, server_sha256, server_size=None):
    """Record-time provenance (v5). Bounds: regular file <= ARCHIVE_MAX_BYTES,
    archive hash reads no more than the size the cap was checked on, the member
    <= ARCHIVE_MAX_INFLATED_BYTES / totalsize, non-sparse, and the whole
    decompressed stream <= ARCHIVE_MAX_INFLATED_BYTES."""
    import tarfile
    try:
        st = os.stat(archive)
    except OSError:
        raise SetupError('provenance-archive-unreadable')
    if not stat.S_ISREG(st.st_mode):
        raise SetupError('provenance-archive-not-regular')
    if st.st_size > ARCHIVE_MAX_BYTES:
        raise SetupError('provenance-archive-too-large')
    try:
        arc = open(archive, 'rb')
    except OSError:
        raise SetupError('provenance-archive-unreadable')
    with arc:
        h_arc = hashlib.sha256()
        remaining = st.st_size
        while remaining > 0:
            chunk = arc.read(min(1 << 20, remaining))
            if not chunk:
                break
            h_arc.update(chunk)
            remaining -= len(chunk)
        archive_sha = h_arc.hexdigest()
        if archive_sha != asset_sha256:
            raise SetupError('provenance-archive-digest-mismatch')
        arc.seek(0)
        try:
            with tarfile.open(fileobj=arc, mode='r:*') as tf:
                tf.fileobj = _BoundedReader(
                    tf.fileobj, ARCHIVE_MAX_INFLATED_BYTES,
                    'provenance-archive-inflated-too-large')
                found, count = None, 0
                for info in tf:
                    count += 1
                    if count > MEMBER_MAX_COUNT:
                        raise SetupError('provenance-archive-too-many-members')
                    if info.name == member:
                        found = info
                if found is None:
                    raise SetupError('provenance-member-absent')
                if not found.isfile():
                    raise SetupError('provenance-member-not-a-file')
                if found.sparse is not None:
                    raise SetupError('provenance-member-sparse')
                if server_size is not None and found.size != server_size:
                    raise SetupError('provenance-member-size-mismatch')
                h = hashlib.sha256()
                fh = tf.extractfile(found)
                for chunk in iter(lambda: fh.read(1 << 20), b''):
                    h.update(chunk)
        except SetupError:
            raise
        except (OSError, EOFError, RecursionError, tarfile.TarError):
            raise SetupError('provenance-archive-unreadable')
    if h.hexdigest() != server_sha256:
        raise SetupError('provenance-member-digest-mismatch')
    return archive_sha, h.hexdigest()
'''

src = open(SRC).read()
start = src.index('ARCHIVE_MAX_BYTES = 1 << 30')
end = src.index('WITNESS_SCHEMA = ')
patched = src[:start] + NEW + '\n\n' + src[end:]
open(DST, 'w').write(patched)
print('patched bytes', len(patched), '->', DST)

os.environ['KLL_TOOL'] = DST
import importlib
import lib
lib.TOOL = DST
m = lib.load()
print('has bound', hasattr(m, 'ARCHIVE_MAX_INFLATED_BYTES'), m.ARCHIVE_MAX_INFLATED_BYTES)

TARGET = b'S' * 4096
tsha = hashlib.sha256(TARGET).hexdigest()

def emit(label, arch, asha=None, msha=None, size=4096):
    lib.emit(label, lib.run(m, arch, asha or lib.sha(arch), 'rel/llama-server',
                            msha or tsha, size))

class Zeros(io.RawIOBase):
    def __init__(self, n): self.n = n
    def read(self, k=-1):
        if self.n <= 0: return b''
        k = self.n if k in (None, -1) else min(k, self.n)
        self.n -= k
        return b'\0' * k

def bomb(path, opener, n):
    with open(path, 'wb') as raw, opener(raw) as comp:
        with tarfile.open(fileobj=comp, mode='w|', format=tarfile.GNU_FORMAT) as tf:
            ti = tarfile.TarInfo('rel/llama-server'); ti.size = 4096; ti.mtime = 0
            tf.addfile(ti, io.BytesIO(TARGET))
            ti = tarfile.TarInfo('filler'); ti.size = n; ti.mtime = 0
            tf.addfile(ti, Zeros(n))

# 1. gzip bomb 4 GiB (legit archive+member digests): must now refuse fast
p = os.path.join(S, 'p_gzip4g.tar.gz')
import gzip as gz
bomb(p, lambda f: gz.GzipFile(fileobj=f, mode='wb', compresslevel=1), 4 << 30)
emit('patched_gzip4g', p); os.unlink(p)

# 2. bz2 bomb 8 GiB
import bz2
p = os.path.join(S, 'p_bz2_8g.tar.bz2')
bomb(p, lambda f: bz2.BZ2File(f, mode='wb', compresslevel=1), 8 << 30)
emit('patched_bz2_8g', p); os.unlink(p)

# 3. legit compressed archive of a 4096-byte member still verifies
p = os.path.join(S, 'p_good.tar.gz')
with tarfile.open(p, 'w:gz') as tf:
    ti = tarfile.TarInfo('rel/llama-server'); ti.size = 4096; ti.mtime = 0
    tf.addfile(ti, io.BytesIO(TARGET))
emit('patched_good', p); os.unlink(p)

# 4. 1 GiB archive at the cap (uncompressed) still verifies, and the hash read is
#    bounded by the stat size even if the file is larger on disk
FULL = (1 << 30) - 10240 - 512
p = os.path.join(S, 'p_cap.tar')
with tarfile.open(p, 'w', format=tarfile.GNU_FORMAT) as tf:
    ti = tarfile.TarInfo('rel/llama-server'); ti.size = FULL; ti.mtime = 0
    tf.addfile(ti, Zeros(FULL))
h = hashlib.sha256()
for _ in range(FULL >> 20): h.update(b'\0' * (1 << 20))
h.update(b'\0' * (FULL % (1 << 20)))
emit('patched_cap_1GiB', p, msha=h.hexdigest(), size=FULL)

# growth beyond the stat size: stat reports 1 MiB, the fd holds 1.28 GiB
with open(p, 'ab') as fh: fh.write(b'\0' * (1280 << 20))
fake = os.stat(p)
class S2:
    st_mode = statmod.S_IFREG | 0o644
    st_size = 1024 * 1024
orig = m.os
class Shim:
    path = orig.path
    def stat(self, q, *a, **k):
        return S2() if q == p else orig.stat(q, *a, **k)
    def __getattr__(self, n): return getattr(orig, n)
m.os = Shim()
lib.emit('patched_growth_beyond_cap', lib.run(m, p, '0' * 64, 'rel/llama-server', tsha, FULL))
m.os = orig
os.unlink(p)

# 5. chained pax extensions: token, not internal:RecursionError
def pax_record(k, v):
    body = b'%s=%s\n' % (k.encode(), v); n = len(body) + 2
    while True:
        r = str(n).encode() + b' ' + body
        if len(r) == n: return r
        n = len(r)
rec = pax_record('comment', b'c')
blob = b''.join(rawtar.hdr('P', len(rec), typeflag=b'x') + rec + b'\0' * ((-len(rec)) % 512)
                for _ in range(900))
blob += rawtar.member('rel/llama-server', 4096, TARGET) + rawtar.end()
p = os.path.join(S, 'p_chain.tar.gz')
with gzip.open(p, 'wb', compresslevel=1) as fh: fh.write(blob)
emit('patched_chain900', p); os.unlink(p)

# 6. pax extension declaring 1 GiB of body (memory): bounded by the inflated cap
p = os.path.join(S, 'p_pax1g.tar.gz')
with open(p, 'wb') as raw, gz.GzipFile(fileobj=raw, mode='wb', compresslevel=1) as c:
    c.write(rawtar.hdr('P', 1 << 30, typeflag=b'x'))
    chunk = b'\0' * (1 << 20)
    for _ in range(1 << 10): c.write(chunk)
    c.write(rawtar.member('rel/llama-server', 4096, TARGET) + rawtar.end())
emit('patched_pax_ext_1GiB', p); os.unlink(p)
