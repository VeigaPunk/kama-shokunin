import os, ctypes, time, sys, socket, subprocess
libc = ctypes.CDLL(None, use_errno=True)
def probe(pid):
    out = {}
    try:
        out['listdir_fd'] = 'ok:%d' % len(os.listdir(f'/proc/{pid}/fd'))
    except OSError as e:
        out['listdir_fd'] = f'{type(e).__name__}:{e.errno}'
    try:
        out['stat_uid'] = os.stat(f'/proc/{pid}').st_uid
    except OSError as e:
        out['stat_uid'] = f'err{e.errno}'
    try:
        st = open(f'/proc/{pid}/status').read()
        out['status_uid'] = [l for l in st.splitlines() if l.startswith('Uid:')][0]
    except OSError as e:
        out['status_uid'] = f'err{e.errno}'
    try:
        out['exe'] = os.readlink(f'/proc/{pid}/exe')
    except OSError as e:
        out['exe'] = f'err{e.errno}'
    return out
mode = sys.argv[1]
if mode == 'self_dumpable_0':
    libc.prctl(4, 0, 0, 0, 0)
    print('self', probe(os.getpid()))
    sys.exit(0)
# child non-dumpable
child = subprocess.Popen([sys.executable, '-c', 'import ctypes,time;ctypes.CDLL(None).prctl(4,0,0,0,0);time.sleep(30)'])
time.sleep(1.0)
print('child non-dumpable', probe(child.pid))
child2 = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'])
time.sleep(0.5)
print('child dumpable   ', probe(child2.pid))
child.kill(); child2.kill()
