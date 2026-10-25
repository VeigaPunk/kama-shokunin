#!/usr/bin/env python3
"""kama-fault-controls — fault-injection controls for the probe verdict harness.

Lane: local model serving & endpoint health (kama-shokunin); round 17 claim C1,
hardened in round 18 (claim C2, calibration).

check.py is documented as grading verdict, reason, exit and drift — and, after the
round-17 repair, two probe-contract invariants (served_model; every stub-mode row
must record GET /v1/models) plus a malformed-output path that never tracebacks.
This tool proves the gate can actually fail: for each fault below it builds a
scratch copy of the harness (a --check PATH plus byte copies of the nine sibling
matrix *.json files, so the frozen round-16 check.py runs verbatim), injects a
wrapper probe that corrupts exactly ONE output field or behaviour, and requires
check.py to fail every faulted row.

Detection rule (per fault):
    DETECTED  <=>  every run exits 1 AND prints parseable JSON in which every
                   faulted row has "passed": false AND lists the fault's target
                   conjunct among the row's failures (F17 also: the probe's
                   child process is gone once check.py has exited)
    ACCEPTED  <=>  anything else: exit 0, exit 2, a traceback/non-JSON stdout,
                   a missing row, a faulted row still passed, a failure on some
                   other conjunct only, or a probe child that outlived check.py
    F0 is the positive control (identity wrapper): "detected" means check.py
    passed the honest probe (exit 0, all rows passed). A reject-everything
    check.py scores F0 accepted, so the verdict cannot be laundered: F0 gates
    the suite (exit 2) before any fault counts, every fault row must be an F0
    row, and each cached replay comes from a per-row identity pre-pass that
    must itself pass. A wrapper crash (probe exit 9) is an own fault, never a
    detection.

Exit codes: 0 no accepted faults | 1 at least one accepted | 2 own fault.

Faults:
    F0  positive control: unchanged pass-through; must exit 0, all rows pass
    F1  reason suffix "-forged" appended in the emitted row
    F2  probe exit flipped 0<->2 (1+ passes through)
    F3  drift boolean negated (breaks drift == (verdict != MODEL_OK))
    F4  verdict lower-cased
    F5  served_model forced to "kama-forged-id" — also non-empty on a DEAD row
    F6  route skip: wrapper GETs /health itself, then replays a cached real
        output for that one row without ever touching /v1/models (a per-row
        pre-pass records the cache; each stub row is its own run); stub
        requests then contain /health but no /v1/models
    F7  hang: wrapper sleeps past check.py's probe timeout (~40s wall on one row)
    F8  malformed stdout variants: [], {"rows":[]}, {"rows":[["x"]]},
        non-JSON text — the real probe still runs and its exit code is kept, so
        the emitted document is the single corrupted field; a repaired harness
        records a failure, a weak one tracebacks
  Round 18: one fault per check.py mutant that survived F0-F8
  (.ufo/waves/round-17/falsify/advice/MutC1Preregistered{,2}.md):
    F9  reason case-swapped                        kills H1 (casefold compare)
    F10 verdict padded: leading space, trailing space, trailing newline
                                                   kills H2 (.strip() compare)
    F11 cached replay; the stub sees /v1/models only as POST, HEAD and
        lower-case "get"                           kills H3 (method ignored)
    F12 served_model equal only after normalising: case-swapped, ".gguf"
        suffixed, space-padded, fullwidth (NFKC)   kills H5 (normalised ids)
    F13 cached replay that sends the stub no request at all
                                                   kills H6 (no-request passes)
    F14 two-row output: a reason-forged copy first, the honest row last
                                                   kills H7 (grades rows[-1])
  Round 18 crash debts (MalformedNonUtf8.md, TimeoutPath.md):
    F15 stdout {"rows": + 100000-deep nested array (RecursionError in json)
    F16 stdout {"rows":[<5000-digit integer>]} (int-string limit ValueError)
    F17 hang inside a same-process-group child `sleep`: killing only the
        direct probe process leaves the child running (~30s wall on one row)

--selftest validates the table and the detector itself with no real probe and
no port: classifier verdicts on synthetic check.py documents (off-target
failures, tracebacks, missing rows ... never read as detected), single-row
replay caches, the F0 gate against stub reject-/accept-everything check.py
scripts, every wrapper corruption against a canned probe document, and F17's
escaped-child detector both ways.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import hashlib
import json
import os
import secrets
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import unicodedata
from pathlib import Path

SELF = Path(__file__).resolve()
MATRIX_DIR = SELF.parent
LANE = MATRIX_DIR.parents[1]
DEFAULT_CHECK = MATRIX_DIR / "check.py"
DEFAULT_PROBE = LANE / "tools" / "kama-probe.sh"

SCHEMA = "kama-fault-controls/v1"
HANG_SECONDS = 40            # check.py PROBE_TIMEOUT is 30; clear margin
WRAPPER_EXIT = 9             # wrapper's own-fault exit; a probe never exits 9
CHECK_RUN_TIMEOUT = 150      # whole check.py run cap; hangs count as accepted
ESCAPE_SECONDS = CHECK_RUN_TIMEOUT + 90   # F17 child outlives any check run
ESCAPE_GRACE = 2.0           # seconds a killed F17 child gets to disappear
NESTED_DEPTH = 100_000       # F15: far beyond json's C recursion guard
HUGE_DIGITS = 5_000          # F16: past sys.int_info.default_max_str_digits

# Pinned round-16 facts (.ufo/waves/round-16/measure.py:281-290): the staged
# matrix set must reproduce this name+content digest and breadth before the
# controls mean anything.
EXPECTED_MATRIX_SHA256 = ("bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21ed"
                          "b2b8256e22771f32")
EXPECTED_MATRIX_TESTS = 72

# Round-17 check.py mutants that survived F0-F8; each must be named by the
# "kills" of at least one fault (--selftest enforces it).
SURVIVING_MUTANTS = ("H1", "H2", "H3", "H5", "H6", "H7")


# ---------------------------------------------------------------- fault table
# Row names are literal: each fault's set spans MODEL_OK, MODEL_MISMATCH,
# MODEL_LOADING and FOREIGN_SERVICE stub rows plus (where meaningful) the
# closed-port DEAD row. Rows are named exactly as in the matrix files.
ROWS_OK_MIS_LOAD = [
    "ReadyControls.expect-exact-id",            # MODEL_OK matched exit 0
    "ReadyControls.expect-different-id",        # MODEL_MISMATCH exit 2
    "LoadingEnvelope.canonical-alias",          # MODEL_LOADING exit 2
]
ROWS_FULL = [
    "ReadyControls.expect-exact-id",            # MODEL_OK
    "ReadyControls.expect-different-id",        # MODEL_MISMATCH
    "LoadingEnvelope.canonical-alias",          # MODEL_LOADING
    "ForeignControls.openmetrics-text",         # FOREIGN_SERVICE
    "AuthAndDead.closed-port-connection-refused",  # DEAD (closed port)
]
F6_ROWS = ROWS_FULL[:-1]                        # stub rows only; a closed DEAD
# row has no port to hit /health on, so route-skip is meaningless there.
# MODEL_OK / MODEL_MISMATCH are the only verdicts whose served_model is a real
# id (every other verdict emits '-'), so only they can carry a normalised id.
ROWS_SERVED = ROWS_FULL[:2]
# Verdicts whose padding breaks nothing but the verdict conjunct itself: a
# padded MODEL_OK also flips drift, and check.py keys the served_model
# expectation on the observed verdict, so a padded MODEL_MISMATCH would also
# fail served_model (round-17 advice MutC1Preregistered.md, H2).
ROWS_PAD = ROWS_FULL[2:]

REPLAY_MODES = ("f6", "replay")     # cached per-row honest output, replayed
SLOW_MODES = ("hang", "escape")     # each costs a full probe timeout


def _per_row(mode, touch, rows):
    """One run per row: a shared cache cannot tell rows apart when several
    --only entries replay it, so each row gets its own check invocation."""
    return [{"mode": mode, "touch": touch, "rows": [r]} for r in rows]


def _b64(data):
    return base64.b64encode(data).decode()


# F0 is run first and gates the whole suite: if a check.py cannot PASS the
# honest probe, the suite is invalid (exit 2), whatever the faults say.
POSITIVE_CONTROL = {
    "id": "F0",
    "title": "positive control (identity pass-through)",
    "positive": True,
    "target": None,
    "runs": [{"mode": "pass", "touch": None, "rows": ROWS_FULL}],
}

# "target" names the single conjunct each fault corrupts; a row's failure only
# counts as detection when its failed conjuncts include the target — a wrapper
# crash that merely produces an "error" row can never read as DETECTED.
FAULTS = [
    {
        "id": "F1",
        "title": "reason forged",
        "target": "reason",
        "runs": [{"mode": "reason", "touch": None, "rows": ROWS_OK_MIS_LOAD}],
    },
    {
        "id": "F2",
        "title": "exit flipped",
        "target": "exit",
        "runs": [{"mode": "exit", "touch": None, "rows": ROWS_OK_MIS_LOAD}],
    },
    {
        "id": "F3",
        "title": "drift negated",
        "target": "drift",
        "runs": [{"mode": "drift", "touch": None, "rows": ROWS_OK_MIS_LOAD}],
    },
    {
        "id": "F4",
        "title": "verdict lower-cased",
        "target": "verdict",
        "runs": [{"mode": "verdict", "touch": None, "rows": ROWS_OK_MIS_LOAD}],
    },
    {
        "id": "F5",
        "title": "served_model forged (incl. non-empty on DEAD)",
        "target": "served_model",
        "runs": [{"mode": "served", "touch": None,
                  "rows": ["ReadyControls.expect-exact-id",
                           "ReadyControls.expect-different-id",
                           "AuthAndDead.closed-port-connection-refused"]}],
    },
    {
        "id": "F6",
        "title": "route skip (no GET /v1/models; cached replay)",
        "target": "route",
        "runs": _per_row("f6", "/health", F6_ROWS),
    },
    {
        "id": "F7",
        "title": "hang past probe timeout",
        "target": "error",
        "slow": True,
        "runs": [{"mode": "hang", "touch": None,
                  "sleep": HANG_SECONDS,
                  "rows": ["ReadyControls.expect-exact-id"]}],
    },
    {
        "id": "F8",
        "title": "malformed stdout",
        "target": "error",
        "runs": [
            {"mode": "malformed", "variant": "empty-array",
             "body_b64": base64.b64encode(b"[]").decode(), "rows": ROWS_FULL},
            {"mode": "malformed", "variant": "rows-empty",
             "body_b64": base64.b64encode(b'{"rows":[]}').decode(),
             "rows": ROWS_FULL},
            {"mode": "malformed", "variant": "row-not-object",
             "body_b64": base64.b64encode(b'{"rows":[["x"]]}').decode(),
             "rows": ROWS_FULL},
            {"mode": "malformed", "variant": "row-null",
             "body_b64": base64.b64encode(b'{"rows":[null]}').decode(),
             "rows": ROWS_FULL},
            {"mode": "malformed", "variant": "non-json",
             "body_b64": base64.b64encode(b"this is not JSON at all\n").decode(),
             "rows": ROWS_FULL},
            {"mode": "malformed", "variant": "non-utf8",
             "body_b64": base64.b64encode(b"\xff\xfe{bad").decode(),
             "rows": ROWS_FULL},
        ],
    },
    {
        "id": "F9",
        "title": "reason case-swapped",
        "target": "reason",
        "kills": ["H1"],
        "runs": [{"mode": "reason-case", "touch": None, "rows": ROWS_FULL}],
    },
    {
        "id": "F10",
        "title": "verdict whitespace-padded",
        "target": "verdict",
        "kills": ["H2"],
        "runs": [
            {"mode": "verdict-pad", "variant": "leading-space",
             "pad": [" ", ""], "rows": ROWS_PAD},
            {"mode": "verdict-pad", "variant": "trailing-space",
             "pad": ["", " "], "rows": ROWS_PAD},
            {"mode": "verdict-pad", "variant": "trailing-newline",
             "pad": ["", "\n"], "rows": ROWS_PAD},
        ],
    },
    {
        "id": "F11",
        "title": "/v1/models reached by non-GET methods only (cached replay)",
        "target": "route",
        "kills": ["H3"],
        "runs": _per_row("replay",
                         "POST /v1/models,HEAD /v1/models,get /v1/models",
                         F6_ROWS),
    },
    {
        "id": "F12",
        "title": "served_model equal only after normalisation",
        "target": "served_model",
        "kills": ["H5"],
        "runs": [{"mode": "served-norm", "variant": variant, "touch": None,
                  "rows": ROWS_SERVED}
                 for variant in ("case", "gguf-suffix", "whitespace",
                                 "fullwidth")],
    },
    {
        "id": "F13",
        "title": "no stub request at all (cached replay)",
        "target": "route",
        "kills": ["H6"],
        "runs": _per_row("replay", None, F6_ROWS),
    },
    {
        "id": "F14",
        "title": "corruption confined to rows[0] of a two-row output",
        "target": "reason",
        "kills": ["H7"],
        "runs": [{"mode": "first-row", "touch": None, "rows": ROWS_FULL}],
    },
    {
        "id": "F15",
        "title": "nested-JSON depth bomb in stdout",
        "target": "error",
        "debt": "MalformedNonUtf8.md: deep nesting raised RecursionError "
                "out of check.py",
        "runs": [{"mode": "malformed", "variant": f"nested-{NESTED_DEPTH}",
                  "body_b64": _b64(b'{"rows":' + b"[" * NESTED_DEPTH
                                   + b"]" * NESTED_DEPTH + b"}"),
                  "rows": ROWS_FULL}],
    },
    {
        "id": "F16",
        "title": f"{HUGE_DIGITS}-digit integer in stdout",
        "target": "error",
        "debt": "MalformedNonUtf8.md: int-string limit raised ValueError "
                "out of check.py",
        "runs": [{"mode": "malformed", "variant": f"int-{HUGE_DIGITS}-digits",
                  "body_b64": _b64(b'{"rows":[' + b"9" * HUGE_DIGITS + b"]}"),
                  "rows": ROWS_FULL}],
    },
    {
        "id": "F17",
        "title": "hang in a child that outlives the probe process",
        "target": "error",
        "slow": True,
        "debt": "TimeoutPath.md: the timeout killed the probe, not its child",
        "runs": [{"mode": "escape", "touch": None,
                  "rows": ["ReadyControls.expect-exact-id"]}],
    },
]


# ------------------------------------------------------------- wrapper probe
# bash->python3 trampoline: check.py always invokes the probe as `bash <probe>`,
# so the wrapper is a bash script whose python body arrives on stdin via heredoc;
# "$@" still lands in sys.argv[1:]. The real probe path comes from FAULT_PROBE.
WRAPPER = r'''#!/usr/bin/env bash
exec python3 - "$@" <<'FAULT_WRAPPER_EOF'
"""Fault wrapper probe. argv: <probe args...>; FAULT_PROBE is the real probe.
FAULT_MODE selects the single corruption; FAULT_* env carries the replay
cache, stub touches, body file, padding/variant, sleep and escape pidfile."""
import copy, json, os, subprocess, sys, time, urllib.request


args = sys.argv[1:]
real = os.environ.get("FAULT_PROBE", "")
mode = os.environ.get("FAULT_MODE", "pass")


def die(msg):
    sys.stderr.write("fault-wrapper: %s\n" % msg)
    sys.exit(int(os.environ.get("FAULT_WRAPPER_EXIT", "9")))


if not real:
    die("FAULT_PROBE unset")


def opt(flag, default=""):
    for i, a in enumerate(args):
        if a == flag and i + 1 < len(args):
            return args[i + 1]
        if a.startswith(flag + "="):
            return a.split("=", 1)[1]
    return default


def hit(method, path):
    port = opt("--port")
    if not port or port == "0":
        return
    req = urllib.request.Request("http://127.0.0.1:%s%s" % (port, path),
                                 method=method)
    try:
        urllib.request.urlopen(req, timeout=3).read()
    except Exception:
        pass  # closed port or stub rejection is not the wrapper's business


def touch():
    # FAULT_TOUCH: comma-separated "[METHOD ]PATH" requests; METHOD is sent
    # verbatim (HTTP methods are case-sensitive) and defaults to GET.
    for item in os.environ.get("FAULT_TOUCH", "").split(","):
        method, _, path = item.strip().rpartition(" ")
        if path:
            hit(method or "GET", path)


if mode == "hang":
    time.sleep(float(os.environ.get("FAULT_SLEEP", "40")))

if mode == "escape":
    # The hang lives in a child sharing this process group: a harness that
    # kills only this direct probe process leaves the child running.
    child = subprocess.Popen(["sleep", os.environ.get("FAULT_ESCAPE_ARG", "240")])
    with open(os.environ.get("FAULT_PIDFILE", os.devnull), "w") as fh:
        fh.write("%d\n" % child.pid)
    child.wait()
    die("escape child ended before the probe was stopped")

if mode in ("f6", "replay"):
    touch()                 # F6: GET /health; F11: non-GET only; F13: nothing
    cache = os.environ.get("FAULT_CACHE", "")
    if not cache or not os.path.exists(cache):
        die("missing cache %r" % cache)
    sys.stdout.write(open(cache).read())
    try:
        sys.exit(int(open(cache + ".rc").read().strip()))
    except Exception:
        die("missing cache rc")

if mode == "malformed":
    # The real probe still runs (route evidence stays honest); only the
    # emitted document is corrupt. Keep the probe's exit so the stdout body is
    # the single corrupted field. FAULT_BODY_FILE carries raw bytes, so the
    # non-UTF-8 and the large variants survive (env values are capped).
    p = subprocess.run(["bash", real] + args, capture_output=True, text=True)
    try:
        with open(os.environ.get("FAULT_BODY_FILE", ""), "rb") as fh:
            body = fh.read()
    except OSError as exc:
        die("unreadable FAULT_BODY_FILE (%s)" % exc)
    sys.stdout.buffer.write(body)
    if not body.endswith(b"\n"):
        sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()
    sys.exit(p.returncode)

p = subprocess.run(["bash", real] + args, capture_output=True, text=True)
if mode == "pass":
    cache = os.environ.get("FAULT_CACHE", "")
    if cache:
        with open(cache, "w") as f:
            f.write(p.stdout)
        with open(cache + ".rc", "w") as f:
            f.write(str(p.returncode))
    sys.stdout.write(p.stdout)
    sys.exit(p.returncode)

try:
    doc = json.loads(p.stdout)
    row = doc["rows"][0]
    new = copy.deepcopy(row)    # forged copy shares nothing with the honest row
except Exception as exc:
    die("real probe output not mutable (%r); cannot inject a clean fault" % exc)


def served_variant(served, how):
    if not isinstance(served, str) or served in ("", "-"):
        die("served_model %r carries no id to normalise" % (served,))
    if how == "case":
        return served.swapcase()
    if how == "gguf-suffix":
        return ",".join(i + ".gguf" for i in served.split(","))
    if how == "whitespace":
        return " " + served + " "
    if how == "fullwidth":      # NFKC folds U+FF01..U+FF5E back to ASCII
        return "".join(chr(ord(c) + 0xFEE0) if "!" <= c <= "~" else c
                       for c in served)
    die("unknown served variant %r" % how)


if mode == "reason":
    new["reason"] = str(row.get("reason")) + "-forged"
elif mode == "reason-case":
    new["reason"] = str(row.get("reason")).swapcase()
elif mode == "verdict":
    v = row.get("verdict")
    if not isinstance(v, str):
        die("verdict not a string")
    new["verdict"] = v.lower()
elif mode == "verdict-pad":
    v = row.get("verdict")
    if not isinstance(v, str):
        die("verdict not a string")
    new["verdict"] = (os.environ.get("FAULT_PAD_LEAD", "") + v
                      + os.environ.get("FAULT_PAD_TRAIL", ""))
elif mode == "drift":
    new["drift"] = not row.get("drift")
elif mode == "served":
    new["served_model"] = "kama-forged-id"
elif mode == "served-norm":
    new["served_model"] = served_variant(row.get("served_model"),
                                         os.environ.get("FAULT_VARIANT", ""))
elif mode == "first-row":
    new["reason"] = str(row.get("reason")) + "-forged-first-row"
elif mode == "exit":
    pass                                # exit handled after emit
else:
    die("unknown FAULT_MODE %r" % mode)

if mode != "exit" and new == row:
    die("FAULT_MODE %r left the row unchanged; no fault injected" % mode)
if mode == "first-row":
    doc["rows"] = [new, copy.deepcopy(row)]   # forged first; honest deep copy last
else:
    doc["rows"][0] = new
sys.stdout.write(json.dumps(doc) + "\n")
if mode == "exit":
    sys.exit(2 if p.returncode == 0 else (0 if p.returncode == 2 else p.returncode))
sys.exit(p.returncode)
FAULT_WRAPPER_EOF
'''


# ---------------------------------------------------------------- helpers
class OwnFault(Exception):
    """fault-controls' own harness fault -> exit 2."""


def sha256_file(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def load_matrix_tests(matrix_dir):
    """Return {test_name: test_dict} across every sibling *.json, or own-fault."""
    tests = {}
    sources = sorted(Path(matrix_dir).glob("*.json"))
    for source in sources:
        try:
            doc = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise OwnFault(f"unreadable matrix {source.name}: {exc}")
        if not isinstance(doc, list):
            raise OwnFault(f"matrix {source.name}: not a JSON array")
        for test in doc:
            if isinstance(test, dict) and "name" in test:
                tests[test["name"]] = test
    return tests


def matrix_set_digest(matrix_dir):
    """Round-16 measure.py:286-290 formula: sorted "name sha256" lines."""
    files = sorted(Path(matrix_dir).glob("*.json"))
    lines = "".join(
        f"{f.name} {hashlib.sha256(f.read_bytes()).hexdigest()}\n"
        for f in files)
    return len(files), hashlib.sha256(lines.encode()).hexdigest()


def run_check(scratch, only_rows, env_extra):
    """Invoke the scratch check.py once in its own process group; returns
    (exit, stdout, stderr). A wedged check.py (or a mutant that dropped the
    probe timeout) is killed wholesale after CHECK_RUN_TIMEOUT and reported
    with rc=124 so it classifies as accepted, never an own fault."""
    argv = [sys.executable, "check.py", "--probe", "wrap.py", "--json"]
    for name in only_rows:
        argv += ["--only", name]
    env = dict(os.environ)
    env.update(env_extra)
    proc = subprocess.Popen(argv, cwd=scratch, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    try:
        stdout, stderr = proc.communicate(timeout=CHECK_RUN_TIMEOUT)
        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        stdout, stderr = proc.communicate()
        return 124, stdout, stderr


def served_ids_of(body):
    """Extract served ids from a /v1/models body exactly as the probe does
    (tools/kama-probe.sh:335-368): JSON object; first non-empty group wins —
    data[].id -> models[].id -> models[].name -> models[].model -> top-level
    id — deduplicated preserving order."""
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


def contract_served_model(test):
    """The served_model the probe contract REQUIRES for this matrix row,
    derived from the row's own literal routes — never from check.py internals.

    classify() (kama-probe.sh:455-548) only writes a served id in the
    `2xx && model-array` arm (MODEL_OK / MODEL_MISMATCH); every other verdict
    emits '-'. In that arm C_SERVED is the comma-joined served_ids() of the
    /v1/models body, '-' when empty."""
    if test.get("port_mode") != "stub":
        return "-"
    route = (test.get("routes") or {}).get("/v1/models")
    if route is None:
        route = test.get("default_route")
    if route is None or route.get("raw") == "close":
        return "-"
    try:
        status = int(route["status"])
    except (KeyError, TypeError, ValueError):
        return "-"
    if not (200 <= status < 300):
        return "-"
    if "body_json" in route:
        body = route["body_json"]
    elif "body_text" in route:
        body = route["body_text"]
    else:
        return "-"
    # model-array presence first (kama-probe.sh:401-419): no data[]/models[]
    # means no MODEL_OK arm at all.
    if isinstance(body, dict):
        has_array = isinstance(body.get("data"), list) or \
            isinstance(body.get("models"), list)
    else:
        try:
            parsed = json.loads(body) if isinstance(body, str) else None
        except json.JSONDecodeError:
            parsed = None
        has_array = isinstance(parsed, dict) and (
            isinstance(parsed.get("data"), list)
            or isinstance(parsed.get("models"), list))
    if not has_array:
        return "-"
    ids = served_ids_of(body)
    return ",".join(ids) if ids else "-"


def failed_conjuncts(record, test):
    """Which documented conjuncts this record failed, re-derived locally.

    Mirrors the check.py grade() contract from the record's own fields:
    verdict/reason/exit equalities, the drift==verdict!=MODEL_OK invariant,
    the probe-contract served_model for this row, and the stub route
    requirement (GET /v1/models among recorded requests). The "error" conjunct
    fires when the harness recorded one (timeout/unparseable/no-requests)."""
    failed = set()
    if record.get("error"):
        failed.add("error")
    expected = test["expected"]
    if record.get("verdict") != expected["verdict"]:
        failed.add("verdict")
    if record.get("reason") != expected["reason"]:
        failed.add("reason")
    if record.get("probe_exit") != expected["exit"]:
        failed.add("exit")
    if record.get("drift") != (record.get("verdict") != "MODEL_OK"):
        failed.add("drift")
    if record.get("served_model") != contract_served_model(test):
        failed.add("served_model")
    if test.get("port_mode") == "stub":
        requests = record.get("requests") or []
        if not any(isinstance(r, dict)
                   and r.get("method") == "GET"
                   and r.get("path", "").split("?", 1)[0] == "/v1/models"
                   for r in requests):
            failed.add("route")
    return failed


def classify_run(exit_code, stdout, run_rows, matrix_tests, fault):
    """Map one check.py run to (ok_bool, why).

    Fault runs need exit 1 + parseable JSON + every faulted row passed=false
    AND the fault's target conjunct among that row's failures — a row that
    merely carries an "error" (e.g. the wrapper itself crashed) can never read
    as a clean detection of a field fault, and a fault without a target can
    never be detected at all. Positive-control runs need exit 0 + parseable
    JSON + every row passed=true. A record whose probe exited WRAPPER_EXIT is
    the wrapper's own fault (exit 2), never a verdict."""
    positive = bool(fault.get("positive"))
    target = fault.get("target")
    if exit_code == WRAPPER_EXIT:
        raise OwnFault(f"wrapper fault: check exited {WRAPPER_EXIT} "
                       "(stderr: fault-wrapper error)")
    want_exit = 0 if positive else 1
    if exit_code != want_exit:
        return False, (f"check exited {exit_code} (wanted {want_exit}); "
                       f"stdout[:120]={stdout[:120]!r}")
    try:
        doc = json.loads(stdout)
    except (ValueError, RecursionError):
        return False, (f"check exited {exit_code} but stdout is not parseable "
                       f"JSON (traceback or human text); "
                       f"stdout[:120]={stdout[:120]!r}")
    if not isinstance(doc, dict):
        return False, "check JSON is not an object"
    records = doc.get("records")
    if not isinstance(records, list):
        return False, "check JSON lacks a records list"
    seen = {r.get("name"): r for r in records if isinstance(r, dict)}
    wrapper_dead = [n for n in run_rows
                    if n in seen and seen[n].get("probe_exit") == WRAPPER_EXIT]
    if wrapper_dead:
        raise OwnFault(f"wrapper fault: probe exited {WRAPPER_EXIT} on "
                       f"{wrapper_dead}; no fault was injected there")
    missing = [n for n in run_rows if n not in seen]
    if missing:
        return False, f"check JSON is missing rows {missing}"
    if positive:
        failing = [n for n in run_rows if seen[n].get("passed") is not True]
        if failing:
            return False, (f"positive control: rows did not pass a clean "
                           f"identity probe: {failing}")
        return True, (f"check exited 0 with JSON; all {len(run_rows)} "
                      "rows passed (positive control healthy)")
    still_passing = [n for n in run_rows
                     if seen[n].get("passed") is not False]
    if still_passing:
        return False, f"faulted rows still passed: {still_passing}"
    if target:
        off_target = []
        conjunct_notes = []
        for name in run_rows:
            fails = failed_conjuncts(seen[name], matrix_tests[name])
            conjunct_notes.append(
                f"{name.split('.')[-1]}:{','.join(sorted(fails)) or 'none'}")
            if target not in fails:
                off_target.append(name)
        if off_target:
            return False, (f"rows failed but NOT on the targeted '{target}' "
                           f"conjunct: {off_target} "
                           f"({' '.join(conjunct_notes)})")
        return True, (f"check exited 1 with JSON; all {len(run_rows)} faulted "
                      f"rows failed the '{target}' conjunct "
                      f"({' '.join(conjunct_notes)})")
    raise OwnFault(f"{fault.get('id')}: fault declares no target conjunct; "
                   "a row failure cannot be attributed to it")


def stage_scratch(tmpdir, check_path, matrix_dir):
    """Byte-copy check.py -> check.py and every matrix *.json into tmpdir."""
    scratch = Path(tmpdir)
    shutil.copyfile(check_path, scratch / "check.py")
    n = 0
    for source in sorted(Path(matrix_dir).glob("*.json")):
        shutil.copyfile(source, scratch / source.name)
        n += 1
    wrapper = scratch / "wrap.py"
    wrapper.write_text(WRAPPER, encoding="utf-8")
    wrapper.chmod(0o755)
    cache_dir = scratch / "cache"
    cache_dir.mkdir()
    return n, cache_dir


def run_env(fault, run, index, probe_path, work_dir):
    """Wrapper environment for one run (replay caches are added by the
    caller). Malformed bodies travel as files: the 200 KB F15 body is far
    past the kernel's 128 KiB cap on one environment string."""
    env = {
        "FAULT_MODE": run["mode"],
        "FAULT_PROBE": str(probe_path),
        "FAULT_WRAPPER_EXIT": str(WRAPPER_EXIT),
    }
    if run.get("touch"):
        env["FAULT_TOUCH"] = run["touch"]
    if run["mode"] == "hang":
        env["FAULT_SLEEP"] = str(run.get("sleep", HANG_SECONDS))
    if run["mode"] == "malformed":
        body_file = Path(work_dir) / f"body-{fault['id']}-{index}.bin"
        body_file.write_bytes(base64.b64decode(run["body_b64"]))
        env["FAULT_BODY_FILE"] = str(body_file)
    if run["mode"] == "verdict-pad":
        env["FAULT_PAD_LEAD"], env["FAULT_PAD_TRAIL"] = run["pad"]
    if run["mode"] == "served-norm":
        env["FAULT_VARIANT"] = run["variant"]
    return env


def prepass_for(scratch, cache_dir, row, probe_path, matrix_tests, prepass):
    """Honest output of exactly one row, recorded by an identity pre-pass and
    cached under that row's name for this suite run. The pre-pass must itself
    be an accepted identity run, or its replay would not be honest."""
    if row in prepass:
        return prepass[row]
    key = hashlib.sha256(row.encode()).hexdigest()[:16]
    cache = Path(cache_dir) / f"prepass-{key}"
    env = {
        "FAULT_MODE": "pass",
        "FAULT_PROBE": str(probe_path),
        "FAULT_WRAPPER_EXIT": str(WRAPPER_EXIT),
        "FAULT_CACHE": str(cache),
    }
    p_exit, p_out, p_err = run_check(scratch, [row], env)
    if (p_exit == WRAPPER_EXIT or not cache.exists()
            or not Path(str(cache) + ".rc").exists()):
        raise OwnFault(f"pre-pass for {row} failed (exit {p_exit}): "
                       f"{p_err[-200:]}")
    ok, why = classify_run(p_exit, p_out, [row], matrix_tests,
                           POSITIVE_CONTROL)
    if not ok:
        raise OwnFault(f"pre-pass for {row} is not an accepted identity run, "
                       f"so its replay would not be honest: {why}")
    prepass[row] = cache
    return cache


def new_escape(work_dir, tag):
    """Identity of one F17 child: a unique sleep argument plus an
    environment token, so only that process is ever judged or killed."""
    return {"pidfile": Path(work_dir) / f"escape-{tag}.pid",
            "arg": f"{ESCAPE_SECONDS}.{secrets.randbelow(10**6):06d}",
            "token": secrets.token_hex(8)}


def escape_env(escape):
    return {"FAULT_PIDFILE": str(escape["pidfile"]),
            "FAULT_ESCAPE_ARG": escape["arg"],
            "FAULT_ESCAPE_TOKEN": escape["token"]}


def is_escape_child(pid, escape):
    """True iff *pid* is still a live (non-zombie) F17 child of this run."""
    proc = Path("/proc") / str(pid)
    try:
        stat = (proc / "stat").read_bytes()
        cmdline = (proc / "cmdline").read_bytes()
    except OSError:
        return False
    state = stat[stat.rfind(b")") + 2:][:1]
    if state in (b"Z", b"X", b""):
        return False
    if cmdline.split(b"\0")[1:2] != [escape["arg"].encode()]:
        return False
    try:
        environ = (proc / "environ").read_bytes()
    except OSError:
        return True             # unreadable environ: the unique argv decides
    token = f"FAULT_ESCAPE_TOKEN={escape['token']}".encode()
    return token in environ.split(b"\0")


def reap_escape_child(escape, grace=ESCAPE_GRACE):
    """After check.py exits: (pid, survived). A child still alive after
    *grace* seconds escaped the probe teardown; it is killed here, so no
    run of this tool leaves it behind. pid is None when the wrapper never
    recorded one (the probe never reached the hang)."""
    try:
        pid = int(Path(escape["pidfile"]).read_text().strip())
    except (OSError, ValueError):
        return None, False
    deadline = time.monotonic() + grace
    while is_escape_child(pid, escape):
        if time.monotonic() >= deadline:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            gone_by = time.monotonic() + 5
            while is_escape_child(pid, escape) and time.monotonic() < gone_by:
                time.sleep(0.02)
            return pid, True
        time.sleep(0.05)
    return pid, False


def run_fault(scratch, cache_dir, fault, probe_path, matrix_tests, prepass):
    """Execute one fault's runs inside the staged harness; return its entry."""
    runs_detected = []
    run_whys = []
    exits = []
    all_rows = []
    escaped = []
    for index, run in enumerate(fault["runs"]):
        rows = run["rows"]
        all_rows.extend(r for r in rows if r not in all_rows)
        env = run_env(fault, run, index, probe_path, cache_dir)
        if run["mode"] in REPLAY_MODES:
            if len(rows) != 1:
                raise OwnFault(f"{fault['id']}: a cached replay must target "
                               f"exactly one row (per-row cache), got "
                               f"{len(rows)}")
            env["FAULT_CACHE"] = str(prepass_for(
                scratch, cache_dir, rows[0], probe_path, matrix_tests,
                prepass))
        escape = None
        if run["mode"] == "escape":
            if not Path("/proc/self/cmdline").exists():
                raise OwnFault("F17 needs Linux /proc to observe the probe's "
                               "child")
            escape = new_escape(cache_dir, f"{fault['id']}-{index}")
            env.update(escape_env(escape))
        try:
            exit_code, stdout, _stderr = run_check(scratch, rows, env)
        finally:
            if escape is not None:
                escape_pid, survived = reap_escape_child(escape)
        exits.append(exit_code)
        detected, why = classify_run(exit_code, stdout, rows, matrix_tests,
                                     fault)
        if escape is not None:
            if escape_pid is None:
                detected, why = False, ("wrapper recorded no child pid; the "
                                        f"probe never reached the hang ({why})")
            elif survived:
                escaped.append(escape_pid)
                detected, why = False, (
                    f"probe child pid {escape_pid} (sleep {escape['arg']}) "
                    f"outlived check.py's exit; killed by fault-controls "
                    f"({why})")
        if run.get("variant"):
            why = f"[{run['variant']}] {why}"
        run_whys.append(why)
        runs_detected.append(detected)
    return {
        "id": fault["id"],
        "title": fault["title"],
        "target": fault.get("target"),
        "rows": all_rows,
        "runs": len(fault["runs"]),
        "check_exit": exits[0] if len(exits) == 1 else exits,
        "detected": all(runs_detected),
        "why": " | ".join(run_whys),
        "kills": list(fault.get("kills", [])),
        "debt": fault.get("debt"),
        "slow": bool(fault.get("slow")),
        "escaped_pids": escaped,
    }


def run_suite(check_path, probe_path, matrix_dir, faults):
    """Stage the scratch harness, gate on F0, then run *faults*.

    Returns {"code", "doc", "error"}. No fault counts unless F0 ran first and
    check.py passed it: otherwise code 2 with doc None, as for an own fault."""
    started = time.time()
    try:
        with tempfile.TemporaryDirectory(prefix="kama-fault-controls-") as tmp:
            staged_files, staged_digest = matrix_set_digest(matrix_dir)
            staged_tests = load_matrix_tests(matrix_dir)
            if staged_tests and len(staged_tests) != EXPECTED_MATRIX_TESTS:
                raise OwnFault(f"matrix breadth {len(staged_tests)} != pinned "
                               f"{EXPECTED_MATRIX_TESTS}; refusing to grade")
            if staged_digest != EXPECTED_MATRIX_SHA256:
                raise OwnFault(f"matrix set digest {staged_digest} != pinned "
                               f"{EXPECTED_MATRIX_SHA256}; refusing to grade")
            outside = sorted(fault_rows(faults) - fault_rows([POSITIVE_CONTROL]))
            if outside:
                raise OwnFault(f"fault rows outside the F0 identity run "
                               f"{outside}: no positive control vouches for them")
            n_matrix, cache_dir = stage_scratch(tmp, check_path, matrix_dir)
            if n_matrix == 0:
                raise OwnFault(f"no *.json matrix files in {matrix_dir}")
            _, scratch_digest = matrix_set_digest(tmp)
            if scratch_digest != EXPECTED_MATRIX_SHA256:
                raise OwnFault(f"scratch matrix digest {scratch_digest} != "
                               f"pinned {EXPECTED_MATRIX_SHA256} (copy fault)")

            prepass = {}
            positive = run_fault(tmp, cache_dir, POSITIVE_CONTROL,
                                 probe_path, staged_tests, prepass)
            if not positive["detected"]:
                return {"code": 2, "doc": None,
                        "error": ("suite INVALID — positive control F0 "
                                  f"failed: {positive['why']}")}

            out_faults = [run_fault(tmp, cache_dir, fault, probe_path,
                                    staged_tests, prepass)
                          for fault in faults]
    except OwnFault as exc:
        return {"code": 2, "doc": None, "error": f"own fault: {exc}"}

    detected_n = sum(1 for f in out_faults if f["detected"])
    accepted_n = len(out_faults) - detected_n
    doc = {
        "schema": SCHEMA,
        "check": str(check_path),
        "check_sha256": sha256_file(check_path),
        "probe_sha256": sha256_file(probe_path),
        "matrix": {
            "files": staged_files,
            "tests": len(staged_tests),
            "sha256": staged_digest,
        },
        "positive_control": positive,
        "seconds": round(time.time() - started, 1),
        "faults": out_faults,
        "detected": detected_n,
        "accepted": accepted_n,
        "fault_controls_sha256": sha256_file(SELF),
        "prepass_rows": sorted(prepass),
    }
    return {"code": 0 if accepted_n == 0 else 1, "doc": doc, "error": None}


def fault_rows(faults):
    return {row for fault in faults for run in fault["runs"]
            for row in run["rows"]}


# ---------------------------------------------------------------- selftest
CONJUNCTS = {"verdict", "reason", "exit", "drift", "served_model", "route",
             "error"}

# Wrapper corruption -> the one row field it may change.
FIELD_OF_MODE = {"reason": "reason", "reason-case": "reason",
                 "verdict": "verdict", "verdict-pad": "verdict",
                 "drift": "drift", "served": "served_model",
                 "served-norm": "served_model", "first-row": "reason"}
# Normalisations these fault variants are intended to distinguish. H5 is the
# exact lower()+removesuffix(".gguf") edit; whitespace / fullwidth variants
# separately cover strip and Unicode NFKC normalisers.
def served_normalised_equal(forged, honest, variant):
    def apply(value):
        ids = value.split(",")
        if variant in ("case", "gguf-suffix"):
            return [sid.lower().removesuffix(".gguf") for sid in ids]
        if variant == "whitespace":
            return [sid.strip().lower() for sid in ids]
        if variant == "fullwidth":
            return [unicodedata.normalize("NFKC", sid).lower() for sid in ids]
        raise OwnFault(f"unknown served-model normalization {variant!r}")

    return apply(forged) == apply(honest)


NORMALISED_EQUAL = {
    "reason-case": lambda forged, honest: forged.casefold() == honest.casefold(),
    "verdict-pad": lambda forged, honest: forged.strip() == honest,
}

CANNED_DOC = {"schema": "kama-probe/v1", "subcommand": "check",
              "rows": [{"id": "cli-override", "verdict": "MODEL_MISMATCH",
                        "reason": "served-id-mismatch",
                        "served_model": "kama-ready", "drift": True,
                        "evidence": "selftest canned row"}]}
CANNED_RC = 2
PROBE_ARGV = ["check", "--port", "0", "--expect", "kama-ready", "--json",
              "--timeout", "2", "--connect-timeout", "1"]

# Stub check.py for the F0-gate selftest: answers every --only row with the
# same verdict and never runs the probe.
FAKE_CHECK = '''import json, sys
names = [sys.argv[i + 1] for i, a in enumerate(sys.argv[:-1]) if a == "--only"]
passed = PASSED
print(json.dumps({"records": [{"name": n, "passed": passed} for n in names]}))
sys.exit(0 if passed else 1)
'''


def _by_id(fault_id):
    return next(f for f in FAULTS if f["id"] == fault_id)


def selftest_table(tests, problems):
    """Static invariants of the fault table (no process is started)."""
    ids = [POSITIVE_CONTROL["id"]] + [f["id"] for f in FAULTS]
    if len(ids) != len(set(ids)):
        problems.append(f"duplicate fault ids in {ids}")
    f0_rows = fault_rows([POSITIVE_CONTROL])
    outside = sorted(fault_rows(FAULTS) - f0_rows)
    if outside:
        problems.append(f"fault rows outside the F0 identity run: {outside}")
    killed = {m for f in FAULTS for m in f.get("kills", [])}
    for mutant in SURVIVING_MUTANTS:
        if mutant not in killed:
            problems.append(f"no fault kills surviving mutant {mutant}")
    for fault in FAULTS:
        fid = fault["id"]
        if fault.get("target") not in CONJUNCTS:
            problems.append(f"{fid}: target {fault.get('target')!r} is not a "
                            "conjunct; nothing could attribute its failures")
        for run in fault["runs"]:
            mode, rows = run["mode"], run["rows"]
            if mode in REPLAY_MODES:
                if len(rows) != 1:
                    problems.append(f"{fid}: replay run shares one cache "
                                    f"across {len(rows)} rows; must be per-row")
                if any(tests.get(r, {}).get("port_mode") != "stub"
                       for r in rows):
                    problems.append(f"{fid}: replay rows must be stub rows")
                for item in (run.get("touch") or "").split(","):
                    method, _, path = item.strip().rpartition(" ")
                    if (fault.get("target") == "route" and path == "/v1/models"
                            and (method or "GET") == "GET"):
                        problems.append(f"{fid}: a route fault touches "
                                        "GET /v1/models itself")
            if mode in SLOW_MODES and len(rows) != 1:
                problems.append(f"{fid}: {mode} must run on exactly 1 row")
            if mode in SLOW_MODES and not fault.get("slow"):
                problems.append(f"{fid}: {mode} run but fault not marked slow")
            if mode == "malformed" and "body_b64" not in run:
                problems.append(f"{fid}: malformed run needs body_b64")
            for row in rows:
                test = tests.get(row)
                if test is None:
                    continue
                expected = test["expected"]
                if mode == "served-norm" and contract_served_model(test) == "-":
                    problems.append(f"{fid}: {row} serves no id to normalise")
                if mode == "verdict-pad" and expected["verdict"] == "MODEL_OK":
                    problems.append(f"{fid}: padded MODEL_OK also breaks drift")
                if mode == "reason-case" and \
                        expected["reason"].swapcase() == expected["reason"]:
                    problems.append(f"{fid}: {row} reason has no cased letter")
    return len(ids)


def _clean_record(name, test):
    """A record that satisfies every conjunct failed_conjuncts() checks."""
    expected = test["expected"]
    stub = test.get("port_mode") == "stub"
    return {"name": name, "verdict": expected["verdict"],
            "reason": expected["reason"], "probe_exit": expected["exit"],
            "drift": expected["verdict"] != "MODEL_OK",
            "served_model": contract_served_model(test),
            "requests": [{"method": "GET", "path": "/v1/models"}] if stub
            else [], "error": None, "passed": True}


def selftest_classifier(tests, problems):
    """classify_run() on synthetic check.py documents: only an exit-1 JSON
    document whose faulted row failed ON the target conjunct is a detection."""
    row = ROWS_FULL[0]
    if row not in tests:
        problems.append(f"classifier cases need matrix row {row}")
        return 0
    clean = _clean_record(row, tests[row])

    def doc(**changes):
        return json.dumps({"records": [dict(clean, **changes)]})

    f1, f5, f6, f10 = (_by_id(i) for i in ("F1", "F5", "F6", "F10"))
    cases = [
        ("reason fault failed on reason", f1, 1,
         doc(reason="matched-forged", passed=False), True),
        ("target-conjunct attribution: reason fault failed on verdict only",
         f1, 1, doc(verdict="FORGED", passed=False), False),
        ("reason fault failed on error only", f1, 1,
         doc(error="wrapper crashed", passed=False), False),
        ("served fault failed on served_model", f5, 1,
         doc(served_model="KAMA-READY", passed=False), True),
        ("padded verdict failed on verdict", f10, 1,
         doc(verdict=" MODEL_OK", passed=False), True),
        ("route fault, only GET /health", f6, 1,
         doc(requests=[{"method": "GET", "path": "/health"}],
             passed=False), True),
        ("route fault, /v1/models only by POST", f6, 1,
         doc(requests=[{"method": "POST", "path": "/v1/models"}],
             passed=False), True),
        ("route fault failed on reason only", f6, 1,
         doc(reason="x", passed=False), False),
        ("faulted row still passed", f1, 1, doc(reason="x"), False),
        ("faulted row passed null", f1, 1, doc(reason="x", passed=None),
         False),
        ("exit 0 with failed row", f1, 0, doc(reason="x", passed=False),
         False),
        ("exit 2", f1, 2, "", False),
        ("exit 1 with a traceback", f1, 1,
         "Traceback (most recent call last):\n", False),
        ("exit 1 with empty stdout", f1, 1, "", False),
        ("exit 1 with a JSON array", f1, 1, "[]", False),
        ("records not a list", f1, 1, json.dumps({"records": {}}), False),
        ("faulted row missing", f1, 1, json.dumps({"records": []}), False),
        ("wrapper died (probe exit 9)", f1, 1,
         doc(reason="x", passed=False, probe_exit=WRAPPER_EXIT), "own-fault"),
        ("fault without a target", dict(f1, target=None), 1,
         doc(reason="x", passed=False), "own-fault"),
        ("F0: all rows passed", POSITIVE_CONTROL, 0, doc(), True),
        ("F0: a row failed", POSITIVE_CONTROL, 0, doc(passed=False), False),
        ("F0: exit 1", POSITIVE_CONTROL, 1, doc(), False),
        ("F0: non-JSON stdout", POSITIVE_CONTROL, 0, "all good\n", False),
    ]
    for label, fault, code, stdout, want in cases:
        try:
            got = classify_run(code, stdout, [row], tests, fault)[0]
        except OwnFault:
            got = "own-fault"
        if got != want:
            problems.append(f"classifier: {label}: got {got!r}, want {want!r}")
    return len(cases)


def selftest_gate(matrix_dir, problems):
    """F0 gates the suite: a reject-everything check.py ends it with exit 2
    and no counted fault; an accept-everything one passes F0, then has F1
    accepted (exit 1). Stub check.py scripts; no probe runs, no port."""
    outcomes = {}
    with tempfile.TemporaryDirectory(prefix="kama-fault-controls-gate-") as tmp:
        probe = Path(tmp) / "never-run-probe.sh"
        probe.write_text("#!/usr/bin/env bash\nexit 97\n", encoding="utf-8")
        for label, passed in (("reject-everything", False),
                              ("accept-everything", True)):
            fake = Path(tmp) / f"{label}.py"
            fake.write_text(FAKE_CHECK.replace("PASSED", repr(passed)),
                            encoding="utf-8")
            result = run_suite(fake, probe, matrix_dir, [_by_id("F1")])
            outcomes[label] = {
                "code": result["code"],
                "accepted": (result["doc"] or {}).get("accepted"),
                "error": result["error"]}
    reject = outcomes["reject-everything"]
    if not (reject["code"] == 2 and reject["accepted"] is None
            and str(reject["error"]).startswith("suite INVALID")):
        problems.append("F0 gate: a reject-everything check.py was not "
                        f"refused before any fault counted: {reject}")
    accept = outcomes["accept-everything"]
    if not (accept["code"] == 1 and accept["accepted"] == 1):
        problems.append("F0 gate: an accept-everything check.py did not pass "
                        f"F0 and then have F1 accepted: {accept}")
    return outcomes


def _wrapper_problem(run, rc, out, cache_text):
    """None when the wrapper's output is exactly the declared corruption of
    the canned probe document, else what is wrong with it."""
    mode = run["mode"]
    if rc == WRAPPER_EXIT:
        return "wrapper died"
    if mode == "malformed":
        body = base64.b64decode(run["body_b64"])
        want = body if body.endswith(b"\n") else body + b"\n"
        if out != want:
            return "emitted bytes are not exactly the declared body"
        return None if rc == CANNED_RC else f"exit {rc} != probe exit"
    if mode in ("pass",) + REPLAY_MODES:
        if out.decode("utf-8", "replace") != cache_text:
            return "identity/replay output differs from the honest output"
        return None if rc == CANNED_RC else f"exit {rc} != probe exit"
    try:
        doc = json.loads(out)
    except ValueError:
        return "output is not JSON"
    if mode == "exit":
        if doc != CANNED_DOC:
            return "exit fault changed the document"
        return None if rc == 0 else f"exit {rc} not flipped from 2 to 0"
    if rc != CANNED_RC:
        return f"exit {rc} != probe exit {CANNED_RC}"
    if {k: v for k, v in doc.items() if k != "rows"} != \
            {k: v for k, v in CANNED_DOC.items() if k != "rows"}:
        return "top-level fields changed"
    rows, honest = doc.get("rows"), CANNED_DOC["rows"][0]
    if mode == "first-row":
        if not (isinstance(rows, list) and len(rows) == 2
                and rows[1] == honest):
            return "honest row is not kept as the last of two rows"
    elif not (isinstance(rows, list) and len(rows) == 1):
        return "row count changed"
    forged = rows[0]
    changed = sorted(k for k in set(forged) | set(honest)
                     if forged.get(k) != honest.get(k))
    field = FIELD_OF_MODE.get(mode)
    if changed != [field]:
        return f"changed {changed}; the fault declares only {field!r}"
    if mode == "served-norm":
        same = lambda forged, honest: served_normalised_equal(
            forged, honest, run["variant"])
    else:
        same = NORMALISED_EQUAL.get(mode)
    if same and not same(forged[field], honest[field]):
        return (f"{forged[field]!r} is not {honest[field]!r} under the "
                "mutant's normalisation, so it cannot kill that mutant")
    return None


def selftest_wrapper(problems):
    """Run every non-slow wrapper corruption against a canned probe document
    (port 0: the wrapper never opens a socket) and require exactly the one
    declared change."""
    with tempfile.TemporaryDirectory(prefix="kama-fault-controls-wrap-") as tmp:
        work = Path(tmp)
        wrap = work / "wrap.py"
        wrap.write_text(WRAPPER, encoding="utf-8")
        canned = json.dumps(CANNED_DOC, indent=2) + "\n"
        (work / "canned.json").write_text(canned, encoding="utf-8")
        probe = work / "canned-probe.sh"
        probe.write_text(f"#!/usr/bin/env bash\n"
                         f"cat {shlex.quote(str(work / 'canned.json'))}\n"
                         f"exit {CANNED_RC}\n", encoding="utf-8")
        replay = work / "replay-cache"
        replay.write_text(canned, encoding="utf-8")
        (work / "replay-cache.rc").write_text(str(CANNED_RC), encoding="utf-8")
        jobs = []
        for fault in [POSITIVE_CONTROL] + FAULTS:
            for index, run in enumerate(fault["runs"]):
                if run["mode"] in SLOW_MODES:
                    continue
                env = dict(os.environ)
                env.update(run_env(fault, run, index, probe, work))
                cache = None
                if run["mode"] in REPLAY_MODES:
                    env["FAULT_CACHE"] = str(replay)
                elif run["mode"] == "pass":
                    cache = work / f"pass-{fault['id']}-{index}"
                    env["FAULT_CACHE"] = str(cache)
                jobs.append((fault["id"], index, run, env, cache))

        def invoke(job):
            fid, index, run, env, cache = job
            proc = subprocess.run(["bash", str(wrap), *PROBE_ARGV], env=env,
                                  capture_output=True, timeout=60)
            problem = _wrapper_problem(run, proc.returncode, proc.stdout,
                                       canned)
            if problem is None and cache is not None:
                written = (cache.read_text(encoding="utf-8")
                           if cache.exists() else None)
                rc_file = Path(str(cache) + ".rc")
                if written != canned or not rc_file.exists() or \
                        rc_file.read_text().strip() != str(CANNED_RC):
                    problem = "identity pre-pass did not cache the honest output"
            if problem:
                label = run.get("variant", index)
                return (f"wrapper {fid}[{label}] {run['mode']}: {problem}; "
                        f"stderr={proc.stderr[-200:]!r}")
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for problem in pool.map(invoke, jobs):
                if problem:
                    problems.append(problem)
    return len(jobs)


def _kill_group_member(pidfile, pgid):
    """Last-resort cleanup that does not trust the reaper under test: kill
    the recorded child iff it is still a live member of our process group."""
    try:
        pid = int(Path(pidfile).read_text().strip())
        stat = (Path("/proc") / str(pid) / "stat").read_bytes()
    except (OSError, ValueError):
        return
    fields = stat[stat.rfind(b")") + 2:].split()    # state ppid pgrp ...
    if len(fields) > 2 and fields[0] not in (b"Z", b"X") \
            and int(fields[2]) == pgid:
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def selftest_escape(problems):
    """F17's own detector, both ways: when only the wrapper process is
    killed its child must read as escaped (and be killed by the reaper);
    when the wrapper's whole process group is killed, it must not."""
    outcomes = {}
    if not Path("/proc/self/cmdline").exists():
        problems.append("escape: no Linux /proc; F17 cannot be observed")
        return outcomes
    with tempfile.TemporaryDirectory(prefix="kama-fault-controls-esc-") as tmp:
        wrap = Path(tmp) / "wrap.py"
        wrap.write_text(WRAPPER, encoding="utf-8")
        for label, kill_group in (("direct-kill", False), ("group-kill", True)):
            escape = new_escape(tmp, label)
            env = dict(os.environ, FAULT_MODE="escape", FAULT_PROBE=str(wrap),
                       FAULT_WRAPPER_EXIT=str(WRAPPER_EXIT),
                       **escape_env(escape))
            proc = subprocess.Popen(["bash", str(wrap), *PROBE_ARGV], env=env,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    start_new_session=True)
            pid, survived, alive_after = None, None, None
            try:
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    try:
                        if escape["pidfile"].read_text().strip():
                            break
                    except OSError:
                        pass
                    time.sleep(0.02)
                if kill_group:
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
                proc.wait(timeout=15)
                pid, survived = reap_escape_child(escape, grace=0.5)
                alive_after = pid is not None and is_escape_child(pid, escape)
            finally:            # leave nothing behind, whatever happened
                if proc.poll() is None:     # unreaped: its pgid is still ours
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        proc.kill()
                    proc.wait()
                reap_escape_child(escape, grace=0.0)
                _kill_group_member(escape["pidfile"], proc.pid)
            outcomes[label] = {"pid": pid, "survived": survived,
                               "alive_after_reap": alive_after}
            if pid is None or survived is not (not kill_group) or alive_after:
                problems.append(f"escape {label}: got {outcomes[label]}, "
                                f"want survived={not kill_group} and no "
                                "child left alive")
    return outcomes


def do_selftest(matrix_dir):
    tests = load_matrix_tests(matrix_dir)
    n_files, digest = matrix_set_digest(matrix_dir)
    problems = []
    if len(tests) != EXPECTED_MATRIX_TESTS:
        problems.append(f"matrix breadth {len(tests)} != pinned "
                        f"{EXPECTED_MATRIX_TESTS}")
    if digest != EXPECTED_MATRIX_SHA256:
        problems.append(f"matrix set digest {digest} != pinned "
                        f"{EXPECTED_MATRIX_SHA256}")
    want_modes = {"stub", "closed"}
    verdict_families = {"MODEL_OK", "MODEL_MISMATCH", "MODEL_LOADING",
                        "FOREIGN_SERVICE", "DEAD"}
    seen_rows = set()
    for fault in [POSITIVE_CONTROL] + FAULTS:
        for run in fault["runs"]:
            for row in run["rows"]:
                seen_rows.add(row)
                if row not in tests:
                    problems.append(f"{fault['id']}: row {row!r} not in matrix")
                elif tests[row].get("port_mode") not in want_modes:
                    problems.append(f"{fault['id']}: row {row!r} has bad "
                                    f"port_mode {tests[row].get('port_mode')!r}")
    # F4 must exercise at least one non-MODEL_OK row (lower-casing only bites
    # where the verdict is a real word).
    f4 = _by_id("F4")
    f4_verdicts = {tests[r]["expected"]["verdict"]
                   for run in f4["runs"] for r in run["rows"] if r in tests}
    if not (f4_verdicts - {"MODEL_OK"}):
        problems.append("F4 must include a non-MODEL_OK row")
    covered = {tests[r]["expected"]["verdict"] for r in seen_rows
               if r in tests}
    missing_families = verdict_families - covered
    if missing_families:
        problems.append(f"fault rows miss verdict families "
                        f"{sorted(missing_families)}")
    faults_checked = selftest_table(tests, problems)
    classifier_cases = selftest_classifier(tests, problems)
    gate = selftest_gate(matrix_dir, problems)
    wrapper_checks = selftest_wrapper(problems)
    escape = selftest_escape(problems)
    result = {"selftest": "kama-fault-controls/selftest-v1",
              "matrix_files": n_files,
              "matrix_tests": len(tests),
              "matrix_sha256": digest,
              "rows_checked": len(seen_rows),
              "families_covered": sorted(covered),
              "faults_checked": faults_checked,
              "classifier_cases": classifier_cases,
              "gate": gate,
              "wrapper_checks": wrapper_checks,
              "escape": escape,
              "problems": problems,
              "passed": not problems}
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


# ---------------------------------------------------------------- driver
def build_parser():
    parser = argparse.ArgumentParser(
        description="Run fault-injection controls against a probe-verdict "
                    "check.py: each fault corrupts exactly one probe-output "
                    "field/behaviour and must be failed by the harness.")
    parser.add_argument("--check", default=str(DEFAULT_CHECK),
                        help=f"check.py under test (default {DEFAULT_CHECK}); "
                             "the frozen copy works too")
    parser.add_argument("--probe", default=str(DEFAULT_PROBE),
                        help=f"real probe the wrappers wrap "
                             f"(default {DEFAULT_PROBE})")
    parser.add_argument("--matrix-dir", default=str(MATRIX_DIR),
                        help="directory whose *.json are byte-copied into the "
                             "scratch harness (default: this file's directory)")
    parser.add_argument("--only-fault", action="append", default=[],
                        metavar="ID",
                        help="run only this fault id (repeatable; "
                             "e.g. --only-fault F7)")
    parser.add_argument("--skip-slow", action="store_true",
                        help="skip the slow controls F7 and F17 (each waits "
                             "out check.py's ~30s probe timeout)")
    parser.add_argument("--json", action="store_true",
                        help="emit the machine document on stdout "
                             "(summary moves to stderr)")
    parser.add_argument("--list", action="store_true",
                        help="list the fault table and exit 0")
    parser.add_argument("--selftest", action="store_true",
                        help="validate the fault table, the classifier, the "
                             "F0 gate, every wrapper corruption and the F17 "
                             "child detector without the real probe or check.py "
                             "(no port is opened)")
    return parser


def do_list(faults):
    for fault in faults:
        tags = ""
        if fault.get("kills"):
            tags += f" kills={','.join(fault['kills'])}"
        if fault.get("debt"):
            tags += " debt"
        if fault.get("slow"):
            tags += " slow"
        for run in fault["runs"]:
            variant = f" [{run['variant']}]" if run.get("variant") else ""
            print(f"{fault['id']}{variant} {fault['title']} "
                  f"mode={run['mode']} rows={len(run['rows'])}{tags}")
            for row in run["rows"]:
                print(f"    {row}")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)

    faults = list(FAULTS)
    if args.only_fault:
        wanted = set(args.only_fault)
        known = {f["id"] for f in FAULTS} | {POSITIVE_CONTROL["id"]}
        missing = wanted - known
        if missing:
            print(f"fault-controls: unknown --only-fault {sorted(missing)}; "
                  f"known ids: {sorted(known)}", file=sys.stderr)
            return 2
        faults = [f for f in FAULTS if f["id"] in wanted]
    if args.skip_slow:
        faults = [f for f in faults if not f.get("slow")]

    if args.list:
        return do_list([POSITIVE_CONTROL] + faults)
    if args.selftest:
        try:
            return do_selftest(args.matrix_dir)
        except OwnFault as exc:
            print(f"fault-controls: own fault: {exc}", file=sys.stderr)
            return 2

    check_path = Path(args.check)
    if not check_path.is_file():
        print(f"fault-controls: --check not found: {check_path}",
              file=sys.stderr)
        return 2
    probe_path = Path(args.probe)
    if not probe_path.is_file():
        print(f"fault-controls: --probe not found: {probe_path}",
              file=sys.stderr)
        return 2

    try:
        result = run_suite(check_path, probe_path, args.matrix_dir, faults)
    except KeyboardInterrupt:
        print("fault-controls: interrupted; nothing graded", file=sys.stderr)
        return 2
    except Exception:                                   # pragma: no cover
        traceback.print_exc()
        return 2
    if result["doc"] is None:
        print(f"fault-controls: {result['error']}", file=sys.stderr)
        return result["code"]

    doc = result["doc"]
    ran = {f["id"] for f in faults}
    doc["skipped"] = [f["id"] for f in FAULTS if f["id"] not in ran]
    positive = doc["positive_control"]
    out_faults = doc["faults"]
    if args.json:
        print(json.dumps(doc, indent=2))
    else:
        print(f"[{'PASS' if positive['detected'] else 'FAIL'}] "
              f"{positive['id']} {positive['title']}: {positive['why']}")
        for fault in out_faults:
            status = "DETECTED" if fault["detected"] else "ACCEPTED"
            print(f"[{status}] {fault['id']} {fault['title']}: {fault['why']}")
        print(f"detected={doc['detected']} accepted={doc['accepted']} "
              f"check={check_path}")
    return result["code"]


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:                 # e.g. `--list | head`
        sys.stderr.close()
        sys.exit(0)
