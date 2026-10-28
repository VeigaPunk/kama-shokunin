import os, socket, subprocess, sys, time, urllib.request, errno
SRV = os.path.expanduser('~/.local/opt/llama-b11755/llama-server')
MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
WORK = sys.argv[1]; CASE = sys.argv[2]
def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
P = free_port()
env = {k: v for k, v in os.environ.items() if k in ('PATH','HOME','LANG','LC_ALL','TMPDIR')}
def start_child(tag):
    log = open(os.path.join(WORK, f'exp-{tag}.log'), 'wb')
    return subprocess.Popen([SRV, '--model', MODEL, '--alias', 'kama-completion-probe', '--port', str(P),
        '--host', '127.0.0.1', '-c', '512', '-t', '1'], stdout=log, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, env=env)
def healthy(timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if urllib.request.urlopen(f'http://127.0.0.1:{P}/health', timeout=2).status == 200: return True
        except Exception: pass
        time.sleep(0.2)
    return False
def mk(fam, addr, reuseport, reuseaddr=True):
    s = socket.socket(fam, socket.SOCK_STREAM)
    if reuseaddr: s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if reuseport: s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    return s
if CASE == 'child-then-reuseport-127.0.0.1':
    c = start_child('c'); print('child healthy', healthy(), 'port', P)
    s = mk(socket.AF_INET, None, True)
    try: s.bind(('127.0.0.1', P)); s.listen(4); print('BIND OK (unexpected)')
    except OSError as e: print('127.0.0.1 SO_REUSEPORT beside pinned child:', errno.errorcode[e.errno], e.strerror)
    c.terminate(); c.wait(timeout=20)
elif CASE == 'reuseport-first-then-child':
    s = mk(socket.AF_INET, None, True); s.bind(('127.0.0.1', P)); s.listen(4)
    c = start_child('c2'); time.sleep(10)
    print('forger REUSEPORT bound first; child rc =', c.poll(), '(None = still running, 1/2 = bind failed)')
    if c.poll() is None: c.kill(); c.wait()
    s.close()
elif CASE in ('child-then-127.0.0.2', 'child-then-::1', 'child-then-::1-reuseport'):
    c = start_child('c3'); print('child healthy', healthy(), 'port', P)
    if CASE == 'child-then-127.0.0.2':
        s = mk(socket.AF_INET, None, False); addr = ('127.0.0.2', P); fam = 'v4 127.0.0.2'
    else:
        s = mk(socket.AF_INET6, None, CASE.endswith('reuseport')); addr = ('::1', P, 0, 0); fam = 'v6 ::1'
    try:
        s.bind(addr); s.listen(4); print(fam, 'BIND OK; listening=True')
        # does the counter-style probe to 127.0.0.1 still reach the child?
        print('127.0.0.1 health still:', urllib.request.urlopen(f'http://127.0.0.1:{P}/health', timeout=3).read()[:40])
        keep = True
    except OSError as e: print(fam, errno.errorcode[e.errno], e.strerror)
    c.terminate(); c.wait(timeout=20)
