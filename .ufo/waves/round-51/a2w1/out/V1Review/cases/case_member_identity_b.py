#!/usr/bin/env python3
"""B: hardlink member (same fs) - inode identity cannot distinguish it from an
   extracted file. C: '..' and absolute member strings escape <work>/server."""
import importlib.util, os, shutil, subprocess, sys, time

C1 = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py"
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("c1", C1)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

work = os.path.join(S, "work-b2")
mdir = os.path.join(work, "server", "llama-b11909")
os.makedirs(mdir, exist_ok=True)
member_path = os.path.join(work, "server", "llama-b11909", "llama-server")

print("== B: member is a HARDLINK to the running image (same fs) ==")
real = os.path.join(S, "sleep-real")
shutil.copy("/usr/bin/sleep", real); os.chmod(real, 0o755)
p = subprocess.Popen([real, "60"], start_new_session=True)
time.sleep(0.2)
os.link(real, member_path)   # a 'hardlink member' the replay could have planted
probs = []
got = c1.own_exe(p.pid, member_path, probs)
print("own_exe:", got, "probs:", probs)
print("=> dev:ino equal; only the sha leg notices the bytes are not the frozen server.")
print("   With a same-fs byte-identical copy the sha leg passes too (inherent to inode identity).")
p.terminate(); p.wait()
os.unlink(member_path)

print("\n== C: member string traversal ==")
for m in ("../outside", "../../etc/passwd", "/home/vgpnk/.local/opt/llama-b11909/llama-server"):
    mp = os.path.join(work, "server", m)
    esc = not os.path.commonpath([os.path.realpath(work), os.path.realpath(mp)]) == os.path.realpath(work)
    print(f"member={m!r:60} -> {mp}  escapes={esc}")

probs = []
got = c1.own_exe(os.getpid(), "/home/vgpnk/.local/opt/llama-b11909/llama-server", probs)
print("\nown_exe(pid=self, absolute member):", got, probs)
print("=> an absolute member string bypasses <work>/server entirely; os.path.join")
print("   treats it as the whole path (join's documented behavior).")
