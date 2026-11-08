#!/usr/bin/env python3
"""SN01StepFlips: independent GGUF fixture writer.

Layout follows the GGUF v3 container the lane's probe parses (tools/kama-probe.sh ROUTER_PY):
  magic "GGUF" | u32 version | u64 n_tensors | u64 n_kv
  then n_tensors tensor infos: u64 name_len | name | u32 n_dims | u64 dim[n_dims]
                              | u32 type | u64 offset
  then a 32-byte-aligned data section.

Fixtures carry no data section (the declared offsets therefore do not fit the file), so a file
whose HEADER parses within the step budget grades `invalid` at the offset check, while a file
whose header parse exceeds MAX_STEPS grades `-` (undecidable).

Every write is verified by re-reading the bytes back (no trust in the writer).
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
    spec = [("t800k_nd1", 800_000, 1), ("t520k_nd4", 520_000, 4),
            ("t714286_nd1", 714_286, 1), ("t555554_nd4", 555_554, 4),
            ("ok", 1, 1)]
    for name, T, nd in spec:
        with_data = name == "ok"
        data = gguf(T, 32 if with_data else 1, with_data, nd)
        p = d / f"{name}.gguf"
        p.write_bytes(data)
        back = p.read_bytes()
        assert back == data, name
        n_t = struct.unpack_from("<Q", back, 8)[0]
        n_kv = struct.unpack_from("<Q", back, 16)[0]
        nl = struct.unpack_from("<Q", back, 24)[0]
        nd_read = struct.unpack_from("<I", back, 32 + nl)[0]
        print(f"FIXTURE {name} bytes={len(back)} n_tensors={n_t} n_kv={n_kv} nd={nd_read} "
              f"sha256={hashlib.sha256(back).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
