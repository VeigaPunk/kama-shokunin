#!/usr/bin/env python3
"""Gate reject 2 experiment: /proc/<pid>/maps dev+inode alone does not identify the
frozen model bytes; the hash does.  Uses the counter's own mapped_model() and the live
tool's own model_mapping().

Cases:
  A  genuine model file at path P, mapped by a process -> inode check passes, hash passes.
  B  a host copy with different bytes at the same path P, mapped by a process -> maps
     dev+inode equal stat(path) (the inode check *passes*), hash does not equal MODEL_SHA.
"""
import hashlib
import importlib.util
import mmap
import os
import shutil
import subprocess
import sys
import time
import urllib.request

S = sys.argv[1]
TOOLS = sys.argv[2]
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             "499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf")

E = os.path.join(S, "exp", "e2")
os.makedirs(E, exist_ok=True)
genuine = os.path.join(E, "stories260K.gguf")
copy_path = os.path.join(E, "host-copy.gguf")
if not os.path.isfile(genuine):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(MODEL_URL, timeout=120) as r, open(genuine, "wb") as fh:
        shutil.copyfileobj(r, fh)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


counter = load("r50c1", os.path.join(TOOLS, "round50-replay-bind-audit.py"))
live = load("llamacpp_live", os.path.join(TOOLS, "kama-llamacpp-live.py"))

print(f"genuine path={genuine} size={os.path.getsize(genuine)} sha256={sha(genuine)}")
print(f"genuine hashes to MODEL_SHA: {sha(genuine) == MODEL_SHA}")


def map_in(path, name):
    code = ("import mmap,os,sys,time\n"
            f"f=open({path!r},'rb')\n"
            "m=mmap.mmap(f.fileno(),0,prot=mmap.PROT_READ)\n"
            "print(os.getpid(), flush=True)\n"
            "time.sleep(120)\n")
    p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
    pid = int(p.stdout.readline().strip())
    time.sleep(0.3)
    rows = [r for r in open(f"/proc/{pid}/maps").read().splitlines() if path in r]
    devs = []
    for r in rows:
        f = r.split(None, 5)
        if len(f) == 6 and (f[3], f[4]) not in devs:
            devs.append((f[3], f[4]))
    print(f"{name}: pid {pid} maps rows for path: {len(rows)}; (dev,inode) distinct: {devs}")
    st = os.stat(path)
    print(f"{name}: stat(path) dev={os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x} "
          f"inode={st.st_ino}")
    inode_only = all(f"{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}" == d and
                     str(st.st_ino) == i for d, i in devs)
    print(f"{name}: inode-only identity check would pass: {inode_only}")
    probs = []
    got = counter.mapped_model(pid, probs)
    print(f"{name}: counter.mapped_model -> {got!r} problems={probs}")
    mm = live.model_mapping(pid, path)
    print(f"{name}: live.model_mapping -> mapped={mm.get('mapped')} sha256={mm.get('sha256')} "
          f"reason={mm.get('reason')}")
    print(f"{name}: live.model_mapping sha256 == MODEL_SHA: {mm.get('sha256') == MODEL_SHA}")
    os.kill(pid, 9)
    p.wait()
    return inode_only, got, mm


# A: the genuine file at its own path.
map_in(genuine, "A-genuine")

# B: a host copy with different bytes replaces the mapped path.
with open(genuine, "rb") as fh:
    head = fh.read(4096)
with open(copy_path, "wb") as fh:
    fh.write(b"NOT THE FROZEN MODEL\n" * 200 + head[:1024])
print(f"B mediator path={copy_path} size={os.path.getsize(copy_path)} sha256={sha(copy_path)}")
print(f"B sha256 == MODEL_SHA: {sha(copy_path) == MODEL_SHA}")
inode_only, got, mm = map_in(copy_path, "B-host-copy")
print(f"RESULT inode_only_passes={inode_only} counter_mapped={got is not None} "
      f"counter_hash_gate_failed_closed={got is None} "
      f"live_records_wrong_sha={mm.get('mapped') is True and mm.get('sha256') != MODEL_SHA}")
