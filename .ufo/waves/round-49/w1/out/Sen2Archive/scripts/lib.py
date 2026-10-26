import hashlib, importlib.util, os, sys, time, json, resource

import os as _os
TOOL = _os.environ.get('KLL_TOOL') or '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py'

def load():
    spec = importlib.util.spec_from_file_location('kll', TOOL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def sha(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(chunk), b''):
            h.update(b)
    return h.hexdigest()

def rss_mb():
    # ru_maxrss is unreliable in this environment (6.2 GiB at baseline); read VmHWM.
    with open('/proc/self/status') as fh:
        for line in fh:
            if line.startswith('VmHWM:'):
                return round(int(line.split()[1]) / 1024.0, 1)
    return -1.0

def run(m, archive, asset_sha, member, member_sha, server_size):
    t0 = time.monotonic()
    try:
        got = m.verify_archive_member(archive, asset_sha, member, member_sha, server_size)
        out = {'result': 'ok', 'got': list(got)}
    except m.SetupError as exc:
        out = {'result': 'SetupError', 'token': exc.code}
    except BaseException as exc:
        out = {'result': type(exc).__name__, 'text': str(exc)[:200]}
    out['seconds'] = round(time.monotonic() - t0, 3)
    out['rss_mb'] = round(rss_mb(), 1)
    out['archive_bytes'] = os.path.getsize(archive)
    return out

def emit(label, d):
    print(label, json.dumps(d, sort_keys=True), flush=True)
