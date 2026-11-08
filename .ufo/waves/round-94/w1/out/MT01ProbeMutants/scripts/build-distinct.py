#!/usr/bin/env python3
"""Build direct distinguishing fixtures for MT01 mutant classification (MT01ProbeMutants)."""
import struct, sys
from pathlib import Path

d = Path(sys.argv[1])
d.mkdir(parents=True, exist_ok=True)


def hdr(n_tensors: int, n_kv: int = 0, size: int = 0) -> Path:
    p = d / f"nt{n_tensors}_kv{n_kv}.gguf"
    with open(p, "wb") as f:
        f.write(b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", n_tensors, n_kv))
        f.truncate(size)
    return p


# M14: n_tensors > MAX_TENSORS but the size pre-check passes (24 bytes/tensor):
# 2_000_000 * 24 = 48_000_000 bytes of declared tensor info.
print(hdr(2_000_000, 0, 48_000_000))
# M05: n_tensors under MAX_TENSORS, ~5 parse steps per tensor -> >4M deterministic steps,
# ~29 MB of tensor info so the size pre-check passes.
print(hdr(900_000, 0, 900_000 * 32))
# small control: 1 tensor, valid-looking, truncated data -> invalid fast
print(hdr(1, 0, 4096))
