#!/usr/bin/env python3
"""Fixture builder for the per-file-deadline mutants (MT01ProbeMutants).

Reproduces the frozen counter's gguf() writer exactly (tools/round94-router-budget.py:143-160):
150,000 tensors with no tensor data -> an INVALID file that takes seconds to parse.
"""
import struct
import sys
from pathlib import Path

TENSORS = 150000


def gguf(n_tensors: int, elems: int, with_data: bool) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, elems, 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


d = Path(sys.argv[1])
(d / "slow").mkdir(parents=True, exist_ok=True)
slow = gguf(TENSORS, 1, False)
for k in range(8):
    (d / "slow" / f"s{k}.gguf").write_bytes(slow)
(d / "slow" / "big-valid.gguf").write_bytes(gguf(900000, 1, True))
print(len(slow), "bytes each; 8 slow copies + 1 big valid")
