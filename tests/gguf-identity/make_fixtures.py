#!/usr/bin/env python3
"""Generate small, parser-independent GGUF header fixtures and their oracle manifest.

Binary fields are encoded directly from the GGUF v2/v3 file-structure specification
pinned in expected.json. This module deliberately imports no GGUF implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

SPEC_COMMIT = "da8e2a54b919557b816b1c2beb432ccb766f7ce0"
SPEC_URL = (
    "https://raw.githubusercontent.com/ggml-org/ggml/"
    f"{SPEC_COMMIT}/docs/gguf.md"
)
SPEC_SHA256 = "1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020"
MAGIC = b"GGUF"

# gguf_metadata_value_type enum values from docs/gguf.md:198-228.
TYPE_NAMES = {
    0: "uint8",
    1: "int8",
    2: "uint16",
    3: "int16",
    4: "uint32",
    5: "int32",
    6: "float32",
    7: "bool",
    8: "string",
    9: "array",
    10: "uint64",
    11: "int64",
    12: "float64",
}
SCALAR_FORMATS = {
    0: "B",
    1: "b",
    2: "H",
    3: "h",
    4: "I",
    5: "i",
    6: "f",
    7: "B",
    10: "Q",
    11: "q",
    12: "d",
}


def pack(endian: str, fmt: str, value: int | float) -> bytes:
    return struct.pack(endian + fmt, value)


def gguf_string(value: str | bytes, endian: str) -> bytes:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return pack(endian, "Q", len(raw)) + raw


def encode_value(value_type: int, value: Any, endian: str) -> bytes:
    if value_type == 8:
        return gguf_string(value, endian)
    if value_type == 9:
        element_type, elements = value
        return (
            pack(endian, "I", element_type)
            + pack(endian, "Q", len(elements))
            + b"".join(encode_value(element_type, item, endian) for item in elements)
        )
    if value_type not in SCALAR_FORMATS:
        raise ValueError(f"cannot encode GGUF value type {value_type}")
    if value_type == 7:
        value = int(bool(value))
    return pack(endian, SCALAR_FORMATS[value_type], value)


def kv(key: str | bytes, value_type: int, value: Any, endian: str = "<") -> bytes:
    return gguf_string(key, endian) + pack(endian, "I", value_type) + encode_value(
        value_type, value, endian
    )


def header(
    version: int,
    tensor_count: int,
    kv_count: int,
    *,
    endian: str = "<",
    count_width: str = "Q",
    magic: bytes = MAGIC,
) -> bytes:
    return (
        magic
        + pack(endian, "I", version)
        + pack(endian, count_width, tensor_count)
        + pack(endian, count_width, kv_count)
    )


def valid_file(
    version: int,
    entries: list[tuple[str | bytes, int, Any]],
    *,
    endian: str = "<",
) -> bytes:
    body = b"".join(kv(key, value_type, value, endian) for key, value_type, value in entries)
    return header(version, 0, len(entries), endian=endian) + body


def metadata_summary(entries: list[tuple[str, int, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for key, value_type, value in entries:
        if value_type == 9:
            _, elements = value
            summary[key] = {
                "type": "array",
                "element_type": TYPE_NAMES[value[0]],
                "length": len(elements),
            }
        else:
            summary[key] = {"type": TYPE_NAMES[value_type], "value": value}
    return summary


def make_fixtures() -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []

    def add(
        fixture_id: str,
        data: bytes,
        exit_code: int,
        reason: str,
        description: str,
        *,
        version: int | None = None,
        endianness: str | None = None,
        tensor_count: int | None = None,
        kv_count: int | None = None,
        metadata: dict[str, dict[str, Any]] | None = None,
        basis: str,
    ) -> None:
        if len(data) >= 4096:
            raise ValueError(f"fixture {fixture_id} is not smaller than 4 KiB")
        item: dict[str, Any] = {
            "id": fixture_id,
            "file": f"fixtures/{fixture_id}.gguf",
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "expected_exit": exit_code,
            "expected_reason": reason,
            "description": description,
            "basis": basis,
        }
        if version is not None:
            item["version"] = version
        if endianness is not None:
            item["endianness"] = endianness
        if tensor_count is not None:
            item["tensor_count"] = tensor_count
        if kv_count is not None:
            item["kv_count"] = kv_count
        if metadata is not None:
            item["metadata"] = metadata
        item["_bytes"] = data
        fixtures.append(item)

    valid_basis = "GGUF v2/v3 header and metadata layouts; gguf.md:142-151,198-299,764-780."
    malformed_basis = "Expected fail-closed result from the declared gguf-identity.py tool contract."

    # Structurally valid empty header: magic, v3, uint64 tensor_count=0, uint64 kv_count=0.
    minimal = header(3, 0, 0)
    add(
        "v3-minimal",
        minimal,
        0,
        "decoded",
        "Structurally minimal little-endian v3 header with no tensors or metadata.",
        version=3,
        endianness="little",
        tensor_count=0,
        kv_count=0,
        metadata={},
        basis=valid_basis,
    )

    v2_entries = [
        ("general.architecture", 8, "llama"),
        ("general.name", 8, "fixture-v2"),
        ("llama.context_length", 10, 4096),
    ]
    add(
        "v2-valid",
        valid_file(2, v2_entries),
        0,
        "decoded",
        "Little-endian v2 with three metadata records; v2 uses uint64 count fields.",
        version=2,
        endianness="little",
        tensor_count=0,
        kv_count=len(v2_entries),
        metadata=metadata_summary(v2_entries),
        basis=valid_basis + " v2 uint64 counts: gguf.md:774-776.",
    )

    scalar_entries: list[tuple[str, int, Any]] = [
        ("test.u8", 0, 255),
        ("test.i8", 1, -128),
        ("test.u16", 2, 65535),
        ("test.i16", 3, -32768),
        ("test.u32", 4, 4294967295),
        ("test.i32", 5, -2147483648),
        ("test.f32", 6, 1.5),
        ("test.bool", 7, True),
        ("test.string", 8, "Grüße 🔥"),
        ("test.u64", 10, 18446744073709551615),
        ("test.i64", 11, -9223372036854775808),
        ("test.f64", 12, -2.5),
    ]
    add(
        "v3-all-scalars",
        valid_file(3, scalar_entries),
        0,
        "decoded",
        "One scalar metadata value for every non-array GGUF value type, codes 0-8 and 10-12.",
        version=3,
        endianness="little",
        tensor_count=0,
        kv_count=len(scalar_entries),
        metadata=metadata_summary(scalar_entries),
        basis="GGUF scalar enum and encodings: gguf.md:198-228,231-237.",
    )

    nested_entries: list[tuple[str, int, Any]] = [
        (
            "test.nested",
            9,
            (
                9,
                [
                    (0, [1, 2, 255]),
                    (8, ["a", "β"]),
                ],
            ),
        ),
        ("test.strings", 9, (8, ["", "hello", "λ"])),
        ("test.empty", 9, (5, [])),
    ]
    add(
        "v3-nested-array",
        valid_file(3, nested_entries),
        0,
        "decoded",
        "Nested arrays, nested uint8/string vectors, an empty int32 array and UTF-8 strings.",
        version=3,
        endianness="little",
        tensor_count=0,
        kv_count=len(nested_entries),
        metadata=metadata_summary(nested_entries),
        basis="GGUF arrays may nest; the length counts elements: gguf.md:219-222,252-259.",
    )

    be_entries: list[tuple[str, int, Any]] = [
        ("general.architecture", 8, "llama"),
        ("llama.context_length", 10, 0x0102030405060708),
        ("test.array", 9, (2, [0x1234, 0xABCD])),
    ]
    add(
        "v3-big-endian",
        valid_file(3, be_entries, endian=">") ,
        0,
        "decoded",
        "Big-endian v3; magic remains the literal bytes GGUF and all other fields are big-endian.",
        version=3,
        endianness="big",
        tensor_count=0,
        kv_count=len(be_entries),
        metadata=metadata_summary(be_entries),
        basis="Big-endian encodes all values: gguf.md:151; v3 adds BE: gguf.md:770-772.",
    )

    identity_entries: list[tuple[str, int, Any]] = [
        ("general.architecture", 8, "llama"),
        ("general.name", 8, "fixture-identity"),
        ("llama.context_length", 4, 2048),
        ("llama.block_count", 10, 8),
        ("llama.embedding_length", 10, 64),
        ("general.file_type", 4, 0),
        ("general.alignment", 4, 32),
        ("tokenizer.ggml.model", 8, "llama"),
    ]
    add(
        "v3-identity",
        valid_file(3, identity_entries),
        0,
        "decoded",
        "All eight metadata fields used by the model-identity reader, with mixed integer widths.",
        version=3,
        endianness="little",
        tensor_count=0,
        kv_count=len(identity_entries),
        metadata=metadata_summary(identity_entries),
        basis="Identity key definitions: gguf.md:373-384,388-407,449-453,680-684.",
    )

    for fixture_id, bad_magic in (
        ("bad-magic-near-miss", b"GGUX"),
        ("bad-magic-reversed", b"FUGG"),
    ):
        add(
            fixture_id,
            header(3, 0, 0, magic=bad_magic),
            1,
            "bad_magic",
            f"Invalid magic bytes {bad_magic!r}; remainder is a minimal v3-shaped header.",
            basis="Magic must be the literal bytes GGUF: gguf.md:278-283.",
        )

    for version in (0, 99):
        add(
            f"version-{version}",
            header(version, 0, 0),
            2,
            "unsupported_version",
            f"Little-endian header with unsupported version {version}.",
            version=version,
            endianness="little",
            tensor_count=0,
            kv_count=0,
            basis=malformed_basis + " Tool supports v2/v3 only.",
        )

    # v1 had 32-bit counts; it is explicitly unsupported by the current tool.
    v1 = MAGIC + pack("<", "I", 1) + pack("<", "I", 0) + pack("<", "I", 0)
    add(
        "version-1",
        v1,
        2,
        "unsupported_version",
        "Version 1 shape with its historical uint32 tensor/KV counts.",
        version=1,
        endianness="little",
        tensor_count=0,
        kv_count=0,
        basis="Historical v1: gguf.md:778-780; current tool supports v2/v3 only.",
    )

    partial_tensor_count = MAGIC + pack("<", "I", 3) + b"\x00\x00\x00\x00"
    add(
        "truncated-header",
        partial_tensor_count,
        2,
        "truncated_tensor_count",
        "Valid magic/version followed by only half of the uint64 tensor_count field.",
        basis="Header requires uint64 tensor_count and metadata_kv_count: gguf.md:277-298.",
    )

    trunc_string_key = b"test.truncated"
    trunc_string = (
        header(3, 0, 1)
        + gguf_string(trunc_string_key, "<")
        + pack("<", "I", 8)
        + pack("<", "Q", 8)
        + b"xy"
    )
    add(
        "truncated-string",
        trunc_string,
        2,
        "truncated_string_value",
        "A string declares 8 payload bytes but only 2 remain.",
        basis="String has uint64 byte length and UTF-8 bytes: gguf.md:231-237.",
    )

    huge_string_key = "test.huge"
    huge_string = (
        header(3, 0, 1)
        + gguf_string(huge_string_key, "<")
        + pack("<", "I", 8)
        + pack("<", "Q", (1 << 64) - 1)
    )
    add(
        "string-length-exceeds-file",
        huge_string,
        2,
        "string_too_large",
        "A string declares UINT64_MAX bytes, exceeding both file size and the reader string limit.",
        basis=malformed_basis + " Tool --max-str defaults to 16 MiB; string encoding: gguf.md:231-237.",
    )

    unknown_key = "test.unknown"
    unknown_type = (
        header(3, 0, 1)
        + gguf_string(unknown_key, "<")
        + pack("<", "I", 13)
    )
    add(
        "unknown-value-type-13",
        unknown_type,
        2,
        "unknown_value_type",
        "Metadata value_type is the first unassigned enum value, 13.",
        basis="Only enum codes 0-12 are defined: gguf.md:198-228,270-274.",
    )

    for fixture_id, count in (
        ("kv-count-2pow40", 1 << 40),
        ("kv-count-2pow32-plus1", (1 << 32) + 1),
    ):
        add(
            fixture_id,
            header(3, 0, count),
            2,
            "kv_count_too_large",
            f"v3 metadata_kv_count is {count}; there are no following KV records.",
            version=3,
            endianness="little",
            tensor_count=0,
            kv_count=count,
            basis=malformed_basis + " Count field is uint64: gguf.md:294-298; this parser defaults --max-kv to 100,000.",
        )

    duplicate_key = "test.duplicate"
    duplicate = valid_file(
        3,
        [(duplicate_key, 0, 1), (duplicate_key, 0, 2)],
    )
    add(
        "duplicate-key",
        duplicate,
        2,
        "duplicate_key",
        "Two records use the same key with otherwise valid uint8 values.",
        basis=malformed_basis + " Duplicate keys rejected by assigned tool contract.",
    )

    invalid_key = b"test.\xff"
    non_utf8_key = header(3, 0, 1) + kv(invalid_key, 0, 1)
    add(
        "non-utf8-key",
        non_utf8_key,
        2,
        "invalid_utf8",
        "Key bytes contain an invalid UTF-8 sequence.",
        basis="Keys must be valid ASCII; GGUF strings are UTF-8: gguf.md:231-237,262-267.",
    )

    non_utf8_value = valid_file(3, [("test.bad_utf8", 8, b"\xff")])
    add(
        "non-utf8-value",
        non_utf8_value,
        2,
        "invalid_utf8",
        "String value contains an invalid UTF-8 sequence.",
        basis="GGUF string payloads are UTF-8: gguf.md:231-237.",
    )

    truncated_array = (
        header(3, 0, 1)
        + gguf_string("test.array", "<")
        + pack("<", "I", 9)
        + pack("<", "I", 4)
        + pack("<", "Q", 2)
        + pack("<", "I", 7)
    )
    add(
        "truncated-array-values",
        truncated_array,
        2,
        "truncated_array_values",
        "uint32 array declares two elements but only one element is present.",
        basis="Array length is an element count and all array values follow: gguf.md:219-222,252-259.",
    )

    large_array = (
        header(3, 0, 1)
        + gguf_string("test.array", "<")
        + pack("<", "I", 9)
        + pack("<", "I", 0)
        + pack("<", "Q", 1 << 40)
    )
    add(
        "array-length-exceeds-limit",
        large_array,
        2,
        "array_too_large",
        "uint8 array declares 2^40 elements, above the reader's 1,000,000 element bound.",
        basis=malformed_basis + " Arrays count elements: gguf.md:219-222.",
    )

    nested: Any = (0, [7])
    for _ in range(40):
        nested = (9, [nested])
    deep_array = valid_file(3, [("test.deep", 9, nested)])
    add(
        "array-nesting-exceeds-limit",
        deep_array,
        2,
        "array_nesting_too_deep",
        "Array nesting depth is 40, above the reader's depth bound of 32.",
        basis=malformed_basis + " The tool's bounded nested-array contract; spec permits nesting: gguf.md:219-222.",
    )

    return fixtures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="directory receiving expected.json, SHA256SUMS, and fixtures/",
    )
    args = parser.parse_args()

    out_dir = args.out_dir
    fixture_dir = out_dir / "fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    fixtures = make_fixtures()
    manifest_fixtures = []
    sums = []
    for item in fixtures:
        data = item.pop("_bytes")
        dest = fixture_dir / f"{item['id']}.gguf"
        dest.write_bytes(data)
        manifest_fixtures.append(item)
        sums.append(f"{item['sha256']}  fixtures/{dest.name}")

    manifest = {
        "schema": "kama.gguf-identity-fixtures.v1",
        "specification": {
            "repository": "ggml-org/ggml",
            "commit": SPEC_COMMIT,
            "path": "docs/gguf.md",
            "url": SPEC_URL,
            "sha256": SPEC_SHA256,
        },
        "generator": "make_fixtures.py (Python standard library only; no parser imports)",
        "limits": {
            "maximum_fixture_size_bytes_exclusive": 4096,
            "tool_default_max_kv": 100_000,
            "tool_default_max_string_bytes": 1_048_576,
            "tool_default_max_array_length": 1_000_000,
            "tool_default_max_array_depth": 32,
        },
        "exit_codes": {
            "0": "decoded",
            "1": "not GGUF (bad magic)",
            "2": "malformed or unsupported (named reason)",
            "3": "file unavailable (not exercised by file fixtures)",
        },
        "fixtures": manifest_fixtures,
    }
    (out_dir / "expected.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="ascii")
    print(f"generated {len(manifest_fixtures)} fixtures in {fixture_dir}")
    print(f"wrote {out_dir / 'expected.json'} and {out_dir / 'SHA256SUMS'}")
    for item in manifest_fixtures:
        print(
            f"{item['id']}\t{item['size_bytes']}\t{item['sha256']}"
            f"\texit={item['expected_exit']}\t{item['expected_reason']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
