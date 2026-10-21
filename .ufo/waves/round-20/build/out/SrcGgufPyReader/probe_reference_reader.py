#!/usr/bin/env python3
"""Probe llama.cpp's gguf-py GGUFReader (the C2 oracle) on synthetic GGUF headers.

Read-only seat helper (round 20, SrcGgufPyReader). Imports whichever `gguf` package is
on sys.path (PyPI wheel via `uv run --with gguf`, or a pinned gguf-py checkout via
PYTHONPATH), prints its identity, then one line per synthetic case: OK with the
reader's byte_order/endianess/version and decoded identity keys, or the exception
class and message. Optional argv[1]: a real GGUF file to read (memmap mode 'r').
Synthetic files live in a temporary directory that is removed before exit.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import os
import shutil
import struct
import sys
import tempfile

import gguf
from gguf.gguf_reader import GGUFReader

IDENTITY_KEYS = (
    "general.architecture", "general.name", "general.file_type", "general.alignment",
    "tokenizer.ggml.model",
)
ARCH_KEYS = ("context_length", "block_count", "embedding_length")


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def gstr(o: str, s: bytes) -> bytes:
    return struct.pack(o + "Q", len(s)) + s


def kv_str(o: str, key: str, val: str) -> bytes:
    return gstr(o, key.encode()) + struct.pack(o + "I", 8) + gstr(o, val.encode())


def kv_u32(o: str, key: str, val: int) -> bytes:
    return gstr(o, key.encode()) + struct.pack(o + "I", 4) + struct.pack(o + "I", val)


def kv_u64(o: str, key: str, val: int) -> bytes:
    return gstr(o, key.encode()) + struct.pack(o + "I", 10) + struct.pack(o + "Q", val)


def header(o: str, version: int, kvs: list[bytes], magic: bytes = b"GGUF",
           tensors: tuple[bytes, ...] = (), data: bytes = b"", n_kv: int | None = None) -> bytes:
    body = (magic + struct.pack(o + "I", version)
            + struct.pack(o + "QQ", len(tensors), len(kvs) if n_kv is None else n_kv)
            + b"".join(kvs) + b"".join(tensors))
    if tensors:  # pad to the default 32-byte alignment, then the tensor data
        body += b"\0" * (-len(body) % 32) + data
    return body


def tensor_info(o: str, name: str, dims: tuple[int, ...], ggml_type: int = 0) -> bytes:
    return (gstr(o, name.encode()) + struct.pack(o + "I", len(dims))
            + b"".join(struct.pack(o + "Q", d) for d in dims) + struct.pack(o + "I", ggml_type)
            + struct.pack(o + "Q", 0))


def ident_kvs(o: str) -> list[bytes]:
    return [kv_str(o, "general.architecture", "llama"), kv_u32(o, "llama.context_length", 128),
            kv_u32(o, "general.file_type", 0)]


def field_value(field) -> object:
    if hasattr(field, "contents"):
        return field.contents()
    return field.parts[field.data[0]].tolist()  # pre-contents() wheels


def describe(reader: GGUFReader) -> str:
    out = [f"byte_order={reader.byte_order}", f"endianess={reader.endianess.name}",
           f"version={int(reader.fields['GGUF.version'].parts[0][0])}",
           f"tensor_count={int(reader.fields['GGUF.tensor_count'].parts[0][0])}",
           f"kv_count={int(reader.fields['GGUF.kv_count'].parts[0][0])}",
           f"alignment={int(reader.alignment)}"]
    arch_field = reader.get_field("general.architecture")
    arch = field_value(arch_field) if arch_field is not None else None
    keys = list(IDENTITY_KEYS) + ([f"{arch}.{k}" for k in ARCH_KEYS] if arch else [])
    for key in keys:
        field = reader.get_field(key)
        if field is not None:
            out.append(f"{key}={field_value(field)!r}:{'/'.join(t.name for t in field.types)}")
    return " ".join(out)


CASES: list[tuple[str, bytes]] = [
    ("le_v3_empty", header("<", 3, [])),
    ("be_v3_empty", header(">", 3, [])),
    ("le_v2_empty", header("<", 2, [])),
    ("le_v1_empty", header("<", 1, [])),
    ("le_v4_empty", header("<", 4, [])),
    ("le_v0_empty", header("<", 0, [])),
    ("le_v3_hi16_set", header("<", 0x00010003, [])),
    ("bad_magic", header("<", 3, [], magic=b"GGUG")),
    ("magic_bytes_reversed", header("<", 3, [], magic=b"FUGG")),
    ("le_v3_identity", header("<", 3, ident_kvs("<"))),
    ("be_v3_identity", header(">", 3, ident_kvs(">"))),
    ("le_v3_align_64", header("<", 3, [kv_u32("<", "general.alignment", 64)])),
    ("le_v3_align_3", header("<", 3, [kv_u32("<", "general.alignment", 3)])),
    ("le_v3_align_u64", header("<", 3, [kv_u64("<", "general.alignment", 32)])),
    ("le_v3_dup_key", header("<", 3, [kv_u32("<", "general.file_type", 0)] * 2)),
    ("le_v3_type_13", header("<", 3, [gstr("<", b"k") + struct.pack("<I", 13)])),
    ("truncated_6B", b"GGUF\x03\x00"),
    ("empty_0B", b""),
    # bound checks present at 704366d76 but absent from the PyPI gguf 0.19.0 wheel
    ("le_v3_kv_count_2p31", header("<", 3, [], n_kv=2**31)),
    ("le_v3_key_len_past_eof", header("<", 3, [], n_kv=1) + struct.pack("<Q", 1000) + b"abcde"),
    ("le_v3_tensor_5_dims", header("<", 3, [], tensors=(tensor_info("<", "t", (1, 1, 1, 1, 1)),),
                                   data=struct.pack("<f", 1.0))),
    # declared u8 array length 1000, only 2 element bytes present before EOF
    ("le_v3_u8_array_past_eof", header("<", 3, [], n_kv=1) + gstr("<", b"general.tags")
     + struct.pack("<IIQ", 9, 0, 1000) + b"\x01\x02"),
]


def main() -> int:
    mod_dir = os.path.dirname(gguf.__file__)
    try:
        dist = importlib.metadata.version("gguf")
    except importlib.metadata.PackageNotFoundError:
        dist = "not-installed-as-dist"
    print(f"gguf dist={dist} path={mod_dir} python={sys.version.split()[0]} host_byteorder={sys.byteorder}")
    for name in ("gguf_reader.py", "constants.py"):
        print(f"module {name} sha256={sha256(os.path.join(mod_dir, name))}")
    tmp = tempfile.mkdtemp(prefix="kama-r20-SrcGgufPyReader-probe-")
    try:
        for name, blob in CASES:
            path = os.path.join(tmp, name + ".gguf")
            with open(path, "wb") as fh:
                fh.write(blob)
            try:
                print(f"case {name} OK {describe(GGUFReader(path, 'r'))}")
            except Exception as exc:  # report the oracle's own outcome verbatim
                print(f"case {name} RAISE {type(exc).__name__}: {exc}")
    finally:
        shutil.rmtree(tmp)
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"real {path} sha256={sha256(path)} {describe(GGUFReader(path, 'r'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
