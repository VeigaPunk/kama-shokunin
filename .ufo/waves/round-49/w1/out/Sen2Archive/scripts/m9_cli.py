"""Tool-level (real CLI) record-time cost and failure mode, at 74558c71.
Verification fails before any server start, so no binary is executed."""
import bz2, gzip, hashlib, io, json, os, subprocess, sys, tarfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawtar

S = os.path.dirname(os.path.abspath(__file__))
TOOL = os.environ['KLL_TOOL']
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
MODEL_URL = ('https://huggingface.co/ggml-org/models-moved/resolve/'
             '499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf')

stub = os.path.join(S, 'stub-server.sh')
with open(stub, 'w') as fh:
    fh.write('#!/bin/sh\necho "STUB EXECUTED" >&2\nexit 3\n')
os.chmod(stub, 0o755)
model = os.path.join(S, 'tiny.gguf')
open(model, 'wb').write(b'GGUF' + b'\0' * 1020)

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def pax_record(key, value):
    body = b'%s=%s\n' % (key.encode(), value)
    n = len(body) + 2
    while True:
        r = str(n).encode() + b' ' + body
        if len(r) == n: return r
        n = len(r)

def chain_archive(k):
    rec = pax_record('comment', b'c')
    rec_len = len(rec)
    out = []
    for _ in range(k):
        out.append(rawtar.hdr('P', rec_len, typeflag=b'x'))
        out.append(rec + b'\0' * ((-len(rec)) % 512))
    out.append(rawtar.member('rel/llama-server', 4096, b'S' * 4096))
    out.append(rawtar.end())
    return b''.join(out)

class Zeros(io.RawIOBase):
    def __init__(self, n): self.n = n
    def read(self, k=-1):
        if self.n <= 0: return b''
        k = self.n if k in (None, -1) else min(k, self.n)
        self.n -= k
        return b'\0' * k

def bz2_bomb(path, bomb):
    with open(path, 'wb') as raw, bz2.BZ2File(raw, 'wb', compresslevel=1) as comp:
        with tarfile.open(fileobj=comp, mode='w|', format=tarfile.GNU_FORMAT) as tf:
            ti = tarfile.TarInfo('rel/llama-server'); ti.size = 4096; ti.mtime = 0
            tf.addfile(ti, io.BytesIO(b'X' * 4096))    # wrong bytes: digest will differ
            ti = tarfile.TarInfo('filler'); ti.size = bomb; ti.mtime = 0
            tf.addfile(ti, Zeros(bomb))

def run_tool(archive, label, member_sha=None):
    out = os.path.join(S, label + '.receipt.json')
    if os.path.exists(out): os.unlink(out)
    argv = [sys.executable, TOOL, '--server', stub, '--model', model,
            '--model-sha256', sha(model), '--probe', os.path.join(LANE, 'tools', 'kama-probe.sh'),
            '--ready-timeout', '3', '--out', out,
            '--server-asset-url', 'https://example.invalid/rel.tar.bz2',
            '--server-asset-sha256', sha(archive),
            '--server-member', 'rel/llama-server', '--model-url', MODEL_URL,
            '--server-archive', archive]
    t0 = time.monotonic()
    p = subprocess.run(argv, capture_output=True, text=True, cwd=S, timeout=900)
    dt = round(time.monotonic() - t0, 3)
    rec = {}
    if os.path.exists(out):
        rec = json.load(open(out))
    print(json.dumps({'label': label, 'archive_bytes': os.path.getsize(archive),
                      'exit': p.returncode, 'seconds': dt,
                      'setup_error': rec.get('setup_error'),
                      'internal_fault': rec.get('internal_fault'),
                      'outcome': rec.get('outcome'),
                      'stderr_tail': p.stderr.strip().splitlines()[-1:] }),
          flush=True)
    return dt

# (1) chained pax extensions (900) - RecursionError during the walk
p = os.path.join(S, 'chain900.tar.gz')
with gzip.open(p, 'wb', compresslevel=1) as fh: fh.write(chain_archive(900))
run_tool(p, 'chain900')
os.unlink(p)

# (2) bz2 bomb, 8 GiB inflated, 52 KB archive
p = os.path.join(S, 'bz2_8g.tar.bz2')
t0 = time.monotonic(); bz2_bomb(p, 8 << 30)
print('built bz2_8g in', round(time.monotonic() - t0, 1), 's', os.path.getsize(p), 'bytes', flush=True)
run_tool(p, 'bz2_8g')
os.unlink(p)
