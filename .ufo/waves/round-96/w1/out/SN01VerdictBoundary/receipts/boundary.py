#!/usr/bin/env python3
"""SN01VerdictBoundary - map the decision boundary MAX_STEPS = 5_000_000 induces.

Read-only against the lane repo; writes only into this seat's scratch.

Subcommands:
  steps   <n> <nd> [kv]   -> steps consumed and state, via the landed ROUTER_PY logic
  bsearch                 -> binary search of the largest decidable tensor count
  e2e                     -> run the REAL probe (bash) against a stub router
"""
from __future__ import annotations

import importlib.util as _il
import json
import struct
import subprocess
import sys
import time
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r96/SN01VerdictBoundary")
LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FIX = SCRATCH / "fix"

_spec = _il.spec_from_file_location("router_instr", SCRATCH / "router_instrumented.py")
R = _il.module_from_spec(_spec)
_spec.loader.exec_module(R)


# ----------------------------------------------------------------- fixtures
def gguf(n_tensors: int, nd: int = 1, elems: int = 1, with_data: bool = False,
         kv: list | None = None) -> bytes:
    """A GGUF v3 file. kv = list of (key bytes, value-type u32, value bytes)."""
    kv = kv or []
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, len(kv))]
    for key, vtype, vbytes in kv:
        out.append(struct.pack("<Q", len(key)) + key)
        out.append(struct.pack("<I", vtype) + vbytes)
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name)
        out.append(struct.pack("<I", nd))
        for _ in range(nd):
            out.append(struct.pack("<Q", elems))
        out.append(struct.pack("<IQ", 0, off))  # type 0 = F32, offset
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


def gguf_strbig(n_elems: int) -> bytes:
    """ONE KV whose value is a string array of n_elems EMPTY strings (element type 8).

    Each element is a u64 length prefix (0) and no bytes, so the array's bytes are
    8*n_elems long. The probe's skip_strings needs base + 8*n <= size, else the size
    check raises Bad (-> 'invalid') before the step budget can govern (-> '-').
    """
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 0, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<IIQ", 9, 8, n_elems))  # t=9 array, elem type 8 string
    out.append(struct.pack("<Q", 0) * n_elems)
    return b"".join(out)


def gguf_strbig_counter() -> bytes:
    """The exact bytes the frozen counter writes (tools/round96-router-budget.py)."""
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 0, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<IIQ", 9, 8, 6_000_000))
    out.append(struct.pack("<Q", 1) + b"x" * 6_000_000)
    return b"".join(out)


# ------------------------------------------------------------- landed parser
def state_of(path: Path) -> tuple[str, int]:
    R.SEEN.clear()
    R._LAST[0] = 0
    st = R.gguf_state(str(path))
    return st, R._LAST[0]


def write(name: str, data: bytes) -> Path:
    FIX.mkdir(parents=True, exist_ok=True)
    p = FIX / name
    p.write_bytes(data)
    return p


# ------------------------------------------------------------------- bsearch
def decidable(n: int, nd: int = 1) -> bool:
    p = write(f"bs_{nd}_{n}.gguf", gguf(n, nd=nd))
    st, _ = state_of(p)
    p.unlink()
    return st == "invalid"  # a no-data-section file grades 'invalid' when decidable


def bsearch(nd: int = 1, lo: int = 1, hi: int = 900_000) -> dict:
    t0 = time.time()
    probes = 0
    while lo < hi:
        mid = (lo + hi + 1) // 2
        probes += 1
        if decidable(mid, nd):
            lo = mid
        else:
            hi = mid - 1
    p = write(f"bs_{nd}_{lo}.gguf", gguf(lo, nd=nd))
    st_lo, steps_lo = state_of(p)
    p.unlink()
    p = write(f"bs_{nd}_{lo + 1}.gguf", gguf(lo + 1, nd=nd))
    st_hi, steps_hi = state_of(p)
    p.unlink()
    return {"nd": nd, "largest_decidable": lo, "state_at_max": st_lo,
            "steps_at_max": steps_lo, "state_at_max_plus_1": st_hi,
            "steps_at_max_plus_1": steps_hi, "probes": probes,
            "seconds": round(time.time() - t0, 1)}


# ----------------------------------------------------------------------- e2e
def load_counter():
    p = LANE / "tools" / "round96-router-budget.py"
    s = _il.spec_from_file_location("r96_counter", p)
    m = _il.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def e2e(specs: list[tuple[str, Path, str]]):
    """specs: (label, fixture path, expected verdict)."""
    C = load_counter()
    work = SCRATCH / "e2e"
    work.mkdir(parents=True, exist_ok=True)
    probe_bytes = subprocess.run(["git", "-C", str(LANE), "show", "HEAD:tools/kama-probe.sh"],
                                 capture_output=True, check=True).stdout
    R2 = C.Runner(work)
    R2.install(probe_bytes)
    out = []
    for label, path, want in specs:
        body = C.router_body([[str(path), "-m", str(path)]])
        routes = {"/v1/models": body, "/props": C.PROPS}
        with C.Stub(routes) as st:
            rc, v, r, dt = R2.check(st.port)
        out.append({"label": label, "file": path.name, "want": want, "rc": rc,
                    "verdict": v, "reason": r, "seconds": round(dt, 2),
                    "ok": (v == want)})
        print(json.dumps(out[-1]), flush=True)
    return out


def main() -> int:
    cmd = sys.argv[1]
    if cmd == "steps":
        n, nd = int(sys.argv[2]), int(sys.argv[3])
        kv = []
        if len(sys.argv) > 4 and sys.argv[4] == "kv":
            kv = [(b"k", 4, b"\0\0\0\0")]  # u32 value: 4 need() calls
        p = write(f"st_{nd}_{n}.gguf", gguf(n, nd=nd, kv=kv))
        st, steps = state_of(p)
        print(json.dumps({"n": n, "nd": nd, "kv": len(kv), "state": st, "steps": steps}))
        p.unlink()
        return 0
    if cmd == "bsearch":
        for nd in (1, 2, 3, 4):
            print(json.dumps(bsearch(nd)), flush=True)
        return 0
    if cmd == "e2e":
        FIX.mkdir(parents=True, exist_ok=True)
        specs = []
        p1 = write("e2e_833332_nd1.gguf", gguf(833_332, nd=1))
        specs.append(("tensor-833332-nd1", p1, "MODEL_UNLOADED"))
        p2 = write("e2e_833333_nd1.gguf", gguf(833_333, nd=1))
        specs.append(("tensor-833333-nd1", p2, "MODEL_OK"))
        p3 = write("e2e_833332_nd2.gguf", gguf(833_332, nd=2))
        specs.append(("tensor-833332-nd2", p3, "MODEL_OK"))
        p4 = write("e2e_714285_nd2.gguf", gguf(714_285, nd=2))
        specs.append(("tensor-714285-nd2", p4, "MODEL_UNLOADED"))
        p5 = write("e2e_714286_nd2.gguf", gguf(714_286, nd=2))
        specs.append(("tensor-714286-nd2", p5, "MODEL_OK"))
        p6 = write("e2e_exact_steps.gguf", gguf(833_332, nd=1, kv=[(b"k", 4, b"\0\0\0\0")]))
        specs.append(("exactly-5000000-steps", p6, "MODEL_UNLOADED"))
        p7 = write("e2e_exact_steps_plus1.gguf", gguf(833_333, nd=1, kv=[(b"k", 4, b"\0\0\0\0")]))
        specs.append(("5000006-steps", p7, "MODEL_OK"))
        p8 = write("e2e_w12_proper.gguf", gguf_strbig(5_000_001))
        specs.append(("W12-proper-strarray-5000001", p8, "MODEL_OK"))
        p9 = write("e2e_w12_counter.gguf", gguf_strbig_counter())
        specs.append(("W12-counter-bytes-6000000", p9, "MODEL_UNLOADED"))
        e2e(specs)
        return 0
    print("unknown cmd", cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
