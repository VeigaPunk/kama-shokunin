#!/usr/bin/env python3
"""G1: gguf_tokens() against GGUF spec. Synthetic GGUF v1/v2/v3 files."""
import importlib.util
import struct
import sys

S = "/fast/scratch/hyaku/kama-r49/V1Counter"
OUT = open(f"{S}/out/gguf.txt", "w")

spec = importlib.util.spec_from_file_location(
    "r49c1", f"{S}/lane/tools/round49-replay-witness-audit.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

def w(s=""):
    print(s)
    OUT.write(s + "\n")

def u64(v): return struct.pack("<Q", v)
def u32(v): return struct.pack("<I", v)
def gstr(s):
    b = s.encode("utf-8")
    return u64(len(b)) + b

def kv(key, typ, val):
    return gstr(key) + u32(typ) + val

def gguf(ver, kvs):
    body = b"".join(kvs)
    return b"GGUF" + u32(ver) + u64(0) + u64(len(kvs)) + body

def tokens_arr(*toks):
    out = u32(8) + u64(len(toks))
    for t in toks:
        out += gstr(t)
    return out

def arr(et, *vals):
    out = u32(et) + u64(len(vals))
    for v in vals:
        out += v
    return out

# --- v2 with varied preceding keys ---
kvs = [
    kv("rope.freq_base", 12, struct.pack("<d", 10000.0)),
    kv("block_count", 5, u32(6)),
    kv("arr.u32", 9, arr(4, u32(1), u32(2), u32(3))),
    kv("tokenizer.ggml.tokens", 9, tokens_arr("\u2581kama", "x", "y", "")),
    kv("tailing.key", 8, gstr("tail")),
    kv("boolish", 7, b"\x01"),
]
data2 = gguf(2, kvs)
open(f"{S}/g2.gguf", "wb").write(data2)
w("== v2 file ==")
r = cc.gguf_tokens(f"{S}/g2.gguf")
w(f"tokens={r!r}")
assert r == ["\u2581kama", "x", "y", ""], r

# --- v3 identical body ---
data3 = gguf(3, kvs)
open(f"{S}/g3.gguf", "wb").write(data3)
w("== v3 file ==")
r = cc.gguf_tokens(f"{S}/g3.gguf")
w(f"tokens={r!r}")
assert r == ["\u2581kama", "x", "y", ""], r

w("== v1 rejected ==")
try:
    cc.gguf_tokens(f"{S}/g2.gguf") if False else None
except Exception:
    pass
open(f"{S}/g1.gguf", "wb").write(gguf(1, kvs[:1]))
try:
    cc.gguf_tokens(f"{S}/g1.gguf")
    w("v1: NO ERROR (unexpected)")
except cc.EvalError as e:
    w(f"v1: EvalError {e}")

w("== non-GGUF ==")
open(f"{S}/notgguf.bin", "wb").write(b"XXXX" + b"\0" * 40)
try:
    cc.gguf_tokens(f"{S}/notgguf.bin")
    w("non-GGUF: NO ERROR")
except cc.EvalError as e:
    w(f"non-GGUF: EvalError {e}")

w("== tokens absent ==")
open(f"{S}/no_tokens.gguf", "wb").write(gguf(2, [kv("block_count", 5, u32(6))]))
try:
    cc.gguf_tokens(f"{S}/no_tokens.gguf")
    w("absent: NO ERROR")
except cc.EvalError as e:
    w(f"absent: EvalError {e}")

w("== tokens array of wrong et ==")
open(f"{S}/bad_et.gguf", "wb").write(
    gguf(2, [kv("tokenizer.ggml.tokens", 9, arr(4, u32(1)))])
)
try:
    cc.gguf_tokens(f"{S}/bad_et.gguf")
    w("bad_et: NO ERROR")
except cc.EvalError as e:
    w(f"bad_et: EvalError {e}")

w("== truncated string length beyond EOF: silent truncation ==")
# tokens array declares a 999999-byte string but file ends right after the length word
trunc = gguf(2, [kv("tokenizer.ggml.tokens", 9,
                    u32(8) + u64(1) + u64(999999) + b"ab")])
open(f"{S}/trunc.gguf", "wb").write(trunc)
try:
    r = cc.gguf_tokens(f"{S}/trunc.gguf")
    w(f"trunc: parsed without error -> {r!r} (length field ignored, data exhausted)")
except cc.EvalError as e:
    w(f"trunc: EvalError {e}")

w("== unknown GGUF type -> EvalError ==")
open(f"{S}/unk.gguf", "wb").write(gguf(2, [kv("k", 13, b"\0" * 8)]))
try:
    cc.gguf_tokens(f"{S}/unk.gguf")
    w("unknown type: NO ERROR")
except cc.EvalError as e:
    w(f"unknown type: EvalError {e}")

OUT.close()
print("DONE")
