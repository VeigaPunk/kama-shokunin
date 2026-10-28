import os, sys, socket, ctypes, time, subprocess, json
libc = ctypes.CDLL(None, use_errno=True)
libc.syscall.restype = ctypes.c_long
port = int(sys.argv[1])
child = subprocess.Popen([sys.executable, 'nd_test.py', 'child', str(port)], stdout=subprocess.PIPE, text=True)
time.sleep(1.0)
pfd = libc.syscall(ctypes.c_long(434), ctypes.c_int(child.pid), ctypes.c_uint(0))
# find child's listening socket fd on the port
inodes=set()
for line in open('/proc/net/tcp').read().splitlines()[1:]:
    f=line.split()
    if int(f[1].split(':')[1],16)==port and f[3]=='0A': inodes.add(f[9])
fdnum=None
for fd in os.listdir(f'/proc/{child.pid}/fd'):
    if os.readlink(f'/proc/{child.pid}/fd/{fd}') in {f'socket:[{i}]' for i in inodes}: fdnum=int(fd)
print('child pidfd', pfd, 'listen fd in child', fdnum, flush=True)
newfd = libc.syscall(ctypes.c_long(438), ctypes.c_int(pfd), ctypes.c_int(fdnum), ctypes.c_uint(0))
print('pidfd_getfd ->', newfd, 'errno', ctypes.get_errno(), flush=True)
libc.prctl(4, 0, 0, 0, 0)  # PR_SET_DUMPABLE 0
print('dumpable set', flush=True)
s = socket.socket(fileno=newfd)
print('forger holds listener; child still running', child.poll() is None, flush=True)
subprocess.run([sys.executable, 'nd_test.py', 'observer', str(port)])
s.close(); child.kill()
