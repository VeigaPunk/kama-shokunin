#!/usr/bin/env python3
"""F3: docstring vs code - 'a regular file no larger than when it was mapped'.

The docstring of model_mapping() promises the mapping is accepted only when the
file is 'no larger than when it was mapped'. The code never compares st_size with
the mapped span from the maps row. Shrink the mapped file in place (same dev/ino,
prefix preserved): the tool still records mapped=True with the digest of the
SHORTENED content. Downstream the replay's sha256-vs-receipt check still refuses
(digest differs from the model), so this is a doc/code mismatch, not a false pass.
"""
import hashlib, importlib.util, mmap, os, subprocess, sys

S = "/fast/scratch/hyaku/kama-r50/V2Review"
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py"
spec = importlib.util.spec_from_file_location("kll_f3", TOOL)
kll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kll)

work = os.path.join(S, "f3")
os.makedirs(work, exist_ok=True)
path = os.path.join(work, "model.gguf")
blob = os.urandom(400_000)
with open(path, "wb") as fh:
    fh.write(blob)
model_sha = hashlib.sha256(blob).hexdigest()

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
    os.truncate(path, 200_000)  # same inode, same dev; file now smaller than the mapping
    mm = kll.model_mapping(child.pid, path)
    print("after-truncate:", {k: mm.get(k) for k in ("mapped", "size", "sha256")})
    assert mm["mapped"] is True, "code refused a shrunken file (docstring honoured)"
    assert mm["sha256"] == hashlib.sha256(blob[:200_000]).hexdigest()
    assert mm["sha256"] != model_sha
    print("recorded digest of the shrunken file != receipt model sha ->",
          "replay-side check model-mapping:sha256:... fires (fail-closed downstream)")
finally:
    child.kill()
    child.wait()
print("F3 PASS (doc/code mismatch demonstrated, no false pass reachable via replay)")
