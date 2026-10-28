# Experiment A/B: holder visibility of the counter's own holder_pids() (copied counter, unmodified)
import os, sys, socket, subprocess, time, ctypes, signal
sys.path.insert(0, os.environ['S_WORK'])
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import c1
libc = ctypes.CDLL(None, use_errno=True)
PR_SET_DUMPABLE = 4
CHILD = r'''
import ctypes, os, socket, sys, time
fd = int(sys.argv[1]); mode = sys.argv[2]
if mode == "nondump":
    ctypes.CDLL(None).prctl(4, 0, 0, 0, 0)   # PR_SET_DUMPABLE 0
s = socket.socket(fileno=fd)
print("child-ready", flush=True)
time.sleep(30)
'''
def listen_port():
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 0)); s.listen(8); return s
def inode_of(sock):
    return os.stat(f'/proc/self/fd/{sock.fileno()}').st_ino  # socket inode via readlink below
def sock_inode(sock):
    return int(os.readlink(f'/proc/self/fd/{sock.fileno()}').split('[')[1].rstrip(']'))

def run(mode):
    s = listen_port(); port = s.getsockname()[1]
    ino = sock_inode(s)
    # hold pid = child A (dumpable): holds listener
    a = subprocess.Popen([sys.executable, '-c', CHILD, str(s.fileno()), 'dump'], pass_fds=(s.fileno(),),
                         stdout=subprocess.PIPE, text=True)
    # extra holder = child B (mode) also holds the same listener fd
    b = subprocess.Popen([sys.executable, '-c', CHILD, str(s.fileno()), mode], pass_fds=(s.fileno(),),
                         stdout=subprocess.PIPE, text=True)
    a.stdout.readline(); b.stdout.readline()
    s.close()  # the parent (this process) drops its own copy
    time.sleep(0.3)
    lst = c1.listeners(port)
    pids, unread = c1.holder_pids([i for i, _ in lst])
    rec_b = c1.holder_record(b.pid, '/home/vgpnk/.local/opt/llama-b11755')
    print(f"mode={mode} port={port} listeners={lst} hold(A)={a.pid} extra(B)={b.pid}")
    print(f"  holder_pids={sorted(pids)} unreadable_own={sorted(unread)} A_visible={a.pid in pids} B_visible={b.pid in pids}")
    print(f"  B stat uid={os.stat(f'/proc/{b.pid}').st_uid} me={os.getuid()} fd_readable={os.access(f'/proc/{b.pid}/fd', os.R_OK)} exe_readable={rec_b.get('exe')!r}")
    for p in (a, b): p.kill(); p.wait()
    return pids

print("== A: dumpable extra holder (control)"); run('dump')
print("== B: non-dumpable extra holder (PR_SET_DUMPABLE=0)"); run('nondump')
