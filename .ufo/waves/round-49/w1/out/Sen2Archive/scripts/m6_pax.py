"""PAX extended headers: declared extension bodies are read whole into memory,
chain without being counted, and base-256 sizes exceed the octal maximum."""
import gzip, hashlib, io, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, rawtar

S = os.path.dirname(os.path.abspath(__file__))
m = lib.load()
TARGET = b'S' * 4096
tsha = hashlib.sha256(TARGET).hexdigest()

def pax_record(key, value):
    body = b'%s=%s\n' % (key.encode(), value)
    n = len(body) + 2
    while True:
        rec = str(n).encode() + b' ' + body
        if len(rec) == n: return rec
        n = len(rec)

def hdr_size(name, size_field, typeflag):
    h = bytearray(rawtar.BLOCK)
    h[0:len(name)] = name.encode()
    h[100:108] = rawtar._octal(0o644, 8)
    h[108:116] = rawtar._octal(0, 8)
    h[116:124] = rawtar._octal(0, 8)
    h[124:136] = size_field
    h[136:148] = rawtar._octal(0, 12)
    h[156:157] = typeflag
    h[257:265] = b'ustar  \0'
    h[148:156] = b' ' * 8
    h[148:156] = rawtar._octal(sum(h), 8)[:7] + b'\0'
    return bytes(h)

def b256(n, width=12):
    return bytes([0x80]) + n.to_bytes(width - 1, 'big')

def gz(path, blob_iter):
    t0 = time.monotonic()
    with open(path, 'wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', compresslevel=1) as c:
            for b in blob_iter: c.write(b)
    return round(time.monotonic() - t0, 3)

# (a) one extension whose *valid* single record is N bytes: the whole body is
#     materialised, then decoded to str.
for mib in (256, 1024):
    n = mib << 20
    rec = pax_record('comment', b'y' * (n - 40))
    assert len(rec) <= n
    rec = rec + b'\0' * (n - len(rec))   # pad to exactly n (parse stops at first NUL)
    p = os.path.join(S, 'paxvalid_%dm.tar.gz' % mib)
    bt = gz(p, iter([hdr_size('PaxHeaders/x', rawtar._octal(len(rec), 12), b'x'),
                     rawtar.payload(rec),
                     rawtar.member('rel/llama-server', 4096, TARGET),
                     rawtar.end()]))
    r = lib.run(m, p, lib.sha(p), 'rel/llama-server', tsha, len(TARGET))
    r['record_bytes'] = len(rec); r['build_seconds'] = bt
    lib.emit('pax_valid_%dm' % mib, r)
    os.unlink(p)

# (b) chain of valid extensions: counted by MEMBER_MAX_COUNT?
def chain(k):
    out = []
    rec = pax_record('comment', b'c')
    for _ in range(k):
        out.append(hdr_size('P', rawtar._octal(len(rec), 12), b'x'))
        out.append(rec + b'\0' * ((-len(rec)) % 512))
    out.append(rawtar.member('rel/llama-server', 4096, TARGET))
    out.append(rawtar.end())
    return b''.join(out)

for k in (200, 900, 1500, 3000):
    blob = chain(k)
    p = os.path.join(S, 'chain_%d.tar.gz' % k)
    with gzip.open(p, 'wb', compresslevel=1) as fh: fh.write(blob)
    r = lib.run(m, p, lib.sha(p), 'rel/llama-server', tsha, len(TARGET))
    r['pax_headers'] = k; r['raw_bytes'] = len(blob)
    lib.emit('pax_chain_%d' % k, r)
    os.unlink(p)

# (c) base-256 declared extension size (1 PiB) with no body at all
p = os.path.join(S, 'pax_b256.tar.gz')
gz(p, iter([hdr_size('P', b256(1 << 50), b'x'),
            rawtar.member('rel/llama-server', 4096, TARGET), rawtar.end()]))
lib.emit('pax_b256_1PiB', lib.run(m, p, lib.sha(p), 'rel/llama-server', tsha, len(TARGET)))
os.unlink(p)
