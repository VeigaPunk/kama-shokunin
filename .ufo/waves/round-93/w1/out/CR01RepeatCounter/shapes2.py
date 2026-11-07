#!/usr/bin/env python3
"""CR01RepeatCounter - shapes 2: hardlink aliases and the 65-entry tail.

S8: 64 entries naming ONE slow invalid GGUF through 33 hardlinks (distinct realpaths, one
    inode).  The counter's R05 alias set is a symlink plus `dir/` + `./`*k paths; every alias
    there collapses under os.path.realpath, so a realpath-keyed memo scores R05 and cannot be
    told from the identity memo, while hardlinks bring the base defect (4 s deadline split over
    copies) straight back.
S9: 64 bad entries + one valid at position 65, against a fail-closed cap in the bash caller
    (candidates past N graded bad without being parsed).
"""
import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/CR01RepeatCounter"
SCR = Path("/fast/scratch/hyaku/kama-r93/CR01RepeatCounter")
M1 = "fe5f031cb1b9d33e1160360d892149b8ac3c7771"
BASE = "5af794958b0fc08f574aa2e67650282269549b02"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rr = load("rr", LANE / "tools/round93-router-repeat.py")
fg = load("fg", OUT / "forgeries.py")

fx = SCR / "shapes2-fx"
shutil.rmtree(fx, ignore_errors=True)
fx.mkdir(parents=True)
slow_bytes = rr.gguf(rr.TENSORS, 1, False)
ok2_bytes = rr.gguf(2, 32, True)

slow = fx / "slow.gguf"
slow.write_bytes(slow_bytes)
links = []
for i in range(33):
    p = fx / f"link{i:02d}.gguf"
    os.link(slow, p)
    links.append(p)
assert len({os.stat(p).st_ino for p in links} | {os.stat(slow).st_ino}) == 1
ok2 = fx / "ok2.gguf"
ok2.write_bytes(ok2_bytes)
exe = str(ok2)

PROBES = {
    "M1": fg.TEXT.encode(),
    "base": subprocess.run(["git", "-C", str(LANE), "show", f"{BASE}:tools/kama-probe.sh"],
                           capture_output=True, check=True).stdout,
}
for name in ("key-realpath", "key-path", "key-basename", "cap64-bash-bad", "cap1024-bash-bad",
             "cap64-unknown"):
    PROBES[name] = fg.VARIANTS[name].encode()

work = SCR / "shapes2"
shutil.rmtree(work, ignore_errors=True)
work.mkdir(parents=True)
R = rr.Runner(work)


def check(probe_name, args):
    R.install(PROBES[probe_name])
    routes = {"/v1/models": rr.router_body(args), "/props": rr.PROPS}
    with rr.Stub(routes) as st:
        rc, verdict, reason, dt = R.check(st.port)
    return f"{verdict}/{reason}/rc={rc}/{dt:.2f}s"


def shape(label, args, probes, note=""):
    print(f"SHAPE {label} entries={len(args)} {note}", flush=True)
    for p in probes:
        print(f"SHAPE_ROW {label} probe={p} {check(p, args)}", flush=True)


hl_args = [[exe, "-m", str(links[i % len(links)])] for i in range(64)]
shape("S8-hardlink-aliases", hl_args,
      ["M1", "base", "key-realpath", "key-path", "key-basename"],
      "33 hardlinks to one slow invalid inode, 64 entries")
shape("S9-tail-65", [[exe, "-m", str(slow)]] * 64 + [[exe, "-m", str(ok2)]],
      ["M1", "base", "cap64-bash-bad", "cap1024-bash-bad", "cap64-unknown"],
      "64 slow invalid + a distinct valid at position 65")
print("SHAPES2_DONE", flush=True)
