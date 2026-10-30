#!/usr/bin/env python3
"""MT25: generate forged variants of the tip tool (scratch copy, never the lane).

Each variant is the tip tool with MT25 hooks inserted at unique anchors. The
hooks are inert unless $HOME/mt25-mode.json exists (consumed on first use, so
only the first tool process run under that HOME is forged). Output:
  <out>/tools/kama-completion-live.py   (+ kama-llamacpp-live.py, registry)
"""
import os
import shutil
import sys

TIP = sys.argv[1]          # tip tool text file (blob from the tip)
DEP = sys.argv[2]          # tools/kama-llamacpp-live.py
MT06 = sys.argv[3]         # MT06 forger diff (source of the injector)
OUT = sys.argv[4]          # output root

# the ptrace injector, byte-for-byte from the MT06 forger diff
inj = []
grab = False
for ln in open(MT06).read().splitlines():
    if ln.startswith('+def _mt06_inject'):
        grab = True
    if grab:
        inj.append(ln[1:] if ln.startswith('+') else ln)
        if ln.strip() == '+    return handle':
            break
INJECT = '\n'.join(inj) + '\n'
INJECT = INJECT.replace('_mt06_inject', '_mt25_inject')

HOOKS = r'''
# ---- MT25 forger hooks (clone-only falsification; inert unless $HOME/mt25-mode.json) ----
_MT25 = {}


def _mt25_cfg():
    if not _MT25:
        p = os.path.join(os.environ.get('HOME', ''), 'mt25-mode.json')
        if os.path.exists(p):
            with open(p) as f:
                _MT25.update(json.load(f))
            os.remove(p)
    return _MT25


def _mt25_ev(key, val):
    p = os.path.join(os.environ.get('HOME', ''), 'mt25-evidence.json')
    ev = json.load(open(p)) if os.path.exists(p) else {}
    ev[key] = val
    with open(p, 'w') as f:
        json.dump(ev, f, indent=1)


def _mt25_sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()


def _mt25_patch(path, off, new, restore):
    import atexit
    with open(path, 'r+b') as f:
        f.seek(off)
        old = f.read(len(new))
        f.seek(off)
        f.write(new)
        f.flush()
        os.fsync(f.fileno())
    if restore:
        def _undo(path=path, off=off, old=old):
            with open(path, 'r+b') as g:
                g.seek(off)
                g.write(old)
                g.flush()
                os.fsync(g.fileno())
        atexit.register(_undo)
    return old


def _mt25_wrap(receipt):
    c = _mt25_cfg()
    argv = receipt.get('argv') or []
    m = argv[argv.index('--model') + 1] if '--model' in argv else None
    if c.get('native_swap') and m:
        tmp = m + '.mt25swap'
        subprocess.run(['cp', '--reflink=always', m, tmp], check=True)
        os.replace(tmp, m)
        _mt25_ev('native_swap', {'model': m, 'sha': _mt25_sha(m)[:12],
                                 'ns': time.time_ns()})
    if c.get('native_hardlink') and m:
        os.link(m, m + '.mt25hl')
        _mt25_ev('native_hardlink', {'model': m, 'ns': time.time_ns()})
    if c.get('wrap_pre'):
        prefix = c.get('wrap_prefix') or ['/bin/sh', '-c']
        receipt['argv'] = (prefix + [c['wrap_pre'] + ' && exec "$@"', 'sh']
                           + receipt['argv'])
        _mt25_ev('wrap_argv', receipt['argv'][:6])


def _mt25_pre_hold(model):
    c = _mt25_cfg()
    rw = c.get('rewrite_pre')
    if rw:
        old = _mt25_patch(model, rw['off'], bytes.fromhex(rw['hex']),
                          rw['restore'])
        _mt25_ev('rewrite_pre', {
            'off': rw['off'], 'len': len(old), 'old_hex': old.hex()[:64],
            'restore': rw['restore'], 'sha_in_hold': _mt25_sha(model),
            'ns': time.time_ns()})


def _mt25_after_hold(server, proc, port):
    c = _mt25_cfg()
    ev = {'hold_json_ns': time.time_ns()}
    if c.get('dlopen_lib') is not None:
        time.sleep(float(c.get('dlopen_delay_ms', 0)) / 1000.0)
        lib = os.path.join(os.path.dirname(server), c['dlopen_lib'])
        ev['inject_lib'] = lib
        ev['inject_ns_before'] = time.time_ns()
        ev['handle'] = _mt25_inject(proc.pid, lib)
        ev['inject_ns_after'] = time.time_ns()
    _mt25_ev('after_hold', ev)


def _mt25_post_release(model):
    c = _mt25_cfg()
    rw = c.get('rewrite_post')
    if rw:
        old = _mt25_patch(model, rw['off'], bytes.fromhex(rw['hex']),
                          rw['restore'])
        _mt25_ev('rewrite_post', {'off': rw['off'], 'len': len(old),
                                  'restore': rw['restore'],
                                  'sha_in_post': _mt25_sha(model),
                                  'ns': time.time_ns()})

'''

SRC = open(TIP).read()
CUT = "SCHEMA = 'kama-completion-live/v3'"
assert SRC.count(CUT) == 1
A_HOLDJSON = "            with open(os.path.join(hold, 'hold.json'), 'w') as f:\n"
A_WAIT = "            w = _live.hold_for_witness(\n"
A_REL = "            released = bool(w.get('released'))\n"
A_HOLD = "    hold = None\n"
for a in (A_HOLDJSON, A_WAIT, A_REL, A_HOLD):
    assert SRC.count(a) == 1, a


def build(name, mode_calls=True):
    t = SRC.replace(CUT, HOOKS + '\n' + INJECT + '\n' + CUT, 1)
    t = t.replace(A_HOLDJSON, "            _mt25_pre_hold(model)\n" + A_HOLDJSON, 1)
    t = t.replace(A_WAIT, "            _mt25_after_hold(server, proc, port)\n" + A_WAIT, 1)
    t = t.replace(A_REL, A_REL + "            _mt25_post_release(model)\n", 1)
    t = t.replace(A_HOLD, "    _mt25_wrap(receipt)\n" + A_HOLD, 1)
    d = os.path.join(OUT, name, 'tools')
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(OUT, name, 'registry'), exist_ok=True)
    with open(os.path.join(d, 'kama-completion-live.py'), 'w') as f:
        f.write(t)
    shutil.copy(DEP, os.path.join(d, 'kama-llamacpp-live.py'))
    return os.path.join(d, 'kama-completion-live.py')


if __name__ == '__main__':
    p = build('hooked')
    print('built', p, 'injector lines', len(inj))
