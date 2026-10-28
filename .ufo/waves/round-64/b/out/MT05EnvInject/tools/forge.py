#!/usr/bin/env python3
"""Generate forged variants of tools/kama-completion-live.py in the seat clone.

Every edit is ONE insertion before `def run(args):` (a module-level helper block
that rebinds subprocess.Popen for the server launch). No line of the base tool is
changed, so the counter's own forgeA/forgeB patch controls still apply to the
forged tool text (the first attempt edited the Popen line and tripped the counter's
patch-apply control instead of the binding check).

Usage: forge.py <clone> <variant>   -> prints the commit sha of the variant
"""
import subprocess
import sys

CLONE, VARIANT = sys.argv[1], sys.argv[2]
BASE = 'f6a4ea9a8b5a876d685b08e7e582ec0723412a4a'
SCRATCH = '/fast/scratch/hyaku/kama-r64/b/MT05EnvInject'
PATH = 'tools/kama-completion-live.py'

FLAGS = {  # variant -> which forgery steps are on
    'v1_bindns':      dict(bindns=True),
    'v2_memid':       dict(memid=True),
    'v3_extrakey':    dict(extrakey=True),
    'v4_envkey':      dict(envkey=True),
    'v5_envval':      dict(envval=True),
    'v6_seize_memid': dict(seize=True, memid=True),
    'v7_bindns_memid': dict(bindns=True, memid=True),
    'v9_bindns_model': dict(bindns=True, model=True),
    'v8_model_bind': dict(model=True),
    'v10_etc_preload': dict(preload=True),
}[VARIANT]

HELPERS = r'''
# ---- seat MT05EnvInject forgery block (scratch clone only; not an upstream change) ----
_FORGE = %(flags)r
_FORGE_PRIV = '%(priv)s'
_FORGE_LIB = '/home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so'
_FORGE_MODEL_PRIV = '%(model_priv)s'
_FORGE_HOOK = '%(hook)s'
_FORGE_ETC = '%(etc)s'
_FORGE_MODEL = '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf'


def _forge_argv(argv, server):
    if _FORGE.get('preload'):
        # private mount ns: tmpfs over /etc with a copy + ld.so.preload naming a /usr/lib
        # object (here the hook, bound over /usr/lib/libpcprofile.so inside the ns)
        script = ('mkdir -p "$2" && mount --bind /etc "$2" && mount -t tmpfs tmpfs /etc && '
                  '(cp -r --no-preserve=ownership "$2"/. /etc/ 2>/dev/null; true) && '
                  'echo /usr/lib/libpcprofile.so > /etc/ld.so.preload && '
                  'mount --bind "$1" /usr/lib/libpcprofile.so && shift 2 && exec "$@"')
        return (['unshare', '--map-root-user', '--mount', '--propagation', 'private',
                 '/bin/sh', '-c', script, 'sh', _FORGE_HOOK, _FORGE_ETC] + list(argv))
    # private mount namespace: bind-mount copies over the server directory and/or the
    # model file; every path string the counter sees is unchanged
    binds = []
    if _FORGE.get('bindns'):
        binds.append((_FORGE_PRIV, os.path.dirname(server)))
    if _FORGE.get('model'):
        binds.append((_FORGE_MODEL_PRIV, _FORGE_MODEL))
    script = ' && '.join(f'mount --bind "${2*i+1}" "${2*i+2}"' for i in range(len(binds)))
    script += ' && shift ' + str(2 * len(binds)) + ' && exec "$@"'
    flat = [x for pair in binds for x in pair]
    return (['unshare', '--map-root-user', '--mount', '--propagation', 'private',
             '/bin/sh', '-c', script, 'sh'] + flat + list(argv))


def _forge_patch_mem(pid, libpath, file_off, old, new):
    # copy-on-write write into the live server's mapped library; the file is untouched
    assert len(old) == len(new)
    with open(libpath, 'rb') as fh:
        fh.seek(file_off)
        assert fh.read(len(old)) == old
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            maps = open(f'/proc/{pid}/maps').read().splitlines()
        except OSError:
            maps = []
        for ln in maps:
            parts = ln.split(None, 5)
            if len(parts) == 6 and parts[5].strip() == libpath:
                lo, hi = (int(x, 16) for x in parts[0].split('-'))
                off = int(parts[2], 16)
                if off <= file_off and file_off + len(old) <= off + (hi - lo):
                    fd = os.open(f'/proc/{pid}/mem', os.O_RDWR)
                    try:
                        os.pwrite(fd, new, lo + file_off - off)
                    finally:
                        os.close(fd)
                    return
        time.sleep(0.005)
    raise RuntimeError('forge: library never mapped')


def _forge_env(pid, old, new):
    # same-length rewrite of one entry of the live environment block
    assert len(old) == len(new)
    st = open(f'/proc/{pid}/stat').read()
    rest = st[st.rindex(')') + 2:].split()
    env_start = int(rest[47])
    raw = open(f'/proc/{pid}/environ', 'rb').read()
    idx = raw.index(b'\0' + old) + 1 if b'\0' + old in raw else raw.index(old)
    fd = os.open(f'/proc/{pid}/mem', os.O_RDWR)
    try:
        os.pwrite(fd, new, env_start + idx)
    finally:
        os.close(fd)


def _forge_seize(pid):
    # a real tracer thread: PTRACE_SEIZE (no syscall stops), services every stop with
    # waitid(WNOWAIT) + PTRACE_CONT, passing signals through; TracerPid = this process
    import ctypes
    import threading
    libc = ctypes.CDLL(None, use_errno=True)
    ready = threading.Event()

    def loop():
        if libc.ptrace(0x4206, pid, None, None) != 0:
            ready.set()
            return
        ready.set()
        while True:
            try:
                si = os.waitid(os.P_PID, pid, os.WEXITED | os.WSTOPPED | os.WNOWAIT)
            except ChildProcessError:
                return
            if si is None or si.si_code in (os.CLD_EXITED, os.CLD_KILLED, os.CLD_DUMPED):
                return
            sig = 0 if si.si_status == 5 else si.si_status
            libc.ptrace(7, pid, None, sig)

    threading.Thread(target=loop, daemon=True).start()
    ready.wait(5)


_FORGE_BASE_POPEN = subprocess.Popen


class _ForgePopen(_FORGE_BASE_POPEN):
    def __init__(self, args, *a, **kw):
        served = isinstance(args, (list, tuple)) and bool(args) and \
            os.path.basename(str(args[0])) == 'llama-server'
        if served and _FORGE.get('extrakey'):
            kw['env'] = dict(kw.get('env') or {}, KAMA_R64_PROBE='1')
        if served and (_FORGE.get('bindns') or _FORGE.get('model') or _FORGE.get('preload')):
            args = _forge_argv(args, args[0])
        super().__init__(args, *a, **kw)
        if not served:
            return
        if _FORGE.get('seize'):
            _forge_seize(self.pid)
        if _FORGE.get('memid'):
            _forge_patch_mem(self.pid, _FORGE_LIB, 0x3098bc,
                             b'chatcmpl-', b'forgedid-')
        if _FORGE.get('envkey'):
            _forge_env(self.pid, b'HOME=', b'LD_X=')
        if _FORGE.get('envval'):
            _forge_env(self.pid, b'HOME=/home/vgpnk', b'HOME=/home/vgpnj')


subprocess.Popen = _ForgePopen


''' 

ANCHOR = 'def run(args):\n'

base = subprocess.run(['git', '-C', CLONE, 'show', f'{BASE}:{PATH}'],
                      capture_output=True, check=True).stdout.decode()
assert base.count(ANCHOR) == 1
block = HELPERS % {'flags': FLAGS,
                   'priv': SCRATCH + '/priv',
                   'model_priv': SCRATCH + '/model-x/stories260K.gguf',
                   'hook': SCRATCH + '/hook/libpcprofile-hook.so',
                   'etc': SCRATCH + '/etc-orig'}
text = base.replace(ANCHOR, block + ANCHOR)
open(f'{CLONE}/{PATH}', 'w').write(text)
subprocess.run(['git', '-C', CLONE, 'add', PATH], check=True)
if subprocess.run(['git', '-C', CLONE, 'diff', '--cached', '--quiet']).returncode != 0:
    subprocess.run(['git', '-C', CLONE, '-c', 'user.name=seat', '-c', 'user.email=seat@seat.invalid',
                    'commit', '-q', '-m', f'forgery {VARIANT}'], check=True)
sha = subprocess.run(['git', '-C', CLONE, 'rev-parse', 'HEAD'], capture_output=True,
                     check=True, text=True).stdout.strip()
print(sha)
