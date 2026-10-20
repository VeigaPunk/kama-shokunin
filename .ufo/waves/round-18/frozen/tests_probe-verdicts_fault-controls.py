#!/usr/bin/env python3
"""kama-fault-controls — fault-injection controls for the probe verdict harness.

Lane: local model serving & endpoint health (kama-shokunin), round 17, claim C1.

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
                   faulted row has "passed": false
    ACCEPTED  <=>  anything else: exit 0, exit 2, a traceback/non-JSON stdout,
                   a missing row, or any faulted row still passed
    F0 is the positive control (identity wrapper): "detected" means check.py
    passed the honest probe (exit 0, all rows passed). A reject-everything
    check.py scores F0 accepted, so the verdict cannot be laundered.

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
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
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

# Pinned round-16 facts (.ufo/waves/round-16/measure.py:281-290): the staged
# matrix set must reproduce this name+content digest and breadth before the
# controls mean anything.
EXPECTED_MATRIX_SHA256 = ("bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21ed"
                          "b2b8256e22771f32")
EXPECTED_MATRIX_TESTS = 72


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


def _per_row(mode, touch, rows):
    """One run per row: a shared cache cannot tell rows apart when several
    --only entries replay it, so each row gets its own check invocation."""
    return [{"mode": mode, "touch": touch, "rows": [r]} for r in rows]


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
]


# ------------------------------------------------------------- wrapper probe
# bash->python3 trampoline: check.py always invokes the probe as `bash <probe>`,
# so the wrapper is a bash script whose python body arrives on stdin via heredoc;
# "$@" still lands in sys.argv[1:]. The real probe path comes from FAULT_PROBE.
WRAPPER = r'''#!/usr/bin/env bash
exec python3 - "$@" <<'FAULT_WRAPPER_EOF'
"""Fault wrapper probe. argv: <probe args...>; FAULT_PROBE is the real probe.
FAULT_MODE selects the single corruption; FAULT_* env carries cache paths /
body (base64) / sleep."""
import base64, json, os, subprocess, sys, time, urllib.request


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


def hit(path):
    port = opt("--port")
    if not port or port == "0":
        return
    try:
        urllib.request.urlopen("http://127.0.0.1:%s%s" % (port, path),
                               timeout=3).read()
    except Exception:
        pass  # closed port or stub rejection is not the wrapper's business


if mode == "hang":
    time.sleep(float(os.environ.get("FAULT_SLEEP", "40")))

if mode == "f6":
    hit("/health")                       # reachable port, wrong route
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
    # the single corrupted field. FAULT_BODY_B64 carries raw bytes so the
    # non-UTF-8 variant survives argv/env text encoding.
    p = subprocess.run(["bash", real] + args, capture_output=True, text=True)
    body = base64.b64decode(os.environ.get("FAULT_BODY_B64", ""))
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
except Exception as exc:
    die("real probe output not mutable (%r); cannot inject a clean fault" % exc)

if mode == "reason":
    row["reason"] = str(row.get("reason")) + "-forged"
elif mode == "verdict":
    v = row.get("verdict")
    if not isinstance(v, str):
        die("verdict not a string")
    row["verdict"] = v.lower()
elif mode == "drift":
    row["drift"] = not row.get("drift")
elif mode == "served":
    row["served_model"] = "kama-forged-id"
elif mode == "exit":
    pass                                # exit handled after emit
else:
    die("unknown FAULT_MODE %r" % mode)

doc["rows"][0] = row
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
    as a clean detection of a field fault. Positive-control runs need exit 0 +
    parseable JSON + every row passed=true."""
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
    except (json.JSONDecodeError, ValueError):
        return False, (f"check exited {exit_code} but stdout is not parseable "
                       f"JSON (traceback or human text); "
                       f"stdout[:120]={stdout[:120]!r}")
    records = doc.get("records")
    if not isinstance(records, list):
        return False, "check JSON lacks a records list"
    seen = {r.get("name"): r for r in records if isinstance(r, dict)}
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
    return True, (f"check exited 1 with JSON; all {len(run_rows)} "
                  "faulted rows passed=false")


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


def run_fault(scratch, cache_dir, fault, probe_path, matrix_tests):
    """Execute one fault's runs inside the staged harness; return its entry."""
    runs_detected = []
    run_whys = []
    exits = []
    all_rows = []
    for index, run in enumerate(fault["runs"]):
        rows = run["rows"]
        all_rows.extend(r for r in rows if r not in all_rows)
        env = {
            "FAULT_MODE": run["mode"],
            "FAULT_PROBE": str(probe_path),
            "FAULT_WRAPPER_EXIT": str(WRAPPER_EXIT),
        }
        if run["mode"] == "f6":
            # Per-row pre-pass: this run replays only this row's real output.
            cache = str(cache_dir / f"f6-{fault['id']}-{index}")
            prepass_env = dict(env)
            prepass_env["FAULT_MODE"] = "pass"
            prepass_env["FAULT_CACHE"] = cache
            p_exit, _, p_err = run_check(scratch, rows, prepass_env)
            if (p_exit == WRAPPER_EXIT or not Path(cache).exists()
                    or not Path(cache + ".rc").exists()):
                raise OwnFault(
                    f"F6 pre-pass failed (exit {p_exit}): {p_err[-200:]}")
            env["FAULT_CACHE"] = cache
        if run["mode"] == "hang":
            env["FAULT_SLEEP"] = str(run.get("sleep", HANG_SECONDS))
        if run["mode"] == "malformed":
            env["FAULT_BODY_B64"] = run["body_b64"]
        exit_code, stdout, _stderr = run_check(scratch, rows, env)
        exits.append(exit_code)
        detected, why = classify_run(exit_code, stdout, rows, matrix_tests,
                                     fault)
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
    }


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
                             "(default {DEFAULT_PROBE})")
    parser.add_argument("--matrix-dir", default=str(MATRIX_DIR),
                        help="directory whose *.json are byte-copied into the "
                             "scratch harness (default: this file's directory)")
    parser.add_argument("--only-fault", action="append", default=[],
                        metavar="ID",
                        help="run only this fault id (repeatable; "
                             "e.g. --only-fault F7)")
    parser.add_argument("--skip-slow", action="store_true",
                        help="skip F7 (the ~40s hang control)")
    parser.add_argument("--json", action="store_true",
                        help="emit the machine document on stdout "
                             "(summary moves to stderr)")
    parser.add_argument("--list", action="store_true",
                        help="list the fault table and exit 0")
    parser.add_argument("--selftest", action="store_true",
                        help="validate the fault table against the real matrix "
                             "without invoking check.py")
    return parser


def do_list(faults):
    for fault in faults:
        for run in fault["runs"]:
            variant = f" [{run['variant']}]" if run.get("variant") else ""
            print(f"{fault['id']}{variant} {fault['title']} "
                  f"mode={run['mode']} rows={len(run['rows'])}")
            for row in run["rows"]:
                print(f"    {row}")
    return 0


CONJUNCTS = {"verdict", "reason", "exit", "drift", "served_model", "route",
             "error"}


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
        if fault.get("target") and fault["target"] not in CONJUNCTS:
            problems.append(f"{fault['id']}: unknown target {fault['target']!r}")
        for run in fault["runs"]:
            for row in run["rows"]:
                seen_rows.add(row)
                if row not in tests:
                    problems.append(f"{fault['id']}: row {row!r} not in matrix")
                elif tests[row].get("port_mode") not in want_modes:
                    problems.append(f"{fault['id']}: row {row!r} has bad "
                                    f"port_mode {tests[row].get('port_mode')!r}")
            if run["mode"] == "hang" and len(run["rows"]) != 1:
                problems.append(f"{fault['id']}: hang must run on exactly 1 row")
            if run["mode"] == "malformed" and "body_b64" not in run:
                problems.append(f"{fault['id']}: malformed run needs body_b64")
    # F4 must exercise at least one non-MODEL_OK row (lower-casing only bites
    # where the verdict is a real word).
    f4 = next(f for f in FAULTS if f["id"] == "F4")
    f4_verdicts = {tests[r]["expected"]["verdict"]
                   for run in f4["runs"] for r in run["rows"]}
    if not (f4_verdicts - {"MODEL_OK"}):
        problems.append("F4 must include a non-MODEL_OK row")
    covered = {tests[r]["expected"]["verdict"] for r in seen_rows
               if r in tests}
    missing_families = verdict_families - covered
    if missing_families:
        problems.append(f"fault rows miss verdict families "
                        f"{sorted(missing_families)}")
    result = {"selftest": "kama-fault-controls/selftest-v1",
              "matrix_files": n_files,
              "matrix_tests": len(tests),
              "matrix_sha256": digest,
              "rows_checked": len(seen_rows),
              "families_covered": sorted(covered),
              "problems": problems,
              "passed": not problems}
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


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
        faults = [f for f in faults if f["id"] != "F7"]

    if args.list:
        return do_list([POSITIVE_CONTROL] + faults)
    if args.selftest:
        return do_selftest(args.matrix_dir)

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

    started = time.time()
    try:
        with tempfile.TemporaryDirectory(prefix="kama-fault-controls-") as tmp:
            staged_files, staged_digest = matrix_set_digest(args.matrix_dir)
            staged_tests = load_matrix_tests(args.matrix_dir)
            if staged_tests and len(staged_tests) != EXPECTED_MATRIX_TESTS:
                raise OwnFault(f"matrix breadth {len(staged_tests)} != pinned "
                               f"{EXPECTED_MATRIX_TESTS}; refusing to grade")
            if staged_digest != EXPECTED_MATRIX_SHA256:
                raise OwnFault(f"matrix set digest {staged_digest} != pinned "
                               f"{EXPECTED_MATRIX_SHA256}; refusing to grade")
            n_matrix, cache_dir = stage_scratch(tmp, check_path,
                                                args.matrix_dir)
            if n_matrix == 0:
                raise OwnFault(f"no *.json matrix files in {args.matrix_dir}")
            _, scratch_digest = matrix_set_digest(tmp)
            if scratch_digest != EXPECTED_MATRIX_SHA256:
                raise OwnFault(f"scratch matrix digest {scratch_digest} != "
                               f"pinned {EXPECTED_MATRIX_SHA256} (copy fault)")

            positive = run_fault(tmp, cache_dir, POSITIVE_CONTROL,
                                 probe_path, staged_tests)
            if not positive["detected"]:
                print("fault-controls: suite INVALID — positive control "
                      f"F0 failed: {positive['why']}", file=sys.stderr)
                return 2

            out_faults = [run_fault(tmp, cache_dir, fault, probe_path,
                                    staged_tests) for fault in faults]
    except OwnFault as exc:
        print(f"fault-controls: own fault: {exc}", file=sys.stderr)
        return 2
    except Exception:                                   # pragma: no cover
        traceback.print_exc()
        return 2

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
    }
    if args.json:
        print(json.dumps(doc, indent=2))
    else:
        if positive:
            print(f"[{'PASS' if positive['detected'] else 'FAIL'}] "
                  f"{positive['id']} {positive['title']}: {positive['why']}")
        for fault in out_faults:
            status = "DETECTED" if fault["detected"] else "ACCEPTED"
            print(f"[{status}] {fault['id']} {fault['title']}: {fault['why']}")
        print(f"detected={detected_n} accepted={accepted_n} "
              f"check={check_path}")
    return 0 if accepted_n == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:                 # e.g. `--list | head`
        sys.stderr.close()
        sys.exit(0)
