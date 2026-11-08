#!/usr/bin/env python3
"""EX02 independent GGUF-layout re-derivation for the round-97 C2 fixtures.

Parses the raw bytes captured from the counter's own nat work dir (fixtures/), with no
import of the counter and no use of the probe. The step accounting follows the disclosed
probe rule (`4` preamble steps; `5 + nd` per tensor header; KV/string work charged), and
the verdict classes follow the probe's documented constants: MAX_STEPS 5_000_000,
MAX_META 512 MiB, MAX_TENSORS 1_000_000, MAX_ARR 50_000_000, align 32.
"""
import struct
import sys
from pathlib import Path

QSIZES = {0: (1, 4), 1: (1, 2), 2: (32, 18), 3: (32, 20), 6: (32, 22), 7: (32, 24),
          8: (32, 34), 9: (32, 36), 10: (256, 84), 11: (256, 110), 12: (256, 144),
          13: (256, 176), 14: (256, 210), 15: (256, 292), 16: (256, 66), 17: (256, 74),
          18: (256, 98), 19: (256, 50), 20: (32, 18), 21: (256, 110), 22: (256, 82),
          23: (256, 136), 24: (1, 1), 25: (1, 2), 26: (1, 4), 27: (1, 8), 28: (1, 8),
          29: (256, 56), 30: (1, 2), 34: (256, 54), 35: (256, 66), 39: (32, 17),
          40: (64, 36), 41: (128, 18), 42: (64, 18), 43: (1, 1)}
SCALAR = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
MAX_KV, MAX_ARR, MAX_TENSORS, MAX_META = 100_000, 50_000_000, 1_000_000, 512 * 1024 ** 2
MAX_STEPS = 5_000_000


class Bad(Exception):
    pass


class Unknown(Exception):
    pass


def derive(path: Path):
    b = path.read_bytes()
    size = len(b)
    pos = 0
    steps = 0
    detail = {}

    def need(n):
        nonlocal steps, pos
        steps += 1
        if steps > MAX_STEPS:
            raise Unknown("MAX_STEPS")
        if pos > MAX_META:
            raise Unknown("MAX_META")
        if n < 0 or pos + n > size:
            raise Bad(f"short read at {pos}+{n}>{size}")

    def rd(n):
        nonlocal pos
        need(n)
        out = b[pos:pos + n]
        if len(out) != n:
            raise Bad("short")
        pos += n
        return out

    def skip(n):
        nonlocal pos
        need(n)
        pos += n

    def u32():
        return struct.unpack("<I", rd(4))[0]

    def u64():
        return struct.unpack("<Q", rd(8))[0]

    def skip_value(t, depth=0):
        if t in SCALAR:
            skip(SCALAR[t])
        elif t == 8:
            skip(u64())
        elif t == 9:
            if depth > 8:
                raise Unknown("array depth")
            et, n = u32(), u64()
            if n > MAX_ARR:
                raise Unknown("MAX_ARR")
            if et in SCALAR:
                skip(SCALAR[et] * n)
            elif et == 8:
                if pos + 8 * n > size:
                    raise Bad("string array prefixes")
                for _ in range(n):
                    nonlocal_steps()
                    if pos + 8 > size:
                        raise Bad("string prefix")
                    ln = struct.unpack_from("<Q", b, pos)[0]
                    pos += 8 + ln
                    if pos > size:
                        raise Bad("string payload")
                    if pos > MAX_META:
                        raise Unknown("MAX_META string")
            else:
                for _ in range(n):
                    skip_value(et, depth + 1)
        else:
            raise Bad("value type")

    def nonlocal_steps():
        nonlocal steps
        steps += 1
        if steps > MAX_STEPS:
            raise Unknown("MAX_STEPS")

    try:
        if rd(4) != b"GGUF":
            return "invalid", {"why": "magic"}
        ver = u32()
        if ver == 1 or ver > 3 or (ver & 0xFFFF) == 0:
            return "invalid", {"why": f"version {ver}"}
        n_tensors, n_kv = u64(), u64()
        detail.update(n_tensors=n_tensors, n_kv=n_kv, size=size, preamble_steps=steps)
        if n_kv * 13 + n_tensors * 24 > size:
            return "invalid", {**detail, "why": "counts do not fit"}
        if n_kv > MAX_KV or n_tensors > MAX_TENSORS:
            return "-", {**detail, "why": "count cap", "steps_at_return": steps}
        align = 32
        kv_steps = 0
        for _ in range(n_kv):
            before = steps
            klen = u64()
            key = rd(klen) if klen <= 64 else (skip(klen) or b"")
            t = u32()
            if key == b"general.alignment":
                if t != 4:
                    return "invalid", {**detail, "why": "alignment type"}
                align = u32()
                if align == 0 or align & (align - 1):
                    return "invalid", {**detail, "why": "alignment value"}
            else:
                skip_value(t)
            kv_steps += steps - before
        detail["kv_steps"] = kv_steps
        infos = []
        header_steps = 0
        nds = set()
        for i in range(n_tensors):
            before = steps
            skip(u64())  # name length, skip name bytes
            nd = u32()
            if nd > 4:
                return "invalid", {**detail, "why": f"nd={nd}", "tensor_index": i}
            nds.add(nd)
            ne = [u64() for _ in range(nd)] or [1]
            tt, off = u32(), u64()
            header_steps += steps - before
            if tt not in QSIZES:
                return "-", {**detail, "why": f"unknown tensor type {tt}", "tensor_index": i,
                             "steps_at_return": steps}
            blk, tsz = QSIZES[tt]
            if ne[0] % blk:
                return "invalid", {**detail, "why": "block size", "tensor_index": i}
            n = 1
            for d in ne:
                n *= d
            infos.append((off, n // blk * tsz))
        detail["header_steps"] = header_steps
        detail["nd_values"] = sorted(nds)
        detail["steps_per_header"] = (header_steps / n_tensors) if n_tensors else None
        start = (pos + align - 1) // align * align
        expect = 0
        for i, (off, nbytes) in enumerate(infos):
            if off != expect:
                return "invalid", {**detail, "why": f"offset {off} != expect {expect} on tensor {i}",
                                   "steps_at_return": steps}
            if start + off + nbytes > size:
                return "invalid", {**detail, "why": f"data beyond EOF on tensor {i}: "
                                   f"{start}+{off}+{nbytes}>{size}", "steps_at_return": steps}
            expect += (nbytes + align - 1) // align * align
        return "ok", {**detail, "steps_at_return": steps}
    except Bad as e:
        return "invalid", {**detail, "why": f"Bad: {e}", "steps_at_return": steps}
    except Unknown as e:
        return "-", {**detail, "why": f"Unknown: {e}", "steps_at_return": steps}


def main():
    fx = Path(sys.argv[1])
    designed = {"t900k.gguf": "-", "mid4.gguf": "-", "maxmeta.gguf": "invalid",
                "t833333.gguf": "-"}
    agree = True
    for name, want in designed.items():
        cls, d = derive(fx / name)
        ok = cls == want
        agree &= ok
        print(f"ORACLE {name} designed={want} derived={cls} agree={int(ok)} {d}")
    # Arithmetic cross-check against the plan's stated boundaries.
    print("ARITH t900k  steps=4+900000*(5+1) =", 4 + 900_000 * 6)
    print("ARITH mid4   steps=4+700000*(5+4) =", 4 + 700_000 * 9)
    print("ARITH edge   steps=4+833333*(5+1) =", 4 + 833_333 * 6)
    print("ARITH edge-1 steps=4+833332*(5+1) =", 4 + 833_332 * 6)
    print("ARITH maxmeta preamble 4 + KV 5 + header (5+1) =", 4 + 5 + 6)
    return 0 if agree else 1


if __name__ == "__main__":
    sys.exit(main())
