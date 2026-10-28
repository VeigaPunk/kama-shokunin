"""Decisive observations for memid / envval / envkey: /proc/<pid>/mem bytes vs disk, environ values (not printed beyond HOME)."""
import json, os, subprocess, sys, time
variant = sys.argv[1]
S = '/fast/scratch/hyaku/kama-r64/b/MT05EnvInject'; D = S + '/clone'
PIN = '/home/vgpnk/.local/opt/llama-b11755'; MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
W = f'{S}/obs2/{variant}'; os.system(f'rm -rf {W}'); os.makedirs(W + '/hold', mode=0o700)
env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')}
p = subprocess.Popen([sys.executable, D + '/tools/kama-completion-live.py', '--nonce', 'obs', '--work', W + '/tw',
    '--server', PIN + '/llama-server', '--model', MODEL, '--model-sha256', '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d',
    '--server-sha256', 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804', '--alias', 'kama-completion-probe',
    '--hold-dir', W + '/hold', '--hold-timeout', '60', '--out', W + '/receipt.json'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
hp = W + '/hold/hold.json'; doc = None
for _ in range(300):
    if os.path.exists(hp):
        try: doc = json.load(open(hp)); break
        except ValueError: pass
    time.sleep(0.1)
if doc is None: print('no hold'); p.kill(); sys.exit(1)
pid = doc['pid']
# (1) memory vs disk for the patched offset (counter = ancestor of the server: yama scope 1 allows)
lib = PIN + '/libllama-server-impl.so'
for ln in open(f'/proc/{pid}/maps'):
    f = ln.split(None, 5)
    if len(f) == 6 and f[5].strip() == lib:
        lo, hi = (int(x, 16) for x in f[0].split('-')); off = int(f[2], 16)
        if off <= 0x3098bc < off + (hi - lo):
            addr = lo + 0x3098bc - off
            fd = os.open(f'/proc/{pid}/mem', os.O_RDONLY); mem = os.pread(fd, 9, addr); os.close(fd)
            disk = open(lib, 'rb'); disk.seek(0x3098bc); d = disk.read(9)
            print('mem bytes at chatcmpl offset:', mem, 'disk bytes:', d, 'mem==disk:', mem == d, 'perms', f[1]); break
# (2) environ values: HOME only, and LD_X presence
raw = open(f'/proc/{pid}/environ', 'rb').read().split(b'\0')
print('environ HOME value:', [e.decode() for e in raw if e.startswith(b'HOME=')], 'LD_X key present:', any(e.startswith(b'LD_X=') for e in raw))
print('TracerPid', [l for l in open(f'/proc/{pid}/status') if l.startswith('TracerPid')][0].split()[1])
open(W + '/hold/release', 'w').write('go\n')
p.wait(timeout=90); print('tool rc', p.returncode)
