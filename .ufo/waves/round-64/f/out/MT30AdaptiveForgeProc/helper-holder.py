#!/usr/bin/env python3
"""Pre-existing, non-dumpable holder for the F3 forgery.

Started BEFORE the counter run.  It makes itself non-dumpable
(PR_SET_DUMPABLE=0), so /proc/<pid>/fd is root-owned and unreadable by the
counter's own-uid scan.  It then receives one duplicate of the run-port
LISTEN socket over SCM_RIGHTS, holds it (never accepts on it, so the
answering behaviour is untouched) and closes it once the server that
created the socket is gone, so the port still closes for the teardown
observation.

argv: <unix-socket-path>
"""
import array
import ctypes
import os
import socket
import sys
import time

libc = ctypes.CDLL('libc.so.6', use_errno=True)
PR_SET_DUMPABLE = 4
libc.prctl(PR_SET_DUMPABLE, 0, 0, 0, 0)

path = sys.argv[1]
if os.path.exists(path):
    os.unlink(path)
srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
srv.bind(path)
srv.listen(8)
print(f'{time.time():.3f} helper-ready', flush=True)

conn, _ = srv.accept()
msg, anc, _flags, _addr = conn.recvmsg(4, socket.CMSG_SPACE(4))
fds = array.array('i')
fds.frombytes(anc[0][2][:len(anc[0][2]) - (len(anc[0][2]) % 4)])
data = b''
while len(data) < 24:
    chunk = conn.recv(64)
    if not chunk:
        break
    data += chunk
conn.close()
srv_pid = int(data.decode().strip() or '0')
# proof that the received descriptor really is the run-port LISTEN socket:
# its /proc link carries the socket inode, and /proc/net/tcp lists that
# inode as a LISTEN socket on the run port.
link = os.readlink(f'/proc/self/fd/{fds[0]}')
inode = link.split('[')[1].split(']')[0]
ports = []
for p in ('/proc/net/tcp', '/proc/net/tcp6'):
    try:
        for line in open(p).read().splitlines()[1:]:
            f = line.split()
            if f[9] == inode:
                ports.append((f[1].split(':')[1], f[3]))
    except OSError:
        pass
print(f'{time.time():.3f} helper-got fd={fds[0]} link={link} '
      f'server_pid={srv_pid} listening_inodes={ports}', flush=True)

while os.path.exists(f'/proc/{srv_pid}'):
    time.sleep(0.05)
os.close(fds[0])
print(f'{time.time():.3f} helper-closed', flush=True)
