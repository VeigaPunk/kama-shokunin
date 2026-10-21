#!/usr/bin/env python3
"""Read bounded GGUF headers and metadata without parsing tensor payloads.

Usage: gguf-identity.py FILE [--json] [--max-kv N] [--max-str BYTES]
       gguf-identity.py --selftest

The digest is streamed over the complete file; structural decoding stops after
all metadata key/value pairs, before tensor descriptors or tensor data. Arrays
are validated recursively and summarized as element type plus length. JSON
contains only recognized model-identity keys and array summaries.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import stat
import struct
import sys
from dataclasses import dataclass
from typing import BinaryIO

DEFAULT_MAX_KV = 1_000_000
DEFAULT_MAX_STR = 16 * 1024 * 1024
MAX_ARRAY_LENGTH = 1_000_000
MAX_TOTAL_ARRAY_ITEMS = 4_000_000
MAX_ARRAY_DEPTH = 32
HASH_CHUNK = 1024 * 1024
MAGIC = b"GGUF"
TYPE_NAMES = {
    0: "UINT8",
    1: "INT8",
    2: "UINT16",
    3: "INT16",
    4: "UINT32",
    5: "INT32",
    6: "FLOAT32",
    7: "BOOL",
    8: "STRING",
    9: "ARRAY",
    10: "UINT64",
    11: "INT64",
    12: "FLOAT64",
}
SCALARS = {
    0: ("B", 1),
    1: ("b", 1),
    2: ("H", 2),
    3: ("h", 2),
    4: ("I", 4),
    5: ("i", 4),
    6: ("f", 4),
    7: ("B", 1),
    10: ("Q", 8),
    11: ("q", 8),
    12: ("d", 8),
}
STATIC_IDENTITY_KEYS = (
    "general.architecture",
    "general.name",
    "general.file_type",
    "general.alignment",
    "tokenizer.ggml.model",
)
ARCH_IDENTITY_SUFFIXES = (
    "context_length",
    "block_count",
    "embedding_length",
)


class DecodeError(Exception):
    """A stable, named malformed-or-unsupported GGUF condition."""

    def __init__(self, reason: str, exit_code: int = 2) -> None:
        super().__init__(reason)
        self.reason = reason
        self.exit_code = exit_code


@dataclass(frozen=True)
class ArraySummary:
    element_type: str
    length: int

    def as_json(self) -> dict[str, object]:
        return {"type": self.element_type, "length": self.length}


class Reader:
    """A size-bounded stream reader for GGUF metadata fields."""

    __slots__ = (
        "stream", "size", "offset", "endian", "max_str", "array_budget"
    )

    def __init__(self, stream: BinaryIO, size: int, max_str: int) -> None:
        self.stream = stream
        self.size = size
        self.offset = 0
        self.endian = "<"
        self.max_str = max_str
        self.array_budget = MAX_TOTAL_ARRAY_ITEMS

    def read_exact(self, count: int, context: str) -> bytes:
        if count < 0 or self.offset + count > self.size:
            raise DecodeError(f"truncated_{context}")
        first = self.stream.read(count)
        if len(first) == count:
            self.offset += count
            return first
        data = bytearray(first)
        remaining = count - len(first)
        while remaining:
            chunk = self.stream.read(remaining)
            if not chunk:
                self.offset += len(data)
                raise DecodeError(f"truncated_{context}")
            data.extend(chunk)
            remaining -= len(chunk)
        self.offset += count
        return bytes(data)

    def skip(self, count: int, context: str) -> None:
        if count < 0 or self.offset + count > self.size:
            raise DecodeError(f"truncated_{context}")
        try:
            self.stream.seek(count, os.SEEK_CUR)
        except OSError:
            raise
        self.offset += count

    def unpack(self, fmt: str, context: str) -> int | float:
        full_fmt = self.endian + fmt
        size = struct.calcsize(full_fmt)
        return struct.unpack(full_fmt, self.read_exact(size, context))[0]

    def u32(self, context: str) -> int:
        return int(self.unpack("I", context))

    def u64(self, context: str) -> int:
        return int(self.unpack("Q", context))

    def read_string(self, context: str) -> str:
        byte_count = self.u64(f"{context}_length")
        if byte_count > self.max_str:
            raise DecodeError("string_too_large")
        raw = self.read_exact(byte_count, context)
        try:
            return raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            raise DecodeError("invalid_utf8")

    def value(self, type_id: int, *, capture: bool, depth: int = 0):
        if type_id not in TYPE_NAMES:
            raise DecodeError("unknown_value_type")
        if type_id == 8:
            value = self.read_string("string_value")
            return value if capture else None
        if type_id == 9:
            if depth >= MAX_ARRAY_DEPTH:
                raise DecodeError("array_nesting_too_deep")
            element_type = self.u32("array_element_type")
            if element_type not in TYPE_NAMES:
                raise DecodeError("unknown_value_type")
            length = self.u64("array_length")
            if length > MAX_ARRAY_LENGTH:
                raise DecodeError("array_too_large")
            if length > self.array_budget:
                raise DecodeError("array_item_budget_exceeded")
            self.array_budget -= length

            scalar = SCALARS.get(element_type)
            if scalar is not None:
                _, scalar_size = scalar
                byte_count = length * scalar_size
                if element_type == 7:
                    remaining = byte_count
                    while remaining:
                        chunk_size = min(remaining, 64 * 1024)
                        chunk = self.read_exact(chunk_size, "array_values")
                        if any(byte not in (0, 1) for byte in chunk):
                            raise DecodeError("invalid_bool")
                        remaining -= chunk_size
                else:
                    self.skip(byte_count, "array_values")
            else:
                for _ in range(length):
                    self.value(element_type, capture=False, depth=depth + 1)
            return ArraySummary(TYPE_NAMES[element_type], length)

        scalar = SCALARS.get(type_id)
        if scalar is None:
            raise DecodeError("unknown_value_type")
        fmt, scalar_size = scalar
        raw = self.read_exact(scalar_size, "value")
        if type_id == 7:
            value = raw[0]
            if value not in (0, 1):
                raise DecodeError("invalid_bool")
            decoded: int | float | bool = bool(value)
        else:
            decoded = struct.unpack(self.endian + fmt, raw)[0]
        return decoded if capture else None


def is_identity_candidate(key: str) -> bool:
    return (key in STATIC_IDENTITY_KEYS
            or any(key.endswith("." + suffix)
                   for suffix in ARCH_IDENTITY_SUFFIXES))


def decode_metadata(stream: BinaryIO, size: int, *,
                    max_kv: int = DEFAULT_MAX_KV,
                    max_str: int = DEFAULT_MAX_STR) -> dict[str, object]:
    reader = Reader(stream, size, max_str)
    if reader.read_exact(4, "magic") != MAGIC:
        raise DecodeError("bad_magic", exit_code=1)

    raw_version = reader.read_exact(4, "version")
    little_version = struct.unpack("<I", raw_version)[0]
    big_version = struct.unpack(">I", raw_version)[0]
    if little_version in (2, 3):
        version = little_version
        reader.endian = "<"
        endianness = "little"
    elif big_version == 3:
        version = big_version
        reader.endian = ">"
        endianness = "big"
    else:
        raise DecodeError("unsupported_version")

    tensor_count = reader.u64("tensor_count")
    kv_count = reader.u64("kv_count")
    if kv_count > max_kv:
        raise DecodeError("kv_count_too_large")

    seen: set[str] = set()
    candidates: dict[str, object] = {}
    arrays: dict[str, ArraySummary] = {}
    for _ in range(kv_count):
        key = reader.read_string("key")
        if key in seen:
            raise DecodeError("duplicate_key")
        seen.add(key)
        type_id = reader.u32("value_type")
        capture = is_identity_candidate(key)
        value = reader.value(type_id, capture=capture)
        if capture:
            candidates[key] = value
        if type_id == 9:
            if not isinstance(value, ArraySummary):
                raise DecodeError("internal_array_summary_error")
            arrays[key] = value

    keys: dict[str, object] = {
        key: json_safe(candidates.get(key)) for key in STATIC_IDENTITY_KEYS
    }
    architecture = candidates.get("general.architecture")
    if isinstance(architecture, str) and architecture:
        for suffix in ARCH_IDENTITY_SUFFIXES:
            key = f"{architecture}.{suffix}"
            keys[key] = json_safe(candidates.get(key))

    return {
        "version": version,
        "endianness": endianness,
        "tensor_count": tensor_count,
        "kv_count": kv_count,
        "keys": keys,
        "arrays": {
            key: summary.as_json() for key, summary in sorted(arrays.items())
        },
    }


def json_safe(value):
    if isinstance(value, ArraySummary):
        return value.as_json()
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return "NaN"
        return "Infinity" if value > 0 else "-Infinity"
    return value


def stream_sha256(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    while True:
        chunk = stream.read(HASH_CHUNK)
        if not chunk:
            break
        digest.update(chunk)
    return digest.hexdigest()


def inspect_path(path: str, *, max_kv: int, max_str: int) -> dict[str, object]:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise OSError("not a regular file")
        size = before.st_size
        with os.fdopen(fd, "rb", buffering=0, closefd=False) as stream:
            digest = stream_sha256(stream)
            after = os.fstat(fd)
            if after.st_size != size:
                raise OSError("file size changed during read")
            stream.seek(0)
            decoded = decode_metadata(stream, size, max_kv=max_kv,
                                      max_str=max_str)
        return {"path": path, "size": size, "sha256": digest, **decoded}
    finally:
        os.close(fd)


def pack_string(value: str, endian: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack(endian + "Q", len(raw)) + raw


def pack_value(type_id: int, value, endian: str) -> bytes:
    if type_id == 8:
        return pack_string(value, endian)
    if type_id == 9:
        element_type, values = value
        return (struct.pack(endian + "IQ", element_type, len(values))
                + b"".join(pack_value(element_type, item, endian)
                           for item in values))
    fmt = SCALARS[type_id][0]
    if type_id == 7:
        value = int(value)
    return struct.pack(endian + fmt, value)


def fixture(entries: list[tuple[str, int, object]], *, version: int = 3,
            endian: str = "<", tensor_count: int = 1) -> bytes:
    return (MAGIC + struct.pack(endian + "IQQ", version, tensor_count,
                                 len(entries))
            + b"".join(pack_string(key, endian)
                       + struct.pack(endian + "I", type_id)
                       + pack_value(type_id, value, endian)
                       for key, type_id, value in entries))


def run_selftest() -> tuple[dict[str, object], int]:
    failures: list[dict[str, str]] = []
    names: list[str] = []

    def check(name: str, data: bytes, expected_reason: str | None = None,
              *, max_kv: int = DEFAULT_MAX_KV,
              max_str: int = DEFAULT_MAX_STR,
              expected_exit: int | None = None) -> None:
        names.append(name)
        if expected_exit is None:
            expected_exit = (1 if expected_reason == "bad_magic"
                             else 2 if expected_reason is not None else 0)
        try:
            got = decode_metadata(io.BytesIO(data), len(data),
                                  max_kv=max_kv, max_str=max_str)
        except DecodeError as exc:
            if exc.reason != expected_reason or exc.exit_code != expected_exit:
                failures.append({
                    "case": name,
                    "expected": expected_reason or "success",
                    "expected_exit": str(expected_exit),
                    "observed": exc.reason,
                    "observed_exit": str(exc.exit_code),
                })
        else:
            if expected_reason is not None or expected_exit != 0:
                failures.append({"case": name, "expected": expected_reason or
                                 f"exit_{expected_exit}", "observed": "success"})
            elif name == "valid_v3_little_all_types":
                if (got["version"], got["endianness"], got["tensor_count"],
                    got["kv_count"]) != (3, "little", 1, len(all_types)):
                    failures.append({"case": name, "expected": "header_values",
                                     "observed": "incorrect_header_values"})
                expected_keys = {
                    "general.architecture": "llama",
                    "general.name": "fixture-model",
                    "general.file_type": 15,
                    "general.alignment": 32,
                    "tokenizer.ggml.model": "fixture-tokenizer",
                    "llama.context_length": 2048,
                    "llama.block_count": 16,
                    "llama.embedding_length": 128,
                }
                if any(got["keys"].get(key) != value
                       for key, value in expected_keys.items()):
                    failures.append({"case": name, "expected": "identity_values",
                                     "observed": "identity_mismatch"})
                if got["arrays"].get("fixture.nested") != {
                        "type": "ARRAY", "length": 2}:
                    failures.append({"case": name, "expected": "nested_array_summary",
                                     "observed": "array_summary_mismatch"})
            elif name == "valid_v2_little_endian":
                if (got["version"], got["endianness"], got["tensor_count"],
                    got["keys"].get("general.architecture")) != (
                        2, "little", 7, "llama"):
                    failures.append({"case": name, "expected": "v2_little_endian_header",
                                     "observed": "header_mismatch"})
            elif name == "valid_v3_big_endian":
                if (got["version"], got["endianness"], got["tensor_count"],
                    got["keys"].get("general.architecture")) != (
                        3, "big", 8, "llama"):
                    failures.append({"case": name, "expected": "v3_big_endian_header",
                                     "observed": "header_mismatch"})

    all_types = [
        ("general.architecture", 8, "llama"),
        ("general.name", 8, "fixture-model"),
        ("general.file_type", 4, 15),
        ("general.alignment", 4, 32),
        ("tokenizer.ggml.model", 8, "fixture-tokenizer"),
        ("llama.context_length", 4, 2048),
        ("llama.block_count", 4, 16),
        ("llama.embedding_length", 4, 128),
        ("fixture.u8", 0, 255),
        ("fixture.i8", 1, -2),
        ("fixture.u16", 2, 65530),
        ("fixture.i16", 3, -1234),
        ("fixture.u32", 4, 4294967295),
        ("fixture.i32", 5, -123456),
        ("fixture.f32", 6, 1.25),
        ("fixture.bool", 7, True),
        ("fixture.string", 8, "valid-λ"),
        ("fixture.u64", 10, 18446744073709551615),
        ("fixture.i64", 11, -1234567890123),
        ("fixture.f64", 12, -2.5),
        ("fixture.array", 9, (3, [1, -2, 300])),
        ("fixture.strings", 9, (8, ["", "hello", "λ"])),
        ("fixture.nested", 9, (9, [
            (0, [0, 255]),
            (9, [(8, ["nested", "array"])]),
        ])),
    ]
    check("valid_v3_little_all_types", fixture(all_types))
    check("valid_v2_little_endian", fixture(
        [("general.architecture", 8, "llama"),
         ("llama.context_length", 10, 4096)],
        version=2, endian="<", tensor_count=7))
    check("valid_v3_big_endian", fixture(
        [("general.architecture", 8, "llama"),
         ("llama.context_length", 10, 4096)],
        version=3, endian=">", tensor_count=8))
    check("v2_big_endian_unsupported", fixture(
        [("general.architecture", 8, "llama")],
        version=2, endian=">"), "unsupported_version")

    valid = fixture([("general.name", 8, "valid")])
    check("tensor_tail_is_not_parsed", valid + b"\xff\x00tensor-payload")
    check("bad_magic", b"NOPE" + b"\0" * 20, "bad_magic", expected_exit=1)
    check("truncated_header", b"GGUF\x03\0", "truncated_version")
    check("unsupported_version", MAGIC + struct.pack("<I", 4) + b"\0" * 16,
          "unsupported_version")
    check("truncated_key", MAGIC + struct.pack("<IQQ", 3, 0, 1)
          + struct.pack("<Q", 4) + b"ab", "truncated_key")
    unknown_type = (MAGIC + struct.pack("<IQQ", 3, 0, 1)
                    + pack_string("unknown", "<") + struct.pack("<I", 99))
    check("unknown_type", unknown_type, "unknown_value_type")
    check("duplicate_key", fixture([("same", 4, 1), ("same", 4, 2)]),
          "duplicate_key")
    invalid_utf8 = (MAGIC + struct.pack("<IQQ", 3, 0, 1)
                    + struct.pack("<Q", 1) + b"k"
                    + struct.pack("<I", 8) + struct.pack("<Q", 1) + b"\xff")
    check("invalid_utf8", invalid_utf8, "invalid_utf8")
    check("string_bound", fixture([("long", 8, "abc")]),
          "string_too_large", max_str=2)
    check("kv_bound", fixture([("one", 4, 1), ("two", 4, 2)]),
          "kv_count_too_large", max_kv=1)
    array_bound = (MAGIC + struct.pack("<IQQ", 3, 0, 1)
                   + pack_string("large", "<") + struct.pack("<IIQ", 9, 0,
                                                               MAX_ARRAY_LENGTH + 1))
    check("array_bound", array_bound, "array_too_large")
    nested = (8, ["bottom"])
    for _ in range(MAX_ARRAY_DEPTH + 1):
        nested = (9, [nested])
    check("array_depth_bound", fixture([("deep", 9, nested)]),
          "array_nesting_too_deep")
    check("invalid_bool", fixture([("bad-bool", 7, 2)]), "invalid_bool")

    result = {
        "schema": "gguf-identity-selftest/v1",
        "status": "failed" if failures else "passed",
        "case_count": len(names),
        "passed": len(names) - len(failures),
        "failed": failures,
        "cases": names,
    }
    return result, 1 if failures else 0


def nonnegative_integer(value: str) -> int:
    try:
        parsed = int(value, 10)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="GGUF file to inspect")
    parser.add_argument("--json", action="store_true",
                        help="write the complete result as JSON")
    parser.add_argument("--max-kv", type=nonnegative_integer,
                        default=DEFAULT_MAX_KV,
                        help=f"maximum metadata entries (default {DEFAULT_MAX_KV})")
    parser.add_argument("--max-str", type=nonnegative_integer,
                        default=DEFAULT_MAX_STR,
                        help=f"maximum key/string byte length (default {DEFAULT_MAX_STR})")
    parser.add_argument("--selftest", action="store_true",
                        help="run in-memory parser fixtures")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        if args.file is not None:
            parser.error("--selftest does not accept FILE")
        result, exit_code = run_selftest()
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return exit_code
    if args.file is None:
        parser.error("FILE is required unless --selftest is used")

    try:
        result = inspect_path(args.file, max_kv=args.max_kv,
                              max_str=args.max_str)
    except DecodeError as exc:
        print(f"gguf-identity: {exc.reason}", file=sys.stderr)
        return exc.exit_code
    except (OSError, ValueError) as exc:
        reason = "file_unavailable" if isinstance(exc, OSError) else "invalid_file"
        print(f"gguf-identity: {reason}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(f"GGUF v{result['version']} ({result['endianness']} endian)")
        print(f"path: {result['path']}")
        print(f"size: {result['size']}")
        print(f"sha256: {result['sha256']}")
        print(f"tensors: {result['tensor_count']}; metadata entries: {result['kv_count']}")
        print(json.dumps(result["keys"], indent=2, sort_keys=True,
                         allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
