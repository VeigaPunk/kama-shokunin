import os, sys, socket, ctypes, time, subprocess, json
libc = ctypes.CDLL(None, use_errno=True)
PR_SET_DUMPABLE = 4
SYS_pidfd_open, SYS_pidfd_getfd = 434, 438
libc.syscall.restype = ctypes.c_long
def pidfd_open(pid): return libc.syscall(ctypes.c_long(SYS_pidfd_open), ctypes.c_int(pid), ctypes.c_uint(0))
def pidfd_getfd(pfd, tfd): return libc.syscall(ctypes.c_long(SYS_pidfd_getfd), ctypes.c_int(pfd), ctypes.c_int(tfd), ctypes.c_uint(0))
mode = sys.argv[1]
if mode == 'child':
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', int(sys.argv[2]))); s.listen(5)
    print(json.dumps({'child_listen_fd': s.fileno()}), flush=True)
    time.sleep(30)
elif mode == 'observer':
    # emulate counter holder_pids on the port's inodes
    port = int(sys.argv[2])
    inodes=set()
    for path in ('/proc/net/tcp',):
        for line in open(path).read().splitlines()[1:]:
            f=line.split()
            if int(f[1].split(':')[1],16)==port and f[3]=='0A': inodes.add(f[9])
    wanted={f'socket:[{i}]' for i in inodes}
    pids=set(); unreadable=set(); skipped=[]
    me=os.getuid()
    for name in os.listdir('/proc'):
        if not name.isdigit(): continue
        pid=int(name)
        try: fds=os.listdir(f'/proc/{pid}/fd')
        except PermissionError:
            try:
                st=os.stat(f'/proc/{pid}').st_uid
                if st==me: unreadable.add(pid)
                else: skipped.append((pid, st))
            except OSError: pass
            continue
        except OSError: continue
        for fd in fds:
            try:
                if os.readlink(f'/proc/{pid}/fd/{fd}') in wanted: pids.add(pid); break
            except OSError: continue
    print(json.dumps({'inodes': sorted(inodes), 'holder_pids': sorted(pids), 'unreadable_own': sorted(unreadable), 'skipped_root_owned_sample': [x for x in skipped if x[0] in ()] , 'n_skipped_nonown': len(skipped)}))
