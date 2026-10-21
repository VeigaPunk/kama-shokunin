#!/usr/bin/env python3
"""Finite fail-closed fault matrix for kama-llamacpp-live.install_tree.

The frozen arm loads the producer blob from FROZEN_REVISION and pins its
source digest. The current arm loads only an explicit producer supplied with
--producer. Faults are injected at listdir, lstat, and sha256_file boundaries;
no host permission changes or service launch are used.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest import mock

LANE = Path(__file__).resolve().parents[2]
PRODUCER_REL = Path("tools/kama-llamacpp-live.py")
PRODUCER_PATH = LANE / PRODUCER_REL
FROZEN_REVISION = "10271460cc575fc2280aa831e442726385fc2319"
FROZEN_SOURCE_SHA256 = "cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023"

MEMBER_BYTES = {
    "llama-server": b"server-stub\n",
    "libllama.so.0.7.0": b"lib-0.7.0\n",
    "libllama.so.0.7.1": b"lib-0.7.1\n",
    "libmtmd.so.0.4.0": b"mtmd-0.4.0\n",
}
EXPECTED_TREE = {
    "llama-server": "ba28c4bd990ab8de10ba4e075aaaf1898cf6f8d1c8f9de965e86dd577d8ccf31",
    "libllama.so.0.7.0": "15bc1cbc5801222026914454b05098f5ca16e34b7c383cb670a857be904c889b",
    "libllama.so.0.7.1": "bc80a92210a4483f4ddb7691d71475caaeaf827776b3b7f80cd36a1a789a083b",
    "libmtmd.so.0.4.0": "51ae5bca00ba86fc93551e10ff0322b2eb13098c03fc47ff28183e11b166a0d3",
}
EXPECTED_TREE_SHA256 = "6d17af2a31e5fcf7e42e2abbb0bead8e9b79a2361f8d8dd0f286c11909277469"

# Literal, committed matrix oracle: do not derive rows from producer behavior.
FAULT_CASES = (
    ("listdir:permission", "listdir", None, PermissionError),
    ("listdir:oserror", "listdir", None, OSError),
    ("lstat:server:permission", "lstat", "llama-server", PermissionError),
    ("lstat:server:missing", "lstat", "llama-server", FileNotFoundError),
    ("lstat:server:oserror", "lstat", "llama-server", OSError),
    ("lstat:library:permission", "lstat", "libmtmd.so.0.4.0", PermissionError),
    ("lstat:library:missing", "lstat", "libmtmd.so.0.4.0", FileNotFoundError),
    ("lstat:library:oserror", "lstat", "libmtmd.so.0.4.0", OSError),
    ("read:server:permission", "read", "llama-server", PermissionError),
    ("read:server:missing", "read", "llama-server", FileNotFoundError),
    ("read:server:isdir", "read", "llama-server", IsADirectoryError),
    ("read:server:oserror", "read", "llama-server", OSError),
    ("read:library:permission", "read", "libmtmd.so.0.4.0", PermissionError),
    ("read:library:missing", "read", "libmtmd.so.0.4.0", FileNotFoundError),
    ("read:library:isdir", "read", "libmtmd.so.0.4.0", IsADirectoryError),
    ("read:library:oserror", "read", "libmtmd.so.0.4.0", OSError),
)
FAULT_IDS = tuple(row[0] for row in FAULT_CASES)
CONTROL_IDS = (
    "control:complete-map-digest",
    "control:subdir-member-skipped",
    "control:symlink-member-skipped",
)


class MatrixUnavailable(Exception):
    """A pinned source blob or required local input cannot be obtained."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source(arm: str, producer_path: Path | None) -> tuple[bytes, str, Path]:
    if arm == "frozen":
        try:
            proc = subprocess.run(
                ["git", "-C", str(LANE), "show",
                 f"{FROZEN_REVISION}:{PRODUCER_REL.as_posix()}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
        except OSError as exc:
            raise MatrixUnavailable(f"cannot invoke git for frozen producer: {type(exc).__name__}") from exc
        if proc.returncode:
            raise MatrixUnavailable(f"cannot read pinned producer blob (git exit {proc.returncode})")
        source = proc.stdout
        digest = _sha256(source)
        if digest != FROZEN_SOURCE_SHA256:
            raise MatrixUnavailable(f"frozen producer digest mismatch: {digest}")
        return source, digest, PRODUCER_PATH
    if producer_path is None:
        raise MatrixUnavailable("current arm requires an explicit --producer path")
    try:
        path = producer_path.resolve()
        source = path.read_bytes()
    except OSError as exc:
        raise MatrixUnavailable(f"cannot read explicit producer: {type(exc).__name__}") from exc
    return source, _sha256(source), path


def _load_module(arm: str, producer_path: Path | None) -> tuple[ModuleType, str]:
    source, digest, source_path = _source(arm, producer_path)
    module = ModuleType(f"_install_tree_matrix_{arm}")
    module.__file__ = str(source_path)
    try:
        exec(compile(source, str(source_path), "exec"), module.__dict__)
    except Exception as exc:
        raise MatrixUnavailable(f"cannot load {arm} producer: {type(exc).__name__}") from exc
    if not callable(getattr(module, "install_tree", None)) \
            or not isinstance(getattr(module, "SetupError", None), type):
        raise MatrixUnavailable(f"{arm} producer lacks install_tree/SetupError")
    return module, digest


def _temporary_directory(prefix: str):
    try:
        return tempfile.TemporaryDirectory(prefix=prefix)
    except OSError as exc:
        raise MatrixUnavailable(f"cannot create matrix fixture directory: {type(exc).__name__}") from exc


def _make_fixture(directory: Path, ignored: str | None = None) -> str:
    try:
        for name, body in MEMBER_BYTES.items():
            (directory / name).write_bytes(body)
        if ignored == "symlink":
            os.symlink("libllama.so.0.7.0", directory / "libllama.so.0")
        elif ignored == "directory":
            nested = directory / "openvino-licensing"
            nested.mkdir()
            (nested / "LICENSE.txt").write_bytes(b"not part of the top-level map\n")
    except OSError as exc:
        raise MatrixUnavailable(f"cannot prepare matrix fixture: {type(exc).__name__}") from exc
    return str(directory / "llama-server")




def _expected_exception(exc_type: type[BaseException], path: str) -> BaseException:
    if exc_type is PermissionError:
        return PermissionError(errno.EACCES, "matrix-injected", path)
    if exc_type is FileNotFoundError:
        return FileNotFoundError(errno.ENOENT, "matrix-injected", path)
    if exc_type is IsADirectoryError:
        return IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR), path)
    return OSError(errno.EIO, "matrix-injected", path)


def _combined_digest(tree: dict) -> str:
    lines = "".join(f"{name} {tree[name]}\n" for name in sorted(tree))
    return _sha256(lines.encode("utf-8"))


def _observe(module: ModuleType, server: str) -> dict:
    try:
        result = module.install_tree(server)
    except Exception as exc:
        error_code = getattr(exc, "code", None)
        if isinstance(exc, module.SetupError):
            outcome = "refused" if error_code == "install-tree-unpinnable" else "refused-wrong-token"
        else:
            outcome = "refused-untyped"
        cause = exc.__cause__
        return {
            "observed": outcome,
            "exception": type(exc).__name__,
            "error_message": str(exc),
            "error_code": str(error_code) if error_code is not None else None,
            "cause": type(cause).__name__ if cause is not None else None,
            "cause_errno": getattr(cause, "errno", None),
            "tree_keys": None,
            "digest": None,
            "digest_self_consistent": False,
        }
    if not isinstance(result, tuple) or len(result) != 2:
        return {
            "observed": "escaped-invalid",
            "exception": None,
            "error_code": None,
            "cause": None,
            "cause_errno": None,
            "tree_keys": None,
            "digest": None,
            "digest_self_consistent": False,
        }
    tree, digest = result
    keys = sorted(tree) if isinstance(tree, dict) and all(isinstance(k, str) for k in tree) else None
    if digest is None:
        observed = "escaped-null"
        consistent = False
    elif not isinstance(digest, str) or keys is None:
        observed = "escaped-invalid"
        consistent = False
    else:
        consistent = _combined_digest(tree) == digest
        if tree == EXPECTED_TREE and digest == EXPECTED_TREE_SHA256:
            observed = "complete"
        elif consistent:
            observed = "escaped-partial"
        else:
            observed = "escaped-invalid"
    return {
        "observed": observed,
        "exception": None,
        "error_code": None,
        "cause": None,
        "cause_errno": None,
        "tree_keys": keys,
        "digest": digest if isinstance(digest, str) else None,
        "digest_self_consistent": consistent,
    }


def _fault_row(module: ModuleType, case: tuple) -> dict:
    case_id, operation, member, exc_type = case
    with _temporary_directory("install-io-grid-") as temporary:
        directory = Path(temporary)
        server = _make_fixture(directory)
        injection = {"calls": 0, "raised": 0}
        real_directory = os.path.realpath(directory)
        target = real_directory if operation == "listdir" else member

        def matches_member(path) -> bool:
            value = os.fspath(path)
            return os.path.basename(value) == target \
                and os.path.realpath(os.path.dirname(value)) == real_directory

        def inject(path: str) -> None:
            injection["calls"] += 1
            injection["raised"] += 1
            raise _expected_exception(exc_type, path)

        if operation == "listdir":
            original = module.os.listdir

            def replacement(path):
                if os.path.realpath(os.fspath(path)) == target:
                    inject(os.fspath(path))
                return original(path)

            patch = mock.patch.object(module.os, "listdir", new=replacement)
        elif operation == "lstat":
            original = module.os.lstat

            def replacement(path):
                if matches_member(path):
                    inject(os.fspath(path))
                return original(path)

            patch = mock.patch.object(module.os, "lstat", new=replacement)
        else:
            original = module.sha256_file

            def replacement(path):
                if matches_member(path):
                    inject(os.fspath(path))
                return original(path)

            patch = mock.patch.object(module, "sha256_file", new=replacement)

        with patch:
            observation = _observe(module, server)

    activated = injection["calls"] == 1 and injection["raised"] == 1
    observed = observation["observed"]
    if observed == "complete":
        observed = "escaped-complete"
    if not activated:
        observed = "error"
    return {
        "id": case_id,
        "operation": operation,
        "member": member,
        "injected_exception": exc_type.__name__,
        "injected_errno": _expected_exception(exc_type, target).errno,
        "injected_calls": injection["calls"],
        "injected_exception_raised": bool(injection["raised"]),
        "injection_activated": activated,
        "observed": observed,
        "operation_outcome": observation["observed"],
        "exception": "injection-not-reached" if not activated else observation["exception"],
        "error_message": observation.get("error_message"),
        "error_code": observation["error_code"],
        "cause": observation["cause"],
        "cause_errno": observation["cause_errno"],
        "returned_identity": observation["tree_keys"] is not None,
        "tree_keys": observation["tree_keys"],
        "digest": observation["digest"],
        "digest_self_consistent": observation["digest_self_consistent"],
    }

def _control_row(module: ModuleType, control_id: str) -> dict:
    with _temporary_directory("install-io-grid-control-") as temporary:
        directory = Path(temporary)
        ignored = {
            CONTROL_IDS[1]: "directory",
            CONTROL_IDS[2]: "symlink",
        }.get(control_id)
        server = _make_fixture(directory, ignored=ignored)
        observation = _observe(module, server)
    complete = observation["observed"] == "complete"
    return {
        "id": control_id,
        **observation,
        "matches_pinned_map_and_digest": complete,
    }


def _run_arm(arm: str, producer_path: Path | None) -> dict:
    module, source_digest = _load_module(arm, producer_path)
    faults = [_fault_row(module, case) for case in FAULT_CASES]
    controls = [_control_row(module, control_id) for control_id in CONTROL_IDS]
    refused = sum(row["observed"] == "refused" and row["injection_activated"] for row in faults)
    escaped = sum(row["observed"].startswith("escaped-") and row["injection_activated"] for row in faults)
    errors = sum(row["observed"] == "error" or row["observed"] == "refused-untyped"
                 or row["observed"] == "refused-wrong-token" for row in faults)
    unarmed = sum(not row["injection_activated"] for row in faults)
    controls_ok = all(row["matches_pinned_map_and_digest"] for row in controls)
    property_pass = refused == len(FAULT_CASES) and errors == 0 \
        and unarmed == 0 and controls_ok

    def legacy_escape(row: dict) -> bool:
        if not row["injection_activated"]:
            return False
        if row["operation"] == "listdir":
            return row["operation_outcome"] == "escaped-null" \
                and row["tree_keys"] == [] and row["digest"] is None
        return row["operation_outcome"] == "escaped-partial" \
            and row["tree_keys"] is not None \
            and row["member"] not in row["tree_keys"] \
            and row["digest"] is not None and row["digest_self_consistent"]

    baseline_red = all(legacy_escape(row) for row in faults) and controls_ok
    unavailable = unarmed > 0 and controls_ok
    return {
        "arm": arm,
        "source_sha256": source_digest,
        "fault_population": len(faults),
        "fault_counts": {
            "refused": refused,
            "escaped": escaped,
            "error": errors,
            "injection_not_reached": unarmed,
        },
        "incomplete_identity_escapes": sum(
            row["injection_activated"]
            and row["operation_outcome"] in ("escaped-null", "escaped-partial")
            for row in faults
        ),
        "faults": faults,
        "controls": controls,
        "controls_ok": controls_ok,
        "property_pass": property_pass,
        "baseline_red": baseline_red,
        "unavailable": unavailable,
    }




def _expected_fixture_pins() -> bool:
    tree = {name: _sha256(body) for name, body in MEMBER_BYTES.items()}
    combined = _combined_digest(tree)
    return tree == EXPECTED_TREE and combined == EXPECTED_TREE_SHA256


def _arm_exit(result: dict) -> int:
    if not result["controls_ok"]:
        return 1
    if any(row["injection_activated"] and row["observed"] != "refused"
           for row in result["faults"]):
        return 1
    if result["unavailable"]:
        return 2
    return 0


def _execute(args: argparse.Namespace) -> tuple[dict, int]:
    if args.selftest:
        if not _expected_fixture_pins() or len(FAULT_CASES) != 16 \
                or len(set(FAULT_IDS)) != len(FAULT_IDS) \
                or len(CONTROL_IDS) != 3 or len(set(CONTROL_IDS)) != len(CONTROL_IDS):
            return {"selftest": "failed", "reason": "pinned-fixture-or-case-oracle"}, 1
        try:
            frozen = _run_arm("frozen", args.producer)
            current = _run_arm("current", args.producer)
        except MatrixUnavailable as exc:
            return {"selftest": "unavailable", "reason": str(exc)}, 2
        current_code = _arm_exit(current)
        if current_code == 1:
            return {"selftest": "failed", "arms": [frozen, current]}, 1
        if current_code == 2 or frozen["unavailable"]:
            return {"selftest": "unavailable", "arms": [frozen, current]}, 2
        clean = frozen["baseline_red"] and current["property_pass"]
        return {
            "selftest": "clean" if clean else "failed",
            "expected": {"frozen": "all-faults-escape", "current": "all-faults-refuse"},
            "arms": [frozen, current],
        }, 0 if clean else 1

    arms = ("frozen", "current") if args.arm == "both" else (args.arm,)
    results = []
    try:
        results = [_run_arm(arm, args.producer) for arm in arms]
    except MatrixUnavailable as exc:
        return {"status": "unavailable", "reason": str(exc), "arms": results}, 2

    if args.arm == "both":
        frozen, current = results
        current_code = _arm_exit(current)
        if current_code == 1:
            return {"status": "violated-property", "arms": results}, 1
        if current_code == 2 or frozen["unavailable"]:
            return {"status": "unavailable", "arms": results}, 2
        clean = frozen["baseline_red"] and current["property_pass"]
    else:
        code = _arm_exit(results[0])
        if code == 2:
            return {"status": "unavailable", "arms": results}, 2
        clean = results[0]["property_pass"]
    return {
        "status": "clean" if clean else "violated-property",
        "arms": results,
    }, 0 if clean else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("frozen", "current", "both"), default="current")
    parser.add_argument("--producer", type=Path,
                        help="explicit current producer path; required for current/both/selftest")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--selftest", action="store_true", help="check pinned red-before/green-after behavior")
    args = parser.parse_args(argv)
    try:
        result, exit_code = _execute(args)
    except Exception as exc:
        # Harness/runtime failures are could-not-evaluate, not property evidence.
        result, exit_code = {
            "status": "unavailable",
            "error": type(exc).__name__,
            "detail": str(exc),
        }, 2
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
