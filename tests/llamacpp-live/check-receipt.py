#!/usr/bin/env python3
"""Independent validator for kama-llamacpp-live/v1 and /v2 receipts.

Bound to the exact receipt keys emitted by
``tools/kama-llamacpp-live.py`` (round-16 hardening batch + round-17
v2 fail-capable checks):
started_utc/ended_utc, server{arg,realpath,sha256,install_tree,
install_tree_sha256,server_impl_sha256|null}, model{path,sha256},
model_sha256_post, probe{path,sha256}, alias, ctx, threads, port,
port_refusal_set, child_env_keys, argv, transitions, loading_503,
loading_observed, loading_envelope_exact, port_listener_ownership,
captures{health,models,props,slots,metrics}, probes[2]
{expect,argv,exit,result,stderr_tail}, teardown{returncode,
sigterm_sent,sigkill_sent,alive_at_teardown_start,port_refuses,...},
checks[] {id,documented_by,passed,observed}, setup_error,
port_pick_note, pdeathsig.

Every claim is re-derived from the stored evidence; a bare
``"passed": true`` is never trusted.  Under v2 each check's claimed
``passed`` is additionally compared against the value re-derived here.

v1 checks (each exactly once, all passed, all re-derived):
  health_ready, models_alias_id, models_owned_by_llamacpp,
  metrics_not_enabled (status must be exactly 501), props_alias,
  probe_model_ok, probe_mismatch, teardown_exited,
  teardown_port_closed, model_unchanged

v2 checks (each exactly once, all passed, all re-derived):
  health_ready (status 200 AND body parses to {"status":"ok"}),
  models_alias_id, models_owned_by_llamacpp, metrics_not_enabled,
  props_alias, probe_model_ok, probe_mismatch,
  teardown_graceful (alive_at_teardown_start, SIGTERM sent, no
  SIGKILL, graceful exit status 0), teardown_port_closed (only
  after the port was proven owned by the child), and
  loading_envelope_graded (a check must consume the stored loading
  evidence), model_unchanged

Usage:
  check-receipt.py RECEIPT [--expect-model-sha256 HEX]
                           [--expect-server-sha256 HEX]
                           [--expect-probe-sha256 HEX]
  check-receipt.py --selftest

Exit: 0 receipt valid, 1 receipt invalid (every problem listed),
      2 receipt unreadable / not JSON.
"""
import argparse
import copy
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile


RECEIPT_SCHEMA = "kama-llamacpp-live/v1"
RECEIPT_SCHEMA_V2 = "kama-llamacpp-live/v2"
PROBE_SCHEMA = "kama-probe/v1"
HARD_PINS = (8080, 34113)
MISMATCH_EXPECT = "kama-not-this-model"
# Producer CHILD_ENV_KEYS: the server child sees only these names when
# present in the harness env; the receipt records names, never values.
CHILD_ENV_ALLOWLIST = {"PATH", "HOME", "LANG", "LC_ALL", "TMPDIR"}

REQUIRED_CHECKS_V1 = (
    "health_ready",
    "models_alias_id",
    "models_owned_by_llamacpp",
    "metrics_not_enabled",
    "props_alias",
    "probe_model_ok",
    "probe_mismatch",
    "teardown_exited",
    "teardown_port_closed",
    "model_unchanged",
)

REQUIRED_CHECKS_V2 = (
    "health_ready",
    "models_alias_id",
    "models_owned_by_llamacpp",
    "metrics_not_enabled",
    "props_alias",
    "probe_model_ok",
    "probe_mismatch",
    "teardown_graceful",
    "teardown_port_closed",
    "loading_envelope_graded",
    "model_unchanged",
)

HEALTH_READY_DOC = {"status": "ok"}

MISSING = object()


def install_tree_sha(tree):
    """Recompute producer install_tree_sha256(): sha256 over the sorted
    'name sha\\n' lines."""
    return hashlib.sha256(
        ''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()
    ).hexdigest()


def loading_envelope_ok(doc):
    """Mirror of producer loading_envelope_exact(): message/type exact,
    code an int equal to 503."""
    err = doc.get("error") if isinstance(doc, dict) else None
    if not isinstance(err, dict):
        return False
    code = err.get("code")
    return (err.get("message") == "Loading model"
            and err.get("type") == "unavailable_error"
            and type(code) is int and code == 503)


def dig(node, *keys):
    """Exact-key descent through dicts; MISSING on any miss."""
    cur = node
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return MISSING
        cur = cur[k]
    return cur


def is_hex64(v):
    return (isinstance(v, str) and len(v) == 64
            and all(c in "0123456789abcdef" for c in v))


def check_digest(problems, where, value, allow_none=False):
    """A sha256 receipt field: 64-char lowercase hex, or None where the
    producer permits null."""
    if value is None and allow_none:
        return
    if not is_hex64(value):
        problems.append(f"{where} {value!r} is not a 64-char lowercase "
                        "hex string")


def parse_ts(v):
    if not isinstance(v, str) or not v.strip():
        return None
    s = v.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def parse_body(text):
    """A stored body string parsed as JSON, or None."""
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


def argv_flag(argv, flag):
    """Value following `flag` in an argv list, or None."""
    if not isinstance(argv, list):
        return None
    for i, a in enumerate(argv[:-1]):
        if a == flag:
            return argv[i + 1]
    return None


def probe_row0(rec):
    """rows[0] of a parsed kama-probe check result, or MISSING."""
    res = rec.get("result")
    if isinstance(res, dict):
        rows = res.get("rows")
        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            return rows[0]
    return MISSING


# --------------------------------------------------------------- validation


def validate(receipt, expect_model=None, expect_server=None,
             expect_probe=None, expect_tool=None):

    problems = []

    def bad(msg):
        problems.append(msg)

    if not isinstance(receipt, dict):
        return ["receipt is not a JSON object"]

    # --- schema / run outcome ---------------------------------------------
    schema = receipt.get("schema")
    is_v2 = schema == RECEIPT_SCHEMA_V2
    if schema not in (RECEIPT_SCHEMA, RECEIPT_SCHEMA_V2):
        bad(f"schema is {schema!r}, want {RECEIPT_SCHEMA!r} or "
            f"{RECEIPT_SCHEMA_V2!r}")
    if receipt.get("setup_error") is not None:
        bad(f"setup_error is {receipt.get('setup_error')!r} "
            "(a complete run has setup_error null)")

    # --- timestamps ---------------------------------------------------------
    started = parse_ts(receipt.get("started_utc"))
    ended = parse_ts(receipt.get("ended_utc"))
    if started is None:
        bad(f"started_utc {receipt.get('started_utc')!r} is not a "
            "parseable ISO timestamp")
    if ended is None:
        bad(f"ended_utc {receipt.get('ended_utc')!r} is not a parseable "
            "ISO timestamp")
    if started is not None and ended is not None and ended < started:
        bad(f"ended_utc {receipt['ended_utc']!r} precedes started_utc "
            f"{receipt['started_utc']!r}")

    # --- alias / scalars ------------------------------------------------------
    alias = receipt.get("alias")
    if not isinstance(alias, str) or not alias:
        bad(f"alias {alias!r} is not a non-empty string")
    for name in ("ctx", "threads"):
        v = receipt.get(name)
        if isinstance(v, bool) or not isinstance(v, int) or v < 1:
            bad(f"{name} {v!r} is not a positive integer")

    # --- port / refusal set ---------------------------------------------------
    port = receipt.get("port")
    if isinstance(port, bool) or not isinstance(port, int):
        bad(f"port {port!r} is not an integer")
        port = None
    elif not 1 <= port <= 65535:
        bad(f"port {port} out of range")
    refusal = receipt.get("port_refusal_set")
    if not isinstance(refusal, list) or not refusal:
        bad("port_refusal_set is missing or not a non-empty array")
        refusal = []
    else:
        if not all(isinstance(n, int) and not isinstance(n, bool)
                   and 1 <= n <= 65535 for n in refusal):
            bad("port_refusal_set contains a non-port element")
        if refusal != sorted(refusal):
            bad("port_refusal_set is not sorted (producer emits "
                "sorted(refused))")
        if len(set(refusal)) != len(refusal):
            bad("port_refusal_set has duplicate entries")
    for pin in HARD_PINS:
        if pin not in refusal:
            bad(f"port_refusal_set does not contain hard pin {pin}")
    if isinstance(port, int):
        if port in HARD_PINS:
            bad(f"port {port} is a registered consumer pin")
        if port in refusal:
            bad(f"port {port} is inside the receipt's own "
                "port_refusal_set")

    # --- server block ---------------------------------------------------------
    server = receipt.get("server")
    if not isinstance(server, dict):
        bad("server is missing or not an object")
        server = {}
    for k in ("arg", "realpath"):
        if not isinstance(server.get(k), str) or not server[k]:
            bad(f"server.{k} missing or not a non-empty string")
    server_sha = server.get("sha256")
    check_digest(problems, "server.sha256", server_sha)
    if is_hex64(server_sha) and expect_server is not None \
            and server_sha != expect_server:
        bad(f"server.sha256 {server_sha} != expected {expect_server}")

    tree = server.get("install_tree")
    if not isinstance(tree, dict):
        bad("server.install_tree is missing or not an object of "
            "basename -> sha256")
    else:
        for name, h in tree.items():
            if not is_hex64(h):
                bad(f"server.install_tree[{name!r}] is not a 64-char "
                    "hex digest")
        real = server.get("realpath")
        if isinstance(real, str) and "/" in real:
            base = real.rsplit("/", 1)[1]
            if tree and base not in tree:
                bad(f"server.install_tree does not contain the server "
                    f"basename {base!r}")
            elif is_hex64(server_sha) and base in tree \
                    and tree[base] != server_sha:
                bad(f"server.install_tree[{base!r}] != server.sha256")
    # install_tree_sha256 = sha256 over sorted 'name sha\n' lines; null
    # only when the producer could not list the directory.
    tree_sha = server.get("install_tree_sha256")
    check_digest(problems, "server.install_tree_sha256", tree_sha,
                 allow_none=True)
    if isinstance(tree, dict) and tree and is_hex64(tree_sha):
        if install_tree_sha(tree) != tree_sha:
            bad("server.install_tree_sha256 != recomputation over "
                "install_tree members")
    # server_impl_sha256 is null when the release has no impl .so.
    check_digest(problems, "server.server_impl_sha256",
                 server.get("server_impl_sha256"), allow_none=True)


    # --- model ----------------------------------------------------------------
    model = receipt.get("model")
    if not isinstance(model, dict):
        bad("model is missing or not an object")
        model = {}
    if not isinstance(model.get("path"), str) or not model["path"]:
        bad("model.path missing or not a non-empty string")
    model_sha = model.get("sha256")
    check_digest(problems, "model.sha256", model_sha)
    if is_hex64(model_sha) and expect_model is not None \
            and model_sha != expect_model:
        bad(f"model.sha256 {model_sha} != expected {expect_model}")

    model_post = receipt.get("model_sha256_post")
    if model_post is not None and not is_hex64(model_post) and not (
            isinstance(model_post, str)
            and model_post.startswith("rehash-error:")):
        bad(f"model_sha256_post {model_post!r} is not a 64-char hex "
            "digest or 'rehash-error:*'")

    # --- probe identity ---------------------------------------------------------
    probe = receipt.get("probe")
    if not isinstance(probe, dict):
        bad("probe is missing or not an object {path, sha256}")
        probe = {}
    if not isinstance(probe.get("path"), str) or not probe["path"]:
        bad("probe.path missing or not a non-empty string")
    probe_sha = probe.get("sha256")
    check_digest(problems, "probe.sha256", probe_sha)
    if is_hex64(probe_sha) and expect_probe is not None \
            and probe_sha != expect_probe:
        bad(f"probe.sha256 {probe_sha} != expected {expect_probe}")

    for name, val in (("model", expect_model), ("server", expect_server),
                      ("probe", expect_probe)):
        if val is not None and not is_hex64(val):
            bad(f"--expect-{name}-sha256 {val!r} is not 64 lowercase "
                "hex chars")

    # --- tool identity (optional block LiveHarness adds after the fact) ---
    tool = receipt.get("tool")
    if tool is not None:
        if not isinstance(tool, dict):
            bad("tool is present but not an object {path, sha256}")
        else:
            if not isinstance(tool.get("path"), str) \
                    or not tool["path"]:
                bad("tool.path missing or not a non-empty string")
            check_digest(problems, "tool.sha256", tool.get("sha256"))
            if is_hex64(tool.get("sha256")) and expect_tool is not None \
                    and tool["sha256"] != expect_tool:
                bad(f"tool.sha256 {tool['sha256']} != expected "
                    f"{expect_tool}")
    elif expect_tool is not None:
        bad("--expect-tool-sha256 given but receipt has no tool block")
    if expect_tool is not None and not is_hex64(expect_tool):
        bad(f"--expect-tool-sha256 {expect_tool!r} is not 64 lowercase "
            "hex chars")


    # --- child env keys: allowlisted names only, never values -------------------
    env_keys = receipt.get("child_env_keys")
    if not isinstance(env_keys, list):
        bad("child_env_keys is missing or not an array")
    else:
        for k in env_keys:
            if not isinstance(k, str) or not k or "=" in k:
                bad(f"child_env_keys element {k!r} is not a bare "
                    "variable name")
            elif k not in CHILD_ENV_ALLOWLIST:
                bad(f"child_env_keys element {k!r} is outside the "
                    "allowlist PATH/HOME/LANG/LC_ALL/TMPDIR")
        if env_keys != sorted(set(env_keys)):
            bad("child_env_keys is not the producer's sorted unique "
                "list")

    # --- argv consistency -----------------------------------------------------
    argv = receipt.get("argv")
    if not isinstance(argv, list) or not all(
            isinstance(a, str) for a in argv):
        bad("argv is missing or not an array of strings")
    else:
        if argv and argv[0] != server.get("realpath"):
            bad(f"argv[0] {argv[0]!r} != server.realpath "
                f"{server.get('realpath')!r}")
        model_path = model.get("path")
        if isinstance(model_path, str) \
                and argv_flag(argv, "-m") != model_path:
            bad(f"argv -m {argv_flag(argv, '-m')!r} != model.path "
                f"{model_path!r}")
        if alias and argv_flag(argv, "--alias") != alias:
            bad(f"argv --alias {argv_flag(argv, '--alias')!r} != "
                f"receipt alias {alias!r}")
        if argv_flag(argv, "--host") != "127.0.0.1":
            bad(f"argv --host {argv_flag(argv, '--host')!r} != "
                "'127.0.0.1'")
        if isinstance(port, int) and argv_flag(argv, "--port") != str(
                port):
            bad(f"argv --port {argv_flag(argv, '--port')!r} != "
                f"receipt port {port}")
        ctx, threads = receipt.get("ctx"), receipt.get("threads")
        if isinstance(ctx, int) and not isinstance(ctx, bool) \
                and argv_flag(argv, "-c") != str(ctx):
            bad(f"argv -c {argv_flag(argv, '-c')!r} != ctx {ctx!r}")
        if isinstance(threads, int) and not isinstance(threads, bool) \
                and argv_flag(argv, "-t") != str(threads):
            bad(f"argv -t {argv_flag(argv, '-t')!r} != threads "
                f"{threads!r}")
        tail = argv[-2:]
        if tail != ["--no-webui", "--offline"]:
            bad(f"argv tail {tail!r} != ['--no-webui', '--offline']")

    # --- loading lifecycle ----------------------------------------------------
    lo = receipt.get("loading_observed")
    if not isinstance(lo, bool):
        bad(f"loading_observed {lo!r} is not a boolean")
    l503 = receipt.get("loading_503")
    if l503 is not None and not isinstance(l503, dict):
        bad("loading_503 is present but not an object")
    if isinstance(l503, dict):
        if l503.get("status") != 503:
            bad(f"loading_503.status {l503.get('status')!r} != 503")
        if l503.get("path") not in ("/v1/models", "/health"):
            bad(f"loading_503.path {l503.get('path')!r} not in "
                "/v1/models|/health")

    transitions = receipt.get("transitions")
    if not isinstance(transitions, list):
        bad("transitions is missing or not an array")
        transitions = []
    has_503_transition = any(
        isinstance(t, dict) and t.get("status") == 503
        for t in transitions)
    if isinstance(lo, bool):
        if lo != (l503 is not None):
            bad(f"loading_observed {lo} != (loading_503 is not None)")
        if lo != has_503_transition:
            bad(f"loading_observed {lo} but transitions "
                f"{'record' if has_503_transition else 'record no'} "
                "status-503 row")

    # loading_envelope_exact is a receipt FIELD (bool|null), not a check.
    lef = receipt.get("loading_envelope_exact")
    if l503 is None:
        want_lef = None
    elif isinstance(l503, dict):
        want_lef = loading_envelope_ok(parse_body(l503.get("body")))
    else:
        want_lef = False
    if not isinstance(lef, bool) and lef is not None:
        bad(f"loading_envelope_exact {lef!r} is not bool|null")
    elif lef != want_lef:
        bad(f"loading_envelope_exact is {lef!r} but re-derivation from "
            f"the stored loading_503 body gives {want_lef!r}")

    own = receipt.get("port_listener_ownership")
    if own not in ("child", "foreign", "unproven"):
        bad(f"port_listener_ownership {own!r} not in "
            "child|foreign|unproven")
    elif own != "child":
        bad(f"port_listener_ownership is {own!r} — a valid receipt "
            "requires the ready listener proven to be our child")

    pd = receipt.get("pdeathsig")
    if pd is not None and not (isinstance(pd, dict)
                               and pd.get("requested") is True):
        bad(f"pdeathsig {pd!r} is not the producer's "
            "{requested: true, prctl_ok: ...} record")

    # --- captures -------------------------------------------------------------
    captures = receipt.get("captures")
    if not isinstance(captures, dict):
        bad("captures is missing or not an object")
        captures = {}
    for name in ("health", "models", "props", "slots", "metrics"):
        if not isinstance(captures.get(name), dict):
            bad(f"captures.{name} missing or not an object")

    models_doc = parse_body(dig(captures, "models", "body")
                            if dig(captures, "models", "body")
                            is not MISSING else None)
    data = models_doc.get("data") if isinstance(models_doc, dict) \
        else None
    # Producer predicate: e.get('id')/e.get('owned_by') are appended as-is —
    # an entry lacking the key contributes None and fails the all() checks.
    ids, owners = [], []
    if isinstance(data, list):
        ids = [e.get("id") for e in data if isinstance(e, dict)]
        owners = [e.get("owned_by") for e in data
                  if isinstance(e, dict)]

    props_fields = dig(captures, "props", "fields")
    metrics_status = dig(captures, "metrics", "status")
    health_status = dig(captures, "health", "status")

    # --- probes ---------------------------------------------------------------
    probes = receipt.get("probes")
    if not isinstance(probes, list):
        bad("probes is missing or not an array")
        probes = []
    elif len(probes) != 2:
        bad(f"probes holds {len(probes)} records, want exactly 2")
    ok_probe = bad_probe = None
    for rec in probes:
        if not isinstance(rec, dict):
            bad("a probes[] record is not an object")
            continue
        if rec.get("expect") == alias and ok_probe is None:
            ok_probe = rec
        elif rec.get("expect") == MISMATCH_EXPECT and \
                bad_probe is None:
            bad_probe = rec
        elif rec.get("expect") not in (alias, MISMATCH_EXPECT):
            bad(f"probes[] record has unexpected expect "
                f"{rec.get('expect')!r}")
    if ok_probe is None:
        bad(f"no probes[] record with expect == alias {alias!r}")
    if bad_probe is None:
        bad(f"no probes[] record with expect == {MISMATCH_EXPECT!r}")

    probe_info = {}
    for name, rec in (("ok", ok_probe), ("mismatch", bad_probe)):
        if rec is None:
            continue
        pargv = rec.get("argv")
        if not isinstance(pargv, list) \
                or not all(isinstance(a, str) for a in pargv):
            bad(f"probe {name}: argv missing or not a string array")
        else:
            if "check" not in pargv:
                bad(f"probe {name}: argv does not invoke 'check'")
            if isinstance(port, int) \
                    and argv_flag(pargv, "--port") != str(port):
                bad(f"probe {name}: argv --port "
                    f"{argv_flag(pargv, '--port')!r} != served port "
                    f"{port}")
            if argv_flag(pargv, "--expect") != rec.get("expect"):
                bad(f"probe {name}: argv --expect "
                    f"{argv_flag(pargv, '--expect')!r} != record expect "
                    f"{rec.get('expect')!r}")
        ex = rec.get("exit")
        if isinstance(ex, bool) or not isinstance(ex, int):
            bad(f"probe {name}: exit is {ex!r}, want int")

        row = probe_row0(rec)
        res = rec.get("result")
        res = res if isinstance(res, dict) else None
        probe_info[name] = {"rec": rec, "row": row, "res": res}
        if res is None:
            bad(f"probe {name}: result is not a parsed kama-probe "
                "JSON object")
        else:
            if res.get("schema") != PROBE_SCHEMA:
                bad(f"probe {name}: result.schema "
                    f"{res.get('schema')!r} != {PROBE_SCHEMA!r}")
            sexit = dig(res, "summary", "exit")
            if sexit is not MISSING and sexit != ex:
                bad(f"probe {name}: summary.exit {sexit} != recorded "
                    f"exit {ex}")
        if row is MISSING:
            bad(f"probe {name}: no rows[0] verdict row stored")
            continue
        v, rsn = row.get("verdict"), row.get("reason")
        if v == "MODEL_OK":
            if rsn not in ("matched", "expected-wildcard"):
                bad(f"probe {name}: MODEL_OK but reason {rsn!r}")
            if ex != 0:
                bad(f"probe {name}: verdict MODEL_OK but exit {ex} "
                    "(must be 0)")
            if row.get("drift") is not False:
                bad(f"probe {name}: MODEL_OK row has drift "
                    f"{row.get('drift')!r}")
        else:
            if ex != 2:
                bad(f"probe {name}: verdict {v!r} but exit {ex} "
                    "(drift must exit 2)")
            if row.get("drift") is not True:
                bad(f"probe {name}: non-MODEL_OK row has drift "
                    f"{row.get('drift')!r}")
        if v == "MODEL_MISMATCH" and rsn not in (
                "served-id-mismatch", "unresolvable-id"):
            bad(f"probe {name}: MODEL_MISMATCH but reason {rsn!r}")
        if row.get("expected_model_id") is not None \
                and row["expected_model_id"] != rec.get("expect"):
            bad(f"probe {name}: row expected_model_id "
                f"{row.get('expected_model_id')!r} != record expect "
                f"{rec.get('expect')!r}")
        if isinstance(port, int):
            declared = row.get("declared")
            if declared != f"http://127.0.0.1:{port}/v1":
                bad(f"probe {name}: declared endpoint {declared!r} "
                    f"!= http://127.0.0.1:{port}/v1 (must name the "
                    "served port; null/other rejected)")

    # --- teardown -------------------------------------------------------------
    teardown = receipt.get("teardown")
    if not isinstance(teardown, dict) or not teardown:
        bad("teardown evidence is missing or empty")
        teardown = {}
    else:
        rc = teardown.get("returncode")
        if rc is not None and (isinstance(rc, bool)
                               or not isinstance(rc, int)):
            bad(f"teardown.returncode {rc!r} is not int|null")
        pr = teardown.get("port_refuses")
        if pr is not None and not isinstance(pr, bool):
            bad(f"teardown.port_refuses {pr!r} is not bool|null")
        if is_v2:
            for name in ("sigterm_sent", "sigkill_sent",
                         "alive_at_teardown_start"):
                if not isinstance(teardown.get(name), bool):
                    bad(f"teardown.{name} "
                        f"{teardown.get(name)!r} is not a boolean "
                        "(v2 requires it)")

    # --- checks array ---------------------------------------------------------
    checks = receipt.get("checks")
    by_id = {}
    if not isinstance(checks, list):
        bad("checks is missing or not an array")
        checks = []
    for i, c in enumerate(checks):
        if not isinstance(c, dict):
            bad(f"checks[{i}] is not an object")
            continue
        cid = c.get("id")
        if not isinstance(cid, str):
            bad(f"checks[{i}] has no string id")
            continue
        if cid in by_id:
            bad(f"check id {cid!r} appears more than once")
        else:
            by_id[cid] = c
        if not isinstance(c.get("documented_by"), str) \
                or not c["documented_by"]:
            bad(f"check {cid!r}: documented_by missing")
        if not isinstance(c.get("passed"), bool):
            bad(f"check {cid!r}: passed is not a boolean")
        elif c["passed"] is not True:
            bad(f"check {cid!r}: passed is false")
        if not isinstance(c.get("observed"), dict):
            bad(f"check {cid!r}: observed is not an object")
    required = REQUIRED_CHECKS_V2 if is_v2 else REQUIRED_CHECKS_V1
    for cid in required:
        if cid not in by_id:
            bad(f"required check {cid!r} is absent")
    for cid in by_id:
        if cid not in required:
            bad(f"unexpected check id {cid!r} (the schema names "
                f"exactly {len(required)})")

    def claim(cid, want):
        """v2 only: compare the check's claimed passed against the
        value re-derived from stored evidence."""
        c = by_id.get(cid)
        if isinstance(c, dict) and isinstance(c.get("passed"), bool) \
                and c["passed"] != want:
            bad(f"check {cid!r}: claims passed={c['passed']} but "
                f"evidence re-derivation gives {want}")

    def obs(cid):
        o = by_id.get(cid)
        o = o.get("observed") if isinstance(o, dict) else None
        return o if isinstance(o, dict) else {}

    # --- re-derive each check from the raw evidence ----------------------------
    health_body = parse_body(dig(captures, "health", "body")
                             if dig(captures, "health", "body")
                             is not MISSING else None)
    if "health_ready" in by_id:
        if health_status is MISSING:
            bad("health_ready: captures.health.status missing")
        elif health_status != 200:
            bad(f"health_ready: captures.health.status "
                f"{health_status!r} != 200")
        if is_v2:
            # v2: status alone cannot pass — the ready body must be
            # exactly the documented {"status":"ok"} document; a 200
            # {"status":"degraded"} fails.
            if health_body != HEALTH_READY_DOC:
                bad(f"health_ready: captures.health.body "
                    f"{health_body!r} != the documented ready body "
                    f"{HEALTH_READY_DOC!r}")
            claim("health_ready",
                  health_status == 200 and health_body
                  == HEALTH_READY_DOC)
        o = obs("health_ready")
        if "status" in o and o["status"] != health_status:
            bad(f"health_ready: observed.status {o['status']!r} != "
                f"captured status {health_status!r}")

    if "models_alias_id" in by_id:
        if models_doc is None:
            bad("models_alias_id: captures.models.body is not a "
                "parseable JSON object")
        elif not ids:
            bad("models_alias_id: /v1/models data[] has no ids")
        elif not all(i == alias for i in ids):
            bad(f"models_alias_id: served ids {ids} are not all the "
                f"alias {alias!r}")
        o = obs("models_alias_id")
        if "data_ids" in o and o["data_ids"] != ids:
            bad(f"models_alias_id: observed.data_ids "
                f"{o['data_ids']!r} != re-parsed ids {ids}")
        if o.get("expected_alias") is not None \
                and o["expected_alias"] != alias:
            bad(f"models_alias_id: observed.expected_alias "
                f"{o['expected_alias']!r} != alias {alias!r}")
        if is_v2:
            claim("models_alias_id",
                  models_doc is not None and bool(ids)
                  and all(i == alias for i in ids))

    if "models_owned_by_llamacpp" in by_id:
        if models_doc is None:
            bad("models_owned_by_llamacpp: no parseable models body")
        elif not owners:
            bad("models_owned_by_llamacpp: data[] carries no owned_by")
        elif not all(o == "llamacpp" for o in owners):
            bad(f"models_owned_by_llamacpp: owned_by {owners} not all "
                "'llamacpp'")
        o = obs("models_owned_by_llamacpp")
        if "owned_by" in o and o["owned_by"] != owners:
            bad(f"models_owned_by_llamacpp: observed.owned_by "
                f"{o['owned_by']!r} != re-parsed {owners}")
        if is_v2:
            claim("models_owned_by_llamacpp",
                  models_doc is not None and bool(owners)
                  and all(o == "llamacpp" for o in owners))

    if "metrics_not_enabled" in by_id:
        if metrics_status is MISSING:
            bad("metrics_not_enabled: captures.metrics.status missing")
        elif metrics_status != 501:
            bad(f"metrics_not_enabled: /metrics status "
                f"{metrics_status!r} != 501 (llama.cpp without "
                "--metrics answers exactly 501)")
        o = obs("metrics_not_enabled")
        if "status" in o and o["status"] != metrics_status:
            bad(f"metrics_not_enabled: observed.status "
                f"{o['status']!r} != captured {metrics_status!r}")
        if is_v2:
            claim("metrics_not_enabled", metrics_status == 501)

    if "props_alias" in by_id:
        if not isinstance(props_fields, dict):
            bad("props_alias: captures.props.fields missing/not an "
                "object")
        elif props_fields.get("model_alias") != alias:
            bad(f"props_alias: props.fields.model_alias "
                f"{props_fields.get('model_alias')!r} != alias "
                f"{alias!r}")
        o = obs("props_alias")
        of = o.get("fields")
        if isinstance(of, dict) and isinstance(props_fields, dict) \
                and of.get("model_alias") != props_fields.get(
                    "model_alias"):
            bad("props_alias: observed.fields.model_alias disagrees "
                "with captures.props.fields.model_alias")
        if is_v2:
            claim("props_alias",
                  isinstance(props_fields, dict)
                  and props_fields.get("model_alias") == alias)

    if "probe_model_ok" in by_id:
        info = probe_info.get("ok")
        if info is None:
            bad("probe_model_ok: no matching-expect probe record")
        else:
            row = info["row"]
            if row is not MISSING:
                if row.get("verdict") != "MODEL_OK":
                    bad(f"probe_model_ok: stored verdict "
                        f"{row.get('verdict')!r} != MODEL_OK")
                if row.get("reason") != "matched":
                    bad(f"probe_model_ok: stored reason "
                        f"{row.get('reason')!r} != matched")
            if info["rec"].get("exit") != 0:
                bad(f"probe_model_ok: recorded exit "
                    f"{info['rec'].get('exit')!r} != 0")
            o = obs("probe_model_ok")
            for k, want in (("exit", 0), ("verdict", "MODEL_OK"),
                            ("reason", "matched")):
                if k in o and o[k] != want:
                    bad(f"probe_model_ok: observed.{k} {o[k]!r} != "
                        f"{want!r}")
            if is_v2:
                claim("probe_model_ok",
                      isinstance(row, dict)
                      and row.get("verdict") == "MODEL_OK"
                      and row.get("reason") == "matched"
                      and info["rec"].get("exit") == 0)

    if "probe_mismatch" in by_id:
        info = probe_info.get("mismatch")
        if info is None:
            bad("probe_mismatch: no mismatch-expect probe record")
        else:
            row = info["row"]
            if row is not MISSING:
                if row.get("verdict") != "MODEL_MISMATCH":
                    bad(f"probe_mismatch: stored verdict "
                        f"{row.get('verdict')!r} != MODEL_MISMATCH")
                if row.get("reason") != "served-id-mismatch":
                    bad(f"probe_mismatch: stored reason "
                        f"{row.get('reason')!r} != "
                        "served-id-mismatch")
            if info["rec"].get("exit") != 2:
                bad(f"probe_mismatch: recorded exit "
                    f"{info['rec'].get('exit')!r} != 2")
            o = obs("probe_mismatch")
            for k, want in (("exit", 2), ("verdict", "MODEL_MISMATCH"),
                            ("reason", "served-id-mismatch")):
                if k in o and o[k] != want:
                    bad(f"probe_mismatch: observed.{k} {o[k]!r} != "
                        f"{want!r}")
            if is_v2:
                claim("probe_mismatch",
                      isinstance(row, dict)
                      and row.get("verdict") == "MODEL_MISMATCH"
                      and row.get("reason") == "served-id-mismatch"
                      and info["rec"].get("exit") == 2)

    if not is_v2 and "teardown_exited" in by_id:
        if not teardown:
            bad("teardown_exited: no teardown evidence")
        elif teardown.get("returncode") is None:
            bad("teardown_exited: teardown.returncode is null "
                "(process never reaped)")
        o = obs("teardown_exited")
        if "returncode" in o and o["returncode"] != teardown.get(
                "returncode"):
            bad(f"teardown_exited: observed.returncode "
                f"{o['returncode']!r} != teardown.returncode "
                f"{teardown.get('returncode')!r}")

    if is_v2 and "teardown_graceful" in by_id:
        # v2: a bare reaped returncode cannot pass — teardown must be
        # the harness's own graceful SIGTERM on a child proven alive
        # when teardown began, with no SIGKILL escalation and the
        # documented graceful exit status 0 (llama.cpp installs its
        # own SIGINT/SIGTERM handler and exits 0; a signal death like
        # -15 or an error exit fails).
        td_alive = teardown.get("alive_at_teardown_start")
        td_term = teardown.get("sigterm_sent")
        td_kill = teardown.get("sigkill_sent")
        td_rc = teardown.get("returncode")
        if td_alive is not True:
            bad(f"teardown_graceful: teardown.alive_at_teardown_start "
                f"is {td_alive!r}, want true (must prove the child was "
                "alive when teardown began)")
        if td_term is not True:
            bad(f"teardown_graceful: teardown.sigterm_sent is "
                f"{td_term!r}, want true (harness-initiated SIGTERM)")
        if td_kill is not False:
            bad(f"teardown_graceful: teardown.sigkill_sent is "
                f"{td_kill!r}, want false (SIGKILL escalation fails "
                "graceful teardown)")
        if td_rc != 0:
            bad(f"teardown_graceful: teardown.returncode {td_rc!r} "
                "!= 0 (the documented graceful SIGTERM exit status)")
        claim("teardown_graceful",
              td_alive is True and td_term is True
              and td_kill is False and td_rc == 0)
        o = obs("teardown_graceful")
        for k, want in (("returncode", 0), ("sigterm_sent", True),
                        ("sigkill_sent", False),
                        ("alive_at_teardown_start", True)):
            if k in o and o[k] != want:
                bad(f"teardown_graceful: observed.{k} {o[k]!r} != "
                    f"{want!r}")

    if "teardown_port_closed" in by_id:
        if not teardown:
            bad("teardown_port_closed: no teardown evidence")
        elif teardown.get("port_refuses") is not True:
            bad(f"teardown_port_closed: teardown.port_refuses is "
                f"{teardown.get('port_refuses')!r}, want true")
        if is_v2:
            # v2: port_refuses is only meaningful after the ready
            # listener was proven to be our own child — a refused port
            # we never owned is vacuous evidence of teardown.
            if own != "child":
                bad(f"teardown_port_closed: "
                    f"port_listener_ownership is {own!r}; "
                    "port_refuses is vacuous without recorded child "
                    "ownership")
            claim("teardown_port_closed",
                  own == "child"
                  and teardown.get("port_refuses") is True)
        o = obs("teardown_port_closed")
        if "port_refuses" in o and o["port_refuses"] != teardown.get(
                "port_refuses"):
            bad(f"teardown_port_closed: observed.port_refuses "
                f"{o['port_refuses']!r} != teardown.port_refuses "
                f"{teardown.get('port_refuses')!r}")

    if is_v2 and "loading_envelope_graded" in by_id:
        # v2: the loading envelope is a CHECK, not only a recorded
        # field — its claimed passed must equal the envelope value
        # re-derived from the stored loading_503 body, and a run with
        # nothing to grade cannot pass it.
        if want_lef is None:
            bad("loading_envelope_graded: no loading_503 body stored, "
                "nothing graded")
        elif want_lef is not True:
            bad(f"loading_envelope_graded: stored loading_503 body "
                "re-derives to a non-exact envelope "
                f"(loading_envelope_exact {want_lef!r})")
        # Every distinct stored 503 body must be the exact envelope, not
        # only the first (loading_503); a later malformed body fails.
        bodies = receipt.get("loading_503_bodies")
        if not isinstance(bodies, list) or not bodies:
            bad("loading_envelope_graded: loading_503_bodies missing or "
                "empty in a v2 receipt")
            all_exact = False
        else:
            all_exact = all(
                isinstance(b, dict)
                and loading_envelope_ok(parse_body(b.get("body"))) is True
                for b in bodies)
            if not all_exact:
                bad("loading_envelope_graded: a stored loading_503_bodies "
                    "entry is not the exact envelope")
        claim("loading_envelope_graded", want_lef is True and all_exact)
        o = obs("loading_envelope_graded")
        if "exact" in o and o["exact"] != want_lef:
            bad(f"loading_envelope_graded: observed.exact "
                f"{o['exact']!r} != re-derived loading_envelope_exact "
                f"{want_lef!r}")

    if "model_unchanged" in by_id:
        if is_hex64(model_sha) and is_hex64(model_post):
            if model_sha != model_post:
                bad("model_unchanged: model.sha256 != "
                    "model_sha256_post (the run mutated its input "
                    "model)")
        else:
            bad("model_unchanged: cannot compare — model.sha256 or "
                "model_sha256_post not a 64-hex digest")
        o = obs("model_unchanged")
        if is_hex64(o.get("pre")) and is_hex64(model_sha) \
                and o["pre"] != model_sha:
            bad("model_unchanged: observed.pre != model.sha256")
        if is_hex64(o.get("post")) and is_hex64(model_post) \
                and o["post"] != model_post:
            bad("model_unchanged: observed.post != model_sha256_post")
        if is_v2:
            claim("model_unchanged",
                  is_hex64(model_sha) and is_hex64(model_post)
                  and model_sha == model_post)

    return problems


# ----------------------------------------------------------------- selftest

ALIAS = "kama-live-probe"
PORT = 45678
MODEL_SHA = "a" * 64
SERVER_SHA = "b" * 64
PROBE_SHA = "c" * 64
IMPL_SHA = "d" * 64
TOOL_SHA = "9" * 64
LIB_SHA = "f" * 64


ENVELOPE_BODY = json.dumps({"error": {"message": "Loading model",
                                      "type": "unavailable_error",
                                      "code": 503}},
                           separators=(",", ":"))
MODELS_BODY = json.dumps({
    "object": "list",
    "data": [{"id": ALIAS, "object": "model", "created": 0,
              "owned_by": "llamacpp"}],
}, separators=(",", ":"))


def _probe_rec(expect, verdict, reason, exit_code, drift):
    return {
        "expect": expect,
        "argv": ["bash", "/lane/tools/kama-probe.sh", "check",
                 "--port", str(PORT), "--expect", expect, "--json"],
        "exit": exit_code,
        "result": {
            "schema": PROBE_SCHEMA,
            "subcommand": "check",
            "summary": {"registry_rows_evaluated": 1,
                        "model_ok": 1 if exit_code == 0 else 0,
                        "drift": 0 if exit_code == 0 else 1,
                        "exit": exit_code},
            "rows": [{
                "id": "cli-override",
                "consumer_path": "-",
                "declared": f"http://127.0.0.1:{PORT}/v1",
                "file_match": "cli-override",
                "resolver_kind": "cli-override",
                "expected_model_id": expect,
                "verdict": verdict,
                "reason": reason,
                "served_model": ALIAS,
                "drift": drift,
                "evidence": "GET /v1/models -> 200",
                "notes": "",
            }],
        },
        "stderr_tail": None,
    }


def _selftest_receipt():
    """One valid receipt literal in the producer's exact shape."""
    return {
        "schema": RECEIPT_SCHEMA,
        "started_utc": "2026-10-20T13:00:00.000Z",
        "ended_utc": "2026-10-20T13:00:12.500Z",
        "server": {"arg": "llama-server",
                   "realpath": "/home/x/.local/opt/llama-b11755/bin/"
                               "llama-server",
                   "sha256": SERVER_SHA,
                   "install_tree": {"llama-server": SERVER_SHA,
                                    "libllama-server-impl.so": IMPL_SHA,
                                    "libllama.so": LIB_SHA},
                   "install_tree_sha256": install_tree_sha(
                       {"llama-server": SERVER_SHA,
                        "libllama-server-impl.so": IMPL_SHA,
                        "libllama.so": LIB_SHA}),
                   "server_impl_sha256": IMPL_SHA},
        "model": {"path": "/home/x/.cache/kama-shokunin/models/"
                          "stories260K.gguf",
                  "sha256": MODEL_SHA},
        "model_sha256_post": MODEL_SHA,
        "probe": {"path": "/lane/tools/kama-probe.sh",
                  "sha256": PROBE_SHA},
        "tool": {"path": "/lane/tools/kama-llamacpp-live.py",
                 "sha256": TOOL_SHA},
        "argv": ["/home/x/.local/opt/llama-b11755/bin/llama-server",
                 "-m", "/home/x/.cache/kama-shokunin/models/"
                      "stories260K.gguf",
                 "--alias", ALIAS, "--host", "127.0.0.1",
                 "--port", str(PORT), "-c", "256", "-t", "1",
                 "--no-webui", "--offline"],

        "alias": ALIAS,
        "ctx": 256,
        "threads": 1,
        "port": PORT,
        "port_refusal_set": [8080, 34113],
        "child_env_keys": ["HOME", "LC_ALL", "PATH", "TMPDIR"],
        "transitions": [
            {"t_ms": 4, "path": "/health", "status": None,
             "error": "ConnectionRefusedError",
             "body_sha256": "0" * 64, "body": "",
             "body_over_cap": False, "headers": {}, "repeats": 3},
            {"t_ms": 40, "path": "/v1/models", "status": 503,
             "error": None, "body_sha256": "1" * 64,
             "body": ENVELOPE_BODY, "body_over_cap": False,
             "headers": {"server": "llama.cpp",
                         "content-type": "application/json"},
             "repeats": 12},
            {"t_ms": 900, "path": "/health", "status": 200,
             "error": None, "body_sha256": "2" * 64,
             "body": '{"status":"ok"}', "body_over_cap": False,
             "headers": {"server": "llama.cpp",
                         "content-type": "application/json"},
             "repeats": 0},
        ],
        "loading_503": {"t_ms": 40, "path": "/v1/models", "status": 503,
                        "headers": {"server": "llama.cpp",
                                    "content-type":
                                    "application/json"},
                        "body_sha256": "1" * 64,
                        "body": ENVELOPE_BODY},
        "loading_observed": True,
        "loading_envelope_exact": True,
        "port_listener_ownership": "child",
        "pdeathsig": {"requested": True, "prctl_ok": True},

        "captures": {
            "health": {"path": "/health", "status": 200, "error": None,
                       "headers": {"Content-Type": "application/json"},
                       "body_sha256": "2" * 64,
                       "body": '{"status":"ok"}',
                       "body_truncated": False},
            "models": {"path": "/v1/models", "status": 200,
                       "error": None,
                       "headers": {"Content-Type": "application/json"},
                       "body_sha256": "3" * 64,
                       "body": MODELS_BODY,
                       "body_truncated": False},
            "props": {"path": "/props", "status": 200, "error": None,
                      "headers": {}, "body_sha256": "4" * 64,
                      "fields": {"model_alias": ALIAS,
                                 "total_slots": 1,
                                 "is_sleeping": False,
                                 "build_info": "b11755-704366d",
                                 "default_generation_settings.n_ctx":
                                 256}},
            "slots": {"path": "/slots", "status": 200, "error": None,
                      "headers": {}, "body_sha256": "5" * 64,
                      "element_count": 1},
            "metrics": {"path": "/metrics", "status": 501,
                        "error": None},
        },
        "probes": [
            _probe_rec(ALIAS, "MODEL_OK", "matched", 0, False),
            _probe_rec(MISMATCH_EXPECT, "MODEL_MISMATCH",
                       "served-id-mismatch", 2, True),
        ],
        "teardown": {"returncode": -15, "sigterm_sent": True,
                     "sigkill_sent": False, "term_wait_ms": 320,
                     "port_refuses": True,
                     "log_lines": ["llama.cpp build b11755",
                                   "model loaded",
                                   "listening on 127.0.0.1:45678"],
                     "log_lines_truncated": False,
                     "log_path": "/tmp/kama-llamacpp-live-x.log"},
        "checks": [
            {"id": "health_ready", "documented_by": "d",
             "passed": True, "observed": {"status": 200}},
            {"id": "models_alias_id", "documented_by": "d",
             "passed": True,
             "observed": {"data_ids": [ALIAS],
                          "expected_alias": ALIAS}},
            {"id": "models_owned_by_llamacpp", "documented_by": "d",
             "passed": True, "observed": {"owned_by": ["llamacpp"]}},
            {"id": "metrics_not_enabled", "documented_by": "d",
             "passed": True, "observed": {"status": 501}},
            {"id": "props_alias", "documented_by": "d",
             "passed": True,
             "observed": {"fields": {"model_alias": ALIAS}}},
            {"id": "probe_model_ok", "documented_by": "d",
             "passed": True,
             "observed": {"exit": 0, "verdict": "MODEL_OK",
                          "reason": "matched"}},
            {"id": "probe_mismatch", "documented_by": "d",
             "passed": True,
             "observed": {"exit": 2, "verdict": "MODEL_MISMATCH",
                          "reason": "served-id-mismatch"}},
            {"id": "teardown_exited", "documented_by": "d",
             "passed": True,
             "observed": {"returncode": -15, "sigkill_sent": False}},
            {"id": "teardown_port_closed", "documented_by": "d",
             "passed": True, "observed": {"port_refuses": True}},
            {"id": "model_unchanged", "documented_by": "d",
             "passed": True,
             "observed": {"pre": MODEL_SHA, "post": MODEL_SHA}},
        ],
        "setup_error": None,
        "port_pick_note": "port released after bind(:0) and re-bound "
                          "by the server",
    }


def _selftest_receipt_v2():
    """One valid v2 receipt: the v1 literal upgraded — graceful
    SIGTERM teardown (returncode 0, child alive at teardown start) and
    the v2 check id set (teardown_graceful replaces teardown_exited,
    loading_envelope_graded added)."""
    r = copy.deepcopy(_selftest_receipt())
    r["schema"] = RECEIPT_SCHEMA_V2
    r["teardown"].update(returncode=0, alive_at_teardown_start=True)
    r["loading_503_bodies"] = [
        {"body": r["loading_503"]["body"], "repeats": 0}]
    checks = []
    for c in r["checks"]:
        if c["id"] == "teardown_exited":
            c = {"id": "teardown_graceful", "documented_by": "d",
                 "passed": True,
                 "observed": {"alive_at_teardown_start": True,
                              "sigterm_sent": True,
                              "sigkill_sent": False,
                              "returncode": 0}}
        if c["id"] == "model_unchanged":
            checks.append({"id": "loading_envelope_graded",
                           "documented_by": "d", "passed": True,
                           "observed": {"exact": True}})
        checks.append(c)
    r["checks"] = checks
    return r

def _selftest():
    base = _selftest_receipt()
    expects = ["--expect-model-sha256", MODEL_SHA,
               "--expect-server-sha256", SERVER_SHA,
               "--expect-probe-sha256", PROBE_SHA,
               "--expect-tool-sha256", TOOL_SHA]
    cases = [("valid", base, expects, 0)]


    def mut(name, fn, extra=None):
        r = copy.deepcopy(base)
        fn(r)
        cases.append((name, r, extra or [], 1))

    mut("schema-id-changed",
        lambda r: r.update(schema="kama-llamacpp-live/v0"))
    mut("missing-check-model-unchanged",
        lambda r: r["checks"].remove(
            next(c for c in r["checks"]
                 if c["id"] == "model_unchanged")))
    mut("duplicated-check-id",
        lambda r: r["checks"].append(copy.deepcopy(r["checks"][0])))
    mut("port-34113", lambda r: r.update(port=34113))
    mut("port-inside-refusal-set",
        lambda r: r["port_refusal_set"].append(r["port"]))
    mut("wrong-digest-vs-expect",
        lambda r: r["model"].update(sha256="0" * 64),
        extra=["--expect-model-sha256", MODEL_SHA])
    mut("model-changed-post-digest",
        lambda r: r.update(model_sha256_post="0" * 64))
    mut("missing-teardown", lambda r: r.update(teardown=None))
    mut("model-ok-claimed-exit-2",
        lambda r: (r["probes"][0].update(exit=2),
                   r["probes"][0]["result"]["summary"].update(exit=2)))
    mut("passed-flipped-against-stored-probe",
        lambda r: r["probes"][1]["result"]["rows"][0].update(
            verdict="MODEL_OK", reason="matched", drift=False))
    mut("metrics-200-not-501",
        lambda r: (r["captures"]["metrics"].update(status=200),
                   next(c for c in r["checks"]
                        if c["id"] == "metrics_not_enabled")
                   ["observed"].update(status=200)))
    mut("ended-before-started",
        lambda r: r.update(ended_utc="2026-10-20T12:59:00.000Z"))
    mut("mismatch-probe-expects-alias",
        lambda r: r["probes"][1].update(expect=ALIAS))
    mut("envelope-flag-inconsistent",
        lambda r: r.update(loading_envelope_exact=False))
    mut("env-key-off-allowlist",
        lambda r: r["child_env_keys"].append("AWS_SECRET"))
    mut("argv-missing-offline",
        lambda r: r["argv"].remove("--offline"))
    # falsify-wave survivors: one new rule each
    mut("ownership-unproven",
        lambda r: r.update(port_listener_ownership="unproven"))
    mut("argv0-not-realpath",
        lambda r: r["argv"].__setitem__(0, "/usr/bin/false"))
    mut("argv-wrong-host",
        lambda r: r["argv"].__setitem__(
            r["argv"].index("127.0.0.1"), "0.0.0.0"))
    mut("probe-argv-missing-check",
        lambda r: r["probes"][0]["argv"].remove("check"))
    mut("probe-declared-null",
        lambda r: r["probes"][0]["result"]["rows"][0].update(
            declared=None))
    mut("loading-observed-without-503-transition",
        lambda r: r["transitions"][1].update(status=404))
    mut("loading-503-wrong-path",
        lambda r: r["loading_503"].update(path="/metrics"))
    mut("install-tree-sha-tampered",
        lambda r: r["server"].update(install_tree_sha256="0" * 64))
    mut("models-entry-missing-id",
        lambda r: r["captures"]["models"].update(body=json.dumps(
            {"data": [{"id": ALIAS, "owned_by": "llamacpp"},
                      {"owned_by": "llamacpp"}]})))
    mut("tool-sha-mismatch-expect",
        lambda r: r["tool"].update(sha256="7" * 64),
        extra=["--expect-tool-sha256", TOOL_SHA])

    # ---- v2: valid receipt + fail-capable check mutations ------------------
    base_v2 = _selftest_receipt_v2()
    cases.append(("v2-valid", base_v2, expects, 0))

    def mut2(name, fn, extra=None):
        r = copy.deepcopy(base_v2)
        fn(r)
        cases.append((name, r, extra or [], 1))

    mut2("v2-health-degraded-body",
         lambda r: r["captures"]["health"].update(
             body='{"status":"degraded"}'))
    mut2("v2-sigkill-sent",
         lambda r: r["teardown"].update(sigkill_sent=True))
    mut2("v2-returncode-minus15-sigterm-death",
         lambda r: r["teardown"].update(returncode=-15))
    mut2("v2-returncode-1-error-exit",
         lambda r: r["teardown"].update(returncode=1))
    mut2("v2-sigterm-not-sent-clean-rc",
         lambda r: r["teardown"].update(sigterm_sent=False))
    mut2("v2-ownership-unproven-port-refuses",
         lambda r: r.update(port_listener_ownership="unproven"))
    mut2("v2-loading-exact-false-check-claims-pass",
         lambda r: (r["loading_503"].update(body='{"error":{}}'),
                    r["transitions"][1].update(body='{"error":{}}'),
                    r.update(loading_envelope_exact=False)))
    mut2("v2-loading-503-nonexact-transitions",
         lambda r: (r["transitions"][1].update(
             body='{"error":{"message":"Warming","type":"x","code":503}}'),
            r["loading_503"].update(
                body='{"error":{"message":"Warming","type":"x",'
                     '"code":503}}'),
            r.update(loading_envelope_exact=False)))
    mut2("v2-missing-loading-envelope-graded",
         lambda r: r["checks"].remove(
             next(c for c in r["checks"]
                  if c["id"] == "loading_envelope_graded")))
    mut2("v2-v1-check-id-teardown-exited",
         lambda r: next(c for c in r["checks"]
                        if c["id"] == "teardown_graceful").update(
             id="teardown_exited"))
    mut2("v2-child-not-alive-at-teardown",
         lambda r: r["teardown"].update(alive_at_teardown_start=False))
    mut2("v2-health-body-extra-key",
         lambda r: r["captures"]["health"].update(
             body='{"status":"ok","extra":1}'))
    mut2("v2-later-loading-body-nonexact",
         lambda r: r["loading_503_bodies"].append(
             {"body": '{"error":{"message":"Busy",'
                      '"type":"unavailable_error","code":"503"}}',
              "repeats": 2}))

    failures = []
    with tempfile.TemporaryDirectory(prefix="check-receipt-") as td:
        for i, (name, receipt, extra, want) in enumerate(cases):
            path = os.path.join(td, f"case-{i}-{name}.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(receipt, fh)
            proc = subprocess.run(
                [sys.executable, os.path.abspath(__file__), path,
                 *extra],
                capture_output=True, text=True)
            if proc.returncode != want:
                failures.append(
                    f"{name}: exit {proc.returncode}, want {want}; "
                    f"stdout={proc.stdout.strip()[:400]!r}")
    proc = subprocess.run(
        [sys.executable, os.path.abspath(__file__),
         "/nonexistent/receipt.json"],
        capture_output=True, text=True)
    if proc.returncode != 2:
        failures.append(f"unreadable receipt: exit "
                        f"{proc.returncode}, want 2")
    if failures:
        for f in failures:
            print(f"SELFTEST FAIL {f}", file=sys.stderr)
        return 1
    n_mut = sum(1 for c in cases if c[3] != 0)
    n_ok = len(cases) - n_mut
    print(f"selftest: {n_ok} valid receipt(s) accepted; {n_mut} "
          "mutations + unreadable case all rejected")
    return 0


# --------------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Validate a kama-llamacpp-live/v1 or /v2 receipt.")
    ap.add_argument("receipt", nargs="?", help="receipt JSON path")
    ap.add_argument("--expect-model-sha256", metavar="HEX",
                    help="require the recorded model sha256")
    ap.add_argument("--expect-server-sha256", metavar="HEX",
                    help="require the recorded server sha256")
    ap.add_argument("--expect-probe-sha256", metavar="HEX",
                    help="require the recorded probe sha256")
    ap.add_argument("--expect-tool-sha256", metavar="HEX",
                    help="require the recorded harness-tool sha256")

    ap.add_argument("--selftest", action="store_true",
                    help="run built-in valid/mutation matrix and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not args.receipt:
        ap.error("RECEIPT path required (or --selftest)")

    try:
        with open(args.receipt, "r", encoding="utf-8") as fh:
            receipt = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"check-receipt: cannot read {args.receipt}: {exc}",
              file=sys.stderr)
        return 2

    problems = validate(receipt,
                        expect_model=args.expect_model_sha256,
                        expect_server=args.expect_server_sha256,
                        expect_probe=args.expect_probe_sha256,
                        expect_tool=args.expect_tool_sha256)
    if problems:
        print(f"INVALID {args.receipt}: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"VALID {args.receipt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
