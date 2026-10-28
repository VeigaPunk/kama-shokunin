# (ii) transient holder: the counter's two snapshots bracket a window in which the (descendant) tool
# takes the hold pid's listener via pidfd_getfd, stops the hold pid, answers, and drops the fd.
import os, sys, socket, subprocess, time, ctypes, signal
sys.path.insert(0, os.environ['S_WORK']); os.environ['PYTHONDONTWRITEBYTECODE']='1'
import c1
libc = ctypes.CDLL(None, use_errno=True)
SYS_pidfd_open, SYS_pidfd_getfd = 434, 438
CH = r'''
import socket, sys, time
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", int(sys.argv[1]))); s.listen(8)
print("ready", s.fileno(), flush=True); time.sleep(60)
'''
port = 0
# pick a free port first
t = socket.socket(); t.bind(('127.0.0.1',0)); port = t.getsockname()[1]; t.close()
child = subprocess.Popen([sys.executable,'-c',CH,str(port)], stdout=subprocess.PIPE, text=True)
child_fd = int(child.stdout.readline().split()[1])
time.sleep(0.2)
hold_doc = {'pid': child.pid, 'port': port, 'schema': 'kama-completion-hold/v1'}
def snap(tag):
    raw = c1.collect(port, hold_doc, time.time_ns(), 0, os.getpid(), c1.start_ticks_of(os.getpid()), sys.executable, '/x/m')
    print(f"  {tag}: holders={[h['pid'] for h in raw['holders']]} unreadable_own={raw['unreadable_own']}")
    return raw
raw_a = snap('raw_a (before window)')
# window: tool (this process, ancestor of child) takes the listener
ino = [i for i, _ in c1.listeners(port)][0]
pfd = libc.syscall(SYS_pidfd_open, child.pid, 0)
mine = None
for fd in os.listdir(f'/proc/{child.pid}/fd'):
    try:
        if os.readlink(f'/proc/{child.pid}/fd/{fd}') == f'socket:[{ino}]': cfd = int(fd)
    except OSError: pass
mine = libc.syscall(SYS_pidfd_getfd, pfd, cfd, 0)
print(f"  pidfd_getfd ok: local fd={mine} errno={ctypes.get_errno() if mine<0 else 0}")
os.kill(child.pid, signal.SIGSTOP); time.sleep(0.2)   # hold pid no longer accepts
mid = snap('raw_mid (inside window)')
ls = socket.socket(fileno=mine)
c = socket.create_connection(('127.0.0.1', port), timeout=5); c.sendall(b'ping\n')
ls.settimeout(5); conn, _ = ls.accept(); conn.settimeout(5); print("  tool got:", conn.recv(16).decode().strip()); conn.sendall(b'answered-by-tool\n'); conn.close()
print("  client got:", c.recv(64).decode().strip(), " (answered by this process, the tool)")
c.close()
ls.detach()  # drop the tool's copy of the listener
os.close(mine); os.kill(child.pid, signal.SIGCONT); time.sleep(0.2)
raw_b = snap('raw_b (after window)')
print("  bind_holders on raw_a:", c1.grade_binding(raw_a)['bind_holders'], " raw_b:", c1.grade_binding(raw_b)['bind_holders'], " raw_a==raw_b holder sig:", c1.holders_signature(raw_a)==c1.holders_signature(raw_b))
child.kill(); child.wait()
