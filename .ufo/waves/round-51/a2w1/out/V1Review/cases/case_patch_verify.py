#!/usr/bin/env python3
"""Verifies the proposed own_exe fix on the patched copy:
  A: symlink member -> 'not a regular file' problem (bypass closed)
  B: honest regular member inside work -> only the sha leg complains (expected,
     running image is sleep not the frozen server)
  C: member string is absolute -> lstat sees the host file, regular, but the
     realpath escapes <work> -> 'resolves outside' problem
  D: EMFILE -> OSError folded into probs, returns None, no crash"""
import importlib.util, os, resource, shutil, subprocess, sys, time

P = os.path.join(sys.argv[1], "round51-replay-exe-audit-patched.py")
S = sys.argv[1]
HOST = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
spec = importlib.util.spec_from_file_location("c1p", P)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

work = os.path.join(S, "work-patched")
mdir = os.path.join(work, "server", "llama-b11909")
os.makedirs(mdir, exist_ok=True)
member_path = os.path.join(work, "server", "llama-b11909", "llama-server")
print("== A: symlink member (the bypass) ==")
if os.path.lexists(member_path):
    os.unlink(member_path)
os.symlink(HOST, member_path)
probs = []
got = c1.own_exe(os.getpid(), member_path, work, probs)
print("own_exe:", got, "probs:", probs)
os.unlink(member_path)

print("\n== B: honest regular member inside work ==")
real = os.path.join(work, "server", "llama-b11909", "llama-server")
shutil.copy("/usr/bin/sleep", real); os.chmod(real, 0o755)
p = subprocess.Popen([real, "30"], start_new_session=True)
time.sleep(0.2)
probs = []
got = c1.own_exe(p.pid, member_path, work, probs)
print("own_exe:", got, "probs:", probs)
p.terminate(); p.wait()

print("\n== C: absolute member (traversal) ==")
probs = []
got = c1.own_exe(os.getpid(), HOST, work, probs)
print("own_exe:", got, "probs:", probs)

print("\n== D: EMFILE fail-soft ==")
fds = []
try:
    while True:
        fds.append(os.open("/dev/null", os.O_RDONLY))
except OSError:
    pass
os.close(fds.pop())
probs = []
try:
    got = c1.own_exe(os.getpid(), member_path, work, probs)
    print("own_exe returned:", got, "probs:", probs)
except OSError as e:
    print("STILL CRASHES:", e)
finally:
    for fd in fds:
        os.close(fd)
