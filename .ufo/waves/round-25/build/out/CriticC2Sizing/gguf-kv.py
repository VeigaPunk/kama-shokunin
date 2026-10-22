#!/usr/bin/env python3
"""Print scalar GGUF metadata keys (arrays summarized by length). Read-only."""
import struct
import sys

SCALAR = {0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i", 6: "<f", 7: "<?", 10: "<Q", 11: "<q", 12: "<d"}


def read_str(f):
    (n,) = struct.unpack("<Q", f.read(8))
    return f.read(n).decode("utf-8", "replace")


def read_val(f, t):
    if t in SCALAR:
        fmt = SCALAR[t]
        return struct.unpack(fmt, f.read(struct.calcsize(fmt)))[0]
    if t == 8:
        return read_str(f)
    if t == 9:
        (et,) = struct.unpack("<I", f.read(4))
        (n,) = struct.unpack("<Q", f.read(8))
        for _ in range(n):
            read_val(f, et)
        return f"<array type={et} len={n}>"
    raise ValueError(f"unknown gguf type {t}")


with open(sys.argv[1], "rb") as f:
    magic, version = f.read(4), struct.unpack("<I", f.read(4))[0]
    n_tensors, n_kv = struct.unpack("<QQ", f.read(16))
    print(f"magic={magic!r} version={version} tensors={n_tensors} kv={n_kv}")
    for _ in range(n_kv):
        key = read_str(f)
        (t,) = struct.unpack("<I", f.read(4))
        print(f"{key} = {read_val(f, t)}")
