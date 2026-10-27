#!/usr/bin/env python3
"""Reject probe: a /proc/<pid>/maps dev:inode match is not proof of the model bytes.

A child maps a file read-only; the parent rewrites the same inode in place with
different bytes of the same length.  The maps line (dev, inode, pathname) and a
stat() of the pathname stay identical, while the sha256 of the path changes.  A
check that stops at dev/inode accepts the substitution; only hashing the path
(the counter's `mapped` leg) sees it, and even the hash cannot see a rewrite with
identical bytes (a stated limit of the claim).
"""
import hashlib
import os
import subprocess
import sys
import tempfile
import time

d = tempfile.mkdtemp(prefix="maps-", dir=os.environ.get("TMPDIR") or None)
path = os.path.join(d, "model.gguf")
with open(path, "wb") as fh:
    fh.write(b"MODEL-A" * 64)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def maps_line(pid, p):
    for ln in open(f"/proc/{pid}/maps"):
        if p in ln:
            return ln.rstrip("\n")
    return None


before = sha(path)
child = subprocess.Popen([sys.executable, "-c",
                          "import mmap,os,sys,time\n"
                          "f=open(sys.argv[1],'rb'); m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)\n"
                          "print(m[0:7].decode(), flush=True); time.sleep(30)\n",
                          path], stdout=subprocess.PIPE, text=True)
first = child.stdout.readline().strip()
time.sleep(0.3)
line_before = maps_line(child.pid, path)
with open(path, "r+b") as fh:
    fh.write(b"MODEL-B" * 64)
line_after = maps_line(child.pid, path)
st = os.stat(path)
parts = line_before.split()
st_matches = bool(len(parts) >= 5 and parts[3] == "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
                  and parts[4] == str(st.st_ino))
print("child first 7 bytes at map time:", first)
print("maps line at map time :", line_before)
print("maps line after rewrite:", line_after)
print("stat(path) dev:inode after rewrite:", "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)), st.st_ino)
print("maps dev/inode == stat dev/inode after rewrite:", st_matches)
print("sha256 before:", before)
print("sha256 after :", sha(path))
print("hash changed, dev/inode identical:", before != sha(path) and st_matches)
child.kill()
child.wait()
