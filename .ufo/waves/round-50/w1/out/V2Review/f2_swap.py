#!/usr/bin/env python3
"""F2: race between the maps read and the hashed open, plus the unlinked-model case.

The server child maps the model, then the file at the path is replaced (unlink +
new inode, the classic swap). The maps pathname for a mapped-then-unlinked file
carries the ' (deleted)' suffix, so the code must fail closed rather than hash the
NEW file at the same path (which would happily forge the binding).
"""
import hashlib, importlib.util, mmap, os, subprocess, sys

S = "/fast/scratch/hyaku/kama-r50/V2Review"
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py"
spec = importlib.util.spec_from_file_location("kll_f2", TOOL)
kll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kll)

work = os.path.join(S, "f2")
os.makedirs(work, exist_ok=True)
path = os.path.join(work, "model.gguf")
old_blob = os.urandom(300_000)
new_blob = os.urandom(300_000)
with open(path, "wb") as fh:
    fh.write(old_blob)
old_ino = os.stat(path).st_ino

child = subprocess.Popen(
    [sys.executable, "-c",
     "import mmap,os,sys,time\n"
     "f=os.open(sys.argv[1],os.O_RDONLY)\n"
     "m=mmap.mmap(f,0,prot=mmap.PROT_READ)\n"
     "print('mapped',flush=True)\n"
     "time.sleep(30)\n",
     path],
    stdout=subprocess.PIPE, text=True)
assert child.stdout.readline().strip() == "mapped"
try:
    # swap: unlink the mapped file, put a DIFFERENT file at the same path
    os.unlink(path)
    with open(path, "wb") as fh:
        fh.write(new_blob)
    assert os.stat(path).st_ino != old_ino
    mm = kll.model_mapping(child.pid, path)
    print("after-swap:", mm)
    assert mm["mapped"] is False, "FAIL: hashed the swapped-in file"
    # and the honest case still binds: re-map the new file in a second child
finally:
    child.kill()
    child.wait()

child2 = subprocess.Popen(
    [sys.executable, "-c",
     "import mmap,os,sys,time\n"
     "f=os.open(sys.argv[1],os.O_RDONLY)\n"
     "m=mmap.mmap(f,0,prot=mmap.PROT_READ)\n"
     "print('mapped',flush=True)\n"
     "time.sleep(30)\n",
     path],
    stdout=subprocess.PIPE, text=True)
assert child2.stdout.readline().strip() == "mapped"
try:
    mm = kll.model_mapping(child2.pid, path)
    ok = mm["mapped"] is True and mm["sha256"] == hashlib.sha256(new_blob).hexdigest()
    print("fresh-map:", {k: mm.get(k) for k in ("mapped", "dev", "inode")}, "ok=", ok)
    assert ok
finally:
    child2.kill()
    child2.wait()
print("F2 PASS")
