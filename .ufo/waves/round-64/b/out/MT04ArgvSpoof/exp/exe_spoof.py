import ctypes, os, sys
libc = ctypes.CDLL(None, use_errno=True)
PR_SET_MM, PR_SET_MM_EXE_FILE = 35, 13
fd = os.open('/home/vgpnk/.local/opt/llama-b11755/llama-server', os.O_RDONLY)
r = libc.prctl(PR_SET_MM, PR_SET_MM_EXE_FILE, fd, 0, 0)
e = ctypes.get_errno()
print('prctl=', r, 'errno=', e, os.strerror(e) if e else '', 'exe=', os.readlink('/proc/self/exe'), 'uid=', os.getuid(), flush=True)
