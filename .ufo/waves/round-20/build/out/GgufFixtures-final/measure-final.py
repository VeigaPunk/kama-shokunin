#!/usr/bin/env python3
"""Measure the GGUF header reader against pinned fixtures, oracle and receipt.

The receipt path is passed to the selected parser; this harness never opens or
emits raw receipt contents. No server is started and no model is loaded for
inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

EXIT_PASS = 0
EXIT_MISMATCH = 1
EXIT_UNAVAILABLE = 2
EXIT_CNE = 2
STATUS_SNAPSHOT_TAMPERED = "snapshot_tampered"
BASE_REVISION = "37bd4c5bd456a2f8a54d3312c28495c321715856"
REFERENCE_SHA256 = "fb367e9e2c91eaadf4fb48bddb7a984a2c0c0feda41a45a00d75bbed182c5bc6"
STATIC_KEYS = (
    "general.architecture",
    "general.name",
    "general.file_type",
    "general.alignment",
    "tokenizer.ggml.model",
)
ARCH_KEYS = ("context_length", "block_count", "embedding_length")
REASON_LINE = re.compile(r"gguf-identity: ([a-z][a-z0-9_]*)\Z")


class UnavailableError(Exception):
    """Required evidence or a usable observation is unavailable."""




def read_limited(path: Path, limit: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise UnavailableError("cannot open " + path.name) from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise UnavailableError(path.name + " is not a regular file")
        if info.st_size < 0 or info.st_size > limit:
            raise UnavailableError(path.name + " exceeds the input size bound")
        chunks = bytearray()
        while len(chunks) <= limit:
            block = os.read(fd, min(65536, limit + 1 - len(chunks)))
            if not block:
                break
            chunks.extend(block)
        if len(chunks) > limit:
            raise UnavailableError(path.name + " exceeds the input size bound")
        if len(chunks) != info.st_size:
            raise UnavailableError(path.name + " changed while being read")
        after = os.fstat(fd)
        if after.st_size != info.st_size:
            raise UnavailableError(path.name + " changed while being read")
        return bytes(chunks)
    finally:
        os.close(fd)


def file_facts(path: Path, max_bytes: int) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise UnavailableError("cannot open " + path.name) from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise UnavailableError(path.name + " is not a regular file")
        if before.st_size < 0 or before.st_size > max_bytes:
            raise UnavailableError(path.name + " exceeds the input size bound")
        digest = hashlib.sha256()
        total = 0
        while True:
            block = os.read(fd, 1024 * 1024)
            if not block:
                break
            total += len(block)
            if total > max_bytes:
                raise UnavailableError(path.name + " exceeds the input size bound")
            digest.update(block)
        after = os.fstat(fd)
        if total != before.st_size or after.st_size != before.st_size:
            raise UnavailableError(path.name + " changed while being hashed")
        return {"size_bytes": total, "sha256": digest.hexdigest()}
    finally:
        os.close(fd)


def load_json(path: Path, limit: int = 1024 * 1024) -> tuple[bytes, Any]:
    raw = read_limited(path, limit)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UnavailableError(path.name + " is not valid UTF-8 JSON") from exc
    return raw, value
def load_pinned_json(
    path: Path, limit: int, expected_sha256: str, field: str,
    issues: list[dict[str, Any]],
) -> tuple[Any, str | None, bool]:
    try:
        raw = read_limited(path, limit)
    except UnavailableError as exc:
        add_issue(issues, "unavailable", field, "readable JSON", type(exc).__name__)
        return None, None, False

    digest = hashlib.sha256(raw).hexdigest()
    tampered = digest != expected_sha256
    if tampered:
        add_issue(issues, STATUS_SNAPSHOT_TAMPERED, field + ".sha256", expected_sha256, digest)
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        add_issue(issues, "unavailable", field + ".json", "valid UTF-8 JSON", type(exc).__name__)
        return None, digest, tampered
    return document, digest, tampered


def projection(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        key: entry.get(key)
        for key in (
            "id", "file", "size_bytes", "sha256", "expected_exit", "expected_reason"
        )
    }


def finding_id(kind: str, field: str) -> str:
    if kind == STATUS_SNAPSHOT_TAMPERED:
        if field.startswith("fixture."):
            return "snapshot_tampered:fixture:" + field.split(".", 1)[1]
        if field.startswith("expected_json"):
            return "snapshot_tampered:expected_json"
        if field.startswith("oracle_json") or field.startswith("oracle."):
            return "snapshot_tampered:oracle_json"
        if field.startswith("receipt_evidence"):
            return "snapshot_tampered:receipt_evidence"
        if field.startswith("reference"):
            return "snapshot_tampered:reference"
        return "snapshot_tampered:" + field
    if kind == "unavailable" and field.startswith("fixture."):
        return "unavailable:fixture:" + field.split(".", 1)[1]
    return kind + ":" + field


def add_issue(issues: list[dict[str, Any]], kind: str, field: str, expected: Any, actual: Any) -> None:
    identifier = finding_id(kind, field)
    if kind == STATUS_SNAPSHOT_TAMPERED and any(
        issue.get("finding_id") == identifier for issue in issues
    ):
        return
    issues.append({
        "kind": kind,
        "finding_id": identifier,
        "field": field,
        "expected": expected,
        "actual": actual,
    })
def reference_snapshot(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    facts = file_facts(path, 256 * 1024)
    issues: list[dict[str, Any]] = []
    if facts["sha256"] != REFERENCE_SHA256:
        add_issue(
            issues, STATUS_SNAPSHOT_TAMPERED, "reference.sha256",
            REFERENCE_SHA256, facts["sha256"],
        )
    return facts, issues


def validate_manifest_and_fixtures(
    expected_path: Path, reference: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], dict[str, str], str | None]:
    issues: list[dict[str, Any]] = []
    fixture_states: dict[str, str] = {}
    pinned = reference["fixture_manifest"]
    document, expected_digest, manifest_tampered = load_pinned_json(
        expected_path, 1024 * 1024, pinned["expected_json_sha256"],
        "expected_json", issues,
    )
    if document is None:
        state = STATUS_SNAPSHOT_TAMPERED if manifest_tampered else "unavailable"
        for item in pinned["fixtures"]:
            fixture_states[item["id"]] = state
        return None, issues, fixture_states, expected_digest
    if not isinstance(document, dict) or not isinstance(document.get("fixtures"), list):
        add_issue(issues, "unavailable", "expected_json.fixtures", "array", type(document).__name__)
        for item in pinned["fixtures"]:
            fixture_states[item["id"]] = (
                STATUS_SNAPSHOT_TAMPERED if manifest_tampered else "unavailable"
            )
        return None, issues, fixture_states, expected_digest

    actual_projection = [
        projection(item) if isinstance(item, dict) else {"invalid_item": type(item).__name__}
        for item in document["fixtures"]
    ]
    if not same_json_value(actual_projection, pinned["fixtures"]):
        manifest_tampered = True
        add_issue(
            issues, STATUS_SNAPSHOT_TAMPERED, "expected_json.fixture_manifest",
            pinned["fixtures"], actual_projection,
        )

    expected_by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids: set[str] = set()
    for item in document["fixtures"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        if item["id"] in expected_by_id:
            duplicate_ids.add(item["id"])
        expected_by_id[item["id"]] = item
    for duplicate in sorted(duplicate_ids):
        manifest_tampered = True
        add_issue(
            issues, STATUS_SNAPSHOT_TAMPERED, "expected_json.duplicate_id",
            "unique fixture ids", duplicate,
        )

    for item in pinned["fixtures"]:
        fixture_id = item["id"]
        relative = PurePosixPath(item["file"])
        if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != "fixtures":
            fixture_states[fixture_id] = "unavailable"
            add_issue(issues, "unavailable", "fixture." + fixture_id, "safe fixtures/<name>.gguf path", item["file"])
            continue
        fixture_path = expected_path.parent.joinpath(*relative.parts)
        try:
            facts = file_facts(fixture_path, 1024 * 1024)
        except UnavailableError as exc:
            fixture_states[fixture_id] = "unavailable"
            add_issue(issues, "unavailable", "fixture." + fixture_id, "present regular file", type(exc).__name__)
            continue
        if facts["size_bytes"] != item["size_bytes"] or facts["sha256"] != item["sha256"]:
            fixture_states[fixture_id] = STATUS_SNAPSHOT_TAMPERED
            add_issue(
                issues, STATUS_SNAPSHOT_TAMPERED, "fixture." + fixture_id,
                {"size_bytes": item["size_bytes"], "sha256": item["sha256"]},
                facts,
            )
        elif manifest_tampered:
            fixture_states[fixture_id] = STATUS_SNAPSHOT_TAMPERED
        else:
            fixture_states[fixture_id] = "ready"

    return document, issues, fixture_states, expected_digest


def validate_oracle(
    path: Path, reference: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str | None]:
    issues: list[dict[str, Any]] = []
    pinned = reference["oracle"]
    oracle, actual_digest, tampered = load_pinned_json(
        path, 1024 * 1024, pinned["sha256"], "oracle_json", issues
    )
    if not isinstance(oracle, dict):
        if oracle is not None:
            add_issue(issues, "unavailable", "oracle_json", "object", type(oracle).__name__)
        return None, issues, actual_digest
    if tampered:
        return oracle, issues, actual_digest

    checks: list[tuple[str, Any, Any]] = [
        ("reader.package", pinned["reader"]["package"], oracle.get("reader", {}).get("package") if isinstance(oracle.get("reader"), dict) else None),
        ("reader.version", pinned["reader"]["version"], oracle.get("reader", {}).get("version") if isinstance(oracle.get("reader"), dict) else None),
        ("reader.wheel_sha256", pinned["reader"]["wheel_sha256"], oracle.get("reader", {}).get("wheel_sha256") if isinstance(oracle.get("reader"), dict) else None),
        ("file.size_bytes", pinned["file"]["size_bytes"], oracle.get("file", {}).get("size_bytes") if isinstance(oracle.get("file"), dict) else None),
        ("file.sha256", pinned["file"]["sha256"], oracle.get("file", {}).get("sha256") if isinstance(oracle.get("file"), dict) else None),
        ("version", pinned["version"], oracle.get("version")),
        ("tensor_count", pinned["tensor_count"], oracle.get("tensor_count")),
        ("kv_count", pinned["kv_count"], oracle.get("kv_count")),
    ]
    metadata = oracle.get("metadata") if isinstance(oracle.get("metadata"), dict) else {}
    for key, value in pinned["identity_keys"].items():
        checks.append(("metadata." + key, value, metadata.get(key)))
    for key, summary in pinned["arrays"].items():
        oracle_summary = {"type": "ARRAY<" + summary["type"] + ">", "length": summary["length"]}
        checks.append(("metadata." + key, oracle_summary, metadata.get(key)))
    for field, expected, actual in checks:
        if not same_json_value(expected, actual):
            add_issue(issues, STATUS_SNAPSHOT_TAMPERED, "oracle." + field, expected, actual)
    return oracle, issues, actual_digest
def validate_receipt_evidence(
    path: Path, reference: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    row: dict[str, Any] = {"path": str(path)}
    evidence, digest, tampered = load_pinned_json(
        path, 1024 * 1024, reference["receipt_result_source_sha256"],
        "receipt_evidence", issues,
    )
    if digest is not None:
        row["sha256"] = digest
    if not isinstance(evidence, dict) or not isinstance(evidence.get("receipt"), dict):
        add_issue(issues, "unavailable", "receipt_evidence.receipt", "object", None)
        row["status"] = STATUS_SNAPSHOT_TAMPERED if tampered else "unavailable"
        return row, issues

    actual_receipt = evidence["receipt"]
    row["receipt"] = actual_receipt
    if tampered:
        row["status"] = STATUS_SNAPSHOT_TAMPERED
        return row, issues
    expected_receipt = reference["receipt_result"]
    if not same_json_value(expected_receipt, actual_receipt):
        add_issue(
            issues, STATUS_SNAPSHOT_TAMPERED,
            "receipt_evidence.receipt", expected_receipt, actual_receipt,
        )
    row["status"] = STATUS_SNAPSHOT_TAMPERED if issues else "pass"
    return row, issues




def expected_identity_keys(metadata: Any) -> dict[str, Any]:
    source = metadata if isinstance(metadata, dict) else {}
    result: dict[str, Any] = {}
    architecture_entry = source.get("general.architecture")
    architecture = None
    if isinstance(architecture_entry, dict) and architecture_entry.get("type") == "string":
        architecture = architecture_entry.get("value")
    keys = list(STATIC_KEYS)
    if isinstance(architecture, str) and architecture:
        keys.extend(architecture + "." + suffix for suffix in ARCH_KEYS)
    for key in keys:
        entry = source.get(key)
        if not isinstance(entry, dict):
            result[key] = None
        elif entry.get("type") == "array":
            result[key] = {
                "type": str(entry.get("element_type")).upper(),
                "length": entry.get("length"),
            }
        else:
            result[key] = entry.get("value")
    return result
def expected_identity_types(metadata: Any) -> dict[str, str]:
    source = metadata if isinstance(metadata, dict) else {}
    architecture_entry = source.get("general.architecture")
    architecture = None
    if isinstance(architecture_entry, dict) and architecture_entry.get("type") == "string":
        architecture = architecture_entry.get("value")
    keys = list(STATIC_KEYS)
    if isinstance(architecture, str) and architecture:
        keys.extend(architecture + "." + suffix for suffix in ARCH_KEYS)
    return {
        key: str(source[key]["type"]).upper()
        for key in keys
        if isinstance(source.get(key), dict)
    }




def same_json_value(expected: Any, actual: Any) -> bool:
    if type(expected) is not type(actual):
        return False
    if isinstance(expected, dict):
        return expected.keys() == actual.keys() and all(
            same_json_value(expected[key], actual[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(expected) == len(actual) and all(
            same_json_value(left, right) for left, right in zip(expected, actual)
        )
    return expected == actual


def compare_field(mismatches: list[dict[str, Any]], field: str, expected: Any, actual: Any) -> None:
    if not same_json_value(expected, actual):
        add_issue(mismatches, "mismatch", field, expected, actual)


def parse_reason(stderr: str) -> str | None:
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    if len(lines) != 1:
        return None
    match = REASON_LINE.fullmatch(lines[0])
    return match.group(1) if match else None


def run_tool(tool: Path, path: Path, timeout: float, receipt: Path | None = None) -> dict[str, Any]:
    command = [sys.executable, str(tool), str(path), "--json"]
    if receipt is not None:
        command.extend(("--receipt", str(receipt)))
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return {"kind": "unavailable", "error": "tool_timeout"}
    except OSError as exc:
        return {"kind": "unavailable", "error": "tool_start_failed", "exception": type(exc).__name__}

    if completed.returncode < 0:
        return {"kind": "unavailable", "error": "tool_signal", "signal": -completed.returncode}
    if completed.stdout.strip():
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return {"kind": "unavailable", "error": "tool_stdout_not_json"}
        if not isinstance(result, dict):
            return {"kind": "unavailable", "error": "tool_json_not_object"}
        if completed.returncode == 0:
            if completed.stderr.strip():
                return {"kind": "unavailable", "error": "tool_success_with_stderr"}
            return {"kind": "decoded", "exit": 0, "reason": "decoded", "result": result}
        receipt_result = result.get("receipt")
        if receipt is not None and isinstance(receipt_result, dict):
            reason = receipt_result.get("reason", receipt_result.get("status"))
            return {
                "kind": "decoded",
                "exit": completed.returncode,
                "reason": reason,
                "result": result,
            }
        return {"kind": "unavailable", "error": "nonzero_tool_json_without_receipt"}

    if completed.returncode == 0:
        return {"kind": "unavailable", "error": "tool_success_without_json"}
    reason = parse_reason(completed.stderr)
    if reason is None:
        return {"kind": "unavailable", "error": "unnamed_tool_failure"}
    return {"kind": "rejected", "exit": completed.returncode, "reason": reason}


def compare_decoded_result(
    expected_entry: dict[str, Any], actual: dict[str, Any],
    mismatches: list[dict[str, Any]], prefix: str,
) -> None:
    for field in ("version", "endianness", "tensor_count", "kv_count"):
        compare_field(mismatches, prefix + "." + field, expected_entry.get(field), actual.get(field))
    metadata = expected_entry.get("metadata")
    compare_field(
        mismatches, prefix + ".keys",
        expected_identity_keys(metadata), actual.get("keys"),
    )
    compare_field(
        mismatches, prefix + ".key_types",
        expected_identity_types(metadata), actual.get("key_types"),
    )
    expected_arrays: dict[str, dict[str, Any]] = {}
    if isinstance(metadata, dict):
        for key, entry in metadata.items():
            if isinstance(entry, dict) and entry.get("type") == "array":
                expected_arrays[key] = {
                    "type": str(entry.get("element_type")).upper(),
                    "length": entry.get("length"),
                }
    compare_field(mismatches, prefix + ".arrays", expected_arrays, actual.get("arrays"))
    compare_field(mismatches, prefix + ".size", expected_entry.get("size_bytes"), actual.get("size"))
    compare_field(mismatches, prefix + ".sha256", expected_entry.get("sha256"), actual.get("sha256"))
def measure_fixture(
    pinned: dict[str, Any], expected_entry: dict[str, Any] | None,
    state: str, fixture_path: Path, tool: Path, timeout: float,
    reason_equivalence: dict[str, list[str]],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": pinned["id"],
        "file": pinned["file"],
        "expected_exit": pinned["expected_exit"],
        "expected_reason": pinned["expected_reason"],
    }
    mismatches: list[dict[str, Any]] = []
    if state == STATUS_SNAPSHOT_TAMPERED:
        row.update({"status": STATUS_SNAPSHOT_TAMPERED, "error": "snapshot_tampered"})
        return row
    if state == "unavailable":
        row.update({"status": "unavailable", "error": "fixture_unavailable"})
        return row
    if expected_entry is None:
        row.update({"status": STATUS_SNAPSHOT_TAMPERED, "error": "expected_entry_missing"})
        add_issue(
            mismatches, STATUS_SNAPSHOT_TAMPERED,
            "fixture." + pinned["id"] + ".expected_entry", pinned, None,
        )
        row["mismatches"] = mismatches
        return row

    observation = run_tool(tool, fixture_path, timeout)
    if observation["kind"] == "unavailable":
        row.update({"status": "unavailable", "error": observation["error"]})
        if "signal" in observation:
            row["signal"] = observation["signal"]
        if "exception" in observation:
            row["exception"] = observation["exception"]
        return row

    if observation["kind"] == "rejected" and (
        observation["exit"] == 3 or observation["reason"] == "file_unavailable"
    ):
        row.update({
            "status": "unavailable",
            "error": "file_unavailable",
            "actual_exit": observation["exit"],
            "actual_reason": observation["reason"],
        })
        return row
    actual_exit = observation["exit"]
    actual_reason = observation["reason"]
    row["actual_exit"] = actual_exit
    row["actual_reason"] = actual_reason
    compare_field(mismatches, "fixture." + pinned["id"] + ".exit", pinned["expected_exit"], actual_exit)
    accepted_reasons = reason_equivalence.get(pinned["expected_reason"], [])
    if actual_reason not in accepted_reasons:
        add_issue(mismatches, "mismatch", "fixture." + pinned["id"] + ".reason", accepted_reasons, actual_reason)

    if observation["kind"] == "decoded":
        parsed = observation["result"]
        row["parsed"] = {
            field: parsed.get(field)
            for field in ("version", "endianness", "tensor_count", "kv_count", "keys", "key_types", "arrays", "size", "sha256")
        }
        if expected_entry is not None and pinned["expected_exit"] == 0:
            compare_decoded_result(expected_entry, parsed, mismatches, "fixture." + pinned["id"])
        elif pinned["expected_exit"] != 0:
            add_issue(mismatches, "mismatch", "fixture." + pinned["id"] + ".unexpected_decode", "error", parsed)
    if mismatches:
        row["status"] = "mismatch"
        row["mismatches"] = mismatches
    else:
        row["status"] = "pass"
    return row










def frozen_before(repo: Path, reference: dict[str, Any]) -> dict[str, Any]:
    base = reference["frozen_before"]
    try:
        completed = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", base["revision"], "--", base["path"]],
            cwd=repo,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "GIT_CONFIG_NOSYSTEM": "1"},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "unavailable", "error": type(exc).__name__, "attempted_parser": False}
    if completed.returncode != 0:
        return {"status": "unavailable", "error": "base_revision_unavailable", "attempted_parser": False}
    paths = [line for line in completed.stdout.splitlines() if line]
    status = "capability_present" if base["path"] in paths else "capability_absent"
    row = {
        "revision": base["revision"],
        "path": base["path"],
        "status": status,
        "attempted_parser": False,
        "interpretation": "instrument absent at frozen revision; no parser outcome is fabricated",
    }
    if status != base["expected_status"]:
        row["mismatches"] = [{"field": "frozen_before.status", "expected": base["expected_status"], "actual": status}]
    return row


def measure_model(
    model_path: Path, tool_path: Path, receipt_path: Path, timeout: float,
    reference: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    pinned = reference["oracle"]
    row: dict[str, Any] = {"id": "stories260K.gguf", "path": str(model_path)}
    expected_file = pinned["file"]
    try:
        facts = file_facts(model_path, max(expected_file["size_bytes"] + 1, 8 * 1024 * 1024))
    except UnavailableError as exc:
        row.update({"status": "unavailable", "error": type(exc).__name__})
        return row, None
    row["size_bytes"] = facts["size_bytes"]
    row["sha256"] = facts["sha256"]
    mismatches: list[dict[str, Any]] = []
    compare_field(mismatches, "model.size_bytes", expected_file["size_bytes"], facts["size_bytes"])
    compare_field(mismatches, "model.sha256", expected_file["sha256"], facts["sha256"])
    if mismatches:
        row.update({"status": "mismatch", "mismatches": mismatches, "parser_attempted": False})
        return row, None

    observation = run_tool(tool_path, model_path, timeout, receipt_path)
    if observation["kind"] == "unavailable":
        row.update({"status": "unavailable", "parser_attempted": True, "error": observation["error"]})
        if "signal" in observation:
            row["signal"] = observation["signal"]
        if "exception" in observation:
            row["exception"] = observation["exception"]
        return row, None
    if observation["kind"] == "rejected":
        if observation["exit"] == 3 or observation["reason"] == "file_unavailable":
            row.update({"status": "unavailable", "parser_attempted": True, "error": "file_unavailable"})
        else:
            row.update({
                "status": "mismatch",
                "parser_attempted": True,
                "actual_exit": observation["exit"],
                "actual_reason": observation["reason"],
                "mismatches": [{"field": "model.exit", "expected": 0, "actual": observation["exit"]}],
            })
        return row, None

    result = observation["result"]
    row["parser_attempted"] = True
    row["actual_exit"] = observation["exit"]
    row["actual_reason"] = observation["reason"]
    row["actual"] = {
        field: result.get(field)
        for field in (
            "version", "endianness", "tensor_count", "kv_count", "keys",
            "key_types", "arrays", "sha256", "size",
        )
    }
    oracle_header = {field: pinned[field] for field in ("version", "tensor_count", "kv_count")}
    for field, expected in oracle_header.items():
        compare_field(mismatches, "model." + field, expected, result.get(field))
    compare_field(mismatches, "model.identity_keys", pinned["identity_keys"], result.get("keys"))
    compare_field(mismatches, "model.identity_key_types", pinned["identity_key_types"], result.get("key_types"))
    compare_field(mismatches, "model.arrays", pinned["arrays"], result.get("arrays"))
    compare_field(mismatches, "model.sha256", expected_file["sha256"], result.get("sha256"))
    compare_field(mismatches, "model.size_bytes", expected_file["size_bytes"], result.get("size"))
    if result.get("endianness") != "little":
        compare_field(mismatches, "model.endianness", "little", result.get("endianness"))

    receipt_result = result.get("receipt")
    if not isinstance(receipt_result, dict):
        row.update({"status": "mismatch", "error": "tool_omitted_receipt_result"})
        add_issue(mismatches, "mismatch", "model.receipt", reference["receipt_result"], receipt_result)
    else:
        row["receipt"] = receipt_result
        if observation["exit"] == EXIT_UNAVAILABLE or receipt_result.get("status") == "could-not-evaluate":
            row.update({
                "status": "unavailable",
                "error": "receipt_could_not_evaluate",
                "receipt_reason": receipt_result.get("reason"),
            })
            if mismatches:
                row["mismatches"] = mismatches
            return row, result
        compare_field(mismatches, "model.receipt", reference["receipt_result"], receipt_result)
    compare_field(mismatches, "model.exit", EXIT_PASS, observation["exit"])
    if mismatches:
        row.update({"status": "mismatch", "mismatches": mismatches})
    else:
        row["status"] = "pass"
    return row, result


def code_for(statuses: list[str]) -> int:
    if STATUS_SNAPSHOT_TAMPERED in statuses or "unavailable" in statuses:
        return EXIT_CNE
    if "mismatch" in statuses:
        return EXIT_MISMATCH
    return EXIT_PASS
def result_status(
    exit_code: int, issues: list[dict[str, Any]], rows: list[dict[str, Any]]
) -> str:
    if any(issue["kind"] == STATUS_SNAPSHOT_TAMPERED for issue in issues) or any(
        row.get("status") == STATUS_SNAPSHOT_TAMPERED for row in rows
    ):
        return STATUS_SNAPSHOT_TAMPERED
    if exit_code == EXIT_CNE:
        return "unavailable"
    if exit_code == EXIT_MISMATCH:
        return "mismatch"
    return "pass"




def selftest(
    expected_path: Path, oracle_path: Path, receipt_evidence_path: Path,
    reference_path: Path, reference: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    expected, expected_issues, _, _ = validate_manifest_and_fixtures(expected_path, reference)
    oracle, oracle_issues, _ = validate_oracle(oracle_path, reference)
    receipt_evidence, receipt_issues = validate_receipt_evidence(receipt_evidence_path, reference)
    _, reference_issues = reference_snapshot(reference_path)
    baseline_issues = expected_issues + oracle_issues + receipt_issues + reference_issues
    if expected is None or oracle is None or baseline_issues:
        return {
            "schema": "kama.gguf-identity-measure-selftest.v3",
            "status": "unavailable",
            "reason": "baseline_snapshots_not_pinned_or_readable",
        }, EXIT_CNE

    checks: list[dict[str, Any]] = []

    def record_check(name: str, expected_id: str, issues: list[dict[str, Any]]) -> None:
        observed_ids = sorted({issue["finding_id"] for issue in issues})
        observed_exit = code_for([issue["kind"] for issue in issues])
        checks.append({
            "name": name,
            "expected_finding_id": expected_id,
            "expected_exit": EXIT_CNE,
            "observed_finding_ids": observed_ids,
            "observed_exit": observed_exit,
            "passed": expected_id in observed_ids and observed_exit == EXIT_CNE,
        })

    with tempfile.TemporaryDirectory(prefix="gguf-measure-selftest-") as temp:
        root = Path(temp)
        base = root / "baseline"
        shutil.copytree(expected_path.parent, base, ignore=shutil.ignore_patterns("__pycache__"))

        missing_root = root / "missing"
        shutil.copytree(base, missing_root)
        first = reference["fixture_manifest"]["fixtures"][0]
        (missing_root / first["file"]).unlink()
        _, missing_issues, _, _ = validate_manifest_and_fixtures(
            missing_root / expected_path.name, reference
        )
        record_check("deleted_fixture_unavailable", "unavailable:fixture:" + first["id"], missing_issues)

        changed_fixture_root = root / "changed-fixture"
        shutil.copytree(base, changed_fixture_root)
        changed_fixture = changed_fixture_root / first["file"]
        changed_bytes = bytearray(changed_fixture.read_bytes())
        changed_bytes[-1] ^= 1
        changed_fixture.write_bytes(changed_bytes)
        _, changed_fixture_issues, _, _ = validate_manifest_and_fixtures(
            changed_fixture_root / expected_path.name, reference
        )
        record_check(
            "changed_fixture_snapshot",
            "snapshot_tampered:fixture:" + first["id"],
            changed_fixture_issues,
        )

        relabel_root = root / "relabelled"
        shutil.copytree(base, relabel_root)
        relabel_expected = relabel_root / expected_path.name
        document = json.loads(relabel_expected.read_text(encoding="utf-8"))
        document["fixtures"][0]["id"] += "-renamed"
        relabel_expected.write_text(
            json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _, relabel_issues, _, _ = validate_manifest_and_fixtures(relabel_expected, reference)
        record_check("relabelled_fixture_manifest", "snapshot_tampered:expected_json", relabel_issues)

        wrong_oracle_path = root / "wrong-oracle.json"
        wrong_oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
        wrong_oracle["version"] = int(wrong_oracle["version"]) + 1
        wrong_oracle_path.write_text(
            json.dumps(wrong_oracle, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _, wrong_oracle_issues, _ = validate_oracle(wrong_oracle_path, reference)
        record_check("wrong_oracle_snapshot", "snapshot_tampered:oracle_json", wrong_oracle_issues)

        wrong_receipt_path = root / "wrong-receipt-evidence.json"
        wrong_receipt = json.loads(receipt_evidence_path.read_text(encoding="utf-8"))
        wrong_receipt["receipt"]["context"]["total_slots"] += 1
        wrong_receipt_path.write_text(
            json.dumps(wrong_receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _, wrong_receipt_issues = validate_receipt_evidence(wrong_receipt_path, reference)
        record_check("wrong_receipt_evidence_snapshot", "snapshot_tampered:receipt_evidence", wrong_receipt_issues)

        wrong_reference_path = root / "wrong-reference.json"
        wrong_reference = json.loads(reference_path.read_text(encoding="utf-8"))
        wrong_reference["oracle"]["version"] = int(wrong_reference["oracle"]["version"]) + 1
        wrong_reference_path.write_text(
            json.dumps(wrong_reference, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _, wrong_reference_issues = reference_snapshot(wrong_reference_path)
        record_check("co-drifted_reference_snapshot", "snapshot_tampered:reference", wrong_reference_issues)

    behavior_mismatch_exit = code_for(["mismatch"])
    checks.append({
        "name": "normal_behavior_mismatch_exit",
        "expected_exit": EXIT_MISMATCH,
        "observed_exit": behavior_mismatch_exit,
        "passed": behavior_mismatch_exit == EXIT_MISMATCH,
    })

    passed = all(check["passed"] for check in checks)
    return {
        "schema": "kama.gguf-identity-measure-selftest.v3",
        "status": "passed" if passed else "failed",
        "check_count": len(checks),
        "checks": checks,
    }, EXIT_PASS if passed else EXIT_MISMATCH
def fixture_only_measure(
    expected_path: Path, tool_path: Path, repo: Path, timeout: float,
    reference: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    expected_doc, issues, fixture_states, expected_digest = validate_manifest_and_fixtures(
        expected_path, reference
    )
    tool_row: dict[str, Any]
    try:
        tool_row = {"path": str(tool_path), **file_facts(tool_path, 1024 * 1024)}
    except UnavailableError as exc:
        tool_row = {"path": str(tool_path), "status": "unavailable", "error": type(exc).__name__}
        add_issue(issues, "unavailable", "tool", "readable regular script", type(exc).__name__)

    frozen = frozen_before(repo, reference)
    if frozen.get("status") == "unavailable":
        add_issue(issues, "unavailable", "frozen_before", "capability_absent", frozen.get("error"))
    elif frozen.get("status") != reference["frozen_before"]["expected_status"]:
        add_issue(
            issues, "mismatch", "frozen_before.status",
            reference["frozen_before"]["expected_status"], frozen.get("status"),
        )

    expected_by_id: dict[str, dict[str, Any]] = {}
    if expected_doc is not None and isinstance(expected_doc.get("fixtures"), list):
        expected_by_id = {
            item.get("id"): item
            for item in expected_doc["fixtures"]
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
    reason_equivalence = reference["fixture_manifest"]["reason_equivalence"]
    rows: list[dict[str, Any]] = []
    snapshot_blocked = any(
        issue["kind"] == STATUS_SNAPSHOT_TAMPERED for issue in issues
    )
    for pinned in reference["fixture_manifest"]["fixtures"]:
        if snapshot_blocked:
            rows.append({
                "id": pinned["id"], "file": pinned["file"],
                "status": STATUS_SNAPSHOT_TAMPERED,
                "error": "snapshot_tampered",
            })
            continue
        if tool_row.get("status") == "unavailable":
            rows.append({
                "id": pinned["id"], "file": pinned["file"],
                "status": "unavailable", "error": "tool_unavailable",
            })
            continue
        rows.append(measure_fixture(
            pinned,
            expected_by_id.get(pinned["id"]),
            fixture_states.get(pinned["id"], "unavailable"),
            expected_path.parent / pinned["file"],
            tool_path,
            timeout,
            reason_equivalence,
        ))
    statuses = [row.get("status", "unavailable") for row in rows]
    statuses.extend(issue["kind"] for issue in issues)
    statuses.append(frozen.get("status", "unavailable"))
    exit_code = code_for(statuses)
    status = result_status(exit_code, issues, rows)
    row_mismatches = [
        {"row": row.get("id"), **finding}
        for row in rows
        for finding in row.get("mismatches", [])
    ]
    row_unavailable = [
        {"row": row.get("id"), "error": row.get("error", "not_evaluated")}
        for row in rows if row.get("status") == "unavailable"
    ]
    result = {
        "schema": "kama.gguf-identity-fixture-measurement.v1",
        "mode": "fixtures-only",
        "status": status,
        "base_revision": BASE_REVISION,
        "invocation": {
            "measurement_script": str(Path(__file__).resolve()),
            "python": sys.executable,
            "fixture_command_shape": [sys.executable, str(tool_path), "<fixture>", "--json"],
            "timeout_per_tool_invocation_seconds": timeout,
        },
        "frozen_before": frozen,
        "inputs": {
            "tool": tool_row,
            "reference_sha256": REFERENCE_SHA256,
            "expected_json": {"path": str(expected_path), "sha256": expected_digest},
            "model_read": False,
            "receipt_read": False,
            "oracle_read": False,
        },
        "fixtures": rows,
        "mismatches": [issue for issue in issues if issue["kind"] == "mismatch"] + row_mismatches,
        "snapshot_tampered": [
            issue for issue in issues if issue["kind"] == STATUS_SNAPSHOT_TAMPERED
        ],
        "unavailable": [issue for issue in issues if issue["kind"] == "unavailable"] + row_unavailable,
        "summary": {
            "fixtures_total": len(rows),
            "fixtures_passed": sum(row.get("status") == "pass" for row in rows),
            "fixtures_mismatched": sum(row.get("status") == "mismatch" for row in rows),
            "fixtures_snapshot_tampered": sum(row.get("status") == STATUS_SNAPSHOT_TAMPERED for row in rows),
            "fixtures_unavailable": sum(row.get("status") == "unavailable" for row in rows),
        },
    }
    return result, exit_code




def find_lane_root(script_path: Path | None = None) -> Path:
    script = (script_path or Path(__file__)).resolve()
    for candidate in script.parents:
        if (
            (candidate / "tools" / "gguf-identity.py").is_file()
            and (candidate / "registry").is_dir()
        ):
            return candidate
    raise UnavailableError("lane root not found through tools/ and registry/")


def default_paths() -> dict[str, Path]:
    lane_root = find_lane_root()
    build_out = lane_root / ".ufo" / "waves" / "round-20" / "build" / "out"
    final_tool_dir = build_out / "GgufTool-final"
    return {
        "expected": lane_root / "tests" / "gguf-identity" / "expected.json",
        "oracle": build_out / "GgufOracle" / "stories260K.oracle.json",
        "tool": lane_root / "tools" / "gguf-identity.py",
        "receipt_evidence": final_tool_dir / "stories260K-receipt.json",
        "model": Path("/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"),
        "receipt": lane_root / ".ufo" / "waves" / "round-18" / "live-recovery" / "receipt-1.json",
        "repo": lane_root,
        "reference": Path(__file__).resolve().with_name("measure-reference.json"),
    }

def make_parser() -> argparse.ArgumentParser:
    defaults = default_paths()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path, default=defaults["tool"], help="path to the integrated GGUF identity reader")
    parser.add_argument("--oracle", type=Path, default=defaults["oracle"], help="pinned gguf-py oracle JSON")
    parser.add_argument("--expected", type=Path, default=defaults["expected"], help="fixture expected.json")
    parser.add_argument("--model", type=Path, default=defaults["model"], help="existing stories260K.gguf")
    parser.add_argument("--receipt", type=Path, default=defaults["receipt"], help="existing v3 recovery receipt")
    parser.add_argument("--receipt-evidence", type=Path, default=defaults["receipt_evidence"], help="pinned parser receipt output")
    parser.add_argument("--repo", type=Path, default=defaults["repo"], help="repository used for frozen git-tree query")
    parser.add_argument("--reference", type=Path, default=defaults["reference"], help="independent pinned reference JSON")
    parser.add_argument("--timeout", type=float, default=10.0, help="per-invocation deadline in seconds")
    parser.add_argument("--transcript", type=Path, help="write the JSON result to this path")
    parser.add_argument("--json", action="store_true", help="accepted for wave recipe compatibility; output is always JSON")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--selftest", action="store_true", help="exercise deleted/relabelled fixture and wrong-oracle detection")
    modes.add_argument("--fixtures-only", action="store_true", help="run the bounded fixture matrix only")
    return parser


def emit(result: dict[str, Any], exit_code: int, transcript: Path | None = None) -> int:
    result["exit_code"] = exit_code
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    if transcript is not None:
        transcript.parent.mkdir(parents=True, exist_ok=True)
        transcript.write_text(text + "\n", encoding="utf-8")
    print(text)
    return exit_code


def main(argv: list[str] | None = None) -> int:
    args = None
    try:
        args = make_parser().parse_args(argv)
        if args.timeout <= 0 or args.timeout > 60:
            raise UnavailableError("timeout must be positive and no greater than 60 seconds")

        reference_facts = file_facts(args.reference, 256 * 1024)
        if reference_facts["sha256"] != REFERENCE_SHA256:
            issues: list[dict[str, Any]] = []
            add_issue(
                issues, STATUS_SNAPSHOT_TAMPERED, "reference.sha256",
                REFERENCE_SHA256, reference_facts["sha256"],
            )
            return emit({
                "schema": "kama.gguf-identity-fixture-measurement.v1",
                "status": STATUS_SNAPSHOT_TAMPERED,
                "snapshot_tampered": issues,
                "mismatches": [],
                "unavailable": [],
                "inputs": {"reference": {"path": str(args.reference), **reference_facts}},
            }, EXIT_CNE, args.transcript)

        _, reference = load_json(args.reference, limit=256 * 1024)
        if not isinstance(reference, dict) or reference.get("schema") != "kama.gguf-identity-measure-reference.v1":
            raise UnavailableError("reference file has an unsupported schema")
        if args.selftest:
            result, code = selftest(
                args.expected, args.oracle, args.receipt_evidence,
                args.reference, reference,
            )
            return emit(result, code, args.transcript)
        if args.fixtures_only:
            result, code = fixture_only_measure(
                args.expected, args.tool, args.repo, args.timeout, reference
            )
            if args.transcript is not None:
                result["transcript_path"] = str(args.transcript)
            return emit(result, code, args.transcript)

        expected_doc, expected_issues, fixture_states, expected_digest = validate_manifest_and_fixtures(
            args.expected, reference
        )
        oracle_doc, oracle_issues, oracle_digest = validate_oracle(args.oracle, reference)
        receipt_evidence, receipt_evidence_issues = validate_receipt_evidence(
            args.receipt_evidence, reference
        )
        issues = expected_issues + oracle_issues + receipt_evidence_issues
        snapshot_blocked = any(
            issue["kind"] == STATUS_SNAPSHOT_TAMPERED for issue in issues
        )

        try:
            tool_row = {"path": str(args.tool), **file_facts(args.tool, 1024 * 1024)}
            tool_available = True
        except UnavailableError as exc:
            tool_row = {"path": str(args.tool), "status": "unavailable", "error": type(exc).__name__}
            tool_available = False
            add_issue(issues, "unavailable", "tool", "readable regular script", type(exc).__name__)

        frozen = frozen_before(args.repo, reference)
        if frozen.get("status") == "unavailable":
            add_issue(issues, "unavailable", "frozen_before", "capability_absent", frozen.get("error"))
        elif frozen.get("status") != reference["frozen_before"]["expected_status"]:
            add_issue(
                issues, "mismatch", "frozen_before.status",
                reference["frozen_before"]["expected_status"], frozen.get("status"),
            )

        expected_by_id: dict[str, dict[str, Any]] = {}
        if expected_doc is not None and isinstance(expected_doc.get("fixtures"), list):
            expected_by_id = {
                item.get("id"): item
                for item in expected_doc["fixtures"]
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
        reason_equivalence = reference["fixture_manifest"]["reason_equivalence"]
        fixture_rows: list[dict[str, Any]] = []
        for pinned in reference["fixture_manifest"]["fixtures"]:
            if snapshot_blocked:
                fixture_rows.append({
                    "id": pinned["id"], "file": pinned["file"],
                    "status": STATUS_SNAPSHOT_TAMPERED, "error": "snapshot_tampered",
                })
                continue
            if not tool_available:
                fixture_rows.append({
                    "id": pinned["id"], "file": pinned["file"],
                    "status": "unavailable", "error": "tool_unavailable",
                })
                continue
            fixture_rows.append(measure_fixture(
                pinned,
                expected_by_id.get(pinned["id"]),
                fixture_states.get(pinned["id"], "unavailable"),
                args.expected.parent / pinned["file"],
                args.tool,
                args.timeout,
                reason_equivalence,
            ))

        if snapshot_blocked:
            model_row: dict[str, Any] = {
                "id": "stories260K.gguf",
                "status": STATUS_SNAPSHOT_TAMPERED,
                "parser_attempted": False,
                "error": "snapshot_tampered",
            }
        elif not tool_available:
            model_row = {
                "id": "stories260K.gguf",
                "status": "unavailable",
                "parser_attempted": False,
                "error": "tool_unavailable",
            }
        else:
            model_row, _ = measure_model(
                args.model, args.tool, args.receipt, args.timeout, reference
            )

        statuses = [row.get("status", "unavailable") for row in fixture_rows]
        statuses.extend((
            model_row.get("status", "unavailable"),
            receipt_evidence.get("status", "unavailable"),
            frozen.get("status", "unavailable"),
        ))
        statuses.extend(issue["kind"] for issue in issues)
        exit_code = code_for(statuses)
        all_rows = [*fixture_rows, model_row, receipt_evidence]
        overall = result_status(exit_code, issues, all_rows)
        row_mismatches = [
            {"row": row.get("id"), **finding}
            for row in (*fixture_rows, model_row)
            for finding in row.get("mismatches", [])
        ]
        row_unavailable = [
            {"row": row.get("id"), "error": row.get("error", "not_evaluated")}
            for row in (*fixture_rows, model_row, receipt_evidence)
            if row.get("status") == "unavailable"
        ]
        result = {
            "schema": "kama.gguf-identity-fixture-measurement.v1",
            "status": overall,
            "base_revision": BASE_REVISION,
            "invocation": {
                "measurement_script": str(Path(__file__).resolve()),
                "python": sys.executable,
                "tool": str(args.tool),
                "fixture_command_shape": [sys.executable, str(args.tool), "<fixture>", "--json"],
                "model_command": [
                    sys.executable, str(args.tool), str(args.model), "--json",
                    "--receipt", str(args.receipt),
                ],
                "timeout_per_tool_invocation_seconds": args.timeout,
            },
            "frozen_before": frozen,
            "inputs": {
                "reference": {"path": str(args.reference), "sha256": reference_facts["sha256"]},
                "tool": tool_row,
                "expected_json": {"path": str(args.expected), "sha256": expected_digest},
                "oracle_json": {"path": str(args.oracle), "sha256": oracle_digest},
                "receipt_evidence": receipt_evidence,
                "model": {
                    "path": str(args.model),
                    **({"sha256": model_row.get("sha256"), "size_bytes": model_row.get("size_bytes")}
                       if model_row.get("sha256") else {}),
                },
                "receipt": {"path": str(args.receipt), "parser_result": model_row.get("receipt")},
            },
            "fixtures": fixture_rows,
            "model": model_row,
            "receipt_reconciliation": model_row.get("receipt"),
            "mismatches": [issue for issue in issues if issue["kind"] == "mismatch"] + row_mismatches,
            "snapshot_tampered": [
                issue for issue in issues if issue["kind"] == STATUS_SNAPSHOT_TAMPERED
            ],
            "unavailable": [issue for issue in issues if issue["kind"] == "unavailable"] + row_unavailable,
            "summary": {
                "fixtures_total": len(fixture_rows),
                "fixtures_passed": sum(row.get("status") == "pass" for row in fixture_rows),
                "fixtures_mismatched": sum(row.get("status") == "mismatch" for row in fixture_rows),
                "fixtures_snapshot_tampered": sum(row.get("status") == STATUS_SNAPSHOT_TAMPERED for row in fixture_rows),
                "fixtures_unavailable": sum(row.get("status") == "unavailable" for row in fixture_rows),
                "oracle_validated": oracle_doc is not None and not oracle_issues,
                "receipt_evidence_validated": receipt_evidence.get("status") == "pass",
                "model_parser_observed": bool(model_row.get("parser_attempted")),
                "receipt_status": (model_row.get("receipt") or {}).get("status"),
            },
        }
        if args.transcript is not None:
            result["transcript_path"] = str(args.transcript)
        return emit(result, exit_code, args.transcript)
    except UnavailableError as exc:
        return emit({
            "schema": "kama.gguf-identity-fixture-measurement.v1",
            "status": "unavailable",
            "error": type(exc).__name__,
        }, EXIT_CNE, getattr(args, "transcript", None))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return emit({
            "schema": "kama.gguf-identity-fixture-measurement.v1",
            "status": "unavailable",
            "error": type(exc).__name__,
        }, EXIT_CNE, getattr(args, "transcript", None))


if __name__ == "__main__":
    raise SystemExit(main())
