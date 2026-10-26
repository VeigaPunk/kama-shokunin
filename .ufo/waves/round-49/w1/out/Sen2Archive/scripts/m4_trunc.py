"""Truncated / lying members: header size == --server size, payload short."""
import hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, rawtar

S = os.path.dirname(os.path.abspath(__file__))
m = lib.load()
SERVER = b'B' * 4096
ssha = hashlib.sha256(SERVER).hexdigest()

cases = {
    # declared 4096 (= server size), only 100 payload bytes, archive cut there
    'trunc_payload_100': rawtar.member('rel/llama-server', 4096, b'B' * 100),
    # declared 4096, full payload but wrong bytes (control for the digest token)
    'wrong_payload_full': rawtar.member('rel/llama-server', 4096, b'X' * 4096) + rawtar.end(),
    # declared 4096, no payload at all, end-of-archive right after the header
    'no_payload': rawtar.hdr('rel/llama-server', 4096) + rawtar.end(),
    # declared 4096, payload present but archive ends mid-payload (no trailer)
    'cut_mid_payload': rawtar.hdr('rel/llama-server', 4096) + b'B' * 1000,
    # declared == server size, payload 4096 exact, but a second lying member after
    'good_then_lying': (rawtar.member('rel/llama-server', 4096, b'B' * 4096)
                        + rawtar.hdr('big', 1 << 40) + rawtar.end()),
}
for label, blob in cases.items():
    p = os.path.join(S, label + '.tar')
    open(p, 'wb').write(blob)
    r = lib.run(m, p, lib.sha(p), 'rel/llama-server', ssha, len(SERVER))
    r['archive_bytes'] = len(blob)
    lib.emit(label, r)
    os.unlink(p)
