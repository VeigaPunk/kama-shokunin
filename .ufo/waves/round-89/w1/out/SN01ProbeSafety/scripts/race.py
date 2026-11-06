#!/usr/bin/env python3
"""TOCTOU probe: the checker is `os.stat(path)` -> S_ISREG -> `open(path,'rb')`.
Between the two syscalls a symlink target can be swapped to a FIFO; a plain open() on a
FIFO with no writer blocks forever. This measures the window directly without hanging:
it repeats stat+open(O_NONBLOCK) while a flipper swaps the symlink target, and counts
trials where stat saw a regular file but open saw a FIFO (i.e. a plain open would block).
Then it runs the real probe against the same flipper and reports any invocation that
exceeded the no-race baseline."""
import os, shutil, subprocess, sys, tempfile, threading, time

ROOT = "/fast/scratch/hyaku/kama-r89/SN01ProbeSafety"
D = tempfile.mkdtemp(prefix="race", dir=ROOT + "/tmp")
GOOD = D + "/good.gguf"
FIFO = D + "/fifo"
LINK = D + "/m.gguf"
shutil.copy(ROOT + "/fx/good.gguf", GOOD)
os.mkfifo(FIFO)
open(LINK + ".tmp", "w").close()
os.remove(LINK + ".tmp")


def swap(target):
    tmp = D + "/.swap.%d" % threading.get_ident()
    if os.path.lexists(tmp):
        os.remove(tmp)
    os.symlink(target, tmp)
    os.replace(tmp, LINK)


stop = False


def flipper():
    i = 0
    while not stop:
        swap(FIFO)
        swap(GOOD)
        i += 1


t = threading.Thread(target=flipper, daemon=True)
t.start()
time.sleep(0.05)

trials = hit = err = 0
t0 = time.time()
while trials < 2_000_000 and time.time() - t0 < 10:
    try:
        st = os.stat(LINK)
    except FileNotFoundError:
        err += 1
        continue
    trials += 1
    if not os.path.isfile(LINK):
        pass
    fd = os.open(LINK, os.O_RDONLY | os.O_NONBLOCK)
    mode = os.fstat(fd).st_mode
    os.close(fd)
    import stat as S
    if S.S_ISREG(st.st_mode) and S.S_ISFIFO(mode):
        hit += 1
rate = hit / trials if trials else 0
print(f"microbenchmark: trials={trials} stat_regular_open_fifo={hit} rate={rate:.2%} "
      f"elapsed={time.time()-t0:.1f}s (plain open() would have blocked {hit} times)")

# real probe: N invocations against the same flipper; port held by a trivial stub
import socket
body = ROOT + "/fx/b-race.json"
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
srv = subprocess.Popen([sys.executable, ROOT + "/srv.py", str(port), body, "", ""],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       start_new_session=True)
time.sleep(0.3)
env = dict(os.environ, TMPDIR=ROOT + "/tmp", KAMA_PROBE_TMPDIR=ROOT + "/tmp")
hang = 0
N = 300
worst = 0.0
for i in range(N):
    t1 = time.time()
    p = subprocess.Popen(["bash", ROOT + "/probe-M.sh", "listeners", "--port", str(port),
                          "--expect", "*"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True, env=env)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        hang += 1
        os.killpg(p.pid, 9)
        p.wait()
    dt = time.time() - t1
    worst = max(worst, dt)
stop = True
os.killpg(srv.pid, 9)
print(f"probe runs={N} hangs={hang} worst_wall={worst:.2f}s")
shutil.rmtree(D, ignore_errors=True)
