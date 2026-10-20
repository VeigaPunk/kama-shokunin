#!/usr/bin/env python3
"""Kama corpus-guard test CLI for the round-14 measurement runner.

For the committed literal matrix shipped in this directory, this harness
checks that the measurement runner (default
``.ufo/waves/round-14/measure.py``) rejects every duplicate-name control
before ANY child classifier process is spawned, and that every valid
all-distinct control corpus still measures. The claim is bounded to those
committed literals; it is not a universal guarantee about arbitrary
corpora.

The committed literal matrix is every sibling ``*.json`` file in this
directory, read in sorted order. Each file is a JSON array of objects:

    {"name": <unique test id>, "names": [<literal case name>, ...],
     "envelope": "array" | "object", "expected_rejected": bool}

For each test the harness stages an isolated temporary corpus by cloning
the first known passing fixture of ``tests/ollama-evidence/cases.json`` and
replacing only the ``name`` field, one clone per ``names`` entry, emitted
as a bare JSON array (``array``) or ``{"cases": [...]}`` (``object``).

Two independent spawn observations are recorded per test:

* a temporary classifier wrapper that appends one line to a marker file
  and then executes the real ``tools/kama-ollama-evidence.py`` through
  ``runpy.run_path`` as ``__main__`` -- its process exit propagates
  unchanged, so the runner exercises the real domain classifier CLI
  contract through a real child process;
* a temporary runner launcher that installs ``sys.addaudithook`` for
  listed process-creation audit events (``subprocess.Popen``, ``os.system``,
  ``os.posix_spawn*``, ``os.fork*``, ``os.exec*``, ``_posixsubprocess.fork_exec``), appending each event to
  an audit file, then executes the real runner through
  ``runpy.run_path`` as ``__main__``.

A rejected expectation requires exit 1, a ``duplicate case names`` error,
``passed == 0``, ``failed == total == len(names)``, ``tool_present`` true,
``observed_exit`` null on every record, marker count 0 and runner process
event count 0. An accepted expectation requires exit 0, ``passed ==
total == len(names)``, ``failed == 0``, marker count ``len(names)`` and
runner ``subprocess.Popen`` count ``len(names)``.

The harness performs no network access and embeds no classifier: it only
stages files, launches the audited runner subprocess, and grades the
result JSON. A missing, empty, or malformed matrix fails closed with
``finding_id: test_failed`` and exit 1. ``--selftest`` runs the same
committed literal matrix (the only mode this CLI has); ``--only TEST``
restricts the run to one test id.
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

CHECK_DIR = Path(__file__).resolve().parent
LANE = CHECK_DIR.parents[1]
DEFAULT_RUNNER = LANE / ".ufo" / "waves" / "round-14" / "measure.py"
CLASSIFIER = LANE / "tools" / "kama-ollama-evidence.py"
SOURCE_CASES = LANE / "tests" / "ollama-evidence" / "cases.json"

SCHEMA = "kama-corpus-guard-test/v1"
DUPLICATE_REASON = "duplicate case names"
MINIMUM_UNIQUE_CASES = 16
PER_CASE_CHILD_TIMEOUT = 30  # mirrors the runner's CHILD_TIMEOUT_SECONDS
RUNNER_TIMEOUT_SLACK = 120
TAIL_CHARS = 600
EXIT_CLEAN = 0
EXIT_FAILED = 1

# Listed audit-hook prefixes recorded by the runner launcher; not an
# exhaustive or malicious-runner process-containment boundary.
PROCESS_EVENT_PREFIXES = (
    "subprocess.Popen",
    "_posixsubprocess.fork_exec",
    "os.system",
    "os.posix_spawn",
    "os.fork",
    "os.exec",
)

LIMITS = [
    "the marker proves the classifier wrapper ran; it counts wrapper process "
    "entries, not classifier internals, and cannot observe the runner "
    "itself",
    "the audit hook runs inside the runner process and observes only the "
    "runner's own process-creation calls; grandchildren of children are not "
    "attributed",
    "a benign runner that spawns extra non-classifier helpers is not "
    "distinguished from the measured classifier children",
    "this harness gives no malicious-runner or security guarantee; it grades "
    "the committed corpus-guard contract only",
]


class HarnessError(Exception):
    """Unmeasurable harness or matrix input; reported as JSON, never clean."""


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # Keep exactly one JSON object on stdout even for bad argv.
        raise HarnessError(message)


def tail(text):
    if not text:
        return None
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    return text[-TAIL_CHARS:]


def sha256_file(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def load_json_file(path, label):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise HarnessError(f"cannot read {label} {path}: {exc}") from exc
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise HarnessError(f"{label} {path} is not valid UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"{label} {path} is not valid JSON: {exc}") from exc


def load_matrix():
    """Read every sibling *.json matrix file in sorted order, fail closed."""
    sources = sorted(
        path for path in CHECK_DIR.glob("*.json") if path.is_file()
    )
    if not sources:
        raise HarnessError(
            f"test matrix absent: no *.json files in {CHECK_DIR}"
        )
    tests = []
    seen = {}
    problems = []
    for source in sources:
        document = load_json_file(source, "matrix file")
        if not isinstance(document, list):
            problems.append(f"{source.name}: matrix document is not an array")
            continue
        for index, test in enumerate(document):
            where = f"{source.name}[{index}]"
            if not isinstance(test, dict):
                problems.append(f"{where}: test is not an object")
                continue
            name = test.get("name")
            names = test.get("names")
            envelope = test.get("envelope")
            expected = test.get("expected_rejected")
            if not isinstance(name, str) or not name:
                problems.append(f"{where}: name is not a non-empty string")
                continue
            if name in seen:
                problems.append(
                    f"{where}: test id {name!r} duplicates {seen[name]}"
                )
                continue
            if (
                not isinstance(names, list)
                or not names
                or not all(isinstance(item, str) for item in names)
            ):
                problems.append(
                    f"{where}: names is not a non-empty string array"
                )
                continue
            if envelope not in ("array", "object"):
                problems.append(
                    f"{where}: envelope {envelope!r} is not 'array' or 'object'"
                )
                continue
            if not isinstance(expected, bool):
                problems.append(
                    f"{where}: expected_rejected is not a boolean"
                )
                continue
            stripped = [item.strip() for item in names]
            distinct = len(set(stripped))
            if distinct < MINIMUM_UNIQUE_CASES:
                problems.append(
                    f"{where}: {distinct} distinct stripped names; "
                    f"at least {MINIMUM_UNIQUE_CASES} required so the "
                    f"minimum-corpus guard cannot mask the duplicate guard"
                )
                continue
            if expected and distinct == len(stripped):
                problems.append(
                    f"{where}: rejected control has no duplicate "
                    "stripped name"
                )
                continue
            if not expected and distinct != len(stripped):
                problems.append(
                    f"{where}: valid control has duplicate stripped names"
                )
                continue
            seen[name] = where
            tests.append(
                {
                    "name": name,
                    "names": names,
                    "envelope": envelope,
                    "expected_rejected": expected,
                    "source": source.name,
                }
            )
    if problems:
        raise HarnessError("invalid test matrix: " + "; ".join(problems))
    if not tests:
        raise HarnessError("test matrix is empty")
    return tests, [source.name for source in sources]


def load_template():
    """Return the first known passing fixture of the committed cases.

    The clone source must be a literal fixture that is known to measure
    clean (``expected_exit`` 0); no lesser fixture is substituted, so an
    absent passing fixture fails the harness instead of guessing.
    """
    document = load_json_file(SOURCE_CASES, "source cases")
    if isinstance(document, dict):
        document = document.get("cases")
    if not isinstance(document, list):
        raise HarnessError(f"source cases {SOURCE_CASES} is not an array")
    for case in document:
        if not isinstance(case, dict):
            continue
        if (
            isinstance(case.get("expect"), str)
            and case.get("expected_exit") == 0
            and type(case.get("expected_exit")) is int
            and isinstance(case.get("expected_finding"), str)
        ):
            return json.loads(json.dumps(case))
    raise HarnessError(
        f"source cases {SOURCE_CASES} has no known passing "
        "(expected_exit 0) fixture to clone"
    )


def write_launcher(directory, audit_path, runner):
    """Write the audited launcher bound to the selected runner path.

    The launcher installs an audit hook over the runner's process-creation
    surface before executing the real runner file as ``__main__``; every
    matching event name is appended to the audit file. ``repr()`` keeps
    the generated source valid for any path text, and no exception is
    caught, so runner failures keep their exit status instead of being
    swallowed into a false zero count.
    """
    launcher = directory / "runner_launcher.py"
    launcher.write_text(
        "import runpy\n"
        "import sys\n"
        "\n"
        f"AUDIT = {str(audit_path)!r}\n"
        f"RUNNER = {str(runner)!r}\n"
        f"PREFIXES = {PROCESS_EVENT_PREFIXES!r}\n"
        "\n"
        "def _hook(event, args):\n"
        "    if event.startswith(PREFIXES):\n"
        '        with open(AUDIT, "a", encoding="utf-8") as stream:\n'
        '            stream.write(event + "\\n")\n'
        "\n"
        "sys.addaudithook(_hook)\n"
        "sys.argv[0] = RUNNER\n"
        'runpy.run_path(RUNNER, run_name="__main__")\n',
        encoding="utf-8",
    )
    return launcher


def write_wrapper(directory, marker_path):
    """Write the classifier wrapper bound to one test's marker file.

    The wrapper appends one line to the marker, then executes the real
    domain classifier as ``__main__`` through runpy, so the runner
    exercises the real classifier CLI contract inside a real child
    process and the child's exit code propagates unchanged.
    """
    wrapper = directory / "classifier_wrapper.py"
    wrapper.write_text(
        "import runpy\n"
        "\n"
        f"MARKER = {str(marker_path)!r}\n"
        f"TOOL = {str(CLASSIFIER)!r}\n"
        "\n"
        'with open(MARKER, "a", encoding="utf-8") as stream:\n'
        '    stream.write("x\\n")\n'
        'runpy.run_path(TOOL, run_name="__main__")\n',
        encoding="utf-8",
    )
    return wrapper


def run_environment(root):
    # Minimal environment: no inherited proxies or user paths, HOME/TMPDIR
    # confined to this test's harness directory so every runner write (its
    # TemporaryDirectory included) lands inside the removed temp tree.
    return {
        "PATH": os.environ.get("PATH") or "/usr/bin:/bin",
        "HOME": str(root),
        "TMPDIR": str(root),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }


def count_lines(path):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    return sum(1 for line in text.splitlines() if line)


def measure_test(index, test, template, runner, temp_root):
    """Run one matrix entry against the audited runner; grade the result."""
    total = len(test["names"])
    names = test["names"]
    test_dir = temp_root / f"test-{index:03d}"
    test_dir.mkdir(parents=True)
    # Marker and audit are precreated empty so 'missing' and 'zero'
    # observations cannot alias each other.
    marker_path = test_dir / "classifier_marker.txt"
    audit_path = test_dir / "runner_audit.txt"
    marker_path.write_text("", encoding="utf-8")
    audit_path.write_text("", encoding="utf-8")
    test_wrapper = write_wrapper(test_dir, marker_path)
    test_launcher = write_launcher(test_dir, audit_path, runner)

    cases = []
    for name in names:
        case = json.loads(json.dumps(template))
        case["name"] = name
        cases.append(case)
    cases_path = test_dir / "cases.json"
    if test["envelope"] == "object":
        document = {"cases": cases}
    else:
        document = cases
    cases_path.write_text(
        json.dumps(document, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    argv = [
        sys.executable,
        "-I",
        "-B",
        str(test_launcher),
        "--tool",
        str(test_wrapper),
        "--cases",
        str(cases_path),
    ]
    timeout = PER_CASE_CHILD_TIMEOUT * total + RUNNER_TIMEOUT_SLACK

    try:
        proc = subprocess.run(
            argv,
            cwd=str(test_dir),
            env=run_environment(test_dir),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        return test_record(
            test,
            argv,
            reasons=[
                f"runner timed out after {timeout}s "
                f"(expected within {PER_CASE_CHILD_TIMEOUT}s x {total} "
                f"cases + {RUNNER_TIMEOUT_SLACK}s slack)"
            ],
            stdout=exc.stdout,
            stderr=exc.stderr,
            marker_path=marker_path,
            audit_path=audit_path,
            total=total,
        )
    except OSError as exc:
        return test_record(
            test,
            argv,
            reasons=[f"runner could not start: {exc}"],
            stdout=None,
            stderr=None,
            marker_path=marker_path,
            audit_path=audit_path,
            total=total,
        )

    return grade(test, argv, proc, marker_path, audit_path, total)


def audit_observation(audit_lines):
    """Project the recorded audit events into count, histogram and list."""
    if audit_lines is None:
        return {
            "runner_process_events": None,
            "runner_popen_events": None,
            "runner_event_histogram": None,
            "runner_event_list": None,
        }
    histogram = {}
    for line in audit_lines:
        histogram[line] = histogram.get(line, 0) + 1
    return {
        "runner_process_events": len(audit_lines),
        "runner_popen_events": histogram.get("subprocess.Popen", 0),
        "runner_event_histogram": histogram,
        "runner_event_list": audit_lines,
    }


def test_record(test, argv, reasons, stdout, stderr, marker_path, audit_path,
                total):
    marker_count = count_lines(marker_path)
    audit_lines = read_audit(audit_path)
    observed = {
        "exit": None,
        "payload_parsed": False,
        "classifier_invocations": marker_count,
    }
    observed.update(audit_observation(audit_lines))
    record = {
        "name": test["name"],
        "source": test["source"],
        "envelope": test["envelope"],
        "expected": {
            "rejected": test["expected_rejected"],
            "total": total,
        },
        "observed": observed,
        "child_count": marker_count,
        "command": argv,
        "stdout_tail": tail(stdout),
        "stderr_tail": tail(stderr),
        "passed": False,
        "reasons": reasons,
    }
    if marker_count is None:
        record["reasons"].append("classifier marker file missing or unreadable")
    if audit_lines is None:
        record["reasons"].append("runner audit file missing or unreadable")
    return record


def read_audit(path):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    return [line for line in text.splitlines() if line]


def grade(test, argv, proc, marker_path, audit_path, total):
    expected_rejected = test["expected_rejected"]
    reasons = []
    marker_count = count_lines(marker_path)
    audit_lines = read_audit(audit_path)
    process_events = None if audit_lines is None else len(audit_lines)
    popen_events = (
        None
        if audit_lines is None
        else sum(
            1 for line in audit_lines if line.startswith("subprocess.Popen")
        )
    )

    payload = None
    parsed = False
    try:
        payload = json.loads(proc.stdout)
        parsed = True
    except json.JSONDecodeError as exc:
        reasons.append(f"runner stdout is not one JSON object: {exc}")

    observed = {
        "exit": proc.returncode,
        "payload_parsed": parsed and isinstance(payload, dict),
        "classifier_invocations": marker_count,
    }
    observed.update(audit_observation(audit_lines))
    if marker_count is None:
        reasons.append("classifier marker file missing or unreadable")
    if audit_lines is None:
        reasons.append("runner audit file missing or unreadable")

    result_payload = payload if isinstance(payload, dict) else {}
    observed["verdict_exit"] = result_payload.get("verdict_exit")
    observed["passed"] = result_payload.get("passed")
    observed["failed"] = result_payload.get("failed")
    observed["total"] = result_payload.get("total")
    observed["error"] = result_payload.get("error")
    observed["tool_present"] = result_payload.get("tool_present")
    records = result_payload.get("records")
    null_exit_records = None
    if isinstance(records, list):
        null_exit_records = sum(
            1
            for record in records
            if isinstance(record, dict) and record.get("observed_exit") is None
        )
    observed["null_observed_exit_records"] = null_exit_records

    if expected_rejected:
        if proc.returncode != 1:
            reasons.append(f"exit {proc.returncode!r} != expected 1")
        if result_payload.get("verdict_exit") != 1:
            reasons.append(
                f"verdict_exit {result_payload.get('verdict_exit')!r} "
                "!= expected 1"
            )
        error = result_payload.get("error")
        if not (isinstance(error, str) and DUPLICATE_REASON in error):
            reasons.append(
                f"error {error!r} does not include {DUPLICATE_REASON!r}"
            )
        if result_payload.get("passed") != 0:
            reasons.append(
                f"passed {result_payload.get('passed')!r} != expected 0"
            )
        if result_payload.get("failed") != total:
            reasons.append(
                f"failed {result_payload.get('failed')!r} != expected {total}"
            )
        if result_payload.get("total") != total:
            reasons.append(
                f"total {result_payload.get('total')!r} != expected {total}"
            )
        if result_payload.get("tool_present") is not True:
            reasons.append(
                f"tool_present {result_payload.get('tool_present')!r} "
                "!= expected True"
            )
        if null_exit_records != total:
            reasons.append(
                f"records with observed_exit null "
                f"{null_exit_records!r} != expected {total}"
            )
        if marker_count != 0:
            reasons.append(
                f"classifier invocations {marker_count!r} != expected 0"
            )
        if process_events != 0:
            reasons.append(
                f"runner process events {process_events!r} != expected 0"
            )
        if popen_events != 0:
            reasons.append(
                f"runner subprocess.Popen events {popen_events!r} "
                "!= expected 0"
            )
    else:
        if proc.returncode != 0:
            reasons.append(f"exit {proc.returncode!r} != expected 0")
        if result_payload.get("verdict_exit") != 0:
            reasons.append(
                f"verdict_exit {result_payload.get('verdict_exit')!r} "
                "!= expected 0"
            )
        if result_payload.get("passed") != total:
            reasons.append(
                f"passed {result_payload.get('passed')!r} != expected {total}"
            )
        if result_payload.get("failed") != 0:
            reasons.append(
                f"failed {result_payload.get('failed')!r} != expected 0"
            )
        if result_payload.get("total") != total:
            reasons.append(
                f"total {result_payload.get('total')!r} != expected {total}"
            )
        if marker_count != total:
            reasons.append(
                f"classifier invocations {marker_count!r} != expected {total}"
            )
        if popen_events != total:
            reasons.append(
                f"runner subprocess.Popen events {popen_events!r} "
                f"!= expected {total}"
            )

    return {
        "name": test["name"],
        "source": test["source"],
        "envelope": test["envelope"],
        "expected": {
            "rejected": expected_rejected,
            "total": total,
        },
        "observed": observed,
        "child_count": marker_count,
        "command": argv,
        "runner_result": payload if isinstance(payload, dict) else None,
        "runner_stdout": proc.stdout,
        "runner_stderr": proc.stderr,
        "stdout_tail": tail(proc.stdout),
        "stderr_tail": tail(proc.stderr),
        "passed": not reasons,
        "reasons": reasons,
    }


def run_matrix(tests, runner):
    template = load_template()
    records = []
    with tempfile.TemporaryDirectory(prefix="kama-corpus-guard-") as tempdir:
        temp_root = Path(tempdir)
        for index, test in enumerate(tests):
            records.append(measure_test(index, test, template, runner,
                                        temp_root))
    return records, template


def result_document(records, matrix_sources, runner, args, template):
    passed = sum(1 for record in records if record["passed"])
    failed = len(records) - passed
    clean = bool(records) and failed == 0
    template_name = template.get("name") if isinstance(template, dict) else None
    return {
        "schema": SCHEMA,
        "finding_id": "clean" if clean else "test_failed",
        "verdict_exit": EXIT_CLEAN if clean else EXIT_FAILED,
        "runner": str(runner),
        "runner_sha256": sha256_file(runner),
        "classifier": str(CLASSIFIER),
        "classifier_sha256": sha256_file(CLASSIFIER),
        "source_cases": str(SOURCE_CASES),
        "source_cases_sha256": sha256_file(SOURCE_CASES),
        "source_template": (
            template_name if isinstance(template_name, str) else None
        ),
        "matrix_sources": matrix_sources,
        "selftest": bool(getattr(args, "selftest", False)),
        "only": getattr(args, "only", None),
        "total": len(records),
        "passed": passed,
        "failed": failed,
        "records": records,
        "limits": LIMITS,
    }


def error_document(message, runner=None, args=None):
    return {
        "schema": SCHEMA,
        "finding_id": "test_failed",
        "verdict_exit": EXIT_FAILED,
        "runner": str(runner) if runner is not None else None,
        "runner_sha256": sha256_file(runner) if runner else None,
        "classifier": str(CLASSIFIER),
        "classifier_sha256": sha256_file(CLASSIFIER),
        "source_cases": str(SOURCE_CASES),
        "source_cases_sha256": sha256_file(SOURCE_CASES),
        "source_template": None,
        "matrix_sources": [],
        "selftest": bool(getattr(args, "selftest", False)),
        "only": getattr(args, "only", None),
        "total": 0,
        "passed": 0,
        "failed": 0,
        "records": [],
        "error": message,
        "limits": LIMITS,
    }


def build_parser():
    parser = Parser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--runner",
        default=str(DEFAULT_RUNNER),
        help=f"measurement runner under test (default: {DEFAULT_RUNNER})",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="run the committed literal matrix (the only mode this CLI has)",
    )
    parser.add_argument(
        "--only",
        default=None,
        metavar="TEST",
        help="run only the test whose name matches exactly",
    )
    return parser


def main(argv=None):
    args = None
    runner = None
    try:
        args = build_parser().parse_args(argv)
        runner = Path(args.runner).expanduser().resolve()
        if not runner.is_file():
            raise HarnessError(f"runner absent: {runner}")
        if not CLASSIFIER.is_file():
            raise HarnessError(f"classifier absent: {CLASSIFIER}")
        tests, matrix_sources = load_matrix()
        if args.only is not None:
            tests = [test for test in tests if test["name"] == args.only]
            if not tests:
                raise HarnessError(
                    f"no committed test matches --only {args.only!r}"
                )
        records, template = run_matrix(tests, runner)
        result = result_document(records, matrix_sources, runner, args,
                                 template)
        code = result["verdict_exit"]
    except HarnessError as exc:
        result = error_document(str(exc), runner, args)
        code = EXIT_FAILED
    except Exception as exc:  # never let an unexpected failure look clean
        result = error_document(f"{type(exc).__name__}: {exc}", runner, args)
        code = EXIT_FAILED
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
