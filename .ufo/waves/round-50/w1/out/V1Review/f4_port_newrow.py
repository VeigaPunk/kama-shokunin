#!/usr/bin/env python3
"""V1Review fixture F4: port_refuses IPv4-only blind spot; newrow_leg parse and the
frozen-BASE-object behaviour. The git fixture lives under the seat scratch; the
toplevel assertion runs after init and BEFORE the first commit."""
import importlib.util, os, sys, socket, subprocess, tempfile, time

S = "/fast/scratch/hyaku/kama-r50/V1Review/f4"
os.makedirs(S, exist_ok=True)
os.environ["TMPDIR"] = S
spec = importlib.util.spec_from_file_location(
    "c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)

print("== port_refuses is IPv4-only (line 255) ==")
s6 = socket.socket(socket.AF_INET6); s6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s6.bind(("::1", 0)); s6.listen(5); p6 = s6.getsockname()[1]
probe = socket.create_connection(("::1", p6), timeout=2)
print("::1 listener on port %d: port_refuses() -> %s while ::1 connect succeeds"
      % (p6, c1.port_refuses(p6)))
probe.close(); s6.close()

print("\n== newrow_leg (lines 529-539) ==")
D = tempfile.mkdtemp(dir=S)
def g(*a):
    return subprocess.run(["git", "-C", D, *a], capture_output=True)
g("init", "-q")
print("toplevel == D (asserted after init, before first commit):",
      g("rev-parse", "--show-toplevel").stdout.decode().strip() == D)
g("config", "user.email", "fixture@example.invalid")
g("config", "user.name", "fixture")
os.makedirs(os.path.join(D, "corpus"), exist_ok=True)
open(os.path.join(D, "corpus", "SOURCES.md"), "w").write(
    "| S1 | round-49 row | |\n| S2 | another old row | |\n")
g("add", "-A"); g("commit", "-qm", "base")
base = g("rev-parse", "HEAD").stdout.decode().strip()
open(os.path.join(D, "corpus", "SOURCES.md"), "a").write(
    "| S496 | proc_pid_maps(5) man7.org/linux/man-pages/man5/proc_pid_maps.5.html "
    "| used-by corpus/lessons/round-50.md |\n")
g("add", "-A"); g("commit", "-qm", "tip")
tip = g("rev-parse", "HEAD").stdout.decode().strip()
detail = []
print("new S496 row:", c1.newrow_leg(D, tip, detail))
for d in detail: print("  detail:", d)
print("NOTE 'rows new since base' counts ALL tip rows: this fixture repo lacks the")
print("frozen BASE object 26ecba64..., git show fails with check=False (lines 531-533)")
print("and rows(BASE) is silently empty.")
detail = []
print("same tip asked twice (base==tip would be 0 if BASE were a parameter):")
c1.newrow_leg(D, base, detail)
for d in detail: print("  detail:", d)
open(os.path.join(D, "corpus", "SOURCES.md"), "w").write(
    "| S1 | round-49 row now citing man7.org/linux/man-pages/man5/proc_pid_maps.5.html | |\n"
    "| S2 | another old row | |\n")
g("add", "-A"); g("commit", "-qm", "tip2-modified-row")
tip2 = g("rev-parse", "HEAD").stdout.decode().strip()
detail = []
print("MODIFIED base row (no new id) counts as new:",
      c1.newrow_leg(D, tip2, detail))
for d in detail: print("  detail:", d)
print("F4 DONE")
