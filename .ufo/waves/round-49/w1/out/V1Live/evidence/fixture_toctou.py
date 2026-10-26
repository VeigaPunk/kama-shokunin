#!/usr/bin/env python3
"""V1Live fixture: verify_archive_member() stat-then-open window.

The function checks S_ISREG and the 1 GiB size cap on os.stat(path) and only
then calls open(path, 'rb').  These two calls are not atomic.  A path that
is a regular file at stat time but a FIFO at open time blocks open() forever
(with no writer); a path swapped to a regular file larger than the cap after
stat bypasses the cap and the hashing loop reads the whole (larger) file.

The 2 GiB file is created with os.truncate on /dev/shm (tmpfs, sparse,
instant) to keep the fixture itself cheap.
"""
import os, sys, tempfile, subprocess, time

d = tempfile.mkdtemp(prefix='v1live-toctou-')
path = os.path.join(d, 'a.tar')
open(path, 'wb').write(b'hello-regular')

# Step 1: stat passes (regular), then the path becomes a FIFO before open.
st = os.stat(path)
print('stat S_ISREG:', (st.st_mode & 0o170000) == 0o100000,
      'size', st.st_size)
os.unlink(path); os.mkfifo(path)
code = "import os,sys; fd=os.open(sys.argv[1], os.O_RDONLY); os.close(fd)"
t0 = time.monotonic()
p = subprocess.Popen([sys.executable, '-c', code, path])
try:
    p.wait(timeout=2)
    print('open returned (unexpected) in %.3fs' % (time.monotonic() - t0))
except subprocess.TimeoutExpired:
    p.kill(); p.wait()
    print('open(path) BLOCKED >2s after stat passed on the same path '
          '(TOCTOU window)')

# Step 2: size cap bypassed: stat sees a small regular file, then the path is
# swapped to a 2 GiB sparse regular file before open.
big = '/dev/shm/v1live-big.tar'
open(big, 'wb').write(b'small')
st = os.stat(big)
print('pre-check size', st.st_size, '<= 1GiB -> would pass the cap')
os.truncate(big, 1 << 31)
fd = os.open(big, os.O_RDONLY)
fs = os.fstat(fd)
print('post-open fstat size', fs.st_size, '-> the cap check (on the pre-open '
      'stat) already passed; the hashing loop would read', fs.st_size, 'bytes')
os.close(fd)
os.unlink(big)
