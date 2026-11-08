#!/usr/bin/env python3
"""End-to-end: the AMENDED counter's W12 fixture through the real probe at the current tip."""
import importlib.util as il
import json
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r96/SN01VerdictBoundary")
import boundary as B

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SRC = open(LANE / "tools" / "round96-router-budget.py").read()
ns = {"struct": struct}
seg = SRC.split("def gguf_strbig()")[1].split("def fixture_class")[0]
exec("def gguf_strbig()" + seg, ns)

C = B.load_counter()
work = B.SCRATCH / "e2e2"
work.mkdir(parents=True, exist_ok=True)
probe_bytes = subprocess.run(["git", "-C", str(LANE), "show", "HEAD:tools/kama-probe.sh"],
                             capture_output=True, check=True).stdout
R2 = C.Runner(work)
R2.install(probe_bytes)

FIX = B.FIX
p = B.write("w12_new.gguf", ns["gguf_strbig"]())
print(f"amended W12 fixture: {p.stat().st_size} bytes")
body = C.router_body([[str(p), "-m", str(p)]])
with C.Stub({"/v1/models": body, "/props": C.PROPS}) as st:
    rc, v, r, dt = R2.check(st.port)
out = {"label": "amended W12 (9 bytes/element, 6M elems)", "verdict": v, "reason": r,
       "rc": rc, "seconds": round(dt, 2), "want": "MODEL_OK/router-unloaded-autoload",
       "ok": (v == "MODEL_OK" and r == "router-unloaded-autoload")}
print(json.dumps(out))

# and the boundary fixtures re-checked end-to-end at the current tip
for label, path, want in [
    ("nd=1 n=833332 (4999996 steps)", B.write("b1.gguf", B.gguf(833_332, nd=1)), "MODEL_UNLOADED"),
    ("nd=1 n=833333 (5000001 steps)", B.write("b2.gguf", B.gguf(833_333, nd=1)), "MODEL_OK"),
    ("nd=3 n=624999 (4999996 steps)", B.write("b3.gguf", B.gguf(624_999, nd=3)), "MODEL_UNLOADED"),
    ("nd=3 n=625000 (5000001 steps)", B.write("b4.gguf", B.gguf(625_000, nd=3)), "MODEL_OK"),
    ("nd=4 n=555555 (4999999 steps)", B.write("b5.gguf", B.gguf(555_555, nd=4)), "MODEL_UNLOADED"),
    ("nd=4 n=555556 (5000008 steps)", B.write("b6.gguf", B.gguf(555_556, nd=4)), "MODEL_OK"),
    ("exactly 5000000 steps", B.write("b7.gguf", B.gguf(833_332, nd=1, kv=[(b"k", 4, b"\0\0\0\0")])), "MODEL_UNLOADED"),
]:
    body = C.router_body([[str(path), "-m", str(path)]])
    with C.Stub({"/v1/models": body, "/props": C.PROPS}) as st:
        rc, v, r, dt = R2.check(st.port)
    print(json.dumps({"label": label, "verdict": v, "reason": r, "want": want,
                      "ok": (v == want), "seconds": round(dt, 2)}), flush=True)
    path.unlink()
