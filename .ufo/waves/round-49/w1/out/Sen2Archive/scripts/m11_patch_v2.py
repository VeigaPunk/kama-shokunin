"""Validate proposed remediation v2: in-process wall-clock bound + RLIMIT_AS bound
around the tar walk, RecursionError/MemoryError mapped to a provenance token, and
the archive hash read bounded by the stat size it was checked against."""
import gzip, hashlib, io, os, stat as statmod, sys, tarfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawtar

S = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(S, 'build74558', 'tools', 'kama-llamacpp-live.py')
DST = os.path.join(S, 'patched', 'kama-llamacpp-live.py')
os.makedirs(os.path.dirname(DST), exist_ok=True)

NEW = '''ARCHIVE_MAX_BYTES = 1 << 30      # release assets are ~70 MB; 1 GiB is generous
MEMBER_MAX_COUNT = 4096          # archive index entries; the b11909 asset has ~60
ARCHIVE_WALK_SECONDS = 20        # wall-clock budget for the index walk + member hash
ARCHIVE_WALK_RSS_BYTES = 2 << 30 # address-space budget for the same


class _ArchiveWalkTimeout(Exception):
    """SIGALRM during the bounded archive walk."""


def _archive_walk_alarm(signum, frame):
    raise _ArchiveWalkTimeout()


def verify_archive_member(archive, asset_sha256, member, server_sha256, server_size=None):
    """Record-time provenance (v5). Bounds: regular file <= ARCHIVE_MAX_BYTES; the
    archive hash reads no more than the size the cap was checked on; the tar walk
    (which must inflate a compressed stream to the end of the catalogue, and which
    materialises any pax extension header at its declared size) runs under
    ARCHIVE_WALK_SECONDS and ARCHIVE_WALK_RSS_BYTES; the member must be a regular,
    non-sparse file whose declared size equals server_size, all before a byte of it
    is hashed."""
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
        old_handler = signal.signal(signal.SIGALRM, _archive_walk_alarm)
        old_alarm = signal.setitimer(signal.ITIMER_REAL, ARCHIVE_WALK_SECONDS)
        old_rss = resource.getrlimit(resource.RLIMIT_AS)
        cur_soft = old_rss[0]
        try:
            resource.setrlimit(resource.RLIMIT_AS, (
                ARCHIVE_WALK_RSS_BYTES
                if cur_soft == resource.RLIM_INFINITY or cur_soft > ARCHIVE_WALK_RSS_BYTES
                else cur_soft,
                old_rss[1]))
        except (ValueError, OSError):
            pass
        try:
            with tarfile.open(fileobj=arc, mode='r:*') as tf:
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
        except _ArchiveWalkTimeout:
            raise SetupError('provenance-archive-walk-timeout')
        except MemoryError:
            raise SetupError('provenance-archive-walk-memory')
        except (OSError, EOFError, RecursionError, tarfile.TarError):
            raise SetupError('provenance-archive-unreadable')
        finally:
            signal.setitimer(signal.ITIMER_REAL, *old_alarm)
            signal.signal(signal.SIGALRM, old_handler)
            try:
                resource.setrlimit(resource.RLIMIT_AS, old_rss)
            except (ValueError, OSError):
                pass
    if h.hexdigest() != server_sha256:
        raise SetupError('provenance-member-digest-mismatch')
    return archive_sha, h.hexdigest()
'''

src = open(SRC).read()
start = src.index('ARCHIVE_MAX_BYTES = 1 << 30')
end = src.index('WITNESS_SCHEMA = ')
patched = src[:start] + NEW + '\n\n' + src[end:]
for mod in ('resource', 'signal'):
    if ('import %s' % mod) not in patched.split('SCHEMA =')[0]:
        pass
# ensure the stdlib imports exist
patched = patched.replace('import re\n', 'import re\nimport resource\n', 1) if '\nimport resource\n' not in patched else patched
open(DST, 'w').write(patched)
print('patched bytes', len(patched), '->', DST)

import lib
lib.TOOL = DST
m = lib.load()
print('walk seconds', m.ARCHIVE_WALK_SECONDS, 'rss', m.ARCHIVE_WALK_RSS_BYTES,
      'has resource', hasattr(m, 'resource'))

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

# time bound: bz2 8 GiB took 13.4 s unbounded; with the 5 s budget it must refuse
m.ARCHIVE_WALK_SECONDS = 5
import bz2
p = os.path.join(S, 'p2_bz2_8g.tar.bz2')
bomb(p, lambda f: bz2.BZ2File(f, mode='wb', compresslevel=1), 8 << 30)
emit('v2_bz2_8g_5s_budget', p); os.unlink(p)

# memory bound: a pax extension body of 1 GiB needs ~5 GiB RSS unbounded
m.ARCHIVE_WALK_RSS_BYTES = 1 << 30
p = os.path.join(S, 'p2_pax1g.tar.gz')
with open(p, 'wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', compresslevel=1) as c:
    c.write(rawtar.hdr('P', 1 << 30, typeflag=b'x'))
    for _ in range(1 << 10): c.write(b'\0' * (1 << 20))
    c.write(rawtar.member('rel/llama-server', 4096, TARGET) + rawtar.end())
emit('v2_pax_1GiB_1GiB_rss_budget', p); os.unlink(p)
m.ARCHIVE_WALK_RSS_BYTES = 2 << 30

# recursion: chain of pax extensions -> provenance token, not internal:RecursionError
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
p = os.path.join(S, 'p2_chain.tar.gz')
with gzip.open(p, 'wb', compresslevel=1) as fh: fh.write(blob)
emit('v2_chain900', p); os.unlink(p)

# growth: stat reports 1 MiB while the fd holds more -> hash stops at the stat size
FULL = 4096
p = os.path.join(S, 'p2_grow.tar')
open(p, 'wb').write(rawtar.member('rel/llama-server', 4096, TARGET) + rawtar.end()
                    + b'\0' * (64 << 20))
class S2:
    st_mode = statmod.S_IFREG | 0o644
    st_size = 4096
orig = m.os
class Shim:
    path = orig.path
    def stat(self, q, *a, **k):
        return S2() if q == p else orig.stat(q, *a, **k)
    def __getattr__(self, n): return getattr(orig, n)
m.os = Shim()
lib.emit('v2_growth_stops_at_stat_size', lib.run(m, p, lib.sha(p)[:64], 'rel/llama-server',
                                                '0' * 64, 4096))
m.os = orig
os.unlink(p)

# regressions: legit archives still verify
p = os.path.join(S, 'p2_good.tar.gz')
with tarfile.open(p, 'w:gz') as tf:
    ti = tarfile.TarInfo('rel/llama-server'); ti.size = 4096; ti.mtime = 0
    tf.addfile(ti, io.BytesIO(TARGET))
emit('v2_good_gz', p); os.unlink(p)

FULLB = (1 << 30) - 10240 - 512
p = os.path.join(S, 'p2_cap.tar')
with tarfile.open(p, 'w', format=tarfile.GNU_FORMAT) as tf:
    ti = tarfile.TarInfo('rel/llama-server'); ti.size = FULLB; ti.mtime = 0
    tf.addfile(ti, Zeros(FULLB))
h = hashlib.sha256()
for _ in range(FULLB >> 20): h.update(b'\0' * (1 << 20))
h.update(b'\0' * (FULLB % (1 << 20)))
emit('v2_cap_1GiB', p, msha=h.hexdigest(), size=FULLB)
os.unlink(p)

# a real 1 GiB compressed-storm archive is now refused well inside 20 s
m.ARCHIVE_WALK_SECONDS = 20
import gzip as gz
p = os.path.join(S, 'p2_gzip_64GiB.tar.gz')
bomb(p, lambda f: gz.GzipFile(fileobj=f, mode='wb', compresslevel=1), 64 << 30)
emit('v2_gzip_64GiB_20s_budget', p); os.unlink(p)
