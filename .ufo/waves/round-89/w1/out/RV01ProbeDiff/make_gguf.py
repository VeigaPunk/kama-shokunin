#!/usr/bin/env python3
"""Build crafted GGUF fixtures for the RV01ProbeDiff C1 diff review (round 89 w1).

Each fixture mutates a minimal valid GGUF v3 template: 2 KVs (general.architecture
string, optional general.alignment u32) + one tensor. Mutations target every
header check in ggml/src/gguf.cpp @ 6c01da62 and llama-model-loader.h
llama_tensor_weight, plus loader-only rejections (dup names, empty key, nested
array, long tensor name, removed/out-of-range tensor types) to separate
false-red risk from remaining false greens.
"""
import os
import struct
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "files"
ALIGN = 32

T_U8, T_I8, T_U16, T_I16, T_U32, T_I32, T_F32, T_BOOL, T_STR, T_ARR, T_U64, T_I64, T_F64 = range(13)


def w_str(b, s):
    e = s.encode()
    b += struct.pack("<Q", len(e)) + e
    return b


def kv_str(b, k, v):
    b = w_str(b, k)
    b += struct.pack("<I", T_STR)
    return w_str(b, v)


def kv_u32(b, k, v):
    b = w_str(b, k)
    return b + struct.pack("<I", T_U32) + struct.pack("<I", v)


def kv_arr_of_arr(b, k):
    b = w_str(b, k)
    b += struct.pack("<I", T_ARR)          # outer array
    b += struct.pack("<I", T_ARR)          # inner type = ARRAY (loader rejects)
    b += struct.pack("<Q", 2)              # 2 elements
    for _ in range(2):                     # each element: array of 2 u32
        b += struct.pack("<I", T_U32) + struct.pack("<Q", 2) + struct.pack("<II", 1, 2)
    return b


def tensor_info(name, ndims, ne, ttype, off):
    b = w_str(b"", name)
    b += struct.pack("<I", ndims)
    for d in range(ndims):
        b += struct.pack("<Q", ne[d])
    return b + struct.pack("<I", ttype) + struct.pack("<Q", off)


def build(path, *, magic=b"GGUF", version=3, kvs=None, infos=None, data=b"",
          after_infos_pad=None, footer=b"", tensor_bytes=None):
    b = magic + struct.pack("<I", version)
    kvs = kvs if kvs is not None else [lambda x: kv_str(x, "general.architecture", "stories")]
    infos = infos if infos is not None else [tensor_info("blk.0.weight", 2, [8, 8], 0, 0)]
    n_kv = len(kvs)
    n_tensors = len(infos)
    b += struct.pack("<Q", n_tensors) + struct.pack("<Q", n_kv)
    for f in kvs:
        b = f(b)
    body = b"".join(infos)
    b += body
    if after_infos_pad is not None:
        b += after_infos_pad
    start = (len(b) + ALIGN - 1) // ALIGN * ALIGN
    b += b"\x00" * (start - len(b))
    b += data if data else b"\x00" * 256
    b += footer
    with open(path, "wb") as f:
        f.write(b)
    return start


def main():
    os.makedirs(OUT, exist_ok=True)

    def p(name):
        return os.path.join(OUT, name)

    # 01 valid template
    build(p("valid.gguf"))
    # 02 bad magic
    build(p("badmagic.gguf"), magic=b"GGUX")
    # 03 version 1
    build(p("v1.gguf"), version=1)
    # 04 version 4
    build(p("v4.gguf"), version=4)
    # 05 version 0
    build(p("v0.gguf"), version=0)
    # 06 byte-swapped version (0x00030000)
    build(p("vend.gguf"), version=0x00030000)
    # 07 alignment 0
    build(p("align0.gguf"), kvs=[lambda x: kv_str(x, "general.architecture", "stories"),
                                 lambda x: kv_u32(x, "general.alignment", 0)])
    # 08 alignment 3 (not power of two)
    build(p("align3.gguf"), kvs=[lambda x: kv_str(x, "general.architecture", "stories"),
                                 lambda x: kv_u32(x, "general.alignment", 3)])
    # 09 alignment as STRING type (loader: must be u32)
    b = b"GGUF" + struct.pack("<I", 3) + struct.pack("<Q", 1) + struct.pack("<Q", 2)
    b = kv_str(b, "general.architecture", "stories")
    b = w_str(b, "general.alignment") + struct.pack("<I", T_STR)
    b = w_str(b, "32")
    b += tensor_info("blk.0.weight", 2, [8, 8], 0, 0)
    start = (len(b) + ALIGN - 1) // ALIGN * ALIGN
    b += b"\x00" * (start - len(b)) + b"\x00" * 256
    open(p("alignstr.gguf"), "wb").write(b)
    # 10 n_dims = 5
    build(p("dims5.gguf"), infos=[tensor_info("blk.0.weight", 5, [8, 8, 1, 1, 1], 0, 0)])
    # 11 quantized (Q4_0, blk 32) tensor with ne[0] not a multiple of 32
    build(p("ne0mod.gguf"), infos=[tensor_info("blk.0.weight", 2, [33, 8], 2, 0)],
          data=b"\x00" * (1 * 8 * 18))
    # 12 tensor offset gap (off=64 instead of 0)
    build(p("gap.gguf"), infos=[tensor_info("blk.0.weight", 2, [8, 8], 0, 64)],
          data=b"\x00" * (64 + 256))
    # 13 tensor data past EOF (ne 16x8 F32 = 512B but only 256B present)
    build(p("pasteof.gguf"), infos=[tensor_info("blk.0.weight", 2, [16, 8], 0, 0)],
          data=b"\x00" * 256)
    # 14 duplicate tensor names (loader rejects; probe skips)
    build(p("duptensor.gguf"),
          infos=[tensor_info("blk.0.weight", 2, [8, 8], 0, 0),
                 tensor_info("blk.0.weight", 2, [8, 8], 0, 256)],
          data=b"\x00" * 512)
    # 15 empty KV key (loader rejects; probe skips)
    build(p("emptykey.gguf"),
          kvs=[lambda x: kv_str(x, "general.architecture", "stories"),
               lambda x: w_str(x, "") + struct.pack("<I", T_U32) + struct.pack("<I", 1)])
    # 16 nested array KV (loader rejects inner ARRAY; probe skips recursively)
    build(p("nestedarr.gguf"),
          kvs=[lambda x: kv_str(x, "general.architecture", "stories"),
               lambda x: kv_arr_of_arr(x, "tester.test.nested")])
    # 17 tensor name >= GGML_MAX_NAME (64) (loader rejects; probe skips)
    build(p("longname.gguf"), infos=[tensor_info("n" * 64, 2, [8, 8], 0, 0)])
    # 18 tensor type 44 (>= GGML_TYPE_COUNT 44; loader rejects range; probe "-")
    build(p("type44.gguf"), infos=[tensor_info("blk.0.weight", 2, [8, 8], 44, 0)])
    # 19 tensor type 4 (legacy removed Q4_2; loader blck_size 0 -> reject; probe "-")
    build(p("type4.gguf"), infos=[tensor_info("blk.0.weight", 2, [32, 8], 4, 0)],
          data=b"\x00" * (8 * 18))
    # 20 zero-dim quantized tensor (probe nd=0 -> ne=[1], 1 % 32 -> invalid; loader same)
    build(p("zerodim.gguf"), infos=[tensor_info("blk.0.weight", 0, [], 2, 0)],
          data=b"\x00" * 18)
    # 21 near-end truncation: drop the last 8 bytes of a minimal valid file
    # (tensor claims 256 bytes; file provides data_start+248)
    build(p("truncnear.gguf"))
    with open(p("truncnear.gguf"), "r+b") as f:
        f.seek(-8, os.SEEK_END)
        f.truncate()
    # 25 second clean copy used as a loadable companion entry
    build(p("valid2.gguf"))
    # 22 header cut at 6 bytes (version short read)
    with open(p("cut6.gguf"), "wb") as f:
        f.write(b"GGUF" + struct.pack("<H", 3))
    # 23 non-GGUF text file
    with open(p("notgguf.txt"), "wb") as f:
        f.write(b"this is not a gguf model file\n" * 8)
    # 24 huge counts that cannot fit (n_kv*13 > size) -> invalid both sides
    build(p("hugekv.gguf"), kvs=[])
    with open(p("hugekv.gguf"), "r+b") as f:
        f.seek(12)  # n_kv field offset: magic(4)+ver(4)+n_tensors(8)... n_kv at 16
        f.seek(16)
        f.write(struct.pack("<Q", 1 << 40))
    print("fixtures written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
