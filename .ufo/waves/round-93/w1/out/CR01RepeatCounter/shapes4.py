#!/usr/bin/env python3
"""CR01RepeatCounter - shapes 4: one file twice in one entry; cross-call cache staleness.

S11: a single entry names ONE valid file under two path flags (`-m X -md X`).  The claim's rule is
     "every candidate naming it gets the same state"; an identity-keyed memo that returns
     "invalid" on a repeat (the seat spec's repeat->invalid shape) reports the second flag bad,
     which makes the only candidate bad -> MODEL_UNLOADED where M1 says MODEL_OK.
S12: two probe calls, same path, a same-size in-place rewrite with mtime restored between them.
     M1 (per-call SEEN) re-parses and sees the corruption; a cross-call on-disk cache keyed by
     the identity tuple serves the stale `ok` -> MODEL_OK (false green, the RV01 DEFECT-1 shape
     moved across calls).  The tip probe (b3765799, key + st_ctime_ns) re-parses; included for
     context, as the landed fix, not as a forgery.
"""
import importlib.util
import os
import shutil
import struct
import subprocess
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/CR01RepeatCounter"
SCR = Path("/fast/scratch/hyaku/kama-r93/CR01RepeatCounter")
BASE = "5af794958b0fc08f574aa2e67650282269549b02"
TIP = "b3765799"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rr = load("rr", LANE / "tools/round93-router-repeat.py")
fg = load("fg", OUT / "forgeries.py")

fx = SCR / "shapes4-fx"
shutil.rmtree(fx, ignore_errors=True)
fx.mkdir(parents=True)
good = rr.gguf(1, 32, True)
bad = bytearray(good)
bad[4:8] = struct.pack("<I", 9)
assert len(good) == len(bad) == 192
ok = fx / "ok.gguf"
ok.write_bytes(good)
P = fx / "swap.gguf"
exe = str(ok)

PROBES = {
    "M1": fg.TEXT.encode(),
    "base": subprocess.run(["git", "-C", str(LANE), "show", f"{BASE}:tools/kama-probe.sh"],
                           capture_output=True, check=True).stdout,
    "tip-b3765799": subprocess.run(["git", "-C", str(LANE), "show", f"{TIP}:tools/kama-probe.sh"],
                                   capture_output=True, check=True).stdout,
}
for name in ("identity-repeat-invalid", "disk-cache-identity"):
    PROBES[name] = fg.VARIANTS[name].encode()

work = SCR / "shapes4"
shutil.rmtree(work, ignore_errors=True)
work.mkdir(parents=True)
R = rr.Runner(work)


def check(probe_name, args):
    R.install(PROBES[probe_name])
    routes = {"/v1/models": rr.router_body(args), "/props": rr.PROPS}
    with rr.Stub(routes) as st:
        rc, verdict, reason, dt = R.check(st.port)
    return f"{verdict}/{reason}/rc={rc}/{dt:.2f}s"


# S11: one entry, one valid file named by two path flags
args11 = [[exe, "-m", str(ok), "-md", str(ok)]]
print(f"SHAPE S11-same-file-twice entries={len(args11)} -m ok.gguf -md ok.gguf", flush=True)
for p in ("M1", "base", "identity-repeat-invalid"):
    print(f"SHAPE_ROW S11-same-file-twice probe={p} {check(p, args11)}", flush=True)

# S12: two calls, same path, same-size rewrite with mtime restored
P.write_bytes(good)
st0 = os.stat(P)
first = {p: check(p, [[exe, "-m", str(P)]]) for p in ("M1", "disk-cache-identity")}
with open(P, "wb") as fh:
    fh.write(bytes(bad))
os.utime(P, ns=(st0.st_atime_ns, st0.st_mtime_ns))
st1 = os.stat(P)
same = (st0.st_ino == st1.st_ino and st0.st_size == st1.st_size
        and st0.st_mtime_ns == st1.st_mtime_ns and st0.st_dev == st1.st_dev)
print(f"SHAPE S12-mtime-restored entries=1 identity_unchanged={int(same)} "
      f"size_before_after={st0.st_size}/{st1.st_size}", flush=True)
for p in ("M1", "disk-cache-identity", "tip-b3765799"):
    first_row = first.get(p, "n/a")
    second = check(p, [[exe, "-m", str(P)]])
    print(f"SHAPE_ROW S12-mtime-restored probe={p} first={first_row} second={second}", flush=True)
print("SHAPES4_DONE", flush=True)
