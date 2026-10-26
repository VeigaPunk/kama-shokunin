"""TOCTOU and cap-enforcement on the fd: (1) stat says regular while the path is
a FIFO at open() -> open blocks; (2) stat says <=1 GiB while the fd holds more."""
import os, stat as statmod, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, rawtar

S = os.path.dirname(os.path.abspath(__file__))
m = lib.load()
mode = sys.argv[1] if len(sys.argv) > 1 else 'all'

TARGET = b'S' * 4096
import hashlib
tsha = hashlib.sha256(TARGET).hexdigest()

if mode in ('all', 'fifo'):
    # Simulate the stat->open window: os.stat(path) sees a regular file, while the
    # path itself is a FIFO with no writer. open() without O_NONBLOCK blocks forever.
    fifo = os.path.join(S, 'swap.fifo')
    real = os.path.join(S, 'swap.tar')
    open(real, 'wb').write(rawtar.member('rel/llama-server', 4096, TARGET) + rawtar.end())
    if os.path.exists(fifo): os.unlink(fifo)
    os.mkfifo(fifo)
    real_stat = os.stat(real)
    orig = m.os
    class Shim:
        path = orig.path
        def stat(self, p, *a, **k):
            return real_stat if p == fifo else orig.stat(p, *a, **k)
        def __getattr__(self, name):
            return getattr(orig, name)
    m.os = Shim()
    t0 = time.monotonic()
    try:
        m.verify_archive_member(fifo, '0' * 64, 'rel/llama-server', tsha, 4096)
        lib.emit('fifo_swapped', {'result': 'returned', 'seconds': round(time.monotonic() - t0, 3)})
    except m.SetupError as exc:
        lib.emit('fifo_swapped', {'result': 'SetupError', 'token': exc.code,
                                  'seconds': round(time.monotonic() - t0, 3)})
    except BaseException as exc:
        lib.emit('fifo_swapped', {'result': type(exc).__name__,
                                  'seconds': round(time.monotonic() - t0, 3)})
    m.os = orig
    os.unlink(fifo); os.unlink(real)

if mode in ('all', 'grow'):
    # Simulated growth: the pre-open stat reports 1 MiB (well under the 1 GiB cap)
    # while the file actually holds 1.25 GiB. The hash loop reads to EOF of the fd,
    # so the cap does not bound the bytes read.
    p = os.path.join(S, 'grow.tar')
    small = rawtar.member('rel/llama-server', 4096, TARGET)
    with open(p, 'wb') as fh:
        fh.write(small)
        fh.write(b'\0' * ((1280 << 20) - len(small)))
    big = os.path.getsize(p)
    fake = os.stat(p)
    class S2:
        st_mode = statmod.S_IFREG | 0o644
        st_size = 1024 * 1024
    orig = m.os
    class Shim2:
        path = orig.path
        def stat(self, q, *a, **k):
            return S2() if q == p else orig.stat(q, *a, **k)
        def __getattr__(self, name):
            return getattr(orig, name)
    m.os = Shim2()
    t0 = time.monotonic()
    r = lib.run(m, p, '0' * 64, 'rel/llama-server', tsha, 4096)   # wrong asset sha: hashes all, then refuses
    lib.emit('grow_beyond_cap', {'stat_size': S2.st_size, 'real_bytes': big,
                                 'seconds': r['seconds'], 'token': r.get('token')})
    # calibration: same bytes hashed directly
    t0 = time.monotonic(); lib.sha(p)
    lib.emit('grow_calibration_sha', {'real_bytes': big,
                                      'seconds': round(time.monotonic() - t0, 3)})
    m.os = orig
    os.unlink(p)
