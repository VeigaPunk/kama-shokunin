#!/usr/bin/env python3
"""survivors.py — C2 counting command: round-17 named survivors, before -> after.

Lane: local model serving & endpoint health (kama-shokunin), round 18, claim C2
(calibration). L1 runs the count; seats run only --selftest.

What is counted
---------------
Every NAMED item below is a weakening (or crash path) that a round-17 outside
seat showed the lane's own detectors could not see. Each mutant is ONE
single-site edit located by an exact, line-anchored source-string match: the
OLD text must occur exactly once in the tool and start at a line start. It is
applied to a scratch COPY of the tool; nothing in the lane is written.

    site_missing    OLD absent                   } reported and counted as
    site_ambiguous  OLD occurs more than once     } NOT killed — never skipped
    stillborn       the edited copy does not compile

(a) check.py mutants H1 H2 H3 H5 H6 H7 — exact edits from
    .ufo/waves/round-17/falsify/advice/MutC1Preregistered.md (H1-H3) and
    MutC1Preregistered2.md (H5-H7) — applied to the CURRENT check.py.
    Detector: `fault-controls.py --check <mutant> --probe tools/kama-probe.sh
    --matrix-dir tests/probe-verdicts --json`, run once with the FROZEN
    fault-controls (before) and once with the CURRENT one (after).
      killed  <=> exit 1 or accepted > 0; exit 2 is an own fault and
                  inconclusive, never a kill. The unmutated current check.py
                  baseline must give exit 0, accepted 0, and healthy F0.
(b) fault-controls self-mutants FC-target / FC-f6cache / FC-f0gate —
    MutFaultControlsSelf.md mutants (a) (c) (d) — applied to the FROZEN tool
    (before) and to the CURRENT tool (after). Detector: `--selftest
    --matrix-dir tests/probe-verdicts` plus its main run `--check <current
    check.py> --probe tools/kama-probe.sh --matrix-dir tests/probe-verdicts
    --json`.
      killed  <=> the selftest exits non-zero where the unmutated copy's
                  exits 0 AND that output names this mutant's target
                  literal (`selftest_arm`: a non-zero exit without the
                  target literal is inconclusive), OR the main run's decision
                  (exit, positive_control.detected, detected, accepted,
                  {fault id: detected}) differs from the unmutated copy's.
    `runs`, `check_exit` and `why` are diagnostics and are not compared:
    round 17's survivors moved only those, and printing a different
    diagnostic is not rejecting the weakened detector.
(c) sources-append-only self-mutants AO-opened (M3a: compared cells taken
    from header[:8], which drops `opened`) and AO-blank (M4b: parsing stops at
    the first blank line after the header) — MutAppendOnlyGuard.md —
    applied to the FROZEN and to the CURRENT tool. Detector: the mutated
    copy's `--selftest`; killed <=> it exits non-zero where the unmutated
    copy's exits 0.
(d) dispatch-provenance refused miscount — ProvenanceRerun.md. The FROZEN
    round-17 tool and the CURRENT round-18 tool each record the round-17
    refused attempt exactly as round 17 invoked mode 2 (its docstring):
        dispatch-provenance.py --attempt-result \\
            .ufo/waves/round-17/build/refused-result-1.json \\
            --label refused --out <fresh scratch ledger>
    correct <=> the appended entry records refused == 82. The 82 is pinned;
    the round-17 operator log .ufo/waves/round-17/build/attempts.json must
    record the same 82 (both evidence files are sha256-pinned).
(e) check.py crash faults — MalformedNonUtf8.md, TimeoutPath.md — against
    the FROZEN and the CURRENT check.py, each staged with byte copies of the
    nine matrix files, `--only AuthAndDead.closed-port-connection-refused
    --json`, with a probe script that
        nested-json    prints {"rows": + 100000 "[" + 1 + 100000 "]" + }
        bigint         prints {"rows":[ + 5000 "9" + ]}
        escaped-sleep  runs a FOREGROUND `(exec -a <nonce> sleep 600)`, the
                       round-17 counterexample shape, past the probe timeout
    handled  <=> check.py exits 1 with a parseable JSON document whose row
                 has passed:false and a non-empty error, no Python traceback
                 reaches stderr, and (escaped-sleep) no <nonce> process is
                 alive 3 s after check.py exits.
    Anything else is `accepted`; a probe that never started is
    `not_exercised`.

Counts: `before` = named items not killed/handled/correct on the frozen side,
`after` = the same on the current side, per family and in total.

Usage
-----
    survivors.py --json --out PATH [--family a,b,c,d,e] [--jobs N]
                 [--fault-controls PATH] [--check PATH]
                 [--append-only PATH] [--provenance PATH]
    survivors.py --selftest [--json]

CURRENT tools default to the lane paths tests/probe-verdicts/fault-controls.py,
tests/probe-verdicts/check.py, tools/sources-append-only.py and
.ufo/waves/round-18/dispatch-provenance.py; the lane root is four directories
above this file. FROZEN copies come from .ufo/waves/round-18/frozen/ and must
match its SHA256SUMS. Every input is read once, sha256-recorded and
snapshotted into scratch before any run starts; only snapshots execute.
fault-controls copies run from a lane-shaped scratch mirror
(tests/probe-verdicts/{fault-controls.py,check.py,*.json}, tools/kama-probe.sh)
so every default a tool derives from its own location resolves in scratch.

--jobs (default 1) bounds concurrent child runs. A fault-controls suite serves
one loopback stub at a time, so --jobs 1 keeps one fake server alive at a
time. All families together execute 20 full fault-controls main runs (slow
timeout faults included), 8 fault-controls selftests, 6 append-only
selftests, 2 provenance records and 6 check.py runs — 42 child runs; an
identical (argv, cwd) run is memoized.

--out is created exclusively: an existing path is refused, never clobbered.

Exit: 0 every named item killed/handled/correct on the CURRENT side of every
selected family and frozen witnesses match; 1 otherwise if outcomes are
conclusive; 2 for own fault or an inconclusive run/baseline/frozen witness.

Safety
------
Children get a generated sitecustomize on PYTHONPATH that refuses
non-loopback binds and binds to 8080, 34113 or any port named in
registry/endpoint-consumers.tsv, and maps port-0 binds into 49152-60999. The
bind log is summarised in the output with an `ss -ltnpH` check that no logged
(pid, port) is still listening. Every child runs in its own session; its
process group is killed once it exits or its cap expires. Children's TMPDIR
is inside the one scratch directory, which is removed at exit.

Limits
------
The universe is the named set only; it says nothing about mutants nobody
named. A run that exceeds its cap is `error`, never a kill. A process that
leaves its run's process group (setsid) is traced only when it carries the
escaped-sleep nonce. Only Python children get the bind guard.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "kama-c2-survivors/v1"
SELF = Path(__file__).resolve()
LANE = SELF.parents[4]
ROUND18 = LANE / ".ufo" / "waves" / "round-18"
FROZEN_DIR = ROUND18 / "frozen"
FROZEN_SUMS = FROZEN_DIR / "SHA256SUMS"
ADVICE17 = ".ufo/waves/round-17/falsify/advice/"

TOOLS = ("fault-controls", "check", "append-only", "provenance")
DEFAULT_CURRENT = {
    "fault-controls": LANE / "tests" / "probe-verdicts" / "fault-controls.py",
    "check": LANE / "tests" / "probe-verdicts" / "check.py",
    "append-only": LANE / "tools" / "sources-append-only.py",
    "provenance": ROUND18 / "dispatch-provenance.py",
}
FROZEN_TOOLS = {
    "fault-controls": FROZEN_DIR / "tests_probe-verdicts_fault-controls.py",
    "check": FROZEN_DIR / "tests_probe-verdicts_check.py",
    "append-only": FROZEN_DIR / "tools_sources-append-only.py",
    "provenance": FROZEN_DIR / "round-17_dispatch-provenance.py",
}
PROBE = LANE / "tools" / "kama-probe.sh"
MATRIX_DIR = LANE / "tests" / "probe-verdicts"
CONSUMERS_TSV = LANE / "registry" / "endpoint-consumers.tsv"
# Pinned by fault-controls.py (EXPECTED_MATRIX_SHA256): nine files, 72 rows;
# formula = sha256 of the sorted "name sha256\n" lines.
MATRIX_FILES = 9
MATRIX_SET_SHA256 = ("bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21ed"
                     "b2b8256e22771f32")
EVIDENCE = {
    "refused-result": (
        LANE / ".ufo" / "waves" / "round-17" / "build" / "refused-result-1.json",
        "7167991932f619a6b805346338799bf6500d0a86387269e95b4c09e208041a5c"),
    "attempts": (
        LANE / ".ufo" / "waves" / "round-17" / "build" / "attempts.json",
        "85e4ba72793a4e76478fd227dbe27d8ff28fcff9f8cdd1639ef4814f313bd0c1"),
}
EXPECTED_REFUSED = 82
CRASH_ROW = "AuthAndDead.closed-port-connection-refused"
FIXED_PROTECTED_PORTS = (8080, 34113)
GUARD_LOW, GUARD_HIGH = 49152, 61000          # randrange: 49152..60999
SLEEP_SECONDS = 600
ESCAPE_GRACE = 3.0
PIPE_GRACE = 10.0
CAP = {"fc-main": 1800, "fc-selftest": 600, "ao-selftest": 120,
       "provenance": 120, "check-crash": 300}
FAMILIES = ("a", "b", "c", "d", "e")
FAMILY_TITLES = {
    "a": "check.py H-mutants vs fault-controls (frozen -> current detector)",
    "b": "fault-controls self-mutants (frozen -> current tool)",
    "c": "sources-append-only self-mutants (frozen -> current tool)",
    "d": "dispatch-provenance refused count on round-17 evidence",
    "e": "check.py crash faults (frozen -> current check.py)",
}
ADVICE_FILES = {
    "a": ("MutC1Preregistered.md", "MutC1Preregistered2.md"),
    "b": ("MutFaultControlsSelf.md",),
    "c": ("MutAppendOnlyGuard.md",),
    "d": ("ProvenanceRerun.md",),
    "e": ("MalformedNonUtf8.md", "TimeoutPath.md"),
}
ADVICE_ROOT = LANE / ".ufo" / "waves" / "round-17" / "falsify" / "advice"
FROZEN_EXPECTED = {
    "a": {"H1": "survived", "H2": "survived", "H3": "survived",
          "H5": "survived", "H6": "survived", "H7": "survived"},
    "b": {"FC-target": "survived", "FC-f6cache": "survived",
          "FC-f0gate": "survived"},
    "c": {"AO-opened": "survived", "AO-blank": "survived"},
    "d": {"refused-count": "miscount"},
    "e": {"nested-json": "accepted", "bigint": "accepted",
          "escaped-sleep": "accepted"},
}
SIDES = ("frozen", "current")
GOOD = frozenset({"killed", "handled", "correct"})
TRACEBACK = b"Traceback (most recent call last)"

# ---------------------------------------------------------------- named edits
MUTANTS = {
    "a": (
        {"id": "H1", "title": "reason compared case-insensitively",
         "advice": ADVICE17 + "MutC1Preregistered.md:24-32",
         "old": '            and record["reason"] == expected["reason"]\n',
         "new": ('            and record["reason"].casefold() == '
                 'expected["reason"].casefold()\n')},
        {"id": "H2", "title": "verdict compared after strip()",
         "advice": ADVICE17 + "MutC1Preregistered.md:44-52",
         "old": '            record["verdict"] == expected["verdict"]\n',
         "new": ('            record["verdict"].strip() == '
                 'expected["verdict"].strip()\n')},
        {"id": "H3", "title": "route match ignores the HTTP method",
         "advice": ADVICE17 + "MutC1Preregistered.md:64-73",
         "old": ('    return any(r.get("method") == "GET"\n'
                 '               and r.get("path", "").split("?", 1)[0] == '
                 '"/v1/models"\n'
                 '               for r in requests)\n'),
         "new": ('    return any(r.get("path", "").split("?", 1)[0] == '
                 '"/v1/models"\n'
                 '               for r in requests)\n')},
        {"id": "H5", "title": "served ids normalised (lower, strip .gguf)",
         "advice": ADVICE17 + "MutC1Preregistered2.md:22-34",
         "old": ('        record["served_model_ok"] = (\n'
                 '            record["served_model"] == '
                 'record["served_model_expected"])\n'),
         "new": ('        record["served_model_ok"] = (\n'
                 '            [sid.lower().removesuffix(".gguf")\n'
                 '             for sid in (record["served_model"] or "")'
                 '.split(",")]\n'
                 '            == [sid.lower().removesuffix(".gguf")\n'
                 '                for sid in record["served_model_expected"]'
                 '.split(",")])\n')},
        {"id": "H6", "title": "no-stub-requests branch marks the row passed",
         "advice": ADVICE17 + "MutC1Preregistered2.md:38-44",
         "old": ('            record["error"] = ("stub accepted no requests; '
                 'probe never "\n'
                 '                               "reached a listening socket")\n'),
         "new": ('            record["error"] = ("stub accepted no requests; '
                 'probe never "\n'
                 '                               "reached a listening socket")\n'
                 '            record["passed"] = True\n')},
        {"id": "H7", "title": "grades the last probe row instead of the first",
         "advice": ADVICE17 + "MutC1Preregistered2.md:48-54",
         "old": "    row = rows[0]\n",
         "new": "    row = rows[-1]\n"},
    ),
    "b": (
        {"id": "FC-target", "title": "targeted-conjunct requirement dropped",
         "advice": ADVICE17 + "MutFaultControlsSelf.md:32-48",
         "old": "    if target:\n",
         "new": "    if False and target:\n"},
        {"id": "FC-f6cache", "title": "F6 replays one shared four-row cache",
         "advice": ADVICE17 + "MutFaultControlsSelf.md:72-93",
         "old": '        "runs": _per_row("f6", "/health", F6_ROWS),\n',
         "new": ('        "runs": [{"mode": "f6", "touch": "/health", '
                 '"rows": F6_ROWS}],\n')},
        {"id": "FC-f0gate", "title": "F0 positive-control gate bypassed",
         "advice": ADVICE17 + "MutFaultControlsSelf.md:95-104",
         "old": '            if not positive["detected"]:\n',
         "new": '            if False and not positive["detected"]:\n'},
    ),
    "c": (
        {"id": "AO-opened",
         "title": "compared cells from header[:8], dropping opened (M3a)",
         "advice": ADVICE17 + "MutAppendOnlyGuard.md:27,36,54",
         "old": ('    immutable_cols = [c for c in header if c not in '
                 'MUTABLE_CELLS and c != "id"]\n'),
         "new": ('    immutable_cols = [c for c in header[:8] if c not in '
                 'MUTABLE_CELLS and c != "id"]\n')},
        {"id": "AO-blank",
         "title": "parsing stops at the first blank line after the header (M4b)",
         "advice": ADVICE17 + "MutAppendOnlyGuard.md:31,55",
         "old": "        if not ROW_RE.match(line):\n",
         "new": ("        if header is not None and not line.strip():\n"
                 "            break\n"
                 "        if not ROW_RE.match(line):\n")},
    ),
}
MUTANT_TOOL = {"a": "check", "b": "fault-controls", "c": "append-only"}

CRASH_FAULTS = (
    {"id": "nested-json", "advice": ADVICE17 + "MalformedNonUtf8.md:6-10,29",
     "title": "100,000-level nested JSON array (RecursionError path)",
     "payload": b'{"rows":' + b"[" * 100_000 + b"1" + b"]" * 100_000 + b"}\n"},
    {"id": "bigint", "advice": ADVICE17 + "MalformedNonUtf8.md:6-10,30",
     "title": "5,000-digit JSON integer (int max-str-digits ValueError)",
     "payload": b'{"rows":[' + b"9" * 5_000 + b"]}\n"},
    {"id": "escaped-sleep", "advice": ADVICE17 + "TimeoutPath.md:15-55",
     "title": "probe timeout leaves a foreground external sleep",
     "payload": None},
)


class OwnFault(Exception):
    """survivors.py could not measure (input, staging or internal) -> exit 2."""


# ---------------------------------------------------------------- helpers
def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def tail(data, limit=1200):
    if isinstance(data, bytes):
        data = data.decode("utf-8", errors="replace")
    return str(data)[-limit:]


def parse_json_bytes(data):
    """(document, None) or (None, why); never raises on hostile output."""
    try:
        return json.loads(data.decode("utf-8")), None
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        return None, f"{type(exc).__name__}: {str(exc)[:160]}"


def matrix_set_digest(named_bytes):
    lines = "".join(f"{name} {sha256_bytes(data)}\n"
                    for name, data in sorted(named_bytes))
    return sha256_bytes(lines.encode())


def locate(text, old):
    """Line-anchored exact occurrences of OLD as [(offset, line_number)]."""
    hits = []
    start = 0
    while True:
        index = text.find(old, start)
        if index < 0:
            return hits
        if index == 0 or text[index - 1] == "\n":
            hits.append((index, text.count("\n", 0, index) + 1))
        start = index + 1


def apply_edit(text, old, new, label):
    """(mutated text or None, site record) for one single-site edit."""
    hits = locate(text, old)
    site = {"count": len(hits), "lines": [line for _, line in hits]}
    if not hits:
        site["status"] = "site_missing"
        return None, site
    if len(hits) > 1:
        site["status"] = "site_ambiguous"
        return None, site
    index = hits[0][0]
    mutated = text[:index] + new + text[index + len(old):]
    try:
        compile(mutated, label, "exec")
    except (SyntaxError, ValueError) as exc:
        site["status"] = "stillborn"
        site["error"] = f"{type(exc).__name__}: {exc}"
        return None, site
    site["status"] = "ok"
    return mutated, site


def killpg_quiet(pgid):
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def marked_pids(marker, prefix=False):
    """Live (non-zombie) pids whose argv[0] is MARKER (or starts with it)."""
    want = marker.encode()
    found = []
    try:
        entries = os.listdir("/proc")
    except OSError:
        return found
    for name in entries:
        if not name.isdigit():
            continue
        try:
            with open(f"/proc/{name}/cmdline", "rb") as fh:
                argv0 = fh.read().split(b"\0", 1)[0]
            if not (argv0.startswith(want) if prefix else argv0 == want):
                continue
            with open(f"/proc/{name}/stat", "rb") as fh:
                stat = fh.read()
        except OSError:
            continue
        close = stat.rfind(b")")
        if stat[close + 2:close + 3] == b"Z":
            continue
        found.append(int(name))
    return sorted(found)


def kill_marked(marker, prefix=False, wait=5.0):
    """SIGKILL every live process carrying MARKER; return the pids signalled."""
    signalled = []
    deadline = time.monotonic() + wait
    while True:
        pids = marked_pids(marker, prefix)
        if not pids or time.monotonic() > deadline:
            return signalled
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                continue
            if pid not in signalled:
                signalled.append(pid)
        time.sleep(0.05)


def settle_marked(marker, grace=ESCAPE_GRACE):
    """Pids still carrying MARKER after GRACE seconds (polled)."""
    deadline = time.monotonic() + grace
    pids = marked_pids(marker)
    while pids and time.monotonic() < deadline:
        time.sleep(0.1)
        pids = marked_pids(marker)
    return pids


def write_exclusive(path, data):
    """Create PATH holding DATA; an existing path raises FileExistsError."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".survivors-",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.link(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def protected_ports(tsv_text):
    ports = set(FIXED_PROTECTED_PORTS)
    for match in re.finditer(r"(?:127\.0\.0\.1|localhost|\[::1\]):(\d{2,5})",
                             tsv_text or ""):
        ports.add(int(match.group(1)))
    return sorted(ports)


def parse_sums(raw):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise OwnFault(f"frozen manifest is not UTF-8: {exc}")
    sums = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2 and re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            sums[parts[1].lstrip("*")] = parts[0]
    return sums


def read_sums():
    try:
        raw = FROZEN_SUMS.read_bytes()
    except OSError as exc:
        raise OwnFault(f"frozen manifest unreadable: {FROZEN_SUMS}: {exc}")
    return parse_sums(raw)


# ---------------------------------------------------------------- bind guard
GUARD_BODY = r'''
import errno
import os
import random
import socket

_LOOPBACK = ("localhost", "::1")
_orig_bind = socket.socket.bind
_rng = random.SystemRandom()


def _is_loopback(host):
    return isinstance(host, str) and (
        host in _LOOPBACK or host.startswith("127.")
        or host.startswith("::ffff:127."))


def decide(family, address):
    """('pass'|'refuse'|'pick'|'bind', detail) for one bind() call."""
    if family not in (socket.AF_INET, socket.AF_INET6) \
            or not isinstance(address, tuple) or len(address) < 2:
        return "pass", None
    host, port = address[0], address[1]
    if not _is_loopback(host):
        return "refuse", "non-loopback bind %r" % (host,)
    if port in PROTECTED:
        return "refuse", "protected port %r" % (port,)
    if port == 0:
        return "pick", None
    return "bind", port


def _log(port):
    path = os.environ.get("KAMA_C2_SURVIVORS_BIND_LOG")
    if not path:
        return
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, ("%d %d\n" % (os.getpid(), port)).encode())
    finally:
        os.close(fd)


def kama_c2_guarded_bind(sock, address):
    action, detail = decide(sock.family, address)
    if action == "pass":
        return _orig_bind(sock, address)
    if action == "refuse":
        raise PermissionError(errno.EACCES, "survivors bind guard: " + detail)
    if action == "bind":
        result = _orig_bind(sock, address)
        _log(detail)
        return result
    for _ in range(1024):
        port = _rng.randrange(LOW, HIGH)
        if port in PROTECTED:
            continue
        try:
            result = _orig_bind(sock, (address[0], port) + tuple(address[2:]))
        except OSError as exc:
            if exc.errno == errno.EADDRINUSE:
                continue
            raise
        _log(port)
        return result
    raise OSError(errno.EADDRINUSE, "survivors bind guard: no free port")
'''
GUARD_INSTALL = "\nsocket.socket.bind = kama_c2_guarded_bind\n"


def guard_source(ports, install=True):
    return ('"""Generated by survivors.py for its own children only: '
            'loopback-only binds,\nnever a protected port; port 0 maps into '
            '[LOW, HIGH)."""\n'
            f"PROTECTED = frozenset({sorted(ports)!r})\n"
            f"LOW, HIGH = {GUARD_LOW}, {GUARD_HIGH}\n" + GUARD_BODY
            + (GUARD_INSTALL if install else ""))


# ---------------------------------------------------------------- runner
def _drain(stream, sink):
    try:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                return
            sink.append(chunk)
    except (OSError, ValueError):
        return


class Runner:
    """Bounded pool of child runs; identical (argv, cwd) runs execute once."""

    def __init__(self, env, jobs):
        self.env = env
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=jobs)
        self.lock = threading.Lock()
        self.live = {}
        self.memo = {}
        self.records = []

    def submit(self, run_id, argv, cwd, cap, post=None):
        argv = [str(item) for item in argv]
        key = None if post is not None else (tuple(argv), str(cwd))
        with self.lock:
            if key is not None and key in self.memo:
                return self.memo[key]
            future = self.pool.submit(self._run, run_id, argv, str(cwd), cap,
                                      post)
            if key is not None:
                self.memo[key] = future
            return future

    def _run(self, run_id, argv, cwd, cap, post):
        record = {"id": run_id, "argv": argv, "cwd": cwd, "cap_seconds": cap,
                  "exit": None, "timed_out": False, "spawn_error": None}
        out, err = [], []
        started = time.monotonic()
        try:
            proc = subprocess.Popen(argv, cwd=cwd, env=self.env,
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    start_new_session=True)
        except OSError as exc:
            record["spawn_error"] = f"{type(exc).__name__}: {exc}"
            record["seconds"] = round(time.monotonic() - started, 2)
            return self._finish(record, b"", b"", None)
        with self.lock:
            self.live[proc.pid] = proc
        readers = [threading.Thread(target=_drain, args=(proc.stdout, out),
                                    daemon=True),
                   threading.Thread(target=_drain, args=(proc.stderr, err),
                                    daemon=True)]
        for reader in readers:
            reader.start()
        try:
            proc.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            record["timed_out"] = True
            killpg_quiet(proc.pid)
            proc.wait()
        finally:
            with self.lock:
                self.live.pop(proc.pid, None)
        record["exit"] = proc.returncode
        record["seconds"] = round(time.monotonic() - started, 2)
        # The post hook (escape scan) must see the run's leftovers before the
        # run's own process group is cleared.
        post_result = post() if post is not None else None
        killpg_quiet(proc.pid)
        for reader in readers:
            reader.join(PIPE_GRACE)
        record["pipe_held_open"] = any(r.is_alive() for r in readers)
        return self._finish(record, b"".join(out), b"".join(err), post_result)

    def _finish(self, record, stdout, stderr, post_result):
        record.update({
            "stdout_sha256": sha256_bytes(stdout), "stdout_bytes": len(stdout),
            "stderr_sha256": sha256_bytes(stderr), "stderr_bytes": len(stderr),
            "stdout_tail": tail(stdout), "stderr_tail": tail(stderr)})
        if post_result is not None:
            record["post"] = post_result
        with self.lock:
            self.records.append(record)
        return {"record": record, "stdout": stdout, "stderr": stderr,
                "post": post_result}

    def shutdown(self):
        with self.lock:
            procs = list(self.live.values())
        for proc in procs:
            killpg_quiet(proc.pid)
        self.pool.shutdown(wait=True, cancel_futures=True)


# ---------------------------------------------------------------- context
class Context:
    """Scratch root, input snapshots, bind guard and runner of one invocation."""

    def __init__(self, jobs):
        self.root = Path(tempfile.mkdtemp(prefix="kama-c2-survivors-"))
        self.sleep_marker = "kama-c2-survivors-sleep-" + sha256_bytes(
            os.urandom(16))[:12]
        self.inputs = {}
        self.snapshots = {}
        self.mirrors = {}
        self.matrix = None
        (self.root / "tmp").mkdir()
        self.bind_log = self.root / "binds.log"
        tsv_text = None
        try:
            data = CONSUMERS_TSV.read_bytes()
            self.inputs["endpoint-consumers.tsv"] = {
                "path": str(CONSUMERS_TSV), "sha256": sha256_bytes(data)}
            tsv_text = data.decode("utf-8", errors="replace")
        except OSError as exc:
            self.inputs["endpoint-consumers.tsv"] = {
                "path": str(CONSUMERS_TSV), "sha256": None, "error": str(exc)}
        self.protected = protected_ports(tsv_text)
        guard_dir = self.root / "guard"
        guard_dir.mkdir()
        source = guard_source(self.protected)
        (guard_dir / "sitecustomize.py").write_text(source, encoding="utf-8")
        self.guard = {"sha256": sha256_bytes(source.encode()),
                      "protected_ports": self.protected,
                      "port_range": [GUARD_LOW, GUARD_HIGH - 1]}
        env = dict(os.environ)
        env["PYTHONPATH"] = str(guard_dir) + (
            os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["TMPDIR"] = str(self.root / "tmp")
        env["KAMA_C2_SURVIVORS_BIND_LOG"] = str(self.bind_log)
        self.runner = Runner(env, jobs)

    # inputs --------------------------------------------------------------
    def snapshot(self, label, path, pinned=None):
        """Read PATH once into scratch; record it; return (copy, bytes)."""
        if label in self.snapshots:
            return self.snapshots[label]
        path = Path(path)
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise OwnFault(f"input {label} unreadable: {path}: {exc}")
        entry = {"path": str(path.resolve()), "sha256": sha256_bytes(data),
                 "bytes": len(data)}
        if pinned is not None:
            entry["pinned_sha256"] = pinned
            entry["pinned_ok"] = entry["sha256"] == pinned
        self.inputs[label] = entry
        if pinned is not None and not entry["pinned_ok"]:
            raise OwnFault(f"input {label} sha256 {entry['sha256']} != pinned "
                           f"{pinned} ({path})")
        dest = self.root / "inputs" / label.replace("/", "_") / path.name
        dest.parent.mkdir(parents=True)
        dest.write_bytes(data)
        dest.chmod(0o755)
        self.snapshots[label] = (dest, data)
        return dest, data

    def tool(self, name, side, current_paths, sums):
        if side == "frozen":
            path = FROZEN_TOOLS[name]
            if path.name not in sums:
                raise OwnFault(f"{FROZEN_SUMS} has no entry for {path.name}")
            return self.snapshot(f"{name}/frozen", path, sums[path.name])
        return self.snapshot(f"{name}/current", current_paths[name])

    def text(self, name, side, current_paths, sums):
        _, data = self.tool(name, side, current_paths, sums)
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise OwnFault(f"{side} {name} is not UTF-8: {exc}")

    def load_matrix(self):
        if self.matrix is not None:
            return self.matrix
        named = []
        for path in sorted(MATRIX_DIR.glob("*.json")):
            try:
                named.append((path.name, path.read_bytes()))
            except OSError as exc:
                raise OwnFault(f"matrix file unreadable: {path}: {exc}")
        digest = matrix_set_digest(named)
        ok = digest == MATRIX_SET_SHA256 and len(named) == MATRIX_FILES
        self.inputs["matrix"] = {
            "dir": str(MATRIX_DIR), "files": len(named), "set_sha256": digest,
            "pinned_set_sha256": MATRIX_SET_SHA256, "pinned_ok": ok,
            "members": {name: sha256_bytes(data) for name, data in named}}
        if not ok:
            raise OwnFault(f"matrix set {MATRIX_DIR}: {len(named)} files, "
                           f"digest {digest} != pinned {MATRIX_SET_SHA256}")
        self.matrix = named
        return named

    # staging -------------------------------------------------------------
    def stage_file(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o755)
        return path

    def fc_mirror(self, label, fc_bytes, check_bytes, probe_bytes):
        """Stage (once per label) a lane-shaped mirror; (tool, matrix, probe)."""
        if label in self.mirrors:
            return self.mirrors[label]
        base = self.root / "fc" / label
        tpv = base / "tests" / "probe-verdicts"
        for name, data in self.load_matrix():
            self.stage_file(tpv.relative_to(self.root) / name, data)
        self.stage_file(tpv.relative_to(self.root) / "check.py", check_bytes)
        tool = self.stage_file(tpv.relative_to(self.root) / "fault-controls.py",
                               fc_bytes)
        probe = self.stage_file(
            base.relative_to(self.root) / "tools" / "kama-probe.sh", probe_bytes)
        self.mirrors[label] = (tool, tpv, probe)
        return self.mirrors[label]

    # teardown ------------------------------------------------------------
    def bind_summary(self):
        pairs = []
        try:
            for line in self.bind_log.read_text().splitlines():
                pid, port = line.split()
                pairs.append((int(pid), int(port)))
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as exc:
            return {"error": f"bind log unreadable: {exc}"}
        ports = {port for _, port in pairs}
        return {"binds": len(pairs), "distinct_ports": len(ports),
                "min_port": min(ports) if ports else None,
                "max_port": max(ports) if ports else None,
                "protected_hits": sorted(ports & set(self.protected)),
                "listening_after": owned_listeners(pairs)}

    def close(self):
        self.runner.shutdown()
        stragglers = kill_marked(self.sleep_marker, prefix=True)
        shutil.rmtree(self.root, ignore_errors=True)
        return {"marked_stragglers_killed": stragglers,
                "scratch_removed": not self.root.exists()}


def owned_listeners(pairs):
    """`ss -ltnpH` rows matching a (pid, port) this invocation bound."""
    if not pairs:
        return {"command": "ss -ltnpH", "owned": [], "skipped": "no binds"}
    try:
        proc = subprocess.run(["ss", "-ltnpH"], capture_output=True, text=True,
                              timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": "ss -ltnpH", "error": str(exc), "owned": None}
    logged = set(pairs)
    owned = []
    for line in proc.stdout.splitlines():
        fields = line.split()
        port = re.search(r":(\d+)$", fields[3]) if len(fields) > 3 else None
        if port and any((int(pid), int(port.group(1))) in logged
                        for pid in re.findall(r"pid=(\d+)", line)):
            owned.append(line.strip())
    return {"command": "ss -ltnpH", "exit": proc.returncode, "owned": owned}


# ---------------------------------------------------------------- classifiers
def fc_decision(exit_code, doc):
    """The compared decision of one fault-controls main run (or None)."""
    if not isinstance(doc, dict):
        return None
    faults = doc.get("faults")
    if not isinstance(faults, list) or not is_int(doc.get("detected")) \
            or not is_int(doc.get("accepted")):
        return None
    positive = doc.get("positive_control")
    return {"exit": exit_code,
            "f0_detected": positive.get("detected")
            if isinstance(positive, dict) else None,
            "detected": doc["detected"], "accepted": doc["accepted"],
            "faults": {str(f.get("id")): f.get("detected")
                       for f in faults if isinstance(f, dict)}}


def fc_view(run):
    """Compact evidence of one fault-controls main run."""
    record = run["record"]
    doc, why = parse_json_bytes(run["stdout"])
    decision = fc_decision(record["exit"], doc)
    view = {"run": record["id"], "exit": record["exit"],
            "timed_out": record["timed_out"],
            "spawn_error": record["spawn_error"], "decision": decision}
    if decision is None:
        view["unparsed"] = why or "document lacks faults/detected/accepted"
        view["stderr_tail"] = tail(run["stderr"], 600)
        return view
    view["accepted_ids"] = sorted(k for k, v in decision["faults"].items()
                                  if v is not True)
    view["faults"] = [{"id": f.get("id"), "detected": f.get("detected"),
                       "check_exit": f.get("check_exit"), "runs": f.get("runs"),
                       "why": str(f.get("why"))[:300]}
                      for f in doc["faults"] if isinstance(f, dict)]
    return view


def classify_a(base_view, view):
    """Family (a): classify only valid detector outcomes, never own faults."""
    base = base_view["decision"]
    if (base is None or base["exit"] != 0 or base["accepted"] != 0
            or base["f0_detected"] is not True):
        return "inconclusive", (
            "unmutated current check.py must give exit 0, accepted 0, and "
            "a healthy F0 positive control")
    if view["spawn_error"] or view["timed_out"]:
        return "inconclusive", view["spawn_error"] or "detector exceeded its cap"
    if view["exit"] == 2:
        return "inconclusive", "fault-controls exit 2 (own fault), not a kill"
    if view["exit"] == 1:
        return "killed", "fault-controls exit 1 (detector rejects the mutant)"
    decision = view["decision"]
    if decision is None:
        return "inconclusive", "detector did not emit a usable decision document"
    if decision["accepted"] > 0:
        return "killed", (f"accepted {decision['accepted']}: "
                          + ",".join(view["accepted_ids"]))
    if view["exit"] != 0:
        return "inconclusive", f"unexpected detector exit {view['exit']}"
    return "survived", "exit 0, accepted 0"
[...]

SELFTEST_TARGETS = {
    "FC-target": "target-conjunct attribution",
    "FC-f6cache": "F6: replay run shares one cache",
    "FC-f0gate": "F0 gate: a reject-everything",
    "AO-opened": "only `opened` changes",
    "AO-blank": "edit after a blank line",
}


def selftest_summary_ok(run):
    record = run["record"]
    if record["exit"] != 0 or record["spawn_error"] or record["timed_out"]:
        return False
    doc, _ = parse_json_bytes(run["stdout"])
    if isinstance(doc, dict) and "passed" in doc:
        return doc["passed"] is True and doc.get("problems") == []
    match = re.search(r"(?m)^(\d+)/(\d+) selftest cases passed\s*$",
                      tail(run["stdout"], 8000))
    return bool(match and match.group(1) == match.group(2))


def selftest_enumeration_matches(base_run, run):
    """Require the mutant selftest to report the baseline's full case set."""
    base_doc, _ = parse_json_bytes(base_run["stdout"])
    doc, _ = parse_json_bytes(run["stdout"])
    if isinstance(base_doc, dict) and isinstance(doc, dict):
        counts = (
            "selftest", "matrix_files", "matrix_tests", "matrix_sha256",
            "rows_checked", "families_covered", "faults_checked",
            "classifier_cases", "wrapper_checks",
        )
        if not all(key in base_doc and doc.get(key) == base_doc[key]
                   for key in counts):
            return False
        return all(
            isinstance(base_doc.get(key), dict)
            and isinstance(doc.get(key), dict)
            and set(doc[key]) == set(base_doc[key])
            for key in ("gate", "escape"))
    summary = r"(?m)^(\d+)/(\d+) selftest cases passed\s*$"
    base_match = re.search(summary, tail(base_run["stdout"], 8000))
    output = tail(run["stdout"], 8000)
    match = re.search(summary, output)
    if not base_match or not match:
        return False
    if (base_match.group(1) != base_match.group(2)
            or match.group(2) != base_match.group(2)):
        return False
    failed_cases = sum(line.startswith("FAIL") for line in output.splitlines())
    return int(match.group(1)) + failed_cases == int(match.group(2))


def selftest_arm(base_run, run, expected_failure):
    """Only a named selftest assertion is a kill; exit 2 is inconclusive."""
    record = run["record"]
    if not selftest_summary_ok(base_run):
        return "inconclusive", "unmutated selftest did not pass cleanly"
    if record["spawn_error"] or record["timed_out"] or record["exit"] == 2:
        return "inconclusive", record["spawn_error"] or (
            "selftest timed out" if record["timed_out"]
            else "selftest exit 2 (own fault)")
    if record["exit"] == 0:
        return ("survived", "selftest passes") if selftest_summary_ok(run) \
            else ("inconclusive", "exit 0 without a valid passing selftest")
    if record["exit"] != 1:
        return "inconclusive", f"unexpected selftest exit {record['exit']}"
    if not selftest_enumeration_matches(base_run, run):
        return "inconclusive", "selftest did not enumerate the baseline case set"
    doc, _ = parse_json_bytes(run["stdout"])
    if isinstance(doc, dict) and isinstance(doc.get("problems"), list):
        targeted = (doc.get("passed") is False and any(
            expected_failure in str(problem) for problem in doc["problems"]))
    else:
        targeted = any(expected_failure in line
                       for line in tail(run["stdout"], 8000).splitlines()
                       if line.startswith("FAIL"))
    if targeted:
        return "killed", f"targeted selftest assertion failed: {expected_failure}"
    return "inconclusive", "exit 1 lacks the named selftest failure: " + \
        expected_failure


def main_arm(base_view, view):
    base = base_view["decision"]
    if (base is None or base["exit"] != 0 or base["accepted"] != 0
            or base["f0_detected"] is not True):
        return "inconclusive", (
            "unmutated fault-controls must give exit 0, accepted 0, and "
            "a healthy F0 positive control")
    if view["spawn_error"] or view["timed_out"]:
        return "inconclusive", view["spawn_error"] or "main run exceeded its cap"
    if view["exit"] == 2:
        return "inconclusive", "fault-controls exit 2 (own fault), not a kill"
    if view["decision"] is None:
        return "inconclusive", "fault-controls did not emit a usable decision"
    if view["exit"] not in (0, 1):
        return "inconclusive", f"unexpected main-run exit {view['exit']}"
    if view["decision"] != base:
        return "killed", "main-run decision differs from the unmutated tool's"
    return "survived", "main-run decision identical to the unmutated tool's"


def combine_arms(arms):
    """Any independently conclusive detector arm is sufficient to kill."""
    statuses = [status for status, _ in arms]
    if not statuses:
        return "inconclusive"
    if "killed" in statuses:
        return "killed"
    if any(status == "inconclusive" for status in statuses):
        return "inconclusive"
    if all(status == "survived" for status in statuses):
        return "survived"
    return "inconclusive"


def classify_crash(run, row_name, started):
    """Family (e): check faults must yield per-row failures, not own errors."""
    record = run["record"]
    facts = {"run": record["id"], "exit": record["exit"],
             "seconds": record.get("seconds"),
             "traceback": TRACEBACK in run["stderr"], "started": started}
    if record["spawn_error"] or record["timed_out"]:
        return "inconclusive", (
            record["spawn_error"] or "check.py exceeded its outer cap"), facts
    if record["exit"] == 2:
        return "inconclusive", "check.py exit 2 (own fault), not a result", facts
    doc, why_json = parse_json_bytes(run["stdout"])
    row = None
    if isinstance(doc, dict) and isinstance(doc.get("records"), list):
        row = next((r for r in doc["records"]
                    if isinstance(r, dict) and r.get("name") == row_name), None)
    if row is not None:
        facts["row_passed"] = row.get("passed")
        facts["row_error"] = (str(row["error"])[:300] if row.get("error")
                              else None)
    reasons = []
    if record["exit"] != 1:
        reasons.append(f"exit {record['exit']}, not the per-row failure exit 1")
    if doc is None:
        reasons.append(f"stdout is not a JSON document ({why_json})")
    elif row is None:
        reasons.append(f"row {row_name} missing from records")
    else:
        if row.get("passed") is not False:
            reasons.append("row did not fail")
        if not row.get("error"):
            reasons.append("row failed without an error")
    if facts["traceback"]:
        reasons.append("Python traceback on stderr")
    post = run.get("post")
    if post is not None:
        facts["escaped_pids"] = post["escaped_pids"]
        facts["killed_after_scan"] = post["killed_after_scan"]
        if post["escaped_pids"]:
            reasons.append("escaped child alive after check.py exited: pids "
                           + ",".join(map(str, post["escaped_pids"])))
    if not started:
        return "not_exercised", "probe never started; " + (
            "; ".join(reasons) or "nothing else wrong"), facts
    if reasons:
        return "accepted", "; ".join(reasons), facts
    return "handled", "per-row failure: " + str(facts.get("row_error"))[:200], \
        facts


def classify_provenance(run, ledger):
    record = run["record"]
    facts = {"run": record["id"], "exit": record["exit"]}
    if record["spawn_error"] or record["timed_out"]:
        return "inconclusive", record["spawn_error"] or "tool exceeded its cap", facts
    if record["exit"] == 2:
        return "inconclusive", "provenance tool exit 2 (own fault)", facts
    if record["exit"] != 0:
        return "inconclusive", f"provenance tool exit {record['exit']}", facts
    try:
        doc = json.loads(Path(ledger).read_text(encoding="utf-8"))
        entry = doc["entries"][-1]
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        return "inconclusive", f"ledger unreadable: {type(exc).__name__}: {exc}", facts
    if not isinstance(entry, dict) or entry.get("kind") != "attempt" \
            or entry.get("label") != "refused":
        return "inconclusive", "last ledger entry is not the refused attempt", facts
    for key in ("refused", "spawned", "spawned_method", "parseable",
                "result_sha256"):
        facts[key] = entry.get(key)
    refused = entry.get("refused")
    if is_int(refused) and refused == EXPECTED_REFUSED:
        return "correct", f"refused {refused}", facts
    return "miscount", f"refused {refused!r}, expected {EXPECTED_REFUSED}", facts


# ---------------------------------------------------------------- families
def mutants_of(family, text, prefix):
    """Every named edit of FAMILY applied to TEXT (bytes None when not ok)."""
    staged = []
    for mutant in MUTANTS[family]:
        label = f"{prefix}+{mutant['id']}"
        mutated, site = apply_edit(text, mutant["old"], mutant["new"], label)
        data = mutated.encode("utf-8") if mutated is not None else None
        staged.append({"mutant": mutant, "site": site, "label": label,
                       "bytes": data,
                       "sha256": sha256_bytes(data) if data else None})
    return staged


def head(mutant):
    return {"id": mutant["id"], "title": mutant["title"],
            "advice": mutant["advice"],
            "edit": {"old": mutant["old"], "new": mutant["new"]}}


def close_items(by_id):
    items = []
    for entry in by_id.values():
        entry["before"] = entry["frozen"]["outcome"]
        entry["after"] = entry["current"]["outcome"]
        items.append(entry)
    return items


def fc_main(ctx, label, mirror, target, target_label):
    tool, tpv, probe = mirror
    return ctx.runner.submit(
        f"fault-controls[{label}] --check {target_label}",
        [sys.executable, tool, "--check", target, "--probe", probe,
         "--matrix-dir", tpv, "--json"], tool.parents[2], CAP["fc-main"])


def fc_selftest(ctx, label, mirror):
    tool, tpv, _ = mirror
    return ctx.runner.submit(
        f"fault-controls[{label}] --selftest",
        [sys.executable, tool, "--selftest", "--matrix-dir", tpv],
        tool.parents[2], CAP["fc-selftest"])


def base_mirror(ctx, side, cur, sums):
    """The unmutated fault-controls of SIDE; shared by families (a) and (b)
    so their identical baseline main run executes once."""
    _, fc = ctx.tool("fault-controls", side, cur, sums)
    _, check = ctx.tool("check", "current", cur, sums)
    _, probe = ctx.snapshot("probe", PROBE)
    return ctx.fc_mirror(side, fc, check, probe)


def family_a(ctx, cur, sums):
    check_path, _ = ctx.tool("check", "current", cur, sums)
    text = ctx.text("check", "current", cur, sums)
    mirrors = {side: base_mirror(ctx, side, cur, sums) for side in SIDES}
    baselines = {side: fc_main(ctx, side, mirrors[side], check_path,
                               "check[current]") for side in SIDES}
    plan = []
    for item in mutants_of("a", text, "check[current]"):
        runs = None
        if item["bytes"] is not None:
            path = ctx.stage_file(f"a/{item['mutant']['id']}/check.py",
                                  item["bytes"])
            runs = {side: fc_main(ctx, side, mirrors[side], path, item["label"])
                    for side in SIDES}
        plan.append((item, runs))

    def finish():
        base_views = {side: fc_view(baselines[side].result()) for side in SIDES}
        by_id = {}
        for item, runs in plan:
            entry = head(item["mutant"])
            entry.update(site=item["site"], mutant_sha256=item["sha256"])
            for side in SIDES:
                if runs is None:
                    entry[side] = {"outcome": item["site"]["status"],
                                   "why": "edit not applied"}
                    continue
                view = fc_view(runs[side].result())
                outcome, why = classify_a(base_views[side], view)
                entry[side] = {"outcome": outcome, "why": why, "detector": view}
            by_id[item["mutant"]["id"]] = entry
        return {"title": FAMILY_TITLES["a"], "mutated": "check/current",
                "detectors": {side: f"fault-controls/{side}" for side in SIDES},
                "baselines": base_views, "items": close_items(by_id)}
    return finish


def family_b(ctx, cur, sums):
    check_path, check = ctx.tool("check", "current", cur, sums)
    _, probe = ctx.snapshot("probe", PROBE)
    plans = {}
    for side in SIDES:
        text = ctx.text("fault-controls", side, cur, sums)
        mirror = base_mirror(ctx, side, cur, sums)
        base = (fc_selftest(ctx, side, mirror),
                fc_main(ctx, side, mirror, check_path, "check[current]"))
        mutants = []
        for item in mutants_of("b", text, side):
            pair = None
            if item["bytes"] is not None:
                m = ctx.fc_mirror(item["label"], item["bytes"], check, probe)
                pair = (fc_selftest(ctx, item["label"], m),
                        fc_main(ctx, item["label"], m, check_path,
                                "check[current]"))
            mutants.append((item, pair))
        plans[side] = (base, mutants)

    def finish():
        versions, by_id = {}, {}
        for side in SIDES:
            (base_self, base_main), mutants = plans[side]
            base_self_run = base_self.result()
            base_view = fc_view(base_main.result())
            versions[side] = {
                "tool": f"fault-controls/{side}",
                "selftest": {"run": base_self_run["record"]["id"],
                             "exit": base_self_run["record"]["exit"]},
                "main": base_view}
            for item, pair in mutants:
                entry = by_id.setdefault(item["mutant"]["id"],
                                         head(item["mutant"]))
                result = {"site": item["site"], "mutant_sha256": item["sha256"]}
                if pair is None:
                    result.update(outcome=item["site"]["status"],
                                  why="edit not applied")
                else:
                    self_run = pair[0].result()
                    view = fc_view(pair[1].result())
                    arms = (selftest_arm(
                                base_self_run, self_run,
                                SELFTEST_TARGETS[item["mutant"]["id"]]),
                            main_arm(base_view, view))
                    result.update(
                        outcome=combine_arms(arms),
                        why="; ".join(f"{name} {status} ({why})" for name,
                                      (status, why) in zip(("selftest", "main"),
                                                           arms)),
                        selftest={"run": self_run["record"]["id"],
                                  "exit": self_run["record"]["exit"],
                                  "stdout_tail": tail(self_run["stdout"], 600)},
                        main=view)
                entry[side] = result
        return {"title": FAMILY_TITLES["b"], "baselines": versions,
                "items": close_items(by_id)}
    return finish


def selftest_line(stdout):
    lines = [line for line in tail(stdout, 4000).splitlines()
             if re.search(r"\d+/\d+ .*passed", line)]
    return lines[-1] if lines else None


def family_c(ctx, cur, sums):
    plans = {}
    for side in SIDES:
        path, _ = ctx.tool("append-only", side, cur, sums)
        text = ctx.text("append-only", side, cur, sums)
        base = ctx.runner.submit(f"append-only[{side}] --selftest",
                                 [sys.executable, path, "--selftest"],
                                 path.parent, CAP["ao-selftest"])
        mutants = []
        for item in mutants_of("c", text, side):
            run = None
            if item["bytes"] is not None:
                copy = ctx.stage_file(f"ao/{item['label']}/{path.name}",
                                      item["bytes"])
                run = ctx.runner.submit(
                    f"append-only[{item['label']}] --selftest",
                    [sys.executable, copy, "--selftest"], copy.parent,
                    CAP["ao-selftest"])
            mutants.append((item, run))
        plans[side] = (base, mutants)

    def finish():
        baselines, by_id = {}, {}
        for side in SIDES:
            base, mutants = plans[side]
            base_run = base.result()
            baselines[side] = {"run": base_run["record"]["id"],
                               "exit": base_run["record"]["exit"],
                               "summary": selftest_line(base_run["stdout"])}
            for item, run in mutants:
                entry = by_id.setdefault(item["mutant"]["id"],
                                         head(item["mutant"]))
                result = {"site": item["site"], "mutant_sha256": item["sha256"]}
                if run is None:
                    result.update(outcome=item["site"]["status"],
                                  why="edit not applied")
                else:
                    mutant_run = run.result()
                    status, why = selftest_arm(
                        base_run, mutant_run,
                        SELFTEST_TARGETS[item["mutant"]["id"]])
                    result.update(
                        outcome=status, why=why,
                        run=mutant_run["record"]["id"],
                        exit=mutant_run["record"]["exit"],
                        summary=selftest_line(mutant_run["stdout"]),
                        fail_lines=[line for line in tail(
                            mutant_run["stdout"], 4000).splitlines()
                            if line.startswith("FAIL")][:10])
                entry[side] = result
        return {"title": FAMILY_TITLES["c"], "baselines": baselines,
                "items": close_items(by_id)}
    return finish


def evidence(ctx):
    """Pinned round-17 refused evidence plus its attempts.json corroboration."""
    copy, refused = ctx.snapshot("evidence/refused-result-1.json",
                                 *EVIDENCE["refused-result"])
    _, attempts = ctx.snapshot("evidence/attempts.json", *EVIDENCE["attempts"])
    try:
        logged = [entry.get("refused") for entry in json.loads(attempts)
                  if isinstance(entry, dict) and entry.get("result") == "refused"]
    except (ValueError, TypeError, AttributeError) as exc:
        raise OwnFault(f"attempts.json unparseable: {exc}")
    if logged != [EXPECTED_REFUSED]:
        raise OwnFault(f"attempts.json refused log {logged!r} != "
                       f"[{EXPECTED_REFUSED}]")
    return copy, {"attempts_json_refused": logged[0],
                  "refusal_messages_in_result": refused.decode(
                      "utf-8", errors="replace").count(
                          "Background job limit reached")}


def family_d(ctx, cur, sums):
    refused_copy, corroboration = evidence(ctx)
    runs = {}
    for side in SIDES:
        path, data = ctx.tool("provenance", side, cur, sums)
        policy = re.search(rb'"UFO_CONFIG_PATH":\s*"([^"]+)"', data)
        if policy:
            policy_path = Path(policy.group(1).decode("utf-8", "replace"))
            try:
                digest = sha256_bytes(policy_path.read_bytes())
            except OSError:
                digest = None
            ctx.inputs[f"policy-read-by-provenance/{side}"] = {
                "path": str(policy_path), "sha256": digest}
        ledger = ctx.root / "d" / side / "ledger.json"
        ledger.parent.mkdir(parents=True)
        runs[side] = (ledger, ctx.runner.submit(
            f"provenance[{side}] --attempt-result refused-result-1.json "
            "--label refused",
            [sys.executable, path, "--attempt-result", refused_copy,
             "--label", "refused", "--out", ledger],
            ledger.parent, CAP["provenance"]))

    def finish():
        entry = {"id": "refused-count", "title": "refused tasks recorded for "
                 "the round-17 refused task call",
                 "advice": ADVICE17 + "ProvenanceRerun.md:5-7",
                 "expected_refused": EXPECTED_REFUSED,
                 "corroboration": corroboration}
        for side in SIDES:
            ledger, future = runs[side]
            run = future.result()
            outcome, why, facts = classify_provenance(run, ledger)
            facts["stderr_tail"] = tail(run["stderr"], 600)
            entry[side] = {"outcome": outcome, "why": why, **facts}
        return {"title": FAMILY_TITLES["d"], "items": close_items(
            {"refused-count": entry})}
    return finish


def crash_probe(ctx, where, fault, started, nonce):
    """Write the bash probe for one crash fault under scratch/WHERE."""
    lines = ["#!/usr/bin/env bash",
             f"# survivors.py crash-fault probe: {fault['id']}",
             f"printf 'started %s\\n' \"$$\" > {shlex.quote(str(started))}"]
    if fault["payload"] is not None:
        payload = ctx.stage_file(f"{where}/{fault['id']}.payload",
                                 fault["payload"])
        lines += [f"cat {shlex.quote(str(payload))}", "exit 2"]
    else:
        lines += [f"(exec -a {shlex.quote(nonce)} sleep {SLEEP_SECONDS})",
                  "printf 'sleep completed\\n'"]
    return ctx.stage_file(f"{where}/{fault['id']}.sh",
                          ("\n".join(lines) + "\n").encode())


def escape_post(nonce):
    def post():
        alive = settle_marked(nonce)
        return {"escaped_pids": alive, "killed_after_scan": kill_marked(nonce)}
    return post


def stage_check(ctx, where, data):
    for name, matrix_bytes in ctx.load_matrix():
        ctx.stage_file(f"{where}/{name}", matrix_bytes)
    return ctx.stage_file(f"{where}/check.py", data)


def submit_crash(ctx, label, check, where, fault):
    started = ctx.root / where / f"{fault['id']}.started"
    nonce = f"{ctx.sleep_marker}-{label}-{fault['id']}"
    probe = crash_probe(ctx, where, fault, started, nonce)
    future = ctx.runner.submit(
        f"check[{label}] --probe {fault['id']}.sh --only {CRASH_ROW}",
        [sys.executable, check, "--probe", probe, "--only", CRASH_ROW,
         "--json"], check.parent, CAP["check-crash"],
        post=escape_post(nonce) if fault["payload"] is None else None)
    return started, future


def family_e(ctx, cur, sums):
    plans = {}
    for side in SIDES:
        _, data = ctx.tool("check", side, cur, sums)
        check = stage_check(ctx, f"e/{side}", data)
        plans[side] = [(fault, *submit_crash(ctx, side, check, f"e/{side}",
                                             fault))
                       for fault in CRASH_FAULTS]

    def finish():
        by_id = {}
        for side in SIDES:
            for fault, started, future in plans[side]:
                outcome, why, facts = classify_crash(
                    future.result(), CRASH_ROW, started.exists())
                entry = by_id.setdefault(fault["id"], {
                    "id": fault["id"], "title": fault["title"],
                    "advice": fault["advice"],
                    "payload_sha256": sha256_bytes(fault["payload"])
                    if fault["payload"] is not None else None})
                entry[side] = {"outcome": outcome, "why": why, **facts}
        return {"title": FAMILY_TITLES["e"], "row": CRASH_ROW,
                "items": close_items(by_id)}
    return finish


FAMILY_FUNCS = {"a": family_a, "b": family_b, "c": family_c, "d": family_d,
                "e": family_e}


def prepare(ctx, families, cur, sums):
    """Read, pin-check and snapshot every input before any run starts."""
    need = set()
    if {"a", "b"} & set(families):
        need |= {("fault-controls", "frozen"), ("fault-controls", "current"),
                 ("check", "current")}
    if "c" in families:
        need |= {("append-only", "frozen"), ("append-only", "current")}
    if "d" in families:
        need |= {("provenance", "frozen"), ("provenance", "current")}
        evidence(ctx)
    if "e" in families:
        need |= {("check", "frozen"), ("check", "current")}
    for name, side in sorted(need):
        ctx.tool(name, side, cur, sums)
    if {"a", "b", "e"} & set(families):
        ctx.load_matrix()
    if {"a", "b"} & set(families):
        ctx.snapshot("probe", PROBE)
    for family in families:
        for filename in ADVICE_FILES[family]:
            ctx.snapshot(f"advice/{family}/{filename}", ADVICE_ROOT / filename)


def count(results):
    counts = {"named": {}, "before": {}, "after": {},
              "outcomes": {"before": {}, "after": {}}}
    for family, result in results.items():
        items = result["items"]
        counts["named"][family] = len(items)
        for side in ("before", "after"):
            counts[side][family] = sum(1 for item in items
                                       if item[side] not in GOOD)
            for item in items:
                tally = counts["outcomes"][side]
                tally[item[side]] = tally.get(item[side], 0) + 1
    for key in ("named", "before", "after"):
        counts[key]["total"] = sum(counts[key].values())
    counts["inconclusive"] = {
        side: sum(1 for result in results.values() for item in result["items"]
                  if item[side] in {"inconclusive", "error", "not_exercised",
                                    "baseline_invalid"})
        for side in ("before", "after")}
    return counts
def frozen_witness_validation(results):
    witnesses, mismatches = [], []
    for family, expected in FROZEN_EXPECTED.items():
        if family not in results:
            continue
        observed = {item["id"]: item["before"]
                    for item in results[family]["items"]}
        for mutant, want in expected.items():
            got = observed.get(mutant, "missing")
            row = {"family": family, "id": mutant, "expected": want,
                   "observed": got, "matches": got == want}
            witnesses.append(row)
            if got != want:
                mismatches.append(row)
    return {"witnesses": witnesses, "mismatches": mismatches}


# ---------------------------------------------------------------- driver
def parse_families(value):
    wanted = [part.strip() for part in value.split(",") if part.strip()]
    unknown = sorted(set(wanted) - set(FAMILIES))
    if unknown or not wanted:
        raise argparse.ArgumentTypeError(
            f"--family takes a comma list of {','.join(FAMILIES)}; got {value!r}")
    return [family for family in FAMILIES if family in wanted]


def build_parser():
    parser = argparse.ArgumentParser(
        description="Count round-17 named survivors before (frozen) and "
                    "after (current) for claim C2's detectors.")
    parser.add_argument("--json", action="store_true",
                        help="print the result document on stdout "
                             "(human summary moves to stderr)")
    parser.add_argument("--out", help="also write the document here "
                                      "(created exclusively, never clobbered)")
    parser.add_argument("--family", type=parse_families,
                        default=list(FAMILIES),
                        help="comma list from a,b,c,d,e (default: all)")
    parser.add_argument("--jobs", type=int, default=1,
                        help="concurrent child runs (default 1)")
    for name in TOOLS:
        parser.add_argument(f"--{name}", dest=name.replace("-", "_"),
                            default=str(DEFAULT_CURRENT[name]),
                            help=f"CURRENT {name} (default "
                                 f"{DEFAULT_CURRENT[name]})")
    parser.add_argument("--selftest", action="store_true",
                        help="check the edit table, classifiers, guard, escape "
                             "scan and frozen-tool known answers, then exit")
    return parser


def summarize(doc):
    lines = [f"{SCHEMA} families={','.join(doc['families'])} "
             f"jobs={doc['jobs']} seconds={doc.get('seconds')}"]
    for family, result in doc.get("results", {}).items():
        lines.append(f"[{family}] {result['title']}")
        for item in result["items"]:
            lines.append(f"  {item['id']:<14} frozen {item['before']:<16} "
                         f"current {item['after']:<16} "
                         f"{str(item['current'].get('why'))[:100]}")
    counts = doc.get("counts")
    if counts:
        lines.append("named items not killed/handled/correct: before "
                     f"{counts['before']['total']} -> after "
                     f"{counts['after']['total']} "
                     f"(of {counts['named']['total']} named)")
    for fault in doc["own_faults"]:
        lines.append(f"OWN FAULT: {fault}")
    lines.append(f"exit {doc['exit']}")
    return "\n".join(lines)


def run_count(args):
    if args.jobs < 1:
        print("survivors: --jobs must be >= 1", file=sys.stderr)
        return 2
    out = Path(args.out).absolute() if args.out else None
    if out is not None and (out.exists() or not out.parent.is_dir()):
        print(f"survivors: --out {out} exists or its directory is missing; "
              "refusing (never clobbered)", file=sys.stderr)
        return 2
    cur = {name: Path(getattr(args, name.replace("-", "_"))) for name in TOOLS}
    started = time.monotonic()
    doc = {"schema": SCHEMA, "started_utc": utc_now(),
           "tool": {"path": str(SELF),
                    "sha256": sha256_bytes(SELF.read_bytes())},
           "python": {"executable": sys.executable,
                      "version": sys.version.split()[0]},
           "lane": str(LANE), "families": args.family, "jobs": args.jobs,
           "own_faults": []}
    doc["named_universe"] = "round-17 published named survivors, families a-e"
    doc["fresh_wave2"] = {
        "included": False, "mutants": 0,
        "reason": "fresh wave-2 mutants are a separate denominator"}
    ctx = None
    try:
        ctx = Context(args.jobs)
        manifest_bytes = FROZEN_SUMS.read_bytes()
        sums = parse_sums(manifest_bytes)
        ctx.inputs["frozen/SHA256SUMS"] = {
            "path": str(FROZEN_SUMS),
            "sha256": sha256_bytes(manifest_bytes)}
        prepare(ctx, args.family, cur, sums)
        finishers = {family: FAMILY_FUNCS[family](ctx, cur, sums)
                     for family in args.family}
        doc["results"] = {family: finish()
                          for family, finish in finishers.items()}
        doc["counts"] = count(doc["results"])
        doc["frozen_witness_validation"] = frozen_witness_validation(
            doc["results"])
    except OwnFault as exc:
        doc["own_faults"].append(str(exc))
    except KeyboardInterrupt:
        doc["own_faults"].append("interrupted")
    except Exception as exc:                       # pragma: no cover
        doc["own_faults"].append(
            f"internal error: {type(exc).__name__}: {exc}")
    finally:
        if ctx is not None:
            for name in TOOLS:
                frozen = ctx.inputs.get(f"{name}/frozen")
                current = ctx.inputs.get(f"{name}/current")
                if frozen and current:
                    current["same_as_frozen"] = (
                        current["sha256"] == frozen["sha256"])
            doc["inputs"] = ctx.inputs
            doc["bind_guard"] = dict(ctx.guard, summary=ctx.bind_summary())
            teardown = ctx.close()
            doc["runs"] = sorted(ctx.runner.records, key=lambda r: r["id"])
            doc["teardown"] = teardown
    doc["seconds"] = round(time.monotonic() - started, 1)
    if doc["own_faults"]:
        doc.pop("results", None)
        doc.pop("counts", None)
        doc["exit"] = 2
    else:
        inconclusive = doc["counts"]["inconclusive"]
        witness_mismatches = doc["frozen_witness_validation"]["mismatches"]
        if any(inconclusive.values()) or witness_mismatches:
            doc["exit"] = 2
            doc["inconclusive_reasons"] = {
                "items": [
                    {"family": family, "id": item["id"],
                     "before": item["before"], "after": item["after"]}
                    for family, result in doc["results"].items()
                    for item in result["items"]
                    if item["before"] in {"inconclusive", "error", "not_exercised",
                                          "baseline_invalid"}
                    or item["after"] in {"inconclusive", "error", "not_exercised",
                                         "baseline_invalid"}],
                "frozen_witness_mismatches": witness_mismatches}
        else:
            doc["exit"] = 0 if doc["counts"]["after"]["total"] == 0 else 1
    if out is not None:
        try:
            write_exclusive(out, (json.dumps(doc, indent=2) + "\n").encode())
        except OSError as exc:
            print(f"survivors: cannot write --out {out}: {exc}",
                  file=sys.stderr)
            doc["exit"] = 2
    blob = (json.dumps(doc, indent=2) + "\n").encode("utf-8")
    if args.json:
        sys.stdout.write(blob.decode("utf-8"))
        print(summarize(doc), file=sys.stderr)
    else:
        print(summarize(doc))
    return doc["exit"]


# ---------------------------------------------------------------- selftest
LEAKY_CHECKER = """import subprocess, sys
try:
    subprocess.run(["bash", sys.argv[1]], capture_output=True, timeout=1)
except subprocess.TimeoutExpired:
    pass
"""
GROUP_CHECKER = """import os, signal, subprocess, sys
p = subprocess.Popen(["bash", sys.argv[1]], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, start_new_session=True)
try:
    p.communicate(timeout=1)
except subprocess.TimeoutExpired:
    os.killpg(p.pid, signal.SIGKILL)
    p.communicate()
"""
GUARD_PROBE = """import socket
ok = socket.socket.bind.__name__ == "kama_c2_guarded_bind"
port = None
if ok:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
print(ok, port)
"""


def selftest_pure(check):
    """Edit semantics, the edit table on frozen bytes, and classifiers."""
    mutated, site = apply_edit("def f():\n    x = 1\nb = 3\n",
                               "    x = 1\n", "    x = 2\n", "t")
    check("edit applies at its single line-anchored site",
          mutated == "def f():\n    x = 2\nb = 3\n"
          and site == {"count": 1, "lines": [2], "status": "ok"}, site)
    for text, old, new, want in (
            ("a\nb\n", "  x = 1\n", "  x = 2\n", "site_missing"),
            ("  x = 1\n  x = 1\n", "  x = 1\n", "  x = 2\n", "site_ambiguous"),
            ("zz  x = 1\n", "  x = 1\n", "  x = 2\n", "site_missing"),
            ("x = 1\n", "x = 1\n", "x = (\n", "stillborn")):
        _, site = apply_edit(text, old, new, "t")
        check(f"edit status {want} for {text!r}", site["status"] == want, site)

    try:
        sums = read_sums()
    except OwnFault as exc:
        sums = {}
        check("frozen SHA256SUMS readable", False, exc)
    for path in FROZEN_TOOLS.values():
        try:
            digest = sha256_bytes(path.read_bytes())
        except OSError as exc:
            digest = f"unreadable: {exc}"
        check(f"frozen {path.name} matches SHA256SUMS",
              sums.get(path.name) == digest, digest)
    for family, tool in MUTANT_TOOL.items():
        try:
            text = FROZEN_TOOLS[tool].read_text(encoding="utf-8")
        except OSError as exc:
            check(f"family {family} frozen {tool} readable", False, exc)
            continue
        for mutant in MUTANTS[family]:
            mutated, site = apply_edit(text, mutant["old"], mutant["new"],
                                       mutant["id"])
            restored = mutated is not None and apply_edit(
                mutated, mutant["new"], mutant["old"], mutant["id"])[0] == text
            check(f"{mutant['id']} applies once to frozen {tool}, compiles, "
                  "reverses exactly", site["status"] == "ok"
                  and mutated != text and restored, site)

    def view(exit_code, accepted=None, faults=None, timed_out=False):
        decision = None if accepted is None else {
            "exit": exit_code, "f0_detected": True, "detected": 8 - accepted,
            "accepted": accepted, "faults": faults or {"F1": accepted == 0}}
        return {"exit": exit_code, "timed_out": timed_out, "spawn_error": None,
                "decision": decision, "accepted_ids": ["F1"] if accepted else []}
    good = view(0, 0)
    for name, got, want in (
            ("(a) exit 0 / accepted 0 survives", classify_a(good, view(0, 0)),
             "survived"),
            ("(a) accepted > 0 kills", classify_a(good, view(1, 1)), "killed"),
            ("(a) non-own exit 1 kills even with accepted 0",
             classify_a(good, view(1, 0)), "killed"),
            ("(a) exit 2 is inconclusive",
             classify_a(good, view(2)), "inconclusive"),
            ("(a) exit 0 without a document is inconclusive",
             classify_a(good, view(0)), "inconclusive"),
            ("(a) cap expiry is inconclusive",
             classify_a(good, view(-9, timed_out=True)), "inconclusive"),
            ("(a) dirty baseline is inconclusive",
             classify_a(view(1, 1), view(1, 1)), "inconclusive"),
            ("(b) identical decision survives the main arm",
             main_arm(good, view(0, 0)), "survived"),
            ("(b) a changed decision kills the main arm",
             main_arm(good, view(0, 0, {"F1": True, "F6": True})), "killed")):
        check(name, got[0] == want, got)
    def fake(exit_code, stdout):
        return {"record": {"exit": exit_code, "timed_out": False,
                           "spawn_error": None}, "stdout": stdout}
    fc_counts = {
        "selftest": "kama-fault-controls/selftest-v1",
        "matrix_files": 9,
        "matrix_tests": 72,
        "matrix_sha256": "bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32",
        "rows_checked": 5,
        "families_covered": ["DEAD", "FOREIGN_SERVICE", "MODEL_LOADING",
                             "MODEL_MISMATCH", "MODEL_OK"],
        "faults_checked": 18,
        "classifier_cases": 23,
        "gate": {"reject-everything": {}, "accept-everything": {}},
        "wrapper_checks": 35,
        "escape": {"direct-kill": {}, "group-kill": {}},
    }
    base_selftest = fake(0, json.dumps(dict(
        fc_counts, passed=True, problems=[])).encode())
    target_failure = fake(1, json.dumps(dict(
        fc_counts, passed=False,
        problems=["target-conjunct attribution"])).encode())
    unrelated_failure = fake(1, json.dumps(dict(
        fc_counts, passed=False, problems=["different selftest failed"])).encode())
    check("(b/c) completed FC-target JSON selftest remains a kill",
          selftest_arm(base_selftest, target_failure,
                       SELFTEST_TARGETS["FC-target"])[0] == "killed")
    # Retained C2 evidence for this exact append-only source: 42/42 baseline,
    # and AO-blank's complete targeted failure at 36/42.
    ao_baseline = fake(0, b"42/42 selftest cases passed\n")
    ao_target_line = (
        "FAIL: edit after a blank line (want exit 1 ['S002:teaches'], "
        "got exit 2 error 'from:9: row-like line outside the parsed "
        "registry table; refusing to drop it')")
    ao_fail_lines = [
        ao_target_line,
        ("FAIL: row added after a blank line (want exit 0 added ['S003'], "
         "got exit 2 error 'to:9: row-like line outside the parsed "
         "registry table; refusing to drop it')"),
        ("FAIL: row removed from a later table segment "
         "(want exit 1 ['S002:removed'], got exit 2 error "
         "'from:11: row-like line outside the parsed registry table; "
         "refusing to drop it')"),
        ("FAIL: edit in a later table segment "
         "(want exit 1 ['S002:opened'], got exit 2 error "
         "'from:11: row-like line outside the parsed registry table; "
         "refusing to drop it')"),
        ("FAIL: edit under a deeper subheading "
         "(want exit 1 ['S002:scope'], got exit 2 error "
         "'from:11: row-like line outside the parsed registry table; "
         "refusing to drop it')"),
        ("FAIL: later segment with another header "
         "(want exit 2 error ~'id cell `id` is not', got exit 2 error "
         "'from:11: row-like line outside the parsed registry table; "
         "refusing to drop it')"),
    ]
    ao_complete_failure = fake(
        1, ("\n".join(ao_fail_lines)
            + "\n36/42 selftest cases passed\n").encode())
    ao_early_abort = fake(1, (ao_target_line + "\n").encode())
    ao_short_summary = fake(
        1, (ao_target_line + "\n1/42 selftest cases passed\n").encode())
    check("(b/c) completed 42-case target failure kills",
          selftest_arm(ao_baseline, ao_complete_failure,
                       SELFTEST_TARGETS["AO-blank"])[0] == "killed")
    check("(b/c) early-abort same target literal is inconclusive",
          selftest_arm(ao_baseline, ao_early_abort,
                       SELFTEST_TARGETS["AO-blank"])[0] == "inconclusive")
    check("(b/c) one-of-42 summary with one target FAIL is incomplete",
          selftest_arm(ao_baseline, ao_short_summary,
                       SELFTEST_TARGETS["AO-blank"])[0] == "inconclusive")
    check("(b/c) unrelated selftest failure is inconclusive",
          selftest_arm(base_selftest, unrelated_failure, "targeted")[0]
          == "inconclusive")
    check("(b/c) selftest exit 2 is inconclusive",
          selftest_arm(base_selftest, fake(2, b""), "targeted")[0]
          == "inconclusive")
    check("(b/c) failing baseline selftest is inconclusive",
          selftest_arm(fake(1, b""), target_failure,
                       SELFTEST_TARGETS["FC-target"])[0] == "inconclusive")
    targeted_arm = selftest_arm(base_selftest, target_failure,
                                SELFTEST_TARGETS["FC-target"])
    unrelated_arm = selftest_arm(base_selftest, unrelated_failure, "targeted")
    own_fault_arm = main_arm(good, view(2))
    passing_arm = selftest_arm(base_selftest, base_selftest, "targeted")
    check("(b) targeted selftest kill survives an other-arm exit 2",
          targeted_arm[0] == "killed" and own_fault_arm[0] == "inconclusive"
          and combine_arms([targeted_arm, own_fault_arm]) == "killed")
    check("(b) no targeted selftest kill plus main exit 2 stays inconclusive",
          unrelated_arm[0] == "inconclusive" and own_fault_arm[0] == "inconclusive"
          and combine_arms([unrelated_arm, own_fault_arm]) == "inconclusive")
    check("(b) passing selftest plus main exit 2 remains inconclusive",
          passing_arm[0] == "survived" and own_fault_arm[0] == "inconclusive"
          and combine_arms([passing_arm, own_fault_arm]) == "inconclusive")
    check("(b) both surviving arms survive",
          combine_arms([("survived", ""), ("survived", "")]) == "survived")
    doc = {"positive_control": {"detected": True}, "detected": 8, "accepted": 0,
           "faults": [{"id": "F1", "detected": True}]}
    check("fault-controls decision extracted",
          fc_decision(0, doc) == {"exit": 0, "f0_detected": True,
                                  "detected": 8, "accepted": 0,
                                  "faults": {"F1": True}})

    def crash(code, stdout, stderr=b"", post=None):
        return {"record": {"id": "t", "exit": code, "timed_out": False,
                           "spawn_error": None, "seconds": 0},
                "stdout": stdout, "stderr": stderr, "post": post}
    per_row = json.dumps({"records": [{"name": CRASH_ROW, "passed": False,
                                       "error": "malformed"}]}).encode()
    escaped = {"escaped_pids": [4242], "killed_after_scan": [4242]}
    for name, args, want in (
            ("(e) per-row failure is handled", (crash(1, per_row), True),
             "handled"),
            ("(e) traceback with empty stdout is accepted",
             (crash(1, b"", TRACEBACK + b"\nRecursionError"), True),
             "accepted"),
            ("(e) exit 0 is accepted", (crash(0, per_row), True), "accepted"),
            ("(e) an escaped child is accepted",
             (crash(1, per_row, post=escaped), True), "accepted"),
            ("(e) a probe that never started is not_exercised",
             (crash(1, per_row), False), "not_exercised")):
        got = classify_crash(args[0], CRASH_ROW, args[1])
        check(name, got[0] == want, got[:2])
    check("hostile stdout never raises",
          parse_json_bytes(b"[" * 200_000)[0] is None
          and parse_json_bytes(b"9" * 5_000)[0] is None
          and parse_json_bytes(b"\xff\xfe")[0] is None)
    try:
        parse_families("a,z")
        rejected = False
    except argparse.ArgumentTypeError:
        rejected = True
    check("--family rejects unknown names and keeps a..e order",
          rejected and parse_families("e,a") == ["a", "e"])
    with tempfile.TemporaryDirectory(prefix="kama-c2-survivors-st-") as tmp:
        target = Path(tmp) / "out.json"
        write_exclusive(target, b"{}\n")
        try:
            write_exclusive(target, b"[]\n")
            refused = False
        except FileExistsError:
            refused = True
        check("--out is created exclusively, never clobbered",
              refused and target.read_bytes() == b"{}\n")


def selftest_machinery(ctx, check):
    """Guard, escape scan and frozen-tool known answers, through real runs."""
    namespace = {}
    exec(compile(guard_source({4321}, install=False), "guard", "exec"),
         namespace)
    decide = namespace["decide"]
    check("guard policy: loopback port 0 remapped, non-loopback and "
          "protected refused, AF_UNIX untouched",
          decide(socket.AF_INET, ("127.0.0.1", 0))[0] == "pick"
          and decide(socket.AF_INET6, ("::1", 0, 0, 0))[0] == "pick"
          and decide(socket.AF_INET, ("0.0.0.0", 0))[0] == "refuse"
          and decide(socket.AF_INET6, ("::", 0, 0, 0))[0] == "refuse"
          and decide(socket.AF_INET, ("127.0.0.1", 4321))[0] == "refuse"
          and decide(socket.AF_UNIX, "/tmp/x")[0] == "pass")
    check("guard protects 8080 and 34113", {8080, 34113} <= set(ctx.protected),
          ctx.protected)
    probe = ctx.stage_file("st/guard-probe.py", GUARD_PROBE.encode())
    run = ctx.runner.submit("st guard probe", [sys.executable, probe],
                            probe.parent, 60).result()
    words = tail(run["stdout"]).split()
    port = int(words[1]) if len(words) == 2 and words[1].isdigit() else None
    check("guard is installed in children and maps port 0 into its range",
          words[:1] == ["True"] and port is not None
          and GUARD_LOW <= port < GUARD_HIGH and port not in ctx.protected,
          tail(run["stdout"]) + tail(run["stderr"]))

    sleep_fault = CRASH_FAULTS[-1]
    for label, source, want in (("leaky", LEAKY_CHECKER, True),
                                ("group", GROUP_CHECKER, False)):
        where = f"st/{label}"
        started = ctx.root / where / "sleep.started"
        nonce = f"{ctx.sleep_marker}-st-{label}"
        script = crash_probe(ctx, where, sleep_fault, started, nonce)
        checker = ctx.stage_file(f"{where}/checker.py", source.encode())
        run = ctx.runner.submit(f"st {label} checker",
                                [sys.executable, checker, script],
                                checker.parent, 60,
                                post=escape_post(nonce)).result()
        check(f"escape scan: a {label} checker -> escaped={want}, and "
              "nothing carrying the nonce is left",
              started.exists() and bool(run["post"]["escaped_pids"]) == want
              and not marked_pids(nonce), run["post"])

    # Known answers: round-17 observations on the frozen tools.
    sums = read_sums()
    frozen_as_current = dict(FROZEN_TOOLS)
    results = {family: FAMILY_FUNCS[family](ctx, frozen_as_current, sums)()
               for family in ("c", "d")}
    check("(c) frozen append-only selftest passes unmutated; M3a and M4b "
          "survive it",
          all(results["c"]["baselines"][side]["exit"] == 0 for side in SIDES)
          and all(item[side]["outcome"] == "survived"
                  for item in results["c"]["items"] for side in SIDES),
          [(item["id"], item["before"]) for item in results["c"]["items"]])
    item = results["d"]["items"][0]
    check("(d) frozen provenance records refused 0 for the 82-refusal call",
          item["frozen"].get("refused") == 0
          and item["frozen"]["outcome"] == "miscount"
          and item["corroboration"]["attempts_json_refused"] == 82
          and item["corroboration"]["refusal_messages_in_result"] == 82,
          item["frozen"])

    _, fc = ctx.tool("fault-controls", "frozen", frozen_as_current, sums)
    check_path, check_bytes = ctx.tool("check", "frozen", frozen_as_current,
                                       sums)
    _, probe_bytes = ctx.snapshot("probe", PROBE)
    exits = {}
    for mutant in (None,) + MUTANTS["b"]:
        label = "st-frozen" if mutant is None else f"st-frozen+{mutant['id']}"
        data = fc if mutant is None else apply_edit(
            fc.decode("utf-8"), mutant["old"], mutant["new"],
            label)[0].encode("utf-8")
        mirror = ctx.fc_mirror(label, data, check_bytes, probe_bytes)
        exits[label] = fc_selftest(ctx, label, mirror).result()["record"]["exit"]
        if mutant is None:
            tool, tpv, probe = mirror
            main = ctx.runner.submit(
                "st fault-controls[frozen] --only-fault F1",
                [sys.executable, tool, "--check", check_path, "--probe", probe,
                 "--matrix-dir", tpv, "--only-fault", "F1", "--json"],
                tool.parents[2], CAP["fc-main"]).result()
            decision = fc_view(main)["decision"]
            check("(a/b) a frozen fault-controls main run parses from a "
                  "mirror: F0 healthy, F1 detected, accepted 0",
                  decision == {"exit": 0, "f0_detected": True, "detected": 1,
                               "accepted": 0, "faults": {"F1": True}},
                  decision or tail(main["stderr"]))
    check("(b) frozen fault-controls selftest passes unmutated and misses all "
          "three self-mutants", set(exits.values()) == {0}, exits)

    check_copy = stage_check(ctx, "st/e", check_bytes)
    for fault in CRASH_FAULTS:
        started, future = submit_crash(ctx, "st-frozen", check_copy, "st/e",
                                       fault)
        outcome, why, _ = classify_crash(future.result(), CRASH_ROW,
                                         started.exists())
        check(f"(e) frozen check.py does not handle {fault['id']}",
              outcome == "accepted", why)


def selftest(as_json):
    checks = []

    def check(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

    selftest_pure(check)
    ctx = Context(1)
    try:
        selftest_machinery(ctx, check)
    except OwnFault as exc:
        check("known answers ran", False, exc)
    finally:
        summary = ctx.bind_summary()
        teardown = ctx.close()
    check("no protected port bound; nothing this run bound still listens",
          summary.get("protected_hits") == []
          and (summary.get("listening_after") or {}).get("owned") == [],
          summary)
    check("teardown removed scratch and left no marked process",
          teardown["scratch_removed"]
          and not marked_pids(ctx.sleep_marker, prefix=True), teardown)
    failed = [c for c in checks if not c["ok"]]
    if as_json:
        print(json.dumps({"selftest": f"{SCHEMA}/selftest", "checks": checks,
                          "passed": not failed}, indent=2))
    else:
        for c in checks:
            print(("ok   " if c["ok"] else "FAIL ") + c["name"]
                  + ("" if c["ok"] else f" — {c['detail']}"))
        print(f"selftest: {len(checks) - len(failed)}/{len(checks)} "
              "checks passed")
    return 0 if not failed else 1


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest(args.json)
    return run_count(args)


if __name__ == "__main__":
    sys.exit(main())
