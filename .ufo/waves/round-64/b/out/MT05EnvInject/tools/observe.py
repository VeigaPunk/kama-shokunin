"""Hold a forged tool's server open and print the procfs observables the counter does/doesn't read."""
import json, os, subprocess, sys, time, urllib.request, hashlib
variant = sys.argv[1]
S = '/fast/scratch/hyaku/kama-r64/b/MT05EnvInject'; D = S + '/clone'
PIN = '/home/vgpnk/.local/opt/llama-b11755'; MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
W = f'{S}/obs/{variant}'; os.system(f'rm -rf {W}'); os.makedirs(W + '/hold', mode=0o700)
env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')}
p = subprocess.Popen([sys.executable, D + '/tools/kama-completion-live.py', '--nonce', 'obs', '--work', W + '/tw',
    '--server', PIN + '/llama-server', '--model', MODEL, '--model-sha256', '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d',
    '--server-sha256', 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804', '--alias', 'kama-completion-probe',
    '--hold-dir', W + '/hold', '--hold-timeout', '60', '--out', W + '/receipt.json'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
hp = W + '/hold/hold.json'
print('variant', variant)
for _ in range(600):
    if os.path.exists(hp):
        try: doc = json.load(open(hp)); break
        except ValueError: pass
    time.sleep(0.1)
pid, port = doc['pid'], doc['port']
st = dict(l.split(':\t', 1) for l in open(f'/proc/{pid}/status').read().splitlines() if ':\t' in l)
print('holder pid', pid, 'tool pid', p.pid, 'ppid', st['PPid'].strip(), 'TracerPid', st['TracerPid'].strip())
print('holder mnt ns', os.readlink(f'/proc/{pid}/ns/mnt'), 'counter mnt ns', os.readlink('/proc/self/ns/mnt'))
for ln in open(f'/proc/{pid}/maps'):
    if 'llama-server-impl' in ln:
        f = ln.split(); print('maps line inode', f[4], 'path', f[5]); break
for ln in open(f'/proc/{pid}/maps'):
    if 'libpcprofile' in ln:
        f = ln.split(); print('preload maps line inode', f[4], 'path', f[5]); break
print('counter stat inode libpcprofile', os.stat('/usr/lib/libpcprofile.so').st_ino)
print('counter stat inode', os.stat(PIN + '/libllama-server-impl.so').st_ino)
req = urllib.request.Request(f'http://127.0.0.1:{port}/v1/completions', data=json.dumps({'prompt': 'The cat sat on the', 'n_predict': 3, 'temperature': 0.0, 'seed': 1}).encode(), headers={'Content-Type': 'application/json'})
ek = [e.split(b'=',1)[0].decode() for e in open(f'/proc/{pid}/environ','rb').read().split(b'\0') if e]
print('environ key count', len(ek), 'extra keys (not in base allowlist):', sorted(k for k in ek if k not in ('PATH','HOME','LANG','LC_ALL','TMPDIR','LD_LIBRARY_PATH','LLAMA_ARG_THREADS','XDG_CACHE_HOME')))
print('served id', json.loads(urllib.request.urlopen(req, timeout=20).read())['id'][:16])
open(W + '/hold/release', 'w').write('go\n')
p.wait(timeout=90); print('tool rc', p.returncode)
