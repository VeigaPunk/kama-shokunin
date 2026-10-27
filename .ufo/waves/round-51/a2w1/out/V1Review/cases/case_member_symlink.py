#!/usr/bin/env python3
"""Minimal case: the round-51 C1 own check passes a SYMLINK member.

A live llama-server exec'd from the REAL host install (the exact round-50
J4Decoy binary). <work>/server/<member> is a symlink to it - nothing was ever
extracted. own_exe() appends NO problem and returns the host file's (dev, ino),
because os.stat() and /proc/<pid>/exe both resolve the link. The two
after-release legs (rerun server_exe dev:ino, own_server realpath) are equally
resolved-file-based, so the whole `own` leg passes the J4Decoy class v2 was
built to close."""
import importlib.util, os, socket, subprocess, sys, time

C1 = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py"
HOST = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
S = sys.argv[1]

spec = importlib.util.spec_from_file_location("c1", C1)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

work = os.path.join(S, "work-b1")
mdir = os.path.join(work, "server", "llama-b11909")
os.makedirs(mdir, exist_ok=True)
member_path = os.path.join(mdir, "llama-server")   # == <work>/server/<receipt member>

s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
log = open(os.path.join(S, "llama.log"), "wb")
p = subprocess.Popen([HOST, "--port", str(port), "--model", os.path.join(S, "model.gguf")],
                     stdout=log, stderr=log, start_new_session=True)
try:
    time.sleep(2.5)
    print("server alive:", p.poll() is None, "pid", p.pid)
    os.symlink(HOST, member_path)
    print("member_path:", member_path, "->", os.readlink(member_path))
    probs = []
    got = c1.own_exe(p.pid, member_path, probs)
    print("own_exe returned:", got)
    st = os.stat(HOST)
    print("host install dev:ino: %02x:%02x:%d" % (os.major(st.st_dev), os.minor(st.st_dev), st.st_ino))
    print("probs:", probs)
    print("VERDICT:", "BYPASS - own records no problem; dev:ino and sha legs all satisfied"
          if not probs and got else "caught")
    print("realpath(member) inside realpath(work)?",
          os.path.commonpath([os.path.realpath(work), os.path.realpath(member_path)]) == os.path.realpath(work))
finally:
    if p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill(); p.wait()
    log.close()
print("server reaped:", p.poll() is not None)
