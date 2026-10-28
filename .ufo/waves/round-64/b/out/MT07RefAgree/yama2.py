import ctypes, os, subprocess, sys, time, socket
libc = ctypes.CDLL(None, use_errno=True); libc.syscall.restype = ctypes.c_long
def free_port():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
port = free_port()
A = subprocess.Popen([sys.executable,'-c',f'import socket,time;s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(("127.0.0.1",{port}));s.listen(5);print("ok",flush=True);time.sleep(20)'], stdout=subprocess.PIPE, text=True)
A.stdout.readline()
# B: a sibling process (spawned by this script, not an ancestor of A) that tries to take A's listener
B = subprocess.run([sys.executable,'-c',f'''
import ctypes, os
libc = ctypes.CDLL(None, use_errno=True); libc.syscall.restype = ctypes.c_long
pfd = libc.syscall(ctypes.c_long(434), ctypes.c_int({A.pid}), ctypes.c_uint(0))
print("pidfd_open", pfd, os.strerror(ctypes.get_errno()) if pfd<0 else "")
fd=None
for f in os.listdir("/proc/{A.pid}/fd"):
    if os.readlink("/proc/{A.pid}/fd/"+f).startswith("socket:"): fd=int(f)
r = libc.syscall(ctypes.c_long(438), ctypes.c_int(pfd), ctypes.c_int(fd), ctypes.c_uint(0))
print("sibling pidfd_getfd ->", r, os.strerror(ctypes.get_errno()) if r<0 else "ok")
'''], capture_output=True, text=True)
print(B.stdout, B.stderr[-300:])
r = libc.syscall(ctypes.c_long(434), ctypes.c_int(A.pid), ctypes.c_uint(0))
fd=None
for f in os.listdir(f'/proc/{A.pid}/fd'):
    if os.readlink(f'/proc/{A.pid}/fd/{f}').startswith('socket:'): fd=int(f)
pfd = libc.syscall(ctypes.c_long(434), ctypes.c_int(A.pid), ctypes.c_uint(0))
g = libc.syscall(ctypes.c_long(438), ctypes.c_int(pfd), ctypes.c_int(fd), ctypes.c_uint(0))
print("ancestor (this script is A's parent) pidfd_getfd ->", g, os.strerror(ctypes.get_errno()) if g<0 else "ok")
A.kill()
