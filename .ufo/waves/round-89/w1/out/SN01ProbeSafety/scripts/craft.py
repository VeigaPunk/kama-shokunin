#!/usr/bin/env python3
"""Craft GGUF-shaped files for the probe's header check (S584 rules) with adversarial
counts. Sparse: only the header bytes are written; the payload reads back as zeros."""
import struct, sys

def w(f, b):
    f.write(b)

def u32(v): return struct.pack("<I", v)
def u64(v): return struct.pack("<Q", v)

def kv(f, key: bytes, t: int, payload: bytes):
    w(f, u64(len(key))); w(f, key); w(f, u32(t)); w(f, payload)

def main():
    kind, path = sys.argv[1], sys.argv[2]
    if kind == "cpu-nested-array":
        # n_kv=1; one KV of type array whose elements are arrays of scalars with n=50M.
        # skip_value recurses once per element: ~12 bytes read each -> MAX_META/12 loops.
        n = 50_000_000
        with open(path, "wb") as f:
            w(f, b"GGUF"); w(f, u32(3)); w(f, u64(0)); w(f, u64(1))
            w(f, u64(1)); w(f, b"k"); w(f, u32(9)); w(f, u32(9)); w(f, u64(n))
    elif kind == "mem-tensors":
        # n_tensors=1e6: the checker materialises one (offset, nbytes) tuple per tensor
        # before it can decide the layout is invalid.
        n = 1_000_000
        with open(path, "wb") as f:
            w(f, b"GGUF"); w(f, u32(3)); w(f, u64(n)); w(f, u64(0))
    elif kind == "big-klen":
        with open(path, "wb") as f:
            w(f, b"GGUF"); w(f, u32(3)); w(f, u64(0)); w(f, u64(1))
            w(f, u64(2 ** 40)); w(f, b"\0")            # key longer than any real file
    elif kind == "kv-budget":
        # 100k KVs, each an array of 50M scalars: one seek per KV, the cheap case.
        n = 100_000
        with open(path, "wb") as f:
            w(f, b"GGUF"); w(f, u32(3)); w(f, u64(0)); w(f, u64(n))
            for i in range(n):
                w(f, u64(1)); w(f, b"k"); w(f, u32(9)); w(f, u32(0)); w(f, u64(50_000_000))
    else:
        raise SystemExit("unknown kind " + kind)

main()
