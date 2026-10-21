"""Reconcile decoded GGUF metadata with one llama.cpp live v3 receipt.

The caller supplies the already-decoded flat GGUF metadata map and the SHA-256
of the exact GGUF file it opened.  Wire this module into gguf-identity.py by
adding --receipt RECEIPT and calling run_receipt_reconciliation() after decode.
The helper deliberately does not re-parse or copy GGUF bytes.

Exit codes: 0 reconciled (including an exceeds-train warning), 1
identity-mismatch, 2 receipt/input error.  --selftest integration can call
run_selftest() directly.
"""

import json
import re
import sys
from typing import Mapping


RECEIPT_SCHEMA_V3 = "kama-llamacpp-live/v3"
EXIT_OK = 0
EXIT_IDENTITY_MISMATCH = 1
EXIT_ERROR = 2
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class ReceiptReconciliationError(ValueError):
    """The supplied GGUF metadata or live receipt lacks usable evidence."""


def _mapping(value, label):
    if not isinstance(value, Mapping):
        raise ReceiptReconciliationError(label + " is not an object")
    return value


def _required_nonempty_string(mapping, key, label):
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ReceiptReconciliationError(label + " is missing or not a string")
    return value


def _positive_integer(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReceiptReconciliationError(
            label + " is missing or not a positive integer")
    return value


def _sha256(value, label):
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ReceiptReconciliationError(
            label + " is missing or not a lowercase SHA-256")
    return value


def reconcile_receipt(gguf_metadata, file_sha256, receipt):
    """Return a JSON-ready reconciliation result for decoded metadata.

    ``gguf_metadata`` is a flat key/value mapping with GGUF metadata names,
    including general.architecture, general.name, and
    <architecture>.context_length.  Only model_sha256_post binds the receipt
    to the file; model.sha256 and aliases are not identity authorities.
    """
    metadata = _mapping(gguf_metadata, "decoded GGUF metadata")
    document = _mapping(receipt, "receipt")
    actual_sha = _sha256(file_sha256, "decoded GGUF file sha256")

    if document.get("schema") != RECEIPT_SCHEMA_V3:
        raise ReceiptReconciliationError(
            "receipt schema is not " + RECEIPT_SCHEMA_V3)
    expected_sha = _sha256(document.get("model_sha256_post"),
                           "receipt model_sha256_post")
    if expected_sha != actual_sha:
        return {
            "status": "identity-mismatch",
            "exit_code": EXIT_IDENTITY_MISMATCH,
            "file_sha256": actual_sha,
            "model_sha256_post": expected_sha,
        }

    architecture = _required_nonempty_string(
        metadata, "general.architecture", "GGUF general.architecture")
    train_context = _positive_integer(
        metadata.get(architecture + ".context_length"),
        "GGUF " + architecture + ".context_length")
    general_name = metadata.get("general.name")
    if general_name is not None and not isinstance(general_name, str):
        raise ReceiptReconciliationError("GGUF general.name is not a string")

    captures = _mapping(document.get("captures"), "receipt captures")
    props = _mapping(captures.get("props"), "receipt captures.props")
    fields = _mapping(props.get("fields"), "receipt captures.props.fields")
    model_alias = _required_nonempty_string(
        fields, "model_alias", "receipt captures.props.fields.model_alias")
    served_context = _positive_integer(
        fields.get("default_generation_settings.n_ctx"),
        "receipt captures.props.fields.default_generation_settings.n_ctx")
    total_slots = _positive_integer(
        fields.get("total_slots"),
        "receipt captures.props.fields.total_slots")
    configured_alias = _required_nonempty_string(
        document, "alias", "receipt alias")
    configured_context = _positive_integer(document.get("ctx"), "receipt ctx")

    classification = ("exceeds-train" if served_context > train_context
                      else "within")
    warnings = []
    if classification == "exceeds-train":
        warnings.append(
            "served n_ctx exceeds GGUF declared training context")

    if general_name is None:
        alias_comparison = "unavailable"
    else:
        alias_comparison = "equal" if model_alias == general_name else "different"

    return {
        "status": "reconciled",
        "exit_code": EXIT_OK,
        "identity": {
            "status": "matched",
            "file_sha256": actual_sha,
            "model_sha256_post": expected_sha,
        },
        "context": {
            "architecture": architecture,
            "train_context_length": train_context,
            "served_n_ctx": served_context,
            "configured_ctx": configured_context,
            "total_slots": total_slots,
            "classification": classification,
            "warnings": warnings,
        },
        "names": {
            "general_name": general_name,
            "model_alias": model_alias,
            "configured_alias": configured_alias,
            "comparison": alias_comparison,
            "comparison_is_verdict": False,
        },
    }


def _load_receipt(path):
    try:
        with open(path, "r", encoding="utf-8") as stream:
            receipt = json.load(stream)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ReceiptReconciliationError(
            "cannot read receipt (" + type(exc).__name__ + ")") from None
    return _mapping(receipt, "receipt")


def run_receipt_reconciliation(gguf_metadata, file_sha256, receipt_path,
                               stdout=None, stderr=None):
    """Load --receipt input, emit one JSON result, and return its exit code."""
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    try:
        receipt = _load_receipt(receipt_path)
        result = reconcile_receipt(gguf_metadata, file_sha256, receipt)
    except ReceiptReconciliationError as exc:
        print("gguf-identity: receipt reconciliation error: " + str(exc),
              file=stderr)
        return EXIT_ERROR
    print(json.dumps(result, sort_keys=True, separators=(",", ":")),
          file=stdout)
    return result["exit_code"]


def run_selftest(stdout=None, stderr=None):
    """Exercise the status, identity, context-warning, and alias contracts."""
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    sha = "a" * 64
    metadata = {
        "general.architecture": "llama",
        "general.name": "Stories 260K",
        "llama.context_length": 2048,
    }
    base = {
        "schema": RECEIPT_SCHEMA_V3,
        "model_sha256_post": sha,
        "model": {"sha256": "b" * 64},
        "alias": "kama-stories260k",
        "ctx": 256,
        "captures": {"props": {"fields": {
            "model_alias": "kama-stories260k",
            "default_generation_settings.n_ctx": 256,
            "total_slots": 4,
        }}},
    }
    cases = 0

    result = reconcile_receipt(metadata, sha, base)
    assert result["exit_code"] == EXIT_OK
    assert result["identity"]["status"] == "matched"
    assert result["context"]["classification"] == "within"
    assert result["names"]["comparison"] == "different"
    assert result["names"]["comparison_is_verdict"] is False
    cases += 1

    no_slot_multiplication = json.loads(json.dumps(base))
    no_slot_multiplication["ctx"] = 4096
    no_slot_multiplication["captures"]["props"]["fields"][
        "default_generation_settings.n_ctx"] = 1024
    result = reconcile_receipt(metadata, sha, no_slot_multiplication)
    assert result["context"]["classification"] == "within"
    assert result["context"]["total_slots"] == 4
    assert result["context"]["configured_ctx"] == 4096
    cases += 1

    no_slot_division = json.loads(json.dumps(base))
    no_slot_division["ctx"] = 4096
    no_slot_division["captures"]["props"]["fields"][
        "default_generation_settings.n_ctx"] = 4096
    result = reconcile_receipt(metadata, sha, no_slot_division)
    assert result["context"]["classification"] == "exceeds-train"
    assert result["context"]["total_slots"] == 4
    cases += 1

    exact_boundary = json.loads(json.dumps(base))
    exact_boundary["captures"]["props"]["fields"][
        "default_generation_settings.n_ctx"] = 2048
    result = reconcile_receipt(metadata, sha, exact_boundary)
    assert result["context"]["classification"] == "within"
    cases += 1

    over_train = json.loads(json.dumps(base))
    over_train["captures"]["props"]["fields"][
        "default_generation_settings.n_ctx"] = 2049
    result = reconcile_receipt(metadata, sha, over_train)
    assert result["exit_code"] == EXIT_OK
    assert result["context"]["classification"] == "exceeds-train"
    assert result["context"]["warnings"]
    cases += 1

    post_mismatch = json.loads(json.dumps(base))
    post_mismatch["model_sha256_post"] = "c" * 64
    result = reconcile_receipt(metadata, sha, post_mismatch)
    assert result["exit_code"] == EXIT_IDENTITY_MISMATCH
    assert result["status"] == "identity-mismatch"
    cases += 1

    bad_schema = json.loads(json.dumps(base))
    bad_schema["schema"] = "kama-llamacpp-live/v2"
    try:
        reconcile_receipt(metadata, sha, bad_schema)
    except ReceiptReconciliationError:
        cases += 1
    else:
        print("selftest: non-v3 receipt was accepted", file=stderr)
        return EXIT_ERROR

    missing_context = json.loads(json.dumps(base))
    del missing_context["captures"]["props"]["fields"][
        "default_generation_settings.n_ctx"]
    try:
        reconcile_receipt(metadata, sha, missing_context)
    except ReceiptReconciliationError:
        cases += 1
    else:
        print("selftest: missing served n_ctx was accepted", file=stderr)
        return EXIT_ERROR

    print("selftest: {} receipt reconciliation cases passed".format(cases),
          file=stdout)
    return EXIT_OK
