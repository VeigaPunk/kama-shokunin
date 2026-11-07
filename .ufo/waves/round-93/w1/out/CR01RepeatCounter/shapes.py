#!/usr/bin/env python3
"""CR01RepeatCounter - router-listing shapes where the passing forgeries grade wrong.

Each shape is a real router listing ([id=good, status=unloaded, args=...]) that the frozen
counter does NOT contain; each row runs one probe over that listing on a lane-owned stub.
`real M1` is the measured probe (fe5f031c), `base` is 5af79495 (do-nothing), and the forgery
rows are the variants the frozen counter scored 10/10 (forgeries.py).  A forgery row that
differs from M1 on a shape is a router listing where the counter's 10/10 cannot see the
difference; where it also differs from BASE it is a regression the counter would green.
"""
import importlib.util
import os
import subprocess
import sys
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

fx = SCR / "shapes-fx"
fx.mkdir(parents=True, exist_ok=True)
slow_bytes = rr.gguf(rr.TENSORS, 1, False)
ok_bytes = rr.gguf(1, 32, True)
ok2_bytes = rr.gguf(2, 32, True)
bad_bytes = b"GGUF" + b"\x00" * 12  # small invalid: header too short for the counts

slowA = fx / "a" / "slow.gguf"
slowA.parent.mkdir(exist_ok=True)
slowA.write_bytes(slow_bytes)
slowB = fx / "b" / "slow.gguf"  # distinct file, SAME basename, valid, different size
slowB.parent.mkdir(exist_ok=True)
slowB.write_bytes(ok_bytes)
same_size_valid = fx / "okpad.gguf"  # distinct file, SAME size as slowA, valid
same_size_valid.write_bytes(ok_bytes + b"\0" * (len(slow_bytes) - len(ok_bytes)))
ok = fx / "ok.gguf"
ok.write_bytes(ok_bytes)
ok2 = fx / "ok2.gguf"
ok2.write_bytes(ok2_bytes)
smallbad = fx / "smallbad.gguf"
smallbad.write_bytes(bad_bytes)
missing = str(fx / "absent" / "missing.gguf")
exe = str(ok)
P = fx / "swap.gguf"

PROBES = {
    "M1": fg.TEXT.encode(),
    "base": subprocess.run(["git", "-C", str(LANE), "show", f"{BASE}:tools/kama-probe.sh"],
                           capture_output=True, check=True).stdout,
}
for name in ("key-basename", "key-size", "key-size-mtime", "key-devino", "repeat-invalid",
             "cap64-bad", "cap1024-bad", "ok-as-unknown", "disk-cache-path", "disk-cache-identity"):
    PROBES[name] = fg.VARIANTS[name].encode()

import shutil
work = SCR / "shapes"
shutil.rmtree(work, ignore_errors=True)
work.mkdir(parents=True, exist_ok=True)
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


# S1: 63 copies of an invalid file + one DISTINCT valid file with the SAME basename
shape("S1-basename-collision", [[exe, "-m", str(slowA)]] * 63 + [[exe, "-m", str(slowB)]],
      ["M1", "base", "key-basename", "key-size", "key-size-mtime"],
      "two model dirs, both hold a file named slow.gguf; b/ is a good model")
# S2: 63 copies of an invalid file + one DISTINCT valid file of the SAME byte size
shape("S2-size-collision", [[exe, "-m", str(slowA)]] * 63 + [[exe, "-m", str(same_size_valid)]],
      ["M1", "base", "key-size", "key-size-mtime", "key-basename"],
      "corrupt and complete copies of one model are often the same size")
# S3: 64 bad + the valid file at position 65 (counter P02 is 63+1 = exactly the cap edge)
shape("S3-tail-beyond-64", [[exe, "-m", str(slowA)]] * 64 + [[exe, "-m", str(ok2)]],
      ["M1", "base", "cap64-bad", "cap1024-bad"],
      "P02 = 63 bad + 1 good; one more entry is enough")
# S4: same path, a good model replaced by the slow invalid one between two probe calls
P.write_bytes(ok_bytes)
s4 = {}
for p in ("M1", "base", "disk-cache-path", "disk-cache-identity"):
    s4[p] = check(p, [[exe, "-m", str(P)]])
tmp = fx / "swap.tmp"
tmp.write_bytes(slow_bytes)
os.replace(tmp, P)
print(f"SHAPE S4-cross-call-replace entries=1 first=all-MODEL_OK then os.replace(good->slow invalid)", flush=True)
for p in ("M1", "base", "disk-cache-path", "disk-cache-identity"):
    print(f"SHAPE_ROW S4-cross-call-replace probe={p} first={s4[p]} second={check(p, [[exe, '-m', str(P)]])}",
          flush=True)
# S5: same path, same inode, rewritten in place (mtime changes, inode does not)
P.write_bytes(ok_bytes)
ino0 = os.stat(P).st_ino
s5 = {p: check(p, [[exe, "-m", str(P)]]) for p in ("M1", "base", "key-devino")}
with open(P, "wb") as fh:
    fh.write(slow_bytes)
ino1 = os.stat(P).st_ino
print(f"SHAPE S5-inplace-rewrite entries=1 inode_same={int(ino0 == ino1)} ", flush=True)
for p in ("M1", "base", "key-devino"):
    print(f"SHAPE_ROW S5-inplace-rewrite probe={p} first={s5[p]} second={check(p, [[exe, '-m', str(P)]])}",
          flush=True)
# S6: small-fixture battery for repeat-invalid (no slow file: verdict logic only)
cases = {
    "ok-ok": [[exe, "-m", str(ok)]] * 2,
    "bad-ok": [[exe, "-m", str(smallbad)], [exe, "-m", str(ok)]],
    "ok-bad-bad": [[exe, "-m", str(ok)]] + [[exe, "-m", str(smallbad)]] * 2,
    "missing-missing": [[exe, "-m", missing]] * 2,
    "missing-bad": [[exe, "-m", missing], [exe, "-m", str(smallbad)]],
    "bad-bad": [[exe, "-m", str(smallbad)]] * 2,
    "ok-missing": [[exe, "-m", str(ok)], [exe, "-m", missing]],
    "ok": [[exe, "-m", str(ok)]],
    "bad": [[exe, "-m", str(smallbad)]],
}
diffs = 0
for label, args in cases.items():
    m1 = check("M1", args)
    rep = check("repeat-invalid", args)
    same = m1.split("/rc=")[0] == rep.split("/rc=")[0]
    diffs += 0 if same else 1
    print(f"SHAPE_ROW S6-repeat {label} same={int(same)} M1={m1} repeat-invalid={rep}", flush=True)
print(f"SHAPE S6-repeat diffs={diffs}", flush=True)
# S7: the positive path is unverified: a corrupt SMALL file next to a good one
shape("S7-small-corrupt", [[exe, "-m", str(smallbad)]] * 1,
      ["M1", "base", "ok-as-unknown"], "one small invalid model, no valid file")
print("SHAPES_DONE", flush=True)
