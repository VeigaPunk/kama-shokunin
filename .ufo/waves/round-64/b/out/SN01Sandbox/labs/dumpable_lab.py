import ctypes, os, subprocess, sys
libc = ctypes.CDLL(None, use_errno=True)
PR_SET_DUMPABLE = 4
probe = r'''
import os, sys
ppid = os.getppid()
for p, m in (("/proc/%d/fd/1" % ppid, "ab"), ("/proc/%d/mem" % ppid, "rb")):
    try:
        open(p, m).close(); print(p, "open:ok")
    except OSError as e:
        print(p, "open:" + type(e).__name__)
'''
for label, make_nd in (("dumpable=1 (default)", False), ("dumpable=0 (PR_SET_DUMPABLE)", True)):
    if make_nd:
        assert libc.prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) == 0
    out = subprocess.run([sys.executable, '-c', probe], capture_output=True, text=True).stdout
    print(label, '|', out.strip().replace('\n', '; '))
