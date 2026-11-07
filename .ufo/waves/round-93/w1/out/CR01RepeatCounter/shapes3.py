#!/usr/bin/env python3
"""CR01RepeatCounter - shape 3: name+size collision (a/dup.gguf valid, b/dup.gguf corrupt).

Two distinct model directories both hold `dup.gguf` at the same byte size; one is a good model,
the other a corrupt copy of the same length (version field 9 -> invalid).  A memo keyed by
(basename, size) collapses them; the M1 identity key does not.
"""
import importlib.util
import shutil
import struct
import subprocess
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/CR01RepeatCounter"
SCR = Path("/fast/scratch/hyaku/kama-r93/CR01RepeatCounter")
BASE = "5af794958b0fc08f574aa2e67650282269549b02"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rr = load("rr", LANE / "tools/round93-router-repeat.py")
fg = load("fg", OUT / "forgeries.py")

fx = SCR / "shapes3-fx"
shutil.rmtree(fx, ignore_errors=True)
(fx / "a").mkdir(parents=True)
(fx / "b").mkdir()
good = rr.gguf(1, 32, True)
bad = bytearray(good)
bad[4:8] = struct.pack("<I", 9)  # version 9: invalid, same length
assert len(good) == len(bad)
(fx / "a" / "dup.gguf").write_bytes(good)
(fx / "b" / "dup.gguf").write_bytes(bytes(bad))
exe = str(fx / "a" / "dup.gguf")

PROBES = {
    "M1": fg.TEXT.encode(),
    "base": subprocess.run(["git", "-C", str(LANE), "show", f"{BASE}:tools/kama-probe.sh"],
                           capture_output=True, check=True).stdout,
}
for name in ("key-name-size", "key-basename", "key-size"):
    PROBES[name] = fg.VARIANTS[name].encode()

work = SCR / "shapes3"
shutil.rmtree(work, ignore_errors=True)
work.mkdir(parents=True)
R = rr.Runner(work)


def check(probe_name, args):
    R.install(PROBES[probe_name])
    routes = {"/v1/models": rr.router_body(args), "/props": rr.PROPS}
    with rr.Stub(routes) as st:
        rc, verdict, reason, dt = R.check(st.port)
    return f"{verdict}/{reason}/rc={rc}/{dt:.2f}s"


args = [[exe, "-m", str(fx / "b" / "dup.gguf")]] * 63 + [[exe, "-m", str(fx / "a" / "dup.gguf")]]
print(f"SHAPE S10-name-size-collision entries={len(args)} 63 corrupt b/dup.gguf + valid a/dup.gguf "
      f"size={len(good)}", flush=True)
for p in ("M1", "base", "key-name-size", "key-basename", "key-size"):
    print(f"SHAPE_ROW S10-name-size-collision probe={p} {check(p, args)}", flush=True)
print("SHAPES3_DONE", flush=True)
