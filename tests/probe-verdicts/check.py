#!/usr/bin/env python3
"""kama-probe verdict-matrix harness (round 16, lane: model serving/endpoint health).

Runs every sibling ``*.json`` test matrix in this directory against
``tools/kama-probe.sh`` and grades each probe verdict. It owns nothing but the
loopback stub servers it spawns: no registry, history, config or service writes.

Matrix schema (shared contract): each sibling JSON file is an array of tests::

    {"name": "<unique>", "family": "<Family>", "why": "<one line>",
     "port_mode": "stub"|"closed",
     "routes": {"<path>": <R>}, "default_route": <R>|null,
     "expect": "<value passed as --expect>",
     "expected": {"verdict": V, "reason": R, "exit": 0|2}}

``<R>`` is ``{"status": int, "headers": {name: value}, "body_json": any}`` or
``{"status": int, "headers": {...}, "body_text": str}`` or ``{"raw": "close"}``
(accept the TCP connection, send nothing, close). A path absent from ``routes``
with ``default_route`` null answers 404 with an empty body. ``closed`` mode
binds then closes a socket and probes the dead port.

Probe invocation per test (exact)::

    bash PROBE check --port P --expect E --json --timeout 2 --connect-timeout 1

Exit 0 iff every record passes, 1 on any test failure (including a probe
timeout or malformed probe output), 2 on a harness/schema error. ``--json``
puts the machine document on stdout; without it a human summary is printed.
``--selftest`` additionally feeds 4 embedded malformed tests through the
schema validator, checks the duplicate-name guard across two files, and
fails if any of these is accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import shlex
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

CHECK_DIR = Path(__file__).resolve().parent
LANE = CHECK_DIR.parents[1]
DEFAULT_PROBE = LANE / "tools" / "kama-probe.sh"

SCHEMA = "kama-probe-verdicts/v1"
PROBE_TIMEOUT = 30          # seconds; a hung probe records a failure, never hangs us
HANDLER_TIMEOUT = 10        # seconds; a stalled client cannot wedge a stub thread
STUB_SERVER_HEADER = "kama-stub"

TEST_KEYS = {"name", "family", "why", "port_mode", "routes",
             "default_route", "expect", "expected"}
EXPECTED_KEYS = {"verdict", "reason", "exit"}
ROUTE_BODY_KEYS = ("body_json", "body_text")
VALID_PORT_MODES = ("stub", "closed")
VALID_EXITS = (0, 2)

PROBE_ARGV_TAIL = ("check", "--json", "--timeout", "2", "--connect-timeout", "1")


class HarnessError(Exception):
    """Schema or harness fault; reported as exit 2, never graded as a test."""


# ---------------------------------------------------------------- schema
def fail(where, message):
    raise HarnessError(f"{where}: {message}")


def validate_route(route, where):
    """Validate one R shape; returns the route unchanged on success."""
    if not isinstance(route, dict):
        fail(where, "route must be an object")
    if "raw" in route:
        if route != {"raw": "close"}:
            fail(where, 'raw route must be exactly {"raw":"close"}')
        return route
    allowed = {"status", "headers", "body_json", "body_text"}
    unknown = set(route) - allowed
    if unknown:
        fail(where, f"unknown route keys: {sorted(unknown)}")
    status = route.get("status")
    if not isinstance(status, int) or isinstance(status, bool):
        fail(where, "route.status must be an integer")
    if status < 100 or status > 999:
        fail(where, "route.status out of HTTP range")
    headers = route.get("headers")
    if headers is not None:
        if not isinstance(headers, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in headers.items()
        ):
            fail(where, "route.headers must be an object of string:string")
    bodies = [k for k in ROUTE_BODY_KEYS if k in route]
    if len(bodies) > 1:
        fail(where, "route may carry at most one of body_json/body_text")
    if "body_text" in route and not isinstance(route["body_text"], str):
        fail(where, "route.body_text must be a string")
    return route


def validate_test(test, source, index):
    where = f"{source}[{index}]"
    if not isinstance(test, dict):
        fail(where, "test must be an object")
    unknown = set(test) - TEST_KEYS
    if unknown:
        fail(where, f"unknown test keys: {sorted(unknown)}")
    missing = TEST_KEYS - set(test)
    if missing:
        fail(where, f"missing test keys: {sorted(missing)}")
    for key in ("name", "family", "why", "expect"):
        if not isinstance(test[key], str) or (key != "expect" and not test[key]):
            fail(where, f"test.{key} must be a non-empty string" if key != "expect"
                 else "test.expect must be a string")
    if test["port_mode"] not in VALID_PORT_MODES:
        fail(where, f"test.port_mode must be one of {VALID_PORT_MODES}")
    routes = test["routes"]
    if not isinstance(routes, dict) or not all(
        isinstance(p, str) for p in routes
    ):
        fail(where, "test.routes must be an object keyed by path string")
    for path, route in routes.items():
        validate_route(route, f"{where} route {path!r}")
    if test["default_route"] is not None:
        validate_route(test["default_route"], f"{where} default_route")
    expected = test["expected"]
    if not isinstance(expected, dict):
        fail(where, "test.expected must be an object")
    unknown = set(expected) - EXPECTED_KEYS
    if unknown:
        fail(where, f"unknown expected keys: {sorted(unknown)}")
    missing = EXPECTED_KEYS - set(expected)
    if missing:
        fail(where, f"missing expected keys: {sorted(missing)}")
    for key in ("verdict", "reason"):
        if not isinstance(expected[key], str):
            fail(where, f"expected.{key} must be a string")
    if expected["exit"] not in VALID_EXITS or isinstance(expected["exit"], bool):
        fail(where, "expected.exit must be 0 or 2")
    want = 0 if expected["verdict"] == "MODEL_OK" else 2
    if expected["exit"] != want:
        fail(where, f"expected.exit {expected['exit']} inconsistent with "
                    f"verdict {expected['verdict']} (probe exits {want})")
    return test


def load_matrix(directory=CHECK_DIR):
    """Load every *.json in *directory* in sorted order; fail closed on any fault."""
    sources = sorted(Path(directory).glob("*.json"))
    tests = []
    names = {}
    for source in sources:
        try:
            raw = source.read_text(encoding="utf-8")
        except OSError as exc:
            fail(str(source), f"unreadable matrix file: {exc}")
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(str(source), f"invalid JSON: {exc}")
        if not isinstance(doc, list):
            fail(str(source), "matrix file must be a JSON array of tests")
        for index, test in enumerate(doc):
            validate_test(test, source.name, index)
            name = test["name"]
            if name in names:
                fail(source.name, f"duplicate test name {name!r} "
                                  f"(first defined in {names[name]})")
            names[name] = source.name
            tests.append({"test": test, "source": source.name})
    return tests, [s.name for s in sources]


# ---------------------------------------------------------------- stub server
def make_handler(routes, default_route, seen):
    """Bind one test's routes into a fresh handler class (no shared state)."""

    class StubHandler(http.server.BaseHTTPRequestHandler):
        timeout = HANDLER_TIMEOUT
        _routes = routes
        _default = default_route
        _seen = seen
        _server_header = None

        def version_string(self):
            # Route-supplied Server header wins; otherwise the omit-equivalent
            # stub marker. Called from send_response for every reply.
            return self._server_header or STUB_SERVER_HEADER

        def send_response(self, code, message=None):
            self.log_request(code)
            self.send_response_only(code, message)
            self.send_header("Server", self.version_string())

        def send_error(self, code, message=None, explain=None):
            # Malformed request: a raw-close default still answers with nothing;
            # otherwise a bare status with an empty body (never the stock HTML).
            if (self._default or {}).get("raw") == "close":
                self.close_connection = True
                return
            self._server_header = None
            self.send_response_only(code)
            self.send_header("Server", STUB_SERVER_HEADER)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *args):  # keep harness stdout/stderr clean
            pass

        def _respond(self):
            self._seen.append({"method": self.command, "path": self.path})
            route = self._routes.get(self.path)
            if route is None and "?" in self.path:
                route = self._routes.get(self.path.split("?", 1)[0])
            if route is None:
                route = self._default
            if route is None:
                route = {"status": 404, "headers": {}}
            if route.get("raw") == "close":
                # Accept, send nothing, close. The request was parsed, so it is
                # still recorded in `requests` before the connection dies.
                self.close_connection = True
                return
            headers = route.get("headers") or {}
            self._server_header = None
            for key, value in headers.items():
                if key.lower() == "server":
                    self._server_header = value
            self.send_response(int(route["status"]))
            sent_length = False
            for key, value in headers.items():
                lowered = key.lower()
                if lowered == "server":
                    continue
                if lowered == "content-length":
                    sent_length = True
                self.send_header(key, value)
            body = b""
            if "body_json" in route:
                body = json.dumps(route["body_json"],
                                  separators=(",", ":")).encode("utf-8")
            elif "body_text" in route:
                body = route["body_text"].encode("utf-8")
            if not sent_length:
                self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body and self.command != "HEAD":
                self.wfile.write(body)

        def __getattr__(self, name):
            # Serve every HTTP method through the same route table.
            if name.startswith("do_"):
                return self._respond
            raise AttributeError(name)

    return StubHandler


def bind_closed_port():
    """Bind then release a loopback port; the probe must see refusal."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return sock.getsockname()[1]
    finally:
        sock.close()


def run_probe(probe, port, expect, timeout=PROBE_TIMEOUT):
    argv = ["bash", str(probe), *PROBE_ARGV_TAIL[:1],
            "--port", str(port), "--expect", expect,
            *PROBE_ARGV_TAIL[1:]]
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        # The probe may have spawned descendants that hold the pipes open.
        # Give it an isolated process group so timeout cleanup reaches them too.
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if proc.poll() is None:
            proc.kill()
        proc.communicate()
        raise
    # Decode strictly: non-UTF-8 probe output is malformed probe output (a
    # recorded per-row failure), never an uncaught UnicodeDecodeError.
    try:
        out = stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        out = f"<non-utf8 probe stdout: {exc}>"
    err = stderr.decode("utf-8", errors="replace")
    return subprocess.CompletedProcess(argv, proc.returncode, out, err)


# ------------------------------------------------- probe-contract invariants
# The two graders below re-derive what the probe CONTRACT requires from the
# row's own stub routes, so a grading-weakening mutant cannot widen either.
def served_ids_of(body):
    """Extract served ids from a /v1/models body exactly as the probe does.

    Mirrors tools/kama-probe.sh served_ids() (lines 335-368, python3 path):
    the body must be a JSON object; first non-empty group wins with
    precedence data[].id -> models[].id -> models[].name -> models[].model
    -> top-level id, deduplicated preserving order. Returns [] otherwise.
    """
    if isinstance(body, dict):
        doc = body                      # body_json routes arrive decoded
    else:
        try:
            doc = json.loads(body) if isinstance(body, str) else None
        except json.JSONDecodeError:
            return []
        if not isinstance(doc, dict):
            return []

    def group(seq, key):
        if not isinstance(seq, list):
            return []
        return [item[key] for item in seq
                if isinstance(item, dict)
                and isinstance(item.get(key), str) and item.get(key)]

    for ids in (group(doc.get("data"), "id"),
                group(doc.get("models"), "id"),
                group(doc.get("models"), "name"),
                group(doc.get("models"), "model"),
                [doc["id"]] if isinstance(doc.get("id"), str)
                and doc.get("id") else []):
        if ids:
            return list(dict.fromkeys(ids))
    return []


def models_route(test):
    """Resolve which route the stub serves for GET /v1/models (or None)."""
    route = test["routes"].get("/v1/models")
    if route is None:
        route = test["default_route"]
    if route is None or route.get("raw") == "close":
        return None
    return route


def expected_served_model(test, verdict):
    """The served_model value the probe contract REQUIRES for this row.

    classify() (tools/kama-probe.sh:455) starts every call with C_SERVED='-'
    and only ever rewrites it inside the `is2 && has_models` arm (lines
    524-529), the arm whose verdicts are MODEL_OK / MODEL_MISMATCH: there
    C_SERVED becomes the comma-joined ids parsed from the /v1/models body
    ('-' when the winning group is empty). Every other verdict — DEAD,
    NOT_HTTP, FOREIGN_SERVICE, UNAUTHORIZED_SERVICE, MODEL_LOADING —
    returns with C_SERVED still '-'.

    So, keyed on the OBSERVED verdict: MODEL_OK / MODEL_MISMATCH must carry
    exactly the ids this row's own stub /v1/models body yields via
    served_ids() precedence; every other verdict must carry '-'.
    """
    if verdict not in ("MODEL_OK", "MODEL_MISMATCH"):
        return "-"
    route = models_route(test)
    if route is None:
        return "-"
    body = route.get("body_json", route.get("body_text"))
    ids = served_ids_of(body)
    return ",".join(ids) if ids else "-"


def fetched_models_route(test, requests):
    """True iff the stub recorded GET /v1/models; None for closed-port rows.

    classify() opens with fetch "$port" "/v1/models" (kama-probe.sh:456), so
    any verdict claim about a stub endpoint that the stub never saw on that
    path is a contract violation. The handler's route fallback splits '?'
    (check.py make_handler), so the path is compared without its query.
    """
    if test["port_mode"] != "stub":
        return None
    return any(r.get("method") == "GET"
               and r.get("path", "").split("?", 1)[0] == "/v1/models"
               for r in requests)


def probe_output_row(stdout):
    """Validate probe --json stdout; return (row, why) — row None when bad.

    Contract: one JSON object whose "rows" is a non-empty list and whose
    first element is an object with verdict/reason strings and a drift
    bool (the row fields check() emits via eval_rows json_rows, probe
    lines 852-855). Anything else is malformed probe output: the caller
    records a per-row failure, never a traceback.
    """
    try:
        doc = json.loads(stdout)
    except (ValueError, RecursionError) as exc:
        return None, f"stdout is not JSON ({type(exc).__name__}: {exc})"
    if not isinstance(doc, dict):
        return None, f"top-level value is {type(doc).__name__}, not an object"
    rows = doc.get("rows")
    if not isinstance(rows, list) or not rows:
        return None, "\"rows\" is not a non-empty list"
    row = rows[0]
    if not isinstance(row, dict):
        return None, f"rows[0] is {type(row).__name__}, not an object"
    for key in ("verdict", "reason"):
        if not isinstance(row.get(key), str):
            return None, f"rows[0].{key} is not a string"
    if not isinstance(row.get("drift"), bool):
        return None, "rows[0].drift is not a bool"
    return row, None

def grade(entry, probe, timeout=PROBE_TIMEOUT):
    """Serve one test's stub (or closed port), run the probe, record the row."""
    test, source = entry["test"], entry["source"]
    record = {
        "name": test["name"],
        "family": test["family"],
        "source": source,
        "why": test["why"],
        "port_mode": test["port_mode"],
        "expect": test["expect"],
        "expected": dict(test["expected"]),
        "requests": [],
        "route_ok": None,
        "probe_exit": None,
        "verdict": None,
        "reason": None,
        "drift": None,
        "served_model": None,
        "served_model_expected": None,
        "served_model_ok": None,
        "evidence": None,
        "error": None,
        "passed": False,
    }
    server = None
    try:
        if test["port_mode"] == "closed":
            port = bind_closed_port()
        else:
            handler = make_handler(test["routes"], test["default_route"],
                                   record["requests"])
            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
            server.daemon_threads = True
            port = server.server_address[1]
            # serve_forever on a daemon thread; without it the socket listens
            # but never accepts and shutdown() below would block forever.
            threading.Thread(target=server.serve_forever,
                             daemon=True).start()
        record["port"] = port
        try:
            proc = run_probe(probe, port, test["expect"], timeout)
        except subprocess.TimeoutExpired:
            record["route_ok"] = fetched_models_route(test,
                                                    record["requests"])
            record["error"] = f"probe timed out after {timeout}s"
            return record
        record["probe_exit"] = proc.returncode
        record["route_ok"] = fetched_models_route(test, record["requests"])
        if server is not None and not record["requests"]:
            # A live stub that saw nothing means the probe never reached a
            # listening port — a harness serve fault, not a probe verdict.
            record["error"] = ("stub accepted no requests; probe never "
                               "reached a listening socket")
            return record
        row, why_bad = probe_output_row(proc.stdout)
        if row is None:
            record["error"] = (f"malformed probe output: {why_bad}; "
                               f"stdout={proc.stdout[-300:]!r} "
                               f"stderr={proc.stderr[-300:]!r}")
            return record
        for key in ("verdict", "reason", "drift", "served_model", "evidence"):
            record[key] = row.get(key)
        record["served_model_expected"] = expected_served_model(
            test, record["verdict"])
        record["served_model_ok"] = (
            record["served_model"] == record["served_model_expected"])
        expected = test["expected"]
        record["passed"] = (
            record["verdict"] == expected["verdict"]
            and record["reason"] == expected["reason"]
            and record["probe_exit"] == expected["exit"]
            # probe contract: drift == (verdict != MODEL_OK); assert it so an
            # inconsistent drift flag (e.g. MODEL_LOADING must drift) fails.
            and record["drift"] == (record["verdict"] != "MODEL_OK")
            and record["served_model_ok"]
            and record["route_ok"] is not False
        )
        return record
    except OSError as exc:
        # Bind/exec faults are harness faults (exit 2), not test failures.
        raise HarnessError(f"stub failure in {test['name']}: {exc}") from exc
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()


# ---------------------------------------------------------------- selftest
SELFTEST_MALFORMED = [
    ({"name": "selftest-unknown-key", "family": "Selftest", "why": "x",
      "port_mode": "stub", "routes": {}, "default_route": None,
      "expect": "*", "expected": {"verdict": "DEAD", "reason": "x", "exit": 2},
      "bogus": 1},
     "unknown test key"),
    ({"name": "selftest-bad-route", "family": "Selftest", "why": "x",
      "port_mode": "stub",
      "routes": {"/v1/models": {"status": "200", "headers": {}}},
      "default_route": None, "expect": "*",
      "expected": {"verdict": "DEAD", "reason": "x", "exit": 2}},
     "non-integer route status"),
    ({"name": "selftest-bad-exit", "family": "Selftest", "why": "x",
      "port_mode": "closed", "routes": {}, "default_route": None,
      "expect": "*", "expected": {"verdict": "DEAD", "reason": "x", "exit": 1}},
     "exit outside {0,2}"),
    ({"name": "selftest-inconsistent-exit", "family": "Selftest", "why": "x",
      "port_mode": "stub", "routes": {}, "default_route": None,
      "expect": "*",
      "expected": {"verdict": "MODEL_OK", "reason": "matched", "exit": 2}},
     "MODEL_OK paired with exit 2"),
]

SELFTEST_MALFORMED_OUTPUTS = [
    ("60,000-level JSON nesting",
     '{"rows":' + "[" * 60_000 + "0" + "]" * 60_000 + "}",
     "RecursionError"),
    ("5,000-digit JSON integer",
     '{"rows":[' + "9" * 5_000 + "]}",
     "ValueError"),
]

# One minimal valid test; two files carrying it under the same name exercise
# the duplicate-name guard in load_matrix() without touching the matrix dir.
SELFTEST_VALID_TEST = {"name": "selftest-dup", "family": "Selftest",
                       "why": "x", "port_mode": "closed", "routes": {},
                       "default_route": None, "expect": "*",
                       "expected": {"verdict": "DEAD",
                                    "reason": "x", "exit": 2}}


def selftest_malformed_output_rows():
    """Ensure decoder-limit output fails one row and grading continues."""
    global bind_closed_port
    with tempfile.TemporaryDirectory(
            prefix="kama-check-output-selftest-") as tmp:
        tmp_path = Path(tmp)
        probe = tmp_path / "probe.sh"
        payload_file = tmp_path / "payload.json"
        probe.write_text(
            f"cat {shlex.quote(str(payload_file))}\nexit 2\n",
            encoding="utf-8")
        entry = {"test": dict(SELFTEST_VALID_TEST), "source": "<selftest>"}
        real_bind_closed_port = bind_closed_port
        bind_closed_port = lambda: 0
        output_results = []
        try:
            for label, stdout, exception_type in SELFTEST_MALFORMED_OUTPUTS:
                payload_file.write_text(stdout, encoding="utf-8")
                record = grade(entry, probe)
                row, why_bad = probe_output_row(stdout)
                parser_rejected = (
                    row is None and isinstance(why_bad, str)
                    and why_bad.startswith(
                        f"stdout is not JSON ({exception_type}:"))
                recorded_failure = (
                    record["passed"] is False
                    and isinstance(record["error"], str)
                    and record["error"].startswith("malformed probe output:"))
                output_results.append({
                    "label": label,
                    "rejected": parser_rejected and recorded_failure,
                    "detail": why_bad or "parser accepted malformed output",
                    "recorded_error": record["error"],
                })
            payload_file.write_text(json.dumps({
                "rows": [{"verdict": "DEAD", "reason": "x", "drift": True,
                          "served_model": "-", "evidence": "selftest"}],
            }), encoding="utf-8")
            successor = grade(entry, probe)
        finally:
            bind_closed_port = real_bind_closed_port
        return output_results, successor["passed"] is True


def selftest_timeout_process_group():
    """Check timeout reporting and cleanup of a same-group probe child."""
    global bind_closed_port
    with tempfile.TemporaryDirectory(
            prefix="kama-check-timeout-selftest-") as tmp:
        tmp_path = Path(tmp)
        marker = tmp_path / "escaped"
        probe = tmp_path / "probe.sh"
        child_code = ("import pathlib,sys,time; time.sleep(0.4); "
                      "pathlib.Path(sys.argv[1]).write_text('escaped')")
        probe.write_text(
            f"{shlex.quote(sys.executable)} -c {shlex.quote(child_code)} "
            f"{shlex.quote(str(marker))} &\nwait\n",
            encoding="utf-8")
        entry = {"test": dict(SELFTEST_VALID_TEST), "source": "<selftest>"}
        real_bind_closed_port = bind_closed_port
        bind_closed_port = lambda: 0
        try:
            record = grade(entry, probe, timeout=0.1)
        finally:
            bind_closed_port = real_bind_closed_port
        time.sleep(0.5)
        timed_out = record["error"] == "probe timed out after 0.1s"
        child_completed = marker.exists()
        return {
            "label": "timeout kills probe process-group child",
            "recorded_error": record["error"],
            "child_completed": child_completed,
            "passed": (timed_out and record["passed"] is False
                       and not child_completed),
        }

def run_selftest():
    """Assert schema rejection, malformed-output handling, and timeout cleanup."""
    results = []
    for test, label in SELFTEST_MALFORMED:
        try:
            validate_test(test, "<selftest>", 0)
        except HarnessError as exc:
            results.append({"label": label, "rejected": True,
                            "detail": str(exc)})
        else:
            results.append({"label": label, "rejected": False,
                            "detail": "validator accepted a malformed test"})
    # Duplicate-name guard: the same test name in two sibling files must be
    # a schema error (exit 2 upstream). Proven in a temp dir — never in the
    # real matrix directory.
    with tempfile.TemporaryDirectory(prefix="kama-check-selftest-") as tmp:
        tmp_path = Path(tmp)
        for fname in ("a.json", "b.json"):
            (tmp_path / fname).write_text(
                json.dumps([dict(SELFTEST_VALID_TEST)]), encoding="utf-8")
        try:
            load_matrix(tmp_path)
        except HarnessError as exc:
            results.append({"label": "duplicate test name across files",
                            "rejected": True, "detail": str(exc)})
        else:
            results.append({"label": "duplicate test name across files",
                            "rejected": False,
                            "detail": "load_matrix accepted a duplicate name"})

    output_results, successor_passed = selftest_malformed_output_rows()
    timeout_result = selftest_timeout_process_group()
    return {
        "malformed_tests": len(results),
        "rejected": sum(1 for r in results if r["rejected"]),
        "results": results,
        "malformed_outputs": len(output_results),
        "malformed_outputs_rejected": sum(
            1 for r in output_results if r["rejected"]),
        "output_results": output_results,
        "successor_row_passed": successor_passed,
        "timeout_test": timeout_result,
        "passed": (all(r["rejected"] for r in results)
                   and all(r["rejected"] for r in output_results)
                   and successor_passed
                   and timeout_result["passed"]),
    }


# ---------------------------------------------------------------- driver
def sha256_file(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def human_summary(records, doc):
    lines = []
    for rec in records:
        status = "PASS" if rec["passed"] else "FAIL"
        detail = (f"verdict={rec['verdict']} reason={rec['reason']} "
                  f"exit={rec['probe_exit']} "
                  f"(expected {rec['expected']['verdict']}/"
                  f"{rec['expected']['reason']}/{rec['expected']['exit']})")
        if rec["error"]:
            detail += f" error={rec['error']}"
        if rec.get("served_model_ok") is False:
            detail += (f" served_model={rec['served_model']!r} "
                       f"(expected {rec['served_model_expected']!r})")
        if rec.get("route_ok") is False:
            detail += " route=missing-GET-/v1/models"
        seen = ", ".join(f"{r['method']} {r['path']}" for r in rec["requests"])
        lines.append(f"[{status}] {rec['name']} ({rec['family']}): {detail}"
                     + (f" requests=[{seen}]" if seen else ""))
    lines.append(f"tests={doc['tests']} passes={doc['passes']} "
                 f"failures={doc['failures']}")
    if "selftest" in doc:
        st = doc["selftest"]
        lines.append(f"selftest: {st['rejected']}/{st['malformed_tests']} "
                     f"malformed tests rejected "
                     f"({'ok' if st['passed'] else 'FAILED'})")
    return "\n".join(lines)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise HarnessError(f"argv: {message}")


def build_parser():
    parser = Parser(
        description="Run the kama-probe verdict matrices in this directory "
                    "against a probe script.")
    parser.add_argument("--probe", default=str(DEFAULT_PROBE),
                        help=f"probe script path (default {DEFAULT_PROBE})")
    parser.add_argument("--only", action="append", default=[], metavar="NAME",
                        help="run only tests with this exact name (repeatable)")
    parser.add_argument("--json", action="store_true",
                        help="emit the machine document on stdout "
                             "(human summary moves to stderr)")
    parser.add_argument("--selftest", action="store_true",
                        help="also assert the validator rejects 4 embedded "
                             "malformed tests and a duplicate name")
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
    except HarnessError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    probe = Path(args.probe)
    if not probe.is_file():
        print(f"harness error: probe not found: {probe}", file=sys.stderr)
        return 2
    try:
        entries, sources = load_matrix()
    except HarnessError as exc:
        print(f"schema error: {exc}", file=sys.stderr)
        return 2
    if args.only:
        wanted = set(args.only)
        entries = [e for e in entries if e["test"]["name"] in wanted]
        missing = wanted - {e["test"]["name"] for e in entries}
        if missing:
            print(f"schema error: --only names not found: {sorted(missing)}",
                  file=sys.stderr)
            return 2

    try:
        records = [grade(entry, probe) for entry in entries]
    except HarnessError as exc:
        print(f"harness error: {exc}", file=sys.stderr)
        return 2
    passes = sum(1 for r in records if r["passed"])
    doc = {
        "schema": SCHEMA,
        "probe": str(probe),
        "probe_sha256": sha256_file(probe),
        "matrix_sources": sources,
        "tests": len(records),
        "passes": passes,
        "failures": len(records) - passes,
        "records": records,
    }
    code = 0 if doc["failures"] == 0 else 1
    if args.selftest:
        st = run_selftest()
        doc["selftest"] = st
        if not st["passed"]:
            code = 1

    summary = human_summary(records, doc)
    if args.json:
        print(summary, file=sys.stderr)
        print(json.dumps(doc, indent=2))
    else:
        print(summary)
    return code


if __name__ == "__main__":
    sys.exit(main())
