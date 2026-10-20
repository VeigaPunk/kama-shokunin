#!/usr/bin/env python3
"""Kama round-14 offline Ollama tags/ps evidence replay measurement CLI.

Runs the lane's classifier CLI once per committed fixture, in its own temporary
directory, over caller-supplied exported JSON captures. Each fixture passes only
when the child's process exit code equals the fixture's literal ``expected_exit``,
the child's single JSON ``finding_id`` string equals ``expected_finding``, and
the same JSON document asserts ``schema == "kama-ollama-evidence/v1"``,
``verdict_exit`` equal to the process exit, ``readiness == "unknown"``, and
``scope == "offline-captures-not-runtime"``. Every mismatch is listed in the
record's ``reasons`` with independent expected/observed exit and ID retained.

The fixture document must declare at least 16 unique case names; a narrower or
duplicated corpus fails the whole measurement before any child is spawned.

Fixture document (default ``tests/ollama-evidence/cases.json``) is a JSON array
(or an object with a ``cases`` array) of objects:

    {"name": str, "tags": <JSON>|null, "ps": <JSON>|null, "expect": str,
     "expected_exit": int, "expected_finding": str}

Capture staging rules for ``tags`` and ``ps`` (both flags are always passed,
pointing at per-case ``tags.json``/``ps.json`` paths):

* an absent key or a JSON ``null`` leaves that file uncreated, so the child sees
  an unavailable input path and must fail closed;
* a JSON string is written verbatim as the capture file, which allows fixtures
  with byte-level malformed or empty JSON;
* any other JSON value is serialized as UTF-8 JSON to the capture file.

Each fixture runs in a temporary directory named only by its integer index; a
fixture's ``name`` is evidence text, never a filesystem path component.

This script is a test runner, not a domain classifier: it never classifies a
capture itself and has no fallback classifier. If ``--tool`` is absent or is not
a file, every fixture is recorded as ``unsupported`` and the run fails; nothing
is skipped. Every record carries ``readiness: "unknown"`` as a scope assertion:
even a matching loaded digest or a matching fixture expectation is metadata
correspondence only, never device readiness. Exit 0 only when at least one
fixture exists and every fixture passes, otherwise exit 1. Output is one JSON
object on stdout; no timestamps or liveness inferences are made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

WAVE = Path(__file__).resolve().parent
LANE = WAVE.parents[2]
DEFAULT_TOOL = LANE / "tools" / "kama-ollama-evidence.py"
DEFAULT_CASES = LANE / "tests" / "ollama-evidence" / "cases.json"

SCHEMA = "kama-round-14-measure/v1"
DOMAIN_SCHEMA = "kama-ollama-evidence/v1"
REQUIRED_SCOPE = "offline-captures-not-runtime"
REQUIRED_READINESS = "unknown"
SCOPE = REQUIRED_SCOPE  # harness output scope, same offline-capture boundary
READINESS = REQUIRED_READINESS
MINIMUM_UNIQUE_CASES = 16
CHILD_TIMEOUT_SECONDS = 30
TAIL_CHARS = 600
UNSUPPORTED = "unsupported"
EXIT_PASS = 0
EXIT_FAIL = 1

LIMITS = [
    "each fixture is graded on child process exit, finding_id, schema kama-ollama-evidence/v1, verdict_exit mirroring the process exit, readiness unknown, and scope offline-captures-not-runtime; every mismatch is listed in reasons",
    "fixtures are caller-supplied exported metadata; this harness performs no acquisition, network access, or runtime probe",
    "an absent, non-file, or unlaunchable tool marks every fixture unsupported and fails; no fallback classifier exists",
    "the case document must declare at least 16 unique fixture names; narrower or duplicated corpora fail before any child runs",
    "a passing run measures this fixed fixture set against one tool build; it makes no readiness, liveness, integration, or model-quality claim",
]


class MeasureError(Exception):
    """Unmeasured harness input; reported as JSON, never as a passing verdict."""


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # Keep exactly one JSON object on stdout even for bad argv.
        raise MeasureError(message)


def absolute(text):
    return Path(text).expanduser().resolve()


def sha256_file(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def tail(text):
    if not text:
        return None
    return text[-TAIL_CHARS:]


def load_cases(path):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise MeasureError(f"cannot read cases {path}: {exc}") from exc
    try:
        document = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise MeasureError(f"cases {path} is not valid UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise MeasureError(f"cases {path} is not valid JSON: {exc}") from exc
    if isinstance(document, list):
        cases = document
    elif isinstance(document, dict) and isinstance(document.get("cases"), list):
        cases = document["cases"]
    else:
        raise MeasureError(
            "cases document must be a JSON array of fixtures or an object with a 'cases' array"
        )
    return cases, hashlib.sha256(raw).hexdigest()


def case_name(case, index):
    if isinstance(case, dict):
        name = case.get("name")
        if isinstance(name, str) and name.strip():
            return name
    return f"case-{index:02d}"


def case_problems(case):
    if not isinstance(case, dict):
        return ["fixture is not a JSON object"]
    problems = []
    if not isinstance(case.get("expect"), str):
        problems.append("expect must be a string")
    expected_exit = case.get("expected_exit")
    if not isinstance(expected_exit, int) or isinstance(expected_exit, bool):
        problems.append("expected_exit must be an integer")
    if not isinstance(case.get("expected_finding"), str):
        problems.append("expected_finding must be a string")
    return problems


def record_triplet(case):
    if not isinstance(case, dict):
        return None, None, None
    return case.get("expect"), case.get("expected_exit"), case.get("expected_finding")


def unmeasured_record(case, index, detail, finding):
    expect, expected_exit, expected_finding = record_triplet(case)
    return {
        "name": case_name(case, index),
        "expect": expect if isinstance(expect, str) else None,
        "expected_exit": expected_exit if type(expected_exit) is int else None,
        "expected_finding": expected_finding if isinstance(expected_finding, str) else None,
        "readiness": READINESS,
        "observed_exit": None,
        "observed_finding": finding,
        "observed_schema": None,
        "observed_verdict_exit": None,
        "observed_readiness": None,
        "observed_scope": None,
        "passed": False,
        "reasons": [detail],
        "detail": detail,
    }


def invalid_record(case, index, problems):
    return unmeasured_record(
        case, index, "invalid fixture: " + "; ".join(problems), None
    )


def unsupported_record(case, index, detail):
    return unmeasured_record(case, index, detail, UNSUPPORTED)


def write_capture(path, value):
    if isinstance(value, str):
        Path(path).write_text(value, encoding="utf-8")
    else:
        # Byte-identical staging rule shared with the classifier's selftest.
        Path(path).write_text(
            json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8"
        )


def child_environment(case_dir):
    # Minimal, per-case environment: no inherited proxies or user paths, and
    # HOME/TMPDIR confined to the disposable fixture directory.
    return {
        "PATH": os.environ.get("PATH") or "/usr/bin:/bin",
        "HOME": str(case_dir),
        "TMPDIR": str(case_dir),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }


def measure_case(root, index, tool, case):
    problems = case_problems(case)
    if problems:
        return invalid_record(case, index, problems)

    name = case_name(case, index)
    expect = case["expect"]
    expected_exit = case["expected_exit"]
    expected_finding = case["expected_finding"]
    case_dir = root / f"{index:02d}"

    try:
        case_dir.mkdir(parents=True)
        tags_path = case_dir / "tags.json"
        ps_path = case_dir / "ps.json"
        if case.get("tags") is not None:
            write_capture(tags_path, case["tags"])
        if case.get("ps") is not None:
            write_capture(ps_path, case["ps"])
        argv = [
            sys.executable, "-I", "-B", str(tool),
            "--tags", str(tags_path),
            "--ps", str(ps_path),
            "--expect", expect,
        ]
    except OSError as exc:
        return unsupported_record(case, index, f"fixture staging failed: {exc}")

    try:
        proc = subprocess.run(
            argv,
            cwd=str(case_dir),
            env=child_environment(case_dir),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=CHILD_TIMEOUT_SECONDS,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return unsupported_record(
            case, index, f"child timed out after {CHILD_TIMEOUT_SECONDS}s"
        )
    except OSError as exc:
        return unsupported_record(case, index, f"child could not start: {exc}")

    observed_exit = proc.returncode
    observed_finding = None
    observed_schema = None
    observed_verdict_exit = None
    observed_readiness = None
    observed_scope = None
    detail = None
    parsed = False

    try:
        payload = json.loads(proc.stdout)
        parsed = True
    except json.JSONDecodeError as exc:
        detail = f"child stdout is not one JSON object: {exc}"

    if parsed:
        if isinstance(payload, dict):
            finding = payload.get("finding_id")
            if isinstance(finding, str):
                observed_finding = finding
            elif detail is None:
                detail = "child JSON has no string finding_id"
            schema = payload.get("schema")
            if isinstance(schema, str):
                observed_schema = schema
            verdict = payload.get("verdict_exit")
            if isinstance(verdict, int) and not isinstance(verdict, bool):
                observed_verdict_exit = verdict
            readiness = payload.get("readiness")
            if isinstance(readiness, str):
                observed_readiness = readiness
            scope = payload.get("scope")
            if isinstance(scope, str):
                observed_scope = scope
        elif detail is None:
            detail = "child JSON is not an object"

    reasons = []
    if detail is not None:
        reasons.append(detail)
    if observed_exit != expected_exit:
        reasons.append(
            f"exit {observed_exit!r} != expected {expected_exit!r}"
        )
    if parsed and isinstance(payload, dict):
        if observed_finding != expected_finding:
            reasons.append(
                f"finding_id {observed_finding!r} != expected {expected_finding!r}"
            )
        if observed_schema != DOMAIN_SCHEMA:
            reasons.append(
                f"schema {observed_schema!r} != required {DOMAIN_SCHEMA!r}"
            )
        if observed_verdict_exit != observed_exit:
            reasons.append(
                f"verdict_exit {observed_verdict_exit!r} != process exit {observed_exit!r}"
            )
        if observed_readiness != REQUIRED_READINESS:
            reasons.append(
                f"readiness {observed_readiness!r} != required {REQUIRED_READINESS!r}"
            )
        if observed_scope != REQUIRED_SCOPE:
            reasons.append(
                f"scope {observed_scope!r} != required {REQUIRED_SCOPE!r}"
            )

    passed = not reasons

    record = {
        "name": name,
        "expect": expect,
        "expected_exit": expected_exit,
        "expected_finding": expected_finding,
        "readiness": READINESS,
        "observed_exit": observed_exit,
        "observed_finding": observed_finding,
        "observed_schema": observed_schema,
        "observed_verdict_exit": observed_verdict_exit,
        "observed_readiness": observed_readiness,
        "observed_scope": observed_scope,
        "passed": passed,
        "reasons": reasons,
        "detail": detail,
    }
    if not passed:
        record["stderr_tail"] = tail(proc.stderr)
        if detail is not None and detail.startswith("child stdout"):
            record["stdout_tail"] = tail(proc.stdout)
    return record


def corpus_problems(cases):
    declared = []
    for case in cases:
        name = case.get("name") if isinstance(case, dict) else None
        if isinstance(name, str) and name.strip():
            declared.append(name.strip())
    unique = len(set(declared))
    problems = []
    if unique < MINIMUM_UNIQUE_CASES:
        problems.append(
            f"{unique} unique case names; at least {MINIMUM_UNIQUE_CASES} required"
        )
    return problems, unique


def run(args):
    tool = absolute(args.tool)
    cases_path = absolute(args.cases)
    cases, cases_sha = load_cases(cases_path)

    tool_present = tool.is_file()
    tool_sha = sha256_file(tool) if tool_present else None
    corpus, unique_names = corpus_problems(cases)
    records = []

    if corpus:
        corpus_detail = "corpus: " + "; ".join(corpus)
        for index, case in enumerate(cases):
            records.append(unmeasured_record(case, index, corpus_detail, None))
    elif tool_present:
        with tempfile.TemporaryDirectory(prefix="kama-r14-measure-") as tempdir:
            root = Path(tempdir)
            for index, case in enumerate(cases):
                records.append(measure_case(root, index, tool, case))
    else:
        detail = f"tool absent: {tool}"
        for index, case in enumerate(cases):
            problems = case_problems(case)
            if problems:
                records.append(invalid_record(case, index, problems))
            else:
                records.append(unsupported_record(case, index, detail))

    passed = sum(1 for record in records if record["passed"])
    failed = len(records) - passed
    verdict = EXIT_PASS if records and failed == 0 else EXIT_FAIL

    result = {
        "schema": SCHEMA,
        "scope": SCOPE,
        "readiness": READINESS,
        "tool": str(tool),
        "tool_present": tool_present,
        "tool_sha256": tool_sha,
        "cases": str(cases_path),
        "cases_sha256": cases_sha,
        "child_command": (
            "python -I -B <tool> --tags <tags.json> --ps <ps.json> --expect <expect>"
        ),
        "timeout_seconds": CHILD_TIMEOUT_SECONDS,
        "unique_case_names": unique_names,
        "minimum_unique_cases": MINIMUM_UNIQUE_CASES,
        "total": len(records),
        "passed": passed,
        "failed": failed,
        "records": records,
        "verdict_exit": verdict,
        "limits": LIMITS,
    }
    if corpus:
        result["error"] = "corpus: " + "; ".join(corpus)
    elif not records:
        result["error"] = "cases document contains no fixtures"
    return result, verdict


def error_result(message, args=None):
    tool = None
    cases = None
    tool_present = False
    if args is not None:
        tool = str(Path(args.tool).expanduser())
        cases = str(Path(args.cases).expanduser())
        try:
            tool_present = Path(tool).is_file()
        except OSError:
            tool_present = False
    return {
        "schema": SCHEMA,
        "scope": SCOPE,
        "readiness": READINESS,
        "tool": tool,
        "tool_present": tool_present,
        "tool_sha256": None,
        "cases": cases,
        "cases_sha256": None,
        "unique_case_names": 0,
        "minimum_unique_cases": MINIMUM_UNIQUE_CASES,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "records": [],
        "verdict_exit": EXIT_FAIL,
        "error": message,
        "limits": LIMITS,
    }


def build_parser():
    parser = Parser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--tool",
        default=str(DEFAULT_TOOL),
        help=f"child classifier CLI to measure (default: {DEFAULT_TOOL})",
    )
    parser.add_argument(
        "--cases",
        default=str(DEFAULT_CASES),
        help=f"fixture document to replay (default: {DEFAULT_CASES})",
    )
    return parser


def main(argv=None):
    args = None
    try:
        args = build_parser().parse_args(argv)
        result, code = run(args)
    except MeasureError as exc:
        result = error_result(str(exc), args)
        code = EXIT_FAIL
    except Exception as exc:  # never let an unexpected failure look clean
        result = error_result(f"{type(exc).__name__}: {exc}", args)
        code = EXIT_FAIL
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
