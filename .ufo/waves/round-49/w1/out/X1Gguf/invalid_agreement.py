#!/usr/bin/env python3
"""Seat X1Gguf: divergence probe on an *invalid* GGUF.

Two independent decoders must agree not only on the 512 tokens of the pinned
model but on where a malformed KV table stops.  One fixture whose nested-array
length is deliberately short (the second inner array is missing, so the reader
walks into the next KV) is fed to both:

  * gguf_tokens() of tools/round49-replay-witness-audit.py
  * gguf.GGUFReader of the PyPI `gguf` package

Run:  uv run --with gguf python invalid_agreement.py <counter.py> <out.txt>
"""
import importlib.util
import struct
import sys

COUNTER, OUT = sys.argv[1], sys.argv[2]

nested = struct.pack("<I", 9) + struct.pack("<Q", 2)           # ARRAY<ARRAY>, but only one child
nested += struct.pack("<I", 0) + struct.pack("<Q", 2) + b"\x01\x00"
key = b"general.skipnest"
blob = (b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 0, 2)
        + struct.pack("<Q", len(key)) + key + struct.pack("<I", 9) + nested
        + struct.pack("<Q", len(b"tokenizer.ggml.tokens")) + b"tokenizer.ggml.tokens"
        + struct.pack("<I", 9) + struct.pack("<I", 8) + struct.pack("<Q", 2)
        + struct.pack("<Q", 1) + b"a" + struct.pack("<Q", 1) + b"b")
path = OUT + ".fixture.gguf"
open(path, "wb").write(blob)

spec = importlib.util.spec_from_file_location("c1", COUNTER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    got = mod.gguf_tokens(path)
    counter = f"returned {len(got)} tokens"
except BaseException as exc:
    counter = f"{type(exc).__name__}: {exc}"

import gguf
try:
    pkg = f"returned {len(gguf.GGUFReader(path).get_field('tokenizer.ggml.tokens').contents())} tokens"
except BaseException as exc:
    pkg = f"{type(exc).__name__}: {exc}"

lines = [f"fixture={path} bytes={len(blob)}",
         f"counter: {counter}",
         f"gguf-py: {pkg}",
         "agree_on_rejection=" + str(counter.split(':')[0] != 'returned' and pkg.split(':')[0] != 'returned')]
open(OUT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
