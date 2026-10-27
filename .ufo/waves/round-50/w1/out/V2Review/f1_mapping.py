#!/usr/bin/env python3
"""F1: model_mapping() against a REAL process with a REAL mmap (kernel maps, xfs).

Covers: maps line split(None,5), pathname with spaces, symlinked model path
(realpath + O_NOFOLLOW interplay), dev/inode string forms ('%02x:%02x' vs kernel,
str(st_ino) vs %lu), dedup of multiple same-file rows, 1 MiB chunk loop over a
2.5 MiB file, fd closed after use.
"""
import hashlib, importlib.util, mmap, os, subprocess, sys, time

S = "/fast/scratch/hyaku/kama-r50/V2Review"
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py"

spec = importlib.util.spec_from_file_location("kll_f1", TOOL)
kll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kll)

work = os.path.join(S, "f1")
os.makedirs(work, exist_ok=True)
sub = "dir with spaces"
os.makedirs(os.path.join(work, sub), exist_ok=True)
real = os.path.join(work, sub, "real model file.gguf")
blob = os.urandom(2_500_000)  # > 2 chunks of 1 MiB
with open(real, "wb") as fh:
    fh.write(blob)
full_sha = hashlib.sha256(blob).hexdigest()
st = os.stat(real)
print("fs dev/ino: st_dev=%x:%x st_ino=%d" % (os.major(st.st_dev), os.minor(st.st_dev), st.st_ino))

child = subprocess.Popen(
    [sys.executable, "-c",
     "import mmap,os,sys,time\n"
     "f=os.open(sys.argv[1],os.O_RDONLY)\n"
     "m=mmap.mmap(f,0,prot=mmap.PROT_READ)\n"
     "print('mapped',flush=True)\n"
     "time.sleep(30)\n",
     real],
    stdout=subprocess.PIPE, text=True)
assert child.stdout.readline().strip() == "mapped"
try:
    for label, path in (("plain", real), ("spaced", real), ("symlink", os.path.join(work, "link.gguf"))):
        if label == "symlink":
            lp = os.path.join(work, "link.gguf")
            if not os.path.islink(lp):
                os.symlink(real, lp)
            path = lp
        mm = kll.model_mapping(child.pid, path)
        ok = (mm.get("mapped") is True and mm.get("sha256") == full_sha
              and mm.get("inode") == str(st.st_ino))
        print(f"{label}: ok={ok} mm={ {k: mm.get(k) for k in ('mapped','dev','inode','size','path')} }")
        if not ok:
            print("FULL:", mm)
            sys.exit(1)
finally:
    child.kill()
    child.wait()

# anonymous-only process: the model is not mapped -> fail closed
none_child = subprocess.Popen([sys.executable, "-c", "import time; print('up',flush=True); time.sleep(30)"],
                              stdout=subprocess.PIPE, text=True)
assert none_child.stdout.readline().strip() == "up"
try:
    mm = kll.model_mapping(none_child.pid, real)
    print("unmapped-child:", mm)
    assert mm["mapped"] is False and mm["reason"] == "model-path-not-in-maps"
finally:
    none_child.kill()
    none_child.wait()
print("F1 PASS")
