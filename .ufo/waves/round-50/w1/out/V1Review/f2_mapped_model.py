#!/usr/bin/env python3
"""V1Review fixture F2: mapped_model dev format, stat-vs-maps join, hash gate,
size gate (isolated), deleted-file, replaced-file. Read-only on the lane."""
import importlib.util, os, sys, subprocess, time, hashlib

S = "/fast/scratch/hyaku/kama-r50/V1Review/f2"
os.makedirs(S, exist_ok=True)
os.environ["TMPDIR"] = S
spec = importlib.util.spec_from_file_location(
    "c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)

model = os.path.join(S, "fakemodel.gguf")
payload = os.urandom(8192)
open(model, "wb").write(payload)
sha = hashlib.sha256(payload).hexdigest()
c1.MODEL_SHA = sha  # fixture: substitute the frozen digest with this file's digest

child = subprocess.Popen([sys.executable, "-c",
    "import mmap, time\n"
    f"f = open({model!r}, 'r+b')\n"
    "m = mmap.mmap(f.fileno(), 0)\n"
    "time.sleep(60)\n"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(1.2)
    rows = [l.rstrip() for l in open(f"/proc/{child.pid}/maps") if model in l]
    f5 = rows[0].split(None, 5)
    st = os.stat(model)
    print("maps row:", rows[0])
    print("maps dev/inode: %s %s | stat format: %02x:%02x %d | equal: %s" %
          (f5[3], f5[4], os.major(st.st_dev), os.minor(st.st_dev), st.st_ino,
           f5[3] == "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
           and f5[4] == str(st.st_ino)))
    probs = []
    print("1 found:", c1.mapped_model(child.pid, probs), "probs:", probs)

    # hash gate: rewrite the SAME inode with garbage
    with open(model, "r+b") as fh:
        fh.seek(0); fh.write(os.urandom(8192)); fh.flush()
    probs = []
    print("2 same inode, rewritten content:", c1.mapped_model(child.pid, probs), "probs:", probs)

    # deleted file: maps pathname gains ' (deleted)' -> stat(path) ENOENT -> skipped
    os.unlink(model)
    time.sleep(0.2)
    rows2 = [l.rstrip() for l in open(f"/proc/{child.pid}/maps") if model in l]
    print("maps row after unlink:", rows2[0])
    probs = []
    print("3 deleted mapped file:", c1.mapped_model(child.pid, probs), "probs:", probs)

    # replaced at path: new file at the SAME path has a different inode than maps shows
    open(model, "wb").write(payload)  # restore a file at the old path (new inode)
    rows3 = [l.rstrip() for l in open(f"/proc/{child.pid}/maps") if model in l and "deleted" not in l]
    print("4 stat-vs-maps guard: new file at old path has inode",
          os.stat(model).st_ino, "!= maps inode of deleted mapping",
          rows2[0].split(None, 5)[4] if rows2 else "?")

    # size gate, isolated: make ANY dev/ino-matching candidate pass the hash by
    # monkeypatching sha_file; a 768 B mapping must still be skipped (line 335),
    # while a 2048 B control must be found.
    c1.sha_file = lambda p: c1.MODEL_SHA
    small = os.path.join(S, "small.gguf"); sp = os.urandom(768)
    open(small, "wb").write(sp); c1.MODEL_SHA = hashlib.sha256(sp).hexdigest()
    kid = subprocess.Popen([sys.executable, "-c",
        "import mmap, time\n"
        f"f = open({small!r}, 'r+b')\n"
        "m = mmap.mmap(f.fileno(), 0)\n"
        "time.sleep(20)\n"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    probs = []
    print("5 size gate: 768 B mapped, sha forced to pass:", c1.mapped_model(kid.pid, probs),
          probs, "<- None proves the <1024 skip")
    big = os.path.join(S, "big.gguf"); bp = os.urandom(2048)
    open(big, "wb").write(bp); c1.MODEL_SHA = hashlib.sha256(bp).hexdigest()
    kid2 = subprocess.Popen([sys.executable, "-c",
        "import mmap, time\n"
        f"f = open({big!r}, 'r+b')\n"
        "m = mmap.mmap(f.fileno(), 0)\n"
        "time.sleep(20)\n"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    probs = []
    print("6 control: 2048 B mapped, sha forced to pass:", c1.mapped_model(kid2.pid, probs), probs)
    probs = []
    print("7 nonexistent pid:", c1.mapped_model(4123456, probs), probs)
    kid.kill(); kid2.kill(); kid.wait(); kid2.wait()
finally:
    child.kill(); child.wait()
    for f in (model, os.path.join(S, "small.gguf"), os.path.join(S, "big.gguf")):
        if os.path.exists(f): os.unlink(f)
print("F2 DONE")
