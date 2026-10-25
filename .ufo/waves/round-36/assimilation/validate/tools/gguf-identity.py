#!/usr/bin/env python3
"""Inspect GGUF identity and optionally reconcile one llama.cpp v3 receipt.

Usage: gguf-identity.py FILE [--json] [--max-kv N] [--max-str BYTES]
                           [--receipt RECEIPT]
       gguf-identity.py --selftest

The parser decodes only the fixed header and metadata KV table. SHA-256 is
streamed over the complete bounded file; tensor descriptors and tensor payloads
are never decoded. Receipt results are explicitly receipt-self-report evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import re
import stat
import struct
import sys
from dataclasses import dataclass
from typing import BinaryIO, Mapping

MAGIC = b"GGUF"
HASH_CHUNK = 1024 * 1024
MAX_FILE_BYTES = 64 * 1024 ** 3
MAX_HASH_BYTES = 32 * 1024 ** 3
MAX_METADATA_BYTES = 64 * 1024 ** 2
MAX_KV_LIMIT = 100_000
MAX_STR_LIMIT = 1024 * 1024
DEFAULT_MAX_KV = 100_000
DEFAULT_MAX_STR = 1024 * 1024
MAX_KEY_BYTES = 65_535
MAX_ARRAY_LENGTH = 1_000_000
MAX_TOTAL_ARRAY_ITEMS = 4_000_000
MAX_ARRAY_DEPTH = 32
MAX_RECEIPT_BYTES = 1024 * 1024
MAX_RECEIPT_BODY_BYTES = 512 * 1024
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 100_000
RECEIPT_SCHEMA_V3 = "kama-llamacpp-live/v3"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
KEY_RE = re.compile(
    r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:_[a-z0-9]+)*)+\Z")
ARCH_RE = re.compile(r"[a-z0-9]+\Z")

TYPE_NAMES = {
    0: "UINT8", 1: "INT8", 2: "UINT16", 3: "INT16",
    4: "UINT32", 5: "INT32", 6: "FLOAT32", 7: "BOOL",
    8: "STRING", 9: "ARRAY", 10: "UINT64", 11: "INT64",
    12: "FLOAT64",
}
SCALARS = {
    0: ("B", 1), 1: ("b", 1), 2: ("H", 2), 3: ("h", 2),
    4: ("I", 4), 5: ("i", 4), 6: ("f", 4), 7: ("B", 1),
    10: ("Q", 8), 11: ("q", 8), 12: ("d", 8),
}
STATIC_IDENTITY_TYPES = {
    "general.architecture": 8,
    "general.name": 8,
    "general.file_type": 4,
    "general.alignment": 4,
    "tokenizer.ggml.model": 8,
}
ARCH_IDENTITY_SUFFIXES = (
    "context_length", "block_count", "embedding_length",
)


class GGUFError(Exception):
    def __init__(self, reason: str, exit_code: int = 2) -> None:
        super().__init__(reason)
        self.reason = reason
        self.exit_code = exit_code


class ReceiptError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class ArraySummary:
    element_type: str
    length: int

    def as_json(self) -> dict[str, object]:
        return {"type": self.element_type, "length": self.length}


class Reader:
    """Size-, string-, array-, and metadata-byte-bounded GGUF reader."""

    __slots__ = ("stream", "size", "offset", "endian", "max_str",
                 "max_metadata_bytes", "array_budget")

    def __init__(self, stream: BinaryIO, size: int, max_str: int,
                 max_metadata_bytes: int = MAX_METADATA_BYTES) -> None:
        self.stream = stream
        self.size = size
        self.offset = 0
        self.endian = "<"
        self.max_str = max_str
        self.max_metadata_bytes = max_metadata_bytes
        self.array_budget = MAX_TOTAL_ARRAY_ITEMS

    def _bounds(self, count: int, context: str) -> None:
        if count < 0 or self.offset + count > self.size:
            raise GGUFError(f"truncated_{context}")
        if self.offset + count > self.max_metadata_bytes:
            raise GGUFError("metadata_byte_budget_exceeded")

    def read_exact(self, count: int, context: str) -> bytes:
        self._bounds(count, context)
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
                raise GGUFError(f"truncated_{context}")
            data.extend(chunk)
            remaining -= len(chunk)
        self.offset += count
        return bytes(data)

    def skip(self, count: int, context: str) -> None:
        self._bounds(count, context)
        self.stream.seek(count, os.SEEK_CUR)
        self.offset += count

    def unpack(self, fmt: str, context: str):
        full_fmt = self.endian + fmt
        return struct.unpack(
            full_fmt, self.read_exact(struct.calcsize(full_fmt), context))[0]

    def u32(self, context: str) -> int:
        return int(self.unpack("I", context))

    def u64(self, context: str) -> int:
        return int(self.unpack("Q", context))

    def read_string(self, context: str, *, key: bool = False) -> str:
        length = self.u64(f"{context}_length")
        limit = min(self.max_str, MAX_KEY_BYTES) if key else self.max_str
        if length > limit:
            raise GGUFError("string_too_large")
        raw = self.read_exact(length, context)
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            raise GGUFError("invalid_utf8") from None
        if key and (not raw.isascii() or KEY_RE.fullmatch(text) is None):
            raise GGUFError("invalid_key")
        return text

    def value(self, type_id: int, *, capture: bool, depth: int = 0):
        if type_id not in TYPE_NAMES:
            raise GGUFError("unknown_value_type")
        if type_id == 8:
            value = self.read_string("string_value")
            return value if capture else None
        if type_id == 9:
            if depth >= MAX_ARRAY_DEPTH:
                raise GGUFError("array_nesting_too_deep")
            element_type = self.u32("array_element_type")
            if element_type not in TYPE_NAMES:
                raise GGUFError("unknown_value_type")
            length = self.u64("array_length")
            if length > MAX_ARRAY_LENGTH:
                raise GGUFError("array_too_large")
            if length > self.array_budget:
                raise GGUFError("array_item_budget_exceeded")
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
                        if any(value not in (0, 1) for value in chunk):
                            raise GGUFError("invalid_bool")
                        remaining -= chunk_size
                else:
                    self.skip(byte_count, "array_values")
            else:
                for _ in range(length):
                    self.value(element_type, capture=False, depth=depth + 1)
            return ArraySummary(TYPE_NAMES[element_type], length)

        scalar = SCALARS.get(type_id)
        if scalar is None:
            raise GGUFError("unknown_value_type")
        fmt, size = scalar
        if not capture and type_id != 7:
            self.skip(size, "value")
            return None
        raw = self.read_exact(size, "value")
        if type_id == 7:
            if raw[0] not in (0, 1):
                raise GGUFError("invalid_bool")
            value = bool(raw[0])
        else:
            value = struct.unpack(self.endian + fmt, raw)[0]
        return value if capture else None


def identity_types(key: str) -> frozenset[int] | None:
    if key in STATIC_IDENTITY_TYPES:
        return frozenset((STATIC_IDENTITY_TYPES[key],))
    if any(key.endswith("." + suffix) for suffix in ARCH_IDENTITY_SUFFIXES):
        # Spec type is UINT64; legacy files (including stories260K) use UINT32.
        return frozenset((4, 10))
    return None


def decode_metadata(stream: BinaryIO, size: int, *,
                    max_kv: int = DEFAULT_MAX_KV,
                    max_str: int = DEFAULT_MAX_STR,
                    max_metadata_bytes: int = MAX_METADATA_BYTES
                    ) -> dict[str, object]:
    reader = Reader(stream, size, max_str, max_metadata_bytes)
    if reader.read_exact(4, "magic") != MAGIC:
        raise GGUFError("bad_magic", exit_code=1)
    raw_version = reader.read_exact(4, "version")
    little_version = struct.unpack("<I", raw_version)[0]
    big_version = struct.unpack(">I", raw_version)[0]
    if little_version in (2, 3):
        version, reader.endian, endian_name = little_version, "<", "little"
    elif big_version == 3:
        version, reader.endian, endian_name = 3, ">", "big"
    else:
        raise GGUFError("unsupported_version")

    tensor_count = reader.u64("tensor_count")
    kv_count = reader.u64("kv_count")
    if kv_count > max_kv:
        raise GGUFError("kv_count_too_large")
    seen: set[str] = set()
    candidates: dict[str, object] = {}
    candidate_types: dict[str, str] = {}
    arrays: dict[str, ArraySummary] = {}
    for _ in range(kv_count):
        key = reader.read_string("key", key=True)
        if key in seen:
            raise GGUFError("duplicate_key")
        seen.add(key)
        type_id = reader.u32("value_type")
        expected_types = identity_types(key)
        if expected_types is not None and type_id not in expected_types:
            raise GGUFError("identity_key_type_mismatch")
        value = reader.value(type_id, capture=expected_types is not None)
        if expected_types is not None:
            candidates[key] = value
            candidate_types[key] = TYPE_NAMES[type_id]
        if type_id == 9:
            if not isinstance(value, ArraySummary):
                raise GGUFError("array_summary_error")
            arrays[key] = value

    architecture = candidates.get("general.architecture")
    if architecture is not None:
        if (not isinstance(architecture, str)
                or ARCH_RE.fullmatch(architecture) is None):
            raise GGUFError("invalid_architecture")
    alignment = candidates.get("general.alignment")
    if alignment is not None and (alignment == 0 or alignment % 8):
        raise GGUFError("invalid_alignment")

    static_keys = tuple(STATIC_IDENTITY_TYPES)
    keys: dict[str, object] = {key: candidates.get(key) for key in static_keys}
    if isinstance(architecture, str):
        for suffix in ARCH_IDENTITY_SUFFIXES:
            name = f"{architecture}.{suffix}"
            keys[name] = candidates.get(name)
    return {
        "version": version,
        "endianness": endian_name,
        "tensor_count": tensor_count,
        "kv_count": kv_count,
        "metadata_bytes": reader.offset,
        "keys": keys,
        "key_types": dict(sorted(candidate_types.items())),
        "arrays": {key: value.as_json()
                   for key, value in sorted(arrays.items())},
    }


def _stat_signature(info) -> tuple[int, int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _open_regular(path: str, *, label: str) -> tuple[int, os.stat_result]:
    flags = (os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        fd = os.open(path, flags)
    except OSError:
        raise OSError(label + "_unavailable") from None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise OSError(label + "_not_regular")
        return fd, info
    except BaseException:
        os.close(fd)
        raise


def _hash_stream(stream: BinaryIO, size: int,
                 max_bytes: int = MAX_HASH_BYTES) -> str:
    if size > max_bytes:
        raise GGUFError("hash_byte_budget_exceeded")
    digest = hashlib.sha256()
    remaining = size
    while remaining:
        chunk = stream.read(min(HASH_CHUNK, remaining))
        if not chunk:
            raise GGUFError("file_changed_during_read")
        digest.update(chunk)
        remaining -= len(chunk)
    return digest.hexdigest()


def inspect_path(path: str, *, max_kv: int, max_str: int) -> dict[str, object]:
    fd, before = _open_regular(path, label="model_file")
    try:
        if before.st_size > MAX_FILE_BYTES:
            raise GGUFError("file_byte_budget_exceeded")
        size = before.st_size
        with os.fdopen(fd, "rb", buffering=0, closefd=False) as stream:
            decoded = decode_metadata(stream, size, max_kv=max_kv,
                                      max_str=max_str)
            if _stat_signature(os.fstat(fd)) != _stat_signature(before):
                raise GGUFError("file_changed_during_read")
            stream.seek(0)
            digest = _hash_stream(stream, size)
            if _stat_signature(os.fstat(fd)) != _stat_signature(before):
                raise GGUFError("file_changed_during_read")
        return {"path": path, "size": size, "sha256": digest, **decoded}
    finally:
        os.close(fd)


def _json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptError("duplicate_json_key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ReceiptError("non_finite_json_number")


def _validate_json_tree(root) -> None:
    stack = [(root, 0)]
    nodes = 0
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise ReceiptError("receipt_json_node_budget_exceeded")
        if depth > MAX_JSON_DEPTH:
            raise ReceiptError("receipt_json_depth_exceeded")
        if isinstance(value, str):
            try:
                size = len(value.encode("utf-8"))
            except UnicodeEncodeError:
                raise ReceiptError("receipt_invalid_unicode") from None
            if size > MAX_RECEIPT_BODY_BYTES:
                raise ReceiptError("receipt_string_too_large")
        elif isinstance(value, dict):
            for key, child in value.items():
                if not isinstance(key, str):
                    raise ReceiptError("receipt_json_invalid_key")
                stack.append((key, depth + 1))
                stack.append((child, depth + 1))
        elif isinstance(value, list):
            stack.extend((child, depth + 1) for child in value)
        elif isinstance(value, float) and not math.isfinite(value):
            raise ReceiptError("non_finite_json_number")


def parse_receipt_bytes(raw: bytes) -> dict[str, object]:
    if len(raw) > MAX_RECEIPT_BYTES:
        raise ReceiptError("receipt_byte_budget_exceeded")
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError:
        raise ReceiptError("receipt_invalid_utf8") from None
    try:
        value = json.loads(text, object_pairs_hook=_json_pairs,
                           parse_constant=_reject_constant)
    except ReceiptError:
        raise
    except (ValueError, RecursionError):
        raise ReceiptError("receipt_invalid_json") from None
    if not isinstance(value, dict):
        raise ReceiptError("receipt_not_object")
    _validate_json_tree(value)
    return value


def load_receipt(path: str) -> dict[str, object]:
    try:
        fd, before = _open_regular(path, label="receipt_file")
    except OSError:
        raise ReceiptError("receipt_file_unavailable") from None
    try:
        if before.st_size > MAX_RECEIPT_BYTES:
            raise ReceiptError("receipt_byte_budget_exceeded")
        raw = bytearray()
        with os.fdopen(fd, "rb", buffering=0, closefd=False) as stream:
            remaining = before.st_size
            while remaining:
                chunk = stream.read(min(64 * 1024, remaining))
                if not chunk:
                    raise ReceiptError("receipt_changed_during_read")
                raw.extend(chunk)
                remaining -= len(chunk)
            if _stat_signature(os.fstat(fd)) != _stat_signature(before):
                raise ReceiptError("receipt_changed_during_read")
        return parse_receipt_bytes(bytes(raw))
    finally:
        os.close(fd)


def _mapping(value, reason: str) -> Mapping:
    if not isinstance(value, dict):
        raise ReceiptError(reason)
    return value


def _string(mapping: Mapping, key: str, reason: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ReceiptError(reason)
    return value


def _positive_int(value, reason: str) -> int:
    if (isinstance(value, bool) or not isinstance(value, int)
            or value <= 0 or value > (1 << 64) - 1):
        raise ReceiptError(reason)
    return value


def _sha256(value, reason: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ReceiptError(reason)
    return value


def could_not_evaluate(reason: str) -> dict[str, object]:
    return {"status": "could-not-evaluate", "exit_code": 2, "reason": reason}


def _reconcile_receipt_checked(decoded: Mapping, file_sha256: str,
                               receipt: Mapping) -> dict[str, object]:
    try:
        document = _mapping(receipt, "receipt_not_object")
        if document.get("schema") != RECEIPT_SCHEMA_V3:
            raise ReceiptError("receipt_schema_unsupported")
        model_sha = _sha256(document.get("model_sha256_post"),
                            "receipt_model_sha256_invalid")
        captures = _mapping(document.get("captures"), "receipt_captures_missing")
        props = _mapping(captures.get("props"), "receipt_props_missing")
        models = _mapping(captures.get("models"), "receipt_models_missing")
        if props.get("status") != 200 or isinstance(props.get("status"), bool):
            raise ReceiptError("props_status_not_200")
        if models.get("status") != 200 or isinstance(models.get("status"), bool):
            raise ReceiptError("models_status_not_200")
        if models.get("body_truncated") is not False:
            raise ReceiptError("models_body_truncated")
        if models.get("body_read_truncated") is not False:
            raise ReceiptError("models_body_read_truncated")
        body = models.get("body")
        if not isinstance(body, str) or not body:
            raise ReceiptError("models_body_missing")
        body_bytes = body.encode("utf-8")
        if len(body_bytes) > MAX_RECEIPT_BODY_BYTES:
            raise ReceiptError("models_body_byte_budget_exceeded")
        body_sha = _sha256(models.get("body_sha256"),
                           "models_body_sha256_invalid")
        observed_body_sha = hashlib.sha256(body_bytes).hexdigest()
        if body_sha != observed_body_sha:
            raise ReceiptError("models_body_sha256_mismatch")
        body_object = parse_receipt_bytes(body_bytes)
        props_fields = _mapping(props.get("fields"), "receipt_props_fields_missing")
        alias = _string(props_fields, "model_alias", "receipt_model_alias_missing")
        configured_alias = _string(document, "alias", "receipt_alias_missing")
        props_n_ctx = _positive_int(
            props_fields.get("default_generation_settings.n_ctx"),
            "receipt_props_n_ctx_missing")
        total_slots = _positive_int(props_fields.get("total_slots"),
                                   "receipt_props_total_slots_missing")
        data = body_object.get("data")
        if not isinstance(data, list):
            raise ReceiptError("models_data_missing")
        if not data:
            raise ReceiptError("models_data_empty")
        if any(not isinstance(item, dict) for item in data):
            raise ReceiptError("models_data_item_invalid")
        if any(not isinstance(item.get("id"), str) or not item["id"]
               for item in data):
            raise ReceiptError("models_data_id_missing")
        matching = [item for item in data if item.get("id") == alias]
        if len(matching) > 1:
            raise ReceiptError("models_alias_ambiguous")
        meta = None
        if matching:
            meta = _mapping(matching[0].get("meta"), "models_meta_missing")
    except ReceiptError as exc:
        return could_not_evaluate(exc.reason)

    actual_sha = _sha256(file_sha256, "decoded_file_sha256_invalid")
    if actual_sha != model_sha:
        return {
            "status": "identity-mismatch",
            "exit_code": 1,
            "reason": "model_sha256_post_mismatch",
            "file_sha256": actual_sha,
            "model_sha256_post": model_sha,
        }
    if configured_alias != alias:
        return {"status": "engine-mismatch", "exit_code": 1,
                "reason": "receipt_alias_disagrees_with_props"}
    if not matching:
        return {"status": "engine-mismatch", "exit_code": 1,
                "reason": "served_model_id_does_not_match_alias"}

    keys = _mapping(decoded.get("keys"), "decoded_identity_keys_missing")
    arrays = _mapping(decoded.get("arrays"), "decoded_array_summaries_missing")
    architecture = _string(keys, "general.architecture",
                           "gguf_architecture_missing")
    declared_context = _positive_int(
        keys.get(architecture + ".context_length"),
        "gguf_context_length_missing")
    engine_context = _positive_int(meta.get("n_ctx_train"),
                                   "models_n_ctx_train_missing")
    comparisons = []
    if declared_context != engine_context:
        comparisons.append({
            "field": architecture + ".context_length == meta.n_ctx_train",
            "result": "mismatch",
            "gguf_declared": declared_context,
            "receipt_reported": engine_context,
        })


    if architecture == "llama":
        declared_embedding = _positive_int(
            keys.get(architecture + ".embedding_length"),
            "gguf_embedding_length_missing")
        engine_embedding = _positive_int(meta.get("n_embd"),
                                         "models_n_embd_missing")
        comparisons.append({
            "field": architecture + ".embedding_length == meta.n_embd",
            "result": "agree" if declared_embedding == engine_embedding
                      else "mismatch",
            "gguf_declared": declared_embedding,
            "receipt_reported": engine_embedding,
        })

    token_summary = arrays.get("tokenizer.ggml.tokens")
    token_summary = _mapping(token_summary, "gguf_tokenizer_tokens_missing")
    if token_summary.get("type") != "STRING":
        return could_not_evaluate("gguf_tokenizer_tokens_not_string_array")
    token_count = _positive_int(token_summary.get("length"),
                                "gguf_tokenizer_tokens_length_invalid")
    engine_vocab = _positive_int(meta.get("n_vocab"), "models_n_vocab_missing")
    comparisons.append({
        "field": "len(tokenizer.ggml.tokens) == meta.n_vocab",
        "result": "agree" if token_count == engine_vocab else "mismatch",
        "gguf_declared": token_count,
        "receipt_reported": engine_vocab,
    })

    declared_file_type = keys.get("general.file_type")
    engine_ftype = meta.get("ftype")
    if not isinstance(engine_ftype, str) or not engine_ftype:
        return could_not_evaluate("models_ftype_missing")
    guessed = engine_ftype.startswith("(guessed)")
    if (declared_file_type is None) != guessed:
        comparisons.append({
            "field": "general.file_type presence == inverse ftype guessed marker",
            "result": "mismatch",
        })
    else:
        comparisons.append({
            "field": "general.file_type presence == inverse ftype guessed marker",
            "result": "agree",
        })

    mismatches = [row for row in comparisons if row["result"] == "mismatch"]
    status = "engine-mismatch" if mismatches else "engine-agreement"
    context = {
        "gguf_declared_context_length": declared_context,
        "models_meta_n_ctx_train": engine_context,
        "training_context_comparison": (
            "equal" if declared_context == engine_context else "different"),
        "props_n_ctx": props_n_ctx,
        "props_n_ctx_note": "informational-only; not compared with training context",
        "total_slots": total_slots,
        "slot_division_applied": False,
    }
    return {
        "status": status,
        "exit_code": 1 if mismatches else 0,
        "evidence_scope": "receipt-self-report-not-authenticated-execution",
        "file_sha256": actual_sha,
        "model_sha256_post": model_sha,
        "models_body_sha256": body_sha,
        "alias": alias,
        "selected_model_id": matching[0]["id"],
        "context": context,
        "comparisons": comparisons,
        "uncompared_engine_fields": [
            "meta.architecture (not part of the comparison contract)",
            "meta.n_params",
            "meta.size",
        ],
    }

def reconcile_receipt(decoded: Mapping, file_sha256: str,
                      receipt: Mapping) -> dict[str, object]:
    try:
        return _reconcile_receipt_checked(decoded, file_sha256, receipt)
    except ReceiptError as exc:
        return could_not_evaluate(exc.reason)




def _u32(value: int, endian: str) -> bytes:
    return struct.pack(endian + "I", value)


def _u64(value: int, endian: str) -> bytes:
    return struct.pack(endian + "Q", value)


def _pack_string(value: str, endian: str) -> bytes:
    raw = value.encode("utf-8")
    return _u64(len(raw), endian) + raw


def _pack_value(type_id: int, value, endian: str) -> bytes:
    if type_id == 8:
        return _pack_string(value, endian)
    if type_id == 9:
        element_type, values = value
        return (_u32(element_type, endian) + _u64(len(values), endian)
                + b"".join(_pack_value(element_type, item, endian)
                           for item in values))
    fmt = SCALARS[type_id][0]
    if type_id == 7:
        value = int(value)
    return struct.pack(endian + fmt, value)


def _fixture(entries, *, version=3, endian="<", tensor_count=1) -> bytes:
    return (MAGIC + _u32(version, endian) + _u64(tensor_count, endian)
            + _u64(len(entries), endian)
            + b"".join(_pack_string(key, endian) + _u32(type_id, endian)
                       + _pack_value(type_id, value, endian)
                       for key, type_id, value in entries))


def run_selftest() -> tuple[dict[str, object], int]:
    failures = []
    cases = []

    def parser_case(name, data, reason=None, *, code=None, max_kv=DEFAULT_MAX_KV,
                    max_str=DEFAULT_MAX_STR,
                    max_metadata_bytes=MAX_METADATA_BYTES):
        cases.append(name)
        if code is None:
            code = (1 if reason == "bad_magic" else
                    2 if reason is not None else 0)
        try:
            result = decode_metadata(io.BytesIO(data), len(data), max_kv=max_kv,
                                     max_str=max_str,
                                     max_metadata_bytes=max_metadata_bytes)
        except GGUFError as exc:
            if (exc.reason, exc.exit_code) != (reason, code):
                failures.append({"case": name, "expected": reason or "success",
                                 "observed": exc.reason})
        else:
            if reason is not None or code != 0:
                failures.append({"case": name, "expected": reason or "error",
                                 "observed": "success"})
            elif name == "types_nested_v3_little":
                if (result["version"], result["endianness"],
                    result["keys"].get("llama.context_length"),
                    result["arrays"].get("fixture.nested")) != (
                        3, "little", 2048, {"type": "ARRAY", "length": 2}):
                    failures.append({"case": name, "expected": "identity_and_array_values",
                                     "observed": "mismatch"})
            elif name == "v3_big_endian":
                if (result["version"], result["endianness"],
                    result["tensor_count"]) != (3, "big", 9):
                    failures.append({"case": name, "expected": "big_endian",
                                     "observed": "mismatch"})

    entries = [
        ("general.architecture", 8, "llama"),
        ("general.name", 8, "fixture"),
        ("general.alignment", 4, 32),
        ("general.file_type", 4, 0),
        ("tokenizer.ggml.model", 8, "llama"),
        ("llama.context_length", 10, 2048),
        ("llama.block_count", 10, 16),
        ("llama.embedding_length", 10, 64),
        ("tokenizer.ggml.tokens", 9, (8, ["a", "b", "c"])),
        ("fixture.uint8", 0, 255), ("fixture.int8", 1, -2),
        ("fixture.uint16", 2, 65530), ("fixture.int16", 3, -1234),
        ("fixture.uint32", 4, 4294967295), ("fixture.int32", 5, -123456),
        ("fixture.float32", 6, 1.25), ("fixture.bool", 7, True),
        ("fixture.string", 8, "valid-λ"),
        ("fixture.uint64", 10, 18446744073709551615),
        ("fixture.int64", 11, -1234567890123),
        ("fixture.float64", 12, -2.5),
        ("fixture.array", 9, (3, [1, -2, 300])),
        ("fixture.nested", 9, (9, [
            (0, [0, 255]), (9, [(8, ["nested", "array"])]),
        ])),
    ]
    parser_case("types_nested_v3_little", _fixture(entries))
    parser_case("v2_little_endian", _fixture(
        [("general.architecture", 8, "llama"),
         ("llama.context_length", 10, 4096)],
        version=2, tensor_count=7))
    parser_case("v3_big_endian", _fixture(
        [("general.architecture", 8, "llama"),
         ("llama.context_length", 10, 4096)],
        version=3, endian=">", tensor_count=9))
    parser_case("v3_legacy_uint32_arch_keys", _fixture(
        [("general.architecture", 8, "llama"),
         ("llama.context_length", 4, 2048),
         ("llama.block_count", 4, 5),
         ("llama.embedding_length", 4, 64)]))
    parser_case("v2_big_endian_unsupported", _fixture(
        [("general.architecture", 8, "llama")],
        version=2, endian=">"), "unsupported_version")
    parser_case("tensor_tail_not_parsed",
                 _fixture([("general.name", 8, "tail")]) + b"\xfftensor")
    parser_case("bad_magic", b"NOPE" + b"\0" * 20, "bad_magic")
    parser_case("truncated_tensor_count", MAGIC + _u32(3, "<") + b"\0" * 3,
                 "truncated_tensor_count")
    parser_case("unknown_type", MAGIC + struct.pack("<IQQ", 3, 0, 1)
                 + _pack_string("fixture.unknown", "<") + _u32(99, "<"),
                 "unknown_value_type")
    parser_case("duplicate_key", _fixture([
        ("fixture.same", 4, 1), ("fixture.same", 4, 2)]), "duplicate_key")
    invalid_utf8 = (MAGIC + struct.pack("<IQQ", 3, 0, 1)
                    + _pack_string("fixture.value", "<") + _u32(8, "<")
                    + _u64(1, "<") + b"\xff")
    parser_case("invalid_utf8", invalid_utf8, "invalid_utf8")
    parser_case("wrong_arch_key_type", _fixture([
        ("general.architecture", 8, "llama"),
        ("llama.context_length", 8, "2048")]), "identity_key_type_mismatch")
    parser_case("kv_limit", _fixture([
        ("fixture.one", 4, 1), ("fixture.two", 4, 2)]),
        "kv_count_too_large", max_kv=1)
    parser_case("string_limit", _fixture([
        ("general.name", 8, "oversize")]), "string_too_large", max_str=3)
    parser_case("metadata_byte_limit", _fixture([
        ("fixture.value", 4, 1)]), "metadata_byte_budget_exceeded",
        max_metadata_bytes=8)
    cases.append("hash_byte_budget")
    try:
        _hash_stream(io.BytesIO(b"x"), 1, max_bytes=0)
    except GGUFError as exc:
        if exc.reason != "hash_byte_budget_exceeded":
            failures.append({"case": "hash_byte_budget",
                             "expected": "hash_byte_budget_exceeded",
                             "observed": exc.reason})
    else:
        failures.append({"case": "hash_byte_budget",
                         "expected": "hash_byte_budget_exceeded",
                         "observed": "success"})
    array_limit = (MAGIC + struct.pack("<IQQ", 3, 0, 1)
                   + _pack_string("fixture.large", "<") + _u32(9, "<")
                   + _u32(0, "<") + _u64(MAX_ARRAY_LENGTH + 1, "<"))
    parser_case("array_length_limit", array_limit, "array_too_large")
    deep = (8, ["x"])
    for _ in range(MAX_ARRAY_DEPTH + 1):
        deep = (9, [deep])
    parser_case("array_depth_limit", _fixture([("fixture.deep", 9, deep)]),
                 "array_nesting_too_deep")
    parser_case("invalid_bool", _fixture([("fixture.bad_bool", 7, 2)]),
                 "invalid_bool")
    parser_case("zero_alignment", _fixture([
        ("general.alignment", 4, 0)]), "invalid_alignment")

    sha = "a" * 64
    receipt_meta = {
        "n_ctx_train": 2048, "n_embd": 64, "n_vocab": 3,
        "ftype": "declared F32", "architecture": "llama",
    }
    body = json.dumps({"data": [{"id": "fixture-alias", "meta": receipt_meta}]},
                      separators=(",", ":"))
    good_receipt = {
        "schema": RECEIPT_SCHEMA_V3,
        "model_sha256_post": sha,
        "alias": "fixture-alias",
        "ctx": 256,
        "captures": {
            "props": {"status": 200, "fields": {
                "model_alias": "fixture-alias",
                "default_generation_settings.n_ctx": 256,
                "total_slots": 4,
            }},
            "models": {"status": 200, "body_truncated": False,
                "body_read_truncated": False, "body": body,
                "body_sha256": hashlib.sha256(body.encode()).hexdigest()},
        },
    }
    decoded = {"keys": {
        "general.architecture": "llama", "general.file_type": 0,
        "llama.context_length": 2048, "llama.embedding_length": 64,
    }, "arrays": {"tokenizer.ggml.tokens": {"type": "STRING", "length": 3}}}

    def receipt_case(name, document, expected, actual_sha=sha, reason=None):
        cases.append(name)
        result = reconcile_receipt(decoded, actual_sha, document)
        if (result["exit_code"] != expected
                or (reason is not None and result.get("reason") != reason)):
            failures.append({"case": name, "expected_exit": expected,
                             "expected_reason": reason, "observed": result})
        return result

    positive = receipt_case("receipt_positive", good_receipt, 0)
    if (positive["status"] != "engine-agreement"
            or positive["context"]["props_n_ctx"] != 256
            or positive["context"]["slot_division_applied"] is not False):
        failures.append({"case": "receipt_positive", "expected": "self_report_agreement",
                         "observed": "incorrect_result"})
    wrong_train = json.loads(json.dumps(good_receipt))
    wrong_body_object = json.loads(body)
    wrong_body_object["data"][0]["meta"]["n_ctx_train"] = 1024
    wrong_body = json.dumps(wrong_body_object, separators=(",", ":"))
    wrong_train["captures"]["models"]["body"] = wrong_body
    wrong_train["captures"]["models"]["body_sha256"] = hashlib.sha256(
        wrong_body.encode()).hexdigest()
    mismatch = receipt_case("receipt_train_context_mismatch", wrong_train, 1)
    if mismatch["status"] != "engine-mismatch":
        failures.append({"case": "receipt_train_context_mismatch",
                         "expected": "engine-mismatch", "observed": mismatch["status"]})
    missing = json.loads(json.dumps(good_receipt))
    missing_body_object = json.loads(body)
    del missing_body_object["data"][0]["meta"]["n_ctx_train"]
    missing_body = json.dumps(missing_body_object, separators=(",", ":"))
    missing["captures"]["models"]["body"] = missing_body
    missing["captures"]["models"]["body_sha256"] = hashlib.sha256(
        missing_body.encode()).hexdigest()
    missing_result = receipt_case("receipt_missing_field", missing, 2,
                                  reason="models_n_ctx_train_missing")
    if missing_result["status"] != "could-not-evaluate":
        failures.append({"case": "receipt_missing_field",
                         "expected": "could-not-evaluate", "observed": missing_result["status"]})
    receipt_case("receipt_file_hash_mismatch", good_receipt, 1, "b" * 64,
                 reason="model_sha256_post_mismatch")
    broken_hash = json.loads(json.dumps(good_receipt))
    broken_hash["captures"]["models"]["body_sha256"] = "0" * 64
    receipt_case("receipt_body_hash_mismatch", broken_hash, 2,
                 reason="models_body_sha256_mismatch")
    ambiguous = json.loads(json.dumps(good_receipt))
    ambiguous_body = json.loads(body)
    ambiguous_body["data"].append(ambiguous_body["data"][0])
    ambiguous_text = json.dumps(ambiguous_body, separators=(",", ":"))
    ambiguous["captures"]["models"]["body"] = ambiguous_text
    ambiguous["captures"]["models"]["body_sha256"] = hashlib.sha256(
        ambiguous_text.encode()).hexdigest()
    receipt_case("receipt_ambiguous_alias", ambiguous, 2,
                 reason="models_alias_ambiguous")

    def malformed_case(name, raw, expected_reason):
        cases.append(name)
        try:
            parse_receipt_bytes(raw)
        except ReceiptError as exc:
            if exc.reason != expected_reason:
                failures.append({"case": name, "expected": expected_reason,
                                 "observed": exc.reason})
        else:
            failures.append({"case": name, "expected": expected_reason,
                             "observed": "accepted"})

    malformed_case("receipt_invalid_json", b"{", "receipt_invalid_json")
    malformed_case("receipt_duplicate_json_key",
                    b'{"schema":"x","schema":"y"}', "duplicate_json_key")
    malformed_case("receipt_lone_surrogate", b'{"label":"\\ud800"}',
                   "receipt_invalid_unicode")
    malformed_case("receipt_size_limit", b" " * (MAX_RECEIPT_BYTES + 1),
                    "receipt_byte_budget_exceeded")

    result = {
        "schema": "gguf-identity-selftest/v2",
        "status": "failed" if failures else "passed",
        "case_count": len(cases),
        "passed": len(cases) - len(failures),
        "failed": failures,
        "cases": cases,
    }
    return result, 1 if failures else 0


def nonnegative_limited(value: str, limit: int) -> int:
    try:
        parsed = int(value, 10)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    if parsed < 0 or parsed > limit:
        raise argparse.ArgumentTypeError(f"must be between 0 and {limit}")
    return parsed


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="GGUF file to inspect")
    parser.add_argument("--json", action="store_true",
                        help="write the complete result as JSON")
    parser.add_argument("--max-kv", type=lambda value: nonnegative_limited(
        value, MAX_KV_LIMIT), default=DEFAULT_MAX_KV)
    parser.add_argument("--max-str", type=lambda value: nonnegative_limited(
        value, MAX_STR_LIMIT), default=DEFAULT_MAX_STR)
    parser.add_argument("--receipt", help="llama.cpp live v3 receipt JSON")
    parser.add_argument("--selftest", action="store_true",
                        help="run in-memory parser and receipt fixtures")
    return parser


def main(argv=None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        if args.file is not None or args.receipt is not None:
            parser.error("--selftest accepts no FILE or --receipt")
        result, code = run_selftest()
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return code
    if args.file is None:
        parser.error("FILE is required unless --selftest is used")
    try:
        result = inspect_path(args.file, max_kv=args.max_kv,
                              max_str=args.max_str)
    except GGUFError as exc:
        print(f"gguf-identity: {exc.reason}", file=sys.stderr)
        return exc.exit_code
    except OSError:
        print("gguf-identity: file_unavailable", file=sys.stderr)
        return 3

    exit_code = 0
    if args.receipt is not None:
        try:
            receipt = load_receipt(args.receipt)
        except ReceiptError as exc:
            reconciled = could_not_evaluate(exc.reason)
        else:
            reconciled = reconcile_receipt(result, result["sha256"], receipt)
        result["receipt"] = reconciled
        exit_code = reconciled["exit_code"]

    if args.json or args.receipt is not None:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(f"GGUF v{result['version']} ({result['endianness']} endian)")
        print(f"path: {result['path']!r}")
        print(f"size: {result['size']}; sha256: {result['sha256']}")
        print(f"tensors: {result['tensor_count']}; metadata entries: {result['kv_count']}")
        print(json.dumps(result["keys"], indent=2, sort_keys=True,
                         allow_nan=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())