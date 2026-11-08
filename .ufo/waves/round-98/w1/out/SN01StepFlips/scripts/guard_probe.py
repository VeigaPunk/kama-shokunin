#!/usr/bin/env python3
"""SN01StepFlips - which guard decides each fixture, measured.

Three guards can decide a GGUF file before/around the tensor-header loop, in the probe's
order (tools/kama-probe.sh ROUTER_PY, gguf_parse):
  1. SIZE guard   : `if n_kv * 13 + n_tensors * 24 > size: return "invalid"`  (after the 4
                    preamble steps, BEFORE the tensor loop)
  2. MAX_TENSORS  : `if n_kv > MAX_KV or n_tensors > MAX_TENSORS: return "-"`
  3. STEP budget  : MAX_STEPS exhausted inside the tensor loop -> Unknown -> "-"

Guard 1 decides at ~4 steps and returns `invalid` REGARDLESS of MAX_STEPS and REGARDLESS of
the +1/header mutant (the mutant only patches the tensor loop) - so a fixture that trips it
makes its cell VACUOUS: the mutant would produce the same verdict.

This script measures each fixture's deciding MAX_STEPS threshold (binary search over
MAX_STEPS on a scratch copy of the probe bytes). A threshold near 4-5 means guard 1 fired;
a threshold equal to 4 + T*(5+nd) means the step budget decided and the verdict is
budget-dependent (the cell is a real discriminator).

It also builds a deliberately TRUNCATED variant of the 800k fixture to show guard 1 firing,
and a >MAX_TENSORS variant to show guard 2 firing - both measured, not asserted.
"""
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drive import router_body, extract_router_py, direct_parse  # noqa: E402

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path(sys.argv[1]).resolve()
FX = SCRATCH / "fx"
EDGE = SCRATCH / "edge"
WORK = SCRATCH / "guard"
WORK.mkdir(parents=True, exist_ok=True)
CWD = SCRATCH / "cwd"
CWD.mkdir(parents=True, exist_ok=True)
PROBE = SCRATCH / "probe/kama-probe.sh"
EXE = str(FX / "ok.gguf")

src = PROBE.read_text()
rp = extract_router_py(src)


def threshold(path: Path, mutant: bool = False):
    """Smallest MAX_STEPS at which the parse still decides `invalid`."""
    body = WORK / "b.json"
    body.write_bytes(router_body([[EXE, "-m", str(path)]]))
    lo, hi, best = 4, 8_000_000, None
    while lo <= hi:
        mid = (lo + hi) // 2
        t = src
        if mutant:
            anchor = "            for _ in range(n_tensors):"
            assert t.count(anchor) == 1
            t = t.replace(anchor, anchor + "\n                steps[0] += 1", 1)
        t, n = re.subn(r"(?m)^MAX_STEPS = [0-9_]+", "MAX_STEPS = %d" % mid, t)
        assert n == 1
        p = WORK / "probe-g.sh"
        p.write_text(t)
        state, _ = direct_parse(extract_router_py(t), body, 0, CWD)
        if state == "invalid":
            best = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return best


def facts(path: Path):
    b = path.read_bytes()
    n_t = struct.unpack_from("<Q", b, 8)[0]
    n_kv = struct.unpack_from("<Q", b, 16)[0]
    size = len(b)
    nl = struct.unpack_from("<Q", b, 24)[0]
    nd = struct.unpack_from("<I", b, 32 + nl)[0]
    return n_t, n_kv, size, nd


print("=== the two NEW cells' fixtures (and the two boundary fixtures) ===")
print("%-18s %8s %4s %12s %12s %10s %8s %8s" %
      ("fixture", "T", "nd", "size_guard", "MAX_TENSORS", "threshold", "plan", "guard"))
rows = []
for name, T, nd in [("t800k_nd1", 800_000, 1), ("t520k_nd4", 520_000, 4),
                    ("t714286_nd1", 714_286, 1), ("t555554_nd4", 555_554, 4)]:
    p = FX / (name + ".gguf")
    n_t, n_kv, size, nd_r = facts(p)
    sg = n_kv * 13 + n_t * 24
    sg_fires = sg > size
    mt_fires = n_t > 1_000_000
    th = threshold(p)
    plan = 4 + n_t * (5 + nd_r)
    guard = ("SIZE-GUARD" if th is not None and th < 100 else
             ("MAX_TENSORS" if mt_fires else
              ("STEP-BUDGET" if th == plan else "OTHER")))
    print("%-18s %8d %4d %12d %12s %10s %8d %8s" %
          (name, n_t, nd_r, sg, "FIRES" if mt_fires else "-", th, plan, guard))
    rows.append((name, n_t, nd_r, size, sg, sg_fires, mt_fires, th, plan, guard))

print()
print("=== deliberately TRUNCATED 800k fixture (size guard forced) ===")
b = (FX / "t800k_nd1.gguf").read_bytes()
trunc = WORK / "trunc800k.gguf"
trunc.write_bytes(b[:10_000_000])
n_t, n_kv, size, nd_r = facts(trunc)
sg = n_kv * 13 + n_t * 24
th = threshold(trunc)
print("truncated 800k: size=%d size_guard_needs=%d size_guard_FIRES=%s threshold=%s"
      % (size, sg, sg > size, th))
if th is not None:
    print("  -> threshold near 4-5 proves the SIZE guard decided (before the tensor loop)")
    thm = threshold(trunc, mutant=True)
    print("  -> same fixture under the +1/header mutant: threshold=%s (identical verdict class)" % thm)

print()
print("=== a >MAX_TENSORS fixture (1 200 000 headers, guard 2) ===")
big = WORK / "big1200k.gguf"
if not big.exists():
    hdr = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1_200_000, 0)]
    off = 0
    for i in range(1_200_000):
        name = b"t%07d" % i
        hdr.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", 1)
                   + struct.pack("<Q", 1) + struct.pack("<IQ", 0, off))
        off += 32
    head = b"".join(hdr)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    big.write_bytes(head + b"\0" * pad + b"\0" * 16)
n_t, n_kv, size, nd_r = facts(big)
th = threshold(big)
print("1200k fixture: T=%d MAX_TENSORS_fires=%s threshold=%s (None => never `invalid`)"
      % (n_t, n_t > 1_000_000, th))
