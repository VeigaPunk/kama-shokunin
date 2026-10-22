#!/usr/bin/env python3
"""Read-only GGUF scan: print the KV header only (no tensor data).

Prints general.architecture and every metadata key ending in context_length.
Usage: python3 gguf_ctx_keys.py <file.gguf>
"""
import struct
import sys

SCALAR = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "?", 10: "Q", 11: "q", 12: "d"}


def main(path: str) -> int:
    with open(path, "rb") as f:
        def rd(fmt: str):
            return struct.unpack("<" + fmt, f.read(struct.calcsize("<" + fmt)))[0]

        def rstr() -> str:
            n = rd("Q")
            return f.read(n).decode("utf-8", errors="replace")

        def rval(t: int):
            if t in SCALAR:
                return rd(SCALAR[t])
            if t == 8:
                return rstr()
            if t == 9:
                et = rd("I")
                n = rd("Q")
                if et in SCALAR:
                    fmt = "<" + SCALAR[et] * n
                    return list(struct.unpack(fmt, f.read(struct.calcsize(fmt))))
                if et == 8:
                    return [rstr() for _ in range(n)]
                raise ValueError(f"unsupported array element type {et}")
            raise ValueError(f"unknown gguf value type {t}")

        magic = f.read(4)
        if magic != b"GGUF":
            print(f"not a GGUF file: magic={magic!r}")
            return 2
        version = rd("I")
        tensor_count = rd("Q")
        kv_count = rd("Q")
        print(f"gguf_version={version} tensor_count={tensor_count} kv_count={kv_count}")
        arch = None
        hits = []
        for _ in range(kv_count):
            key = rstr()
            t = rd("I")
            val = rval(t)
            if key == "general.architecture":
                arch = val
            if key.endswith("context_length"):
                hits.append((key, val))
        print(f"general.architecture={arch}")
        for key, val in hits:
            print(f"{key}={val}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
