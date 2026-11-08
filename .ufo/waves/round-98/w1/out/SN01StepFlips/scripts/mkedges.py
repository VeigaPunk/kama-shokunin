#!/usr/bin/env python3
"""SN01StepFlips - exact +1-window edge fixtures.

Real parse  : steps = 4 + T*(5+nd)  -> decides `invalid` iff <= MAX_STEPS
+1/header   : steps = 4 + T*(6+nd)  -> decides `invalid` iff <= MAX_STEPS

The +1 window (real decides, +1 does not) at nd=1 is T in [714286, 833332];
at nd=4 it is T in [500000, 555555]. These fixtures sit ON the edges so the
window's lower bound is measured, not assumed.
"""
import hashlib
import struct
import sys
from pathlib import Path

TYPE_F32 = 0
ALIGN = 32


def gguf(n_tensors: int, elems: int, with_data: bool, nd: int = 1) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        dims = struct.pack("<" + "Q" * nd, elems, *([1] * (nd - 1)))
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims
                   + struct.pack("<IQ", TYPE_F32, off))
        off += (elems * 4 + ALIGN - 1) // ALIGN * ALIGN
    head = b"".join(out)
    pad = (len(head) + ALIGN - 1) // ALIGN * ALIGN - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


def main() -> int:
    d = Path(sys.argv[1])
    d.mkdir(parents=True, exist_ok=True)
    spec = [("edge714285_nd1", 714_285, 1), ("edge714286_nd1", 714_286, 1),
            ("edge714287_nd1", 714_287, 1),
            ("edge499999_nd4", 499_999, 4), ("edge500000_nd4", 500_000, 4),
            ("edge500001_nd4", 500_001, 4)]
    for name, T, nd in spec:
        data = gguf(T, 1, False, nd)
        p = d / f"{name}.gguf"
        p.write_bytes(data)
        back = p.read_bytes()
        assert back == data, name
        n_t = struct.unpack_from("<Q", back, 8)[0]
        nl = struct.unpack_from("<Q", back, 24)[0]
        nd_read = struct.unpack_from("<I", back, 32 + nl)[0]
        real = 4 + n_t * (5 + nd_read)
        over = 4 + n_t * (6 + nd_read)
        print(f"EDGE {name} bytes={len(back)} T={n_t} nd={nd_read} "
              f"real_steps={real} real_decides={int(real <= 5_000_000)} "
              f"over_steps={over} over_decides={int(over <= 5_000_000)} "
              f"sha256={hashlib.sha256(back).hexdigest()[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
