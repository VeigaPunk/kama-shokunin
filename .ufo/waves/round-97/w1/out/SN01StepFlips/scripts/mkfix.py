#!/usr/bin/env python3
"""SN01StepFlips fixture builder.

Two independent GGUF families per (T, nd) so the probe's verdict cannot hinge on one
byte-layout trick:

  famA  counter-identical layout: sequential aligned offsets, NO data section.
        -> the "invalid" verdict comes from `start + off + nbytes > size`.
  famB  a real data section, with one deliberately wrong tensor offset.
        -> the "invalid" verdict comes from `off != expect`, and the file is big enough
           that the size guard `n_kv*13 + n_tensors*24 > size` can never fire.

Both families keep the header layout the probe prices (name u64 + name bytes, nd u32,
nd dims u64, type u32, offset u64) so a header costs 5 + nd steps.
"""
import struct
import sys
from pathlib import Path


def _header(T, nd, offsets, bad_index=None):
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", T, 0)]
    off = 0
    for i in range(T):
        name = b"t%07d" % i
        dims = struct.pack("<" + "Q" * nd, 1, *([1] * (nd - 1)))
        o = offsets[i]
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims
                   + struct.pack("<IQ", 0, o))
        off += 32
    return b"".join(out), off


def famA(T: int, nd: int) -> bytes:
    """Counter-identical: no data section -> invalid via the size check."""
    offsets = [i * 32 for i in range(T)]
    head, _ = _header(T, nd, offsets)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + b"\0" * 16


def famB(T: int, nd: int, bad_index: int = 0) -> bytes:
    """Real data section; tensor `bad_index` declares an offset that breaks `off != expect`."""
    offsets = [i * 32 for i in range(T)]
    offsets[bad_index] += 64
    head, datasize = _header(T, nd, offsets)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + b"\0" * datasize


def probe_layout(T: int, nd: int, blob: bytes):
    """Recompute the probe's own guards from the bytes (no probe involved)."""
    size = len(blob)
    n_tensors = struct.unpack_from("<Q", blob, 8)[0]
    n_kv = struct.unpack_from("<Q", blob, 16)[0]
    size_guard = (n_kv * 13 + n_tensors * 24) > size
    max_tensors_guard = n_tensors > 1_000_000
    # header position ceiling (MAX_META = 512 MiB) is checked per need(); approximate with
    # the end of the header section.
    hdr_end = 24 + n_tensors * (8 + 8 + 4 + 8 * nd + 4 + 8)
    meta_guard = hdr_end > 512 * 1024 ** 2
    steps = 4 + n_tensors * (5 + nd)
    return dict(size=size, n_tensors=n_tensors, n_kv=n_kv, size_guard=size_guard,
                max_tensors_guard=max_tensors_guard, meta_guard=meta_guard,
                hdr_end=hdr_end, steps=steps, steps_over=steps > 5_000_000)


if __name__ == "__main__":
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    cases = [(833332, 1), (833333, 1), (900000, 1), (700000, 4), (555555, 4), (555556, 4)]
    for T, nd in cases:
        for fam, blob in (("A", famA(T, nd)), ("B", famB(T, nd, 0))):
            p = outdir / f"t{T}_nd{nd}_{fam}.gguf"
            p.write_bytes(blob)
            g = probe_layout(T, nd, blob)
            print(f"{p.name} bytes={g['size']} steps={g['steps']} "
                  f"steps_over_5M={g['steps_over']} size_guard={g['size_guard']} "
                  f"max_tensors_guard={g['max_tensors_guard']} meta_guard={g['meta_guard']} "
                  f"hdr_end={g['hdr_end']}")
