#!/usr/bin/env python3
"""Non-dumpable helper that holds a listener dup; reports what procfs exposes."""
import ctypes, os, socket, sys, time
ctypes.CDLL(None).prctl(4, 0, 0, 0, 0)  # PR_SET_DUMPABLE = 0
ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ls.bind(('127.0.0.1', 0)); ls.listen(4)
port = ls.getsockname()[1]
open(sys.argv[1], 'w').write(f'{os.getpid()} {port}\n')
time.sleep(600)
