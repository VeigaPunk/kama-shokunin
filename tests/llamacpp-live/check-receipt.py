#!/usr/bin/env python3
"""Independent validator for kama-llamacpp-live/v1, /v2 and /v3 receipts.

Bound to the exact receipt keys emitted by ``tools/kama-llamacpp-live.py``.
The gate re-derives checks from stored response, probe, and teardown
evidence; it never trusts a claimed check result by itself. v1 and v2
retain their existing verdict behavior. v3 adds a tri-state check contract,
an outcome field, exact launch argv binding, and pinned source-binding
validation. It never fetches upstream source: file digests are checked
against the pinned identities and span hashes are re-derived from text.

v1 checks: health_ready, models_alias_id, models_owned_by_llamacpp,
metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch,
teardown_exited, teardown_port_closed, model_unchanged.

v2 and v3 checks: health_ready (status 200 and exact {"status":"ok"}
body), models_alias_id, models_owned_by_llamacpp, metrics_not_enabled,
props_alias, probe_model_ok, probe_mismatch, teardown_graceful,
teardown_port_closed (only after child ownership), loading_envelope_graded,
model_unchanged. In v3 only loading_envelope_graded may be unevaluated,
and only when no /v1/models 503 was observed.

Usage:
  check-receipt.py RECEIPT [--expect-model-sha256 HEX]
                           [--expect-server-sha256 HEX]
                           [--expect-server-impl-sha256 HEX]
                           [--expect-install-tree-sha256 HEX]
                           [--expect-probe-sha256 HEX]
                           [--expect-tool-sha256 HEX]
                           [--require-schema v1|v2|v3]
  check-receipt.py --selftest

Exit: 0 VALID, 1 INVALID, 2 unreadable / not JSON,
      3 NOT-EVALUATED (otherwise valid v3 with its sole permitted null).
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
RECEIPT_SCHEMA_V3 = "kama-llamacpp-live/v3"
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

LLAMA_COMMIT = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
LLAMA_RAW = (
    "https://raw.githubusercontent.com/ggml-org/llama.cpp/"
    f"{LLAMA_COMMIT}/")
# Pinned source identities emitted by source_bindings() in the harness.
# The receipt's source text is hash-checked against these spans, while the
# whole-file digests are checked against this pinned map; the gate does not
# fetch or independently authenticate upstream file bytes.
SOURCE_BINDING_EXPECTED = (
    ("health_ready", None, "tools/server/server-context.cpp",
     (5288, 5299),
     "dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329",
     "2ff50edd63f4b7a37ccfcd21210c29f781f777f010eb6e2963ed8585ad3447dd"),
    ("loading_envelope_graded", "S036",
     "tools/server/server-http.cpp", (314, 325),
     "24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb",
     "4c5aac23af4cacc39abc525dceeed59f8e95e8584771e6e1a84a752c719da775"),
    ("teardown_graceful", None, "tools/server/server.cpp", (529, 534),
     "2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4",
     "f14a9b67bce667741f028a3fb33239b96281c21de0688a14e3a66da251b1e163"),
    ("teardown_graceful", None, "tools/server/server.cpp", (519, 523),
     "2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4",
     "97408c516bf5c805b12ca6fa407956473489277ec626b41511e3abe6e2510a70"),
    ("teardown_graceful", None, "tools/server/server.cpp", (575, 590),
     "2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4",
     "d0f09fae6947f25b42ccf00ef09231c9e8f9bf46b5499d9e1f070a58d8ad163d"),
)


def validate_source_binding(problems, bindings, check_ids):
    """Re-derive each pinned source span and reject changed identities."""
    if not isinstance(bindings, list):
        problems.append("source_binding is missing or not an array")
        return
    if len(bindings) != len(SOURCE_BINDING_EXPECTED):
        problems.append(
            f"source_binding has {len(bindings)} entries, want exactly "
            f"{len(SOURCE_BINDING_EXPECTED)} pinned spans")
    for i, spec in enumerate(SOURCE_BINDING_EXPECTED):
        if i >= len(bindings):
            break
        binding = bindings[i]
        if not isinstance(binding, dict):
            problems.append(f"source_binding[{i}] is not an object")
            continue
        check, row, path, lines, file_sha, span_sha = spec
        expected = {
            "check": check,
            "row": row,
            "commit": LLAMA_COMMIT,
            "path": path,
            "url": LLAMA_RAW + path,
            "lines": list(lines),
            "file_sha256": file_sha,
            "span_sha256": span_sha,
        }
        for key, value in expected.items():
            if binding.get(key) != value:
                problems.append(
                    f"source_binding[{i}].{key} "
                    f"{binding.get(key)!r} != pinned {value!r}")
        if check not in check_ids:
            problems.append(
                f"source_binding[{i}] names absent check {check!r}")
        text = binding.get("span_text")
        if not isinstance(text, str):
            problems.append(f"source_binding[{i}].span_text is not a string")
        elif hashlib.sha256(text.encode("utf-8")).hexdigest() != span_sha:
            problems.append(
                f"source_binding[{i}].span_text does not match the "
                "pinned span_sha256")
        elif len(text.splitlines(keepends=True)) != lines[1] - lines[0] + 1:
            problems.append(
                f"source_binding[{i}].span_text line count does not match "
                "its pinned lines")

MISSING = object()


def install_tree_sha(tree):
    """Recompute producer install_tree_sha256(): sha256 over the sorted
    'name sha\\n' lines."""
    return hashlib.sha256(
        ''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()
    ).hexdigest()


def install_links_sha(links):
    """Recompute producer install_links_sha256(): sha256 over the sorted
    'name -> link text\\n' lines."""
    return hashlib.sha256(
        ''.join(f'{n} -> {links[n]}\n' for n in sorted(links)).encode()
    ).hexdigest()


def link_chain_problem(name, links, tree):
    """None when the symlink chain from `name` ends at a pinned regular
    member of install_tree; otherwise a reason. Only same-directory
    basenames are followed: any other target escapes the pinned tree."""
    seen = set()
    current = name
    while current in links:
        if current in seen:
            return "symlink loop"
        seen.add(current)
        target = links[current]
        if not isinstance(target, str) or not target or "/" in target \
                or target in (".", ".."):
            return f"target {target!r} leaves the pinned directory"
        current = target
    if current not in tree:
        return f"chain ends at {current!r}, not a pinned install_tree member"
    return None


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
             expect_probe=None, expect_tool=None,
             expect_server_impl=None, expect_tree=None, expect_links=None):

    problems = []

    def bad(msg):
        problems.append(msg)

    if not isinstance(receipt, dict):
        return ["receipt is not a JSON object"]

    # --- schema / run outcome ---------------------------------------------
    schema = receipt.get("schema")
    is_v3 = schema == RECEIPT_SCHEMA_V3
    is_v2 = schema in (RECEIPT_SCHEMA_V2, RECEIPT_SCHEMA_V3)
    if schema not in (RECEIPT_SCHEMA, RECEIPT_SCHEMA_V2,
                      RECEIPT_SCHEMA_V3):
        bad(f"schema is {schema!r}, want {RECEIPT_SCHEMA!r}, "
            f"{RECEIPT_SCHEMA_V2!r} or {RECEIPT_SCHEMA_V3!r}")
    setup_error = receipt.get("setup_error")
    if setup_error is not None:
        bad(f"setup_error is {setup_error!r} "
            "(a complete run has setup_error null)")
    internal_fault = receipt.get("internal_fault")
    if is_v3:
        if internal_fault is not None and not isinstance(
                internal_fault, str):
            bad(f"internal_fault {internal_fault!r} is not string|null")
        if internal_fault is not None and setup_error != internal_fault:
            bad(f"internal_fault {internal_fault!r} != setup_error "
                f"{setup_error!r}")

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
    elif not tree:
        # An empty map plus a copied digest would defeat every tree pin.
        bad("server.install_tree is empty")
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
    if expect_tree is not None:
        if not is_hex64(tree_sha):
            bad("--expect-install-tree-sha256 given but receipt has no "
                "server.install_tree_sha256 digest")
        elif tree_sha != expect_tree:
            bad(f"server.install_tree_sha256 {tree_sha} != expected "
                f"{expect_tree}")
    # server_impl_sha256 is null when the release has no impl .so.
    check_digest(problems, "server.server_impl_sha256",
                 server.get("server_impl_sha256"), allow_none=True)
    impl_sha = server.get("server_impl_sha256")
    if is_hex64(impl_sha) and isinstance(tree, dict) \
            and "libllama-server-impl.so" in tree \
            and tree["libllama-server-impl.so"] != impl_sha:
        bad("server.server_impl_sha256 != "
            "install_tree['libllama-server-impl.so']")
    if expect_server_impl is not None:
        # The launcher is a loader stub; this pin binds the bytes of the
        # recorded implementation library. Other tree members (common/rpc
        # libraries) remain unpinned unless the caller hashes them too.
        if not is_hex64(impl_sha):
            bad("--expect-server-impl-sha256 given but receipt has no "
                "server.server_impl_sha256 digest")
        elif impl_sha != expect_server_impl:
            bad(f"server.server_impl_sha256 {impl_sha} != expected "
                f"{expect_server_impl}")
    # install_links: optional (receipts before round 21 lack it). When
    # present, every soname symlink must be recorded, digested and resolve
    # inside the pinned regular-file tree.
    links = server.get("install_links", MISSING)
    links_sha = server.get("install_links_sha256")
    if links is not MISSING:
        if not isinstance(links, dict) or not all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in links.items()):
            bad("server.install_links is not an object of basename -> "
                "link text")
        else:
            check_digest(problems, "server.install_links_sha256", links_sha,
                         allow_none=not links)
            if is_hex64(links_sha) and install_links_sha(links) != links_sha:
                bad("server.install_links_sha256 != recomputation over "
                    "install_links")
            for name in sorted(links):
                if isinstance(tree, dict) and name in tree:
                    bad(f"server.install_links[{name!r}] is also a regular "
                        "install_tree member")
                    continue
                why = link_chain_problem(name, links,
                                         tree if isinstance(tree, dict)
                                         else {})
                if why:
                    bad(f"server.install_links[{name!r}]: {why}")
    if expect_links is not None:
        if not is_hex64(expect_links):
            bad(f"--expect-install-links-sha256 {expect_links!r} is not 64 "
                "lowercase hex chars")
        elif links is MISSING or not is_hex64(links_sha):
            bad("--expect-install-links-sha256 given but receipt has no "
                "server.install_links_sha256 digest")
        elif links_sha != expect_links:
            bad(f"server.install_links_sha256 {links_sha} != expected "
                f"{expect_links}")


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
                      ("probe", expect_probe),
                      ("server-impl", expect_server_impl),
                      ("install-tree", expect_tree)):
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
                # Never interpolate the element: a receipt carrying
                # NAME=<value> must not leak that value into diagnostics.
                bad("child_env_keys element is not a bare variable name")
            elif k not in CHILD_ENV_ALLOWLIST:
                bad("child_env_keys element is outside the "
                    "allowlist PATH/HOME/LANG/LC_ALL/TMPDIR")
        if all(isinstance(k, str) for k in env_keys) \
                and env_keys != sorted(set(env_keys)):
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
        model_path = model.get("arg") if is_v3 else model.get("path")
        if is_v3 and (not isinstance(model_path, str) or not model_path):
            bad(f"model.arg {model_path!r} missing or not a non-empty string")
        if isinstance(model_path, str) \
                and argv_flag(argv, "-m") != model_path:
            bad(f"argv -m {argv_flag(argv, '-m')!r} != model "
                f"{'arg' if is_v3 else 'path'} {model_path!r}")
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
        if is_v3 and isinstance(model_path, str) \
                and isinstance(server.get("realpath"), str) \
                and isinstance(alias, str) \
                and isinstance(port, int) and not isinstance(port, bool) \
                and isinstance(ctx, int) and not isinstance(ctx, bool) \
                and isinstance(threads, int) and not isinstance(
                    threads, bool):
            expected_argv = [
                server["realpath"], "-m", model_path,
                "--alias", alias, "--host", "127.0.0.1",
                "--port", str(port), "-c", str(ctx), "-t", str(threads),
                "--no-webui", "--offline",
            ]
            if argv != expected_argv:
                bad("argv does not exactly match the producer's "
                    "server.realpath/model.arg/alias/host/port/ctx/"
                    "threads command")

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
        if l503.get("path") not in (
                ("/v1/models",) if is_v3 else
                ("/v1/models", "/health")):
            bad(f"loading_503.path {l503.get('path')!r} not in "
                f"{'/v1/models' if is_v3 else '/v1/models|/health'}")

    transitions = receipt.get("transitions")
    if not isinstance(transitions, list):
        bad("transitions is missing or not an array")
        transitions = []
    if is_v3:
        # Derive the null license only from producer-shaped observations.
        # Alternate paths or string/float status encodings must not hide a 503.
        for i, row in enumerate(transitions):
            if not isinstance(row, dict):
                bad(f"transitions[{i}] is not an object")
                continue
            if row.get("path") not in ("/v1/models", "/health"):
                bad(f"transitions[{i}].path is not a producer route")
            status = row.get("status", MISSING)
            if status is not None and (
                    type(status) is not int or not 100 <= status <= 599):
                bad(f"transitions[{i}].status is not null or an HTTP integer")
    has_503_transition = any(
        isinstance(t, dict) and t.get("status") == 503
        for t in transitions)
    model_503_rows = [
        t for t in transitions
        if isinstance(t, dict) and t.get("path") == "/v1/models"
        and t.get("status") == 503
    ]
    # Any producer route can record a loading envelope (the producer polls
    # /health too); the null license may not ignore a /health 503 envelope.
    envelope_503_rows = [
        t for t in transitions
        if isinstance(t, dict) and t.get("status") == 503
        and isinstance(t.get("body"), str)
        and loading_envelope_ok(parse_body(t.get("body")))
    ]
    if isinstance(lo, bool):
        if lo != (l503 is not None):
            bad(f"loading_observed {lo} != (loading_503 is not None)")
        if is_v3:
            if lo != bool(model_503_rows):
                bad(f"loading_observed {lo} != whether transitions "
                    "contain a /v1/models 503")
            if lo is False and envelope_503_rows:
                bad(f"loading_observed false but transitions record "
                    f"{len(envelope_503_rows)} status-503 loading "
                    "envelope row(s) on "
                    f"{sorted({r.get('path') for r in envelope_503_rows})}")
        elif lo != has_503_transition:
            bad(f"loading_observed {lo} but transitions "
                f"{'record' if has_503_transition else 'record no'} "
                "status-503 row")

    if is_v3:
        for i, row in enumerate(model_503_rows):
            body = row.get("body")
            if not isinstance(body, str) or not loading_envelope_ok(
                    parse_body(body)):
                bad(f"transitions /v1/models 503 row {i} does not carry "
                    "the exact loading envelope")
            if row.get("body_read_truncated") is True \
                    or row.get("body_over_cap") is True:
                bad(f"transitions /v1/models 503 row {i} is truncated")

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

    if is_v3:
        for name in ("health", "models"):
            capture = captures.get(name)
            if not isinstance(capture, dict):
                continue
            body = capture.get("body")
            digest = capture.get("body_sha256")
            if not isinstance(body, str):
                bad(f"captures.{name}.body is not a stored string")
                continue
            if capture.get("body_read_truncated") is True \
                    or capture.get("body_truncated") is True:
                bad(f"captures.{name}.body is truncated")
            if not is_hex64(digest) or hashlib.sha256(
                    body.encode("utf-8")).hexdigest() != digest:
                bad(f"captures.{name}.body_sha256 does not match its "
                    "stored body")
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
        if is_v3:
            if row.get("expected_model_id") != rec.get("expect"):
                bad(f"probe {name}: row expected_model_id "
                    f"{row.get('expected_model_id')!r} != record expect "
                    f"{rec.get('expect')!r}")
            if row.get("served_model") != alias:
                bad(f"probe {name}: served_model "
                    f"{row.get('served_model')!r} != alias {alias!r}")
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
        passed = c.get("passed")
        if is_v3:
            if passed is not True and passed is not False and passed is not None:
                bad(f"check {cid!r}: passed is not true|false|null")
            elif passed is False:
                bad(f"check {cid!r}: passed is false")
            evaluated = c.get("evaluated")
            if not isinstance(evaluated, bool):
                bad(f"check {cid!r}: evaluated is not a boolean")
            elif evaluated and passed is None:
                bad(f"check {cid!r}: evaluated true but passed is null")
            elif not evaluated and passed is not None:
                bad(f"check {cid!r}: evaluated false but passed is "
                    f"{passed!r}, want null")
            elif not evaluated:
                observed = c.get("observed")
                reason = (observed.get("not_evaluated_reason")
                          if isinstance(observed, dict) else None)
                if cid != "loading_envelope_graded" or lo is not False \
                        or model_503_rows or envelope_503_rows:
                    bad(f"check {cid!r}: only loading_envelope_graded "
                        "may be unevaluated, and only with no observed "
                        "loading 503 envelope")
                if reason != "no-loading-503-observed":
                    bad(f"check {cid!r}: observed.not_evaluated_reason "
                        f"{reason!r} != 'no-loading-503-observed'")
        else:
            if not isinstance(passed, bool):
                bad(f"check {cid!r}: passed is not a boolean")
            elif passed is not True:
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
    if is_v3:
        validate_source_binding(problems, receipt.get("source_binding"),
                                set(by_id))

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


    def require_observed(cid, values):
        """v3: require each recorded observation to match raw evidence."""
        observed = obs(cid)
        for key, value in values.items():
            if key not in observed or observed[key] != value:
                bad(f"{cid}: observed.{key} {observed.get(key)!r} "
                    f"!= re-derived {value!r}")
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
        if is_v3:
            require_observed("health_ready", {
                "status": health_status,
                "body": health_body,
                "expected_body": HEALTH_READY_DOC,
            })

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
        if is_v3:
            models_cap_status = dig(captures, "models", "status")
            if models_cap_status != 200:
                bad(f"models_alias_id: captures.models.status "
                    f"{models_cap_status!r} != 200 (round-18 RevTriStateDesign)")
            require_observed("models_alias_id", {
                "data_ids": ids, "expected_alias": alias,
                "status": models_cap_status,
            })
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
        if is_v3:
            models_cap_status = dig(captures, "models", "status")
            if models_cap_status != 200:
                bad(f"models_owned_by_llamacpp: captures.models.status "
                    f"{models_cap_status!r} != 200")
            require_observed("models_owned_by_llamacpp", {
                "owned_by": owners, "status": models_cap_status,
            })
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
        if is_v3:
            require_observed("metrics_not_enabled", {
                "status": metrics_status,
            })
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
        if is_v3:
            require_observed("props_alias", {"fields": props_fields})
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
            if is_v3 and isinstance(row, dict):
                require_observed("probe_model_ok", {
                    "exit": info["rec"].get("exit"),
                    "verdict": row.get("verdict"),
                    "reason": row.get("reason"),
                })
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
            if is_v3 and isinstance(row, dict):
                require_observed("probe_mismatch", {
                    "exit": info["rec"].get("exit"),
                    "verdict": row.get("verdict"),
                    "reason": row.get("reason"),
                })
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
        if is_v3:
            require_observed("teardown_graceful", {
                "returncode": td_rc,
                "sigterm_sent": td_term,
                "sigkill_sent": td_kill,
                "alive_at_teardown_start": td_alive,
                "port_listener_ownership": own,
                "error": teardown.get("error"),
            })

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
        if is_v3:
            require_observed("teardown_port_closed", {
                "port_refuses": teardown.get("port_refuses"),
                "port_listener_ownership": own,
            })

    if is_v2 and not is_v3 and "loading_envelope_graded" in by_id:
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


    if is_v3 and "loading_envelope_graded" in by_id:
        bodies = receipt.get("loading_503_bodies")
        dropped = receipt.get("loading_bodies_dropped")
        bodies_list = bodies if isinstance(bodies, list) else []
        bodies_valid = isinstance(bodies, list)
        if not bodies_valid:
            bad("loading_envelope_graded: loading_503_bodies is not an "
                "array")
        if isinstance(dropped, bool) or not isinstance(dropped, int) \
                or dropped < 0:
            bad(f"loading_bodies_dropped {dropped!r} is not a "
                "non-negative integer")
            dropped_valid = False
        else:
            dropped_valid = True

        transition_counts = {}
        transitions_valid = True
        for i, row in enumerate(model_503_rows):
            text = row.get("body")
            digest = row.get("body_sha256")
            repeats = row.get("repeats")
            exact = isinstance(text, str) and loading_envelope_ok(
                parse_body(text))
            digest_ok = (isinstance(text, str) and is_hex64(digest)
                         and hashlib.sha256(
                             text.encode("utf-8")).hexdigest() == digest)
            repeats_ok = (isinstance(repeats, int)
                          and not isinstance(repeats, bool) and repeats >= 0)
            if not exact:
                transitions_valid = False
            if not digest_ok:
                transitions_valid = False
                bad(f"loading transition {i} body_sha256 does not match "
                    "its stored body")
            if not repeats_ok:
                transitions_valid = False
                bad(f"loading transition {i}.repeats is not a "
                    "non-negative integer")
            if row.get("body_read_truncated") is True \
                    or row.get("body_over_cap") is True:
                transitions_valid = False
            if is_hex64(digest) and repeats_ok:
                transition_counts[digest] = (
                    transition_counts.get(digest, 0) + 1 + repeats)

        body_counts = {}
        body_flags = []
        for i, body in enumerate(bodies_list):
            if not isinstance(body, dict):
                bodies_valid = False
                body_flags.append(False)
                bad(f"loading_503_bodies[{i}] is not an object")
                continue
            text = body.get("body")
            digest = body.get("body_sha256")
            repeats = body.get("repeats")
            exact = (body.get("path") == "/v1/models"
                     and isinstance(text, str)
                     and loading_envelope_ok(parse_body(text)))
            digest_ok = (isinstance(text, str) and is_hex64(digest)
                         and hashlib.sha256(
                             text.encode("utf-8")).hexdigest() == digest)
            repeats_ok = (isinstance(repeats, int)
                          and not isinstance(repeats, bool) and repeats >= 0)
            if not exact:
                bodies_valid = False
                bad(f"loading_503_bodies[{i}] is not an exact "
                    "/v1/models loading envelope")
            if not digest_ok:
                bodies_valid = False
                bad(f"loading_503_bodies[{i}].body_sha256 does not match "
                    "its stored body")
            if not repeats_ok:
                bodies_valid = False
                bad(f"loading_503_bodies[{i}].repeats is not a "
                    "non-negative integer")
            if is_hex64(digest) and repeats_ok:
                if digest in body_counts:
                    bodies_valid = False
                    bad(f"loading_503_bodies duplicates body digest "
                        f"{digest}")
                body_counts[digest] = 1 + repeats
            body_flags.append(exact and digest_ok and repeats_ok)

        if body_counts != transition_counts:
            bad("loading_503_bodies digests/repeats do not cover the "
                "stored /v1/models 503 transitions exactly")
            bodies_valid = False
        dropped_expected = max(0, len(transition_counts) - len(bodies_list))
        if dropped_valid and dropped != dropped_expected:
            bad(f"loading_bodies_dropped {dropped} != re-derived "
                f"omission count {dropped_expected}")
            dropped_valid = False
        if dropped_valid and dropped != 0:
            bad("loading_envelope_graded cannot pass with an unretained "
                "loading body")
            dropped_valid = False

        all_exact = (all(body_flags) if bodies_list else None)
        if l503 is None:
            first_loading_matches = not model_503_rows
        else:
            first_loading_matches = bool(model_503_rows) \
                and l503.get("path") == "/v1/models" \
                and l503.get("body") == model_503_rows[0].get("body") \
                and l503.get("body_sha256") \
                    == model_503_rows[0].get("body_sha256")
        if not first_loading_matches:
            bad("loading_503 does not match the first /v1/models 503 "
                "transition")

        no_loading_observed = (
            lo is False and not model_503_rows and l503 is None
            and bodies_valid and not bodies_list
            and dropped_valid and dropped == 0)
        if no_loading_observed:
            derived_passed = None
        else:
            derived_passed = bool(
                lo is True and model_503_rows and want_lef is True
                and all_exact is True and transitions_valid and bodies_valid
                and dropped_valid and first_loading_matches)
        c = by_id["loading_envelope_graded"]
        if c.get("passed") is not derived_passed:
            bad("check 'loading_envelope_graded' passed "
                f"{c.get('passed')!r} != re-derived {derived_passed!r}")
        if c.get("evaluated") is not (derived_passed is not None):
            bad("check 'loading_envelope_graded' evaluated "
                f"{c.get('evaluated')!r} != re-derived "
                f"{derived_passed is not None}")
        o = obs("loading_envelope_graded")
        expected_observed = {
            "loading_observed": lo,
            "distinct_bodies": len(bodies_list),
            "bodies_dropped": dropped,
            "total_503_responses": sum(body_counts.values()),
            "all_exact": all_exact,
            "exact": all_exact,
        }
        for key, value in expected_observed.items():
            if key not in o or o[key] != value:
                bad(f"loading_envelope_graded: observed.{key} "
                    f"{o.get(key)!r} != re-derived {value!r}")
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
        if is_v3:
            require_observed("model_unchanged", {
                "pre": model_sha, "post": model_post,
            })
        if is_v2:
            claim("model_unchanged",
                  is_hex64(model_sha) and is_hex64(model_post)
                  and model_sha == model_post)

    if is_v3:
        outcome = receipt.get("outcome")
        if outcome not in ("pass", "fail", "not-evaluated",
                           "setup-error"):
            bad(f"outcome {outcome!r} is not a v3 outcome")
        if internal_fault is not None:
            if not internal_fault.startswith("internal:") \
                    or not internal_fault[len("internal:"):]:
                bad(f"internal_fault {internal_fault!r} is not "
                    "'internal:<ExcType>'")
        states = [c.get("passed") for c in by_id.values()
                  if isinstance(c, dict)]
        if setup_error is not None or internal_fault is not None:
            derived_outcome = "setup-error"
        elif any(value is False for value in states):
            derived_outcome = "fail"
        elif any(value is None for value in states):
            derived_outcome = "not-evaluated"
        else:
            derived_outcome = "pass"
        if outcome != derived_outcome:
            bad(f"outcome {outcome!r} != re-derived "
                f"{derived_outcome!r}")

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
# Soname-style chain: libllama-alias.so -> libllama.so.0 -> libllama.so.
SELFTEST_LINKS = {"libllama.so.0": "libllama.so",
                  "libllama-alias.so": "libllama.so.0"}


ENVELOPE_BODY = json.dumps({"error": {"message": "Loading model",
                                      "type": "unavailable_error",
                                      "code": 503}},
                           separators=(",", ":"))
MODELS_BODY = json.dumps({
    "object": "list",
    "data": [{"id": ALIAS, "object": "model", "created": 0,
              "owned_by": "llamacpp"}],
}, separators=(",", ":"))

def _selftest_source_binding():
    texts = (
        "    this->get_health = [this](const server_http_req &) {\n"
        "        // error and loading states are handled by middleware\n"
        "        auto res = create_response(true);\n"
        "\n"
        "        // this endpoint can be accessed during sleeping\n"
        "        // the next LOC is to avoid someone accidentally use "
        "ctx_server\n"
        "        bool ctx_server; // do NOT delete this line\n"
        "        GGML_UNUSED(ctx_server);\n"
        "\n"
        '        res->ok({{"status", "ok"}});\n'
        "        return res;\n"
        "    };\n",
        "            res.status = 503;\n"
        "            res.set_content(\n"
        "                safe_json_to_str(json {\n"
        '                    {"error", {\n'
        '                        {"message", "Loading model"},\n'
        '                        {"type", "unavailable_error"},\n'
        '                        {"code", 503}\n'
        '                    }}\n'
        '                }),\n'
        "                \"application/json; charset=utf-8\"\n"
        "            );\n"
        "            return false;\n",
        "        struct sigaction sigint_action;\n"
        "        sigint_action.sa_handler = signal_handler;\n"
        "        sigemptyset (&sigint_action.sa_mask);\n"
        "        sigint_action.sa_flags = 0;\n"
        "        sigaction(SIGINT, &sigint_action, NULL);\n"
        "        sigaction(SIGTERM, &sigint_action, NULL);\n",
        "        shutdown_handler = [&](int) {\n"
        "            mcp_mgr.shutdown();\n"
        "            // this will unblock start_loop()\n"
        "            ctx_server.terminate();\n"
        '        };\n',
        "        // this call blocks the main thread until "
        "queue_tasks.terminate() is called\n"
        "        ctx_server.start_loop();\n"
        "\n"
        "        clean_up();\n"
        "        ctx_http.join();\n"
        '        if (monitor_thread.joinable()) {\n'
        '            monitor_thread.join();\n'
        '        }\n'
        "\n"
        '        auto * ll_ctx = ctx_server.get_llama_context();\n'
        '        if (ll_ctx != nullptr) {\n'
        '            common_memory_breakdown_print(ll_ctx);\n'
        '        }\n'
        '    }\n'
        "\n"
        "    return 0;\n",
    )
    bindings = []
    for spec, text in zip(SOURCE_BINDING_EXPECTED, texts):
        check, row, path, lines, file_sha, span_sha = spec
        bindings.append({
            "check": check,
            "row": row,
            "commit": LLAMA_COMMIT,
            "path": path,
            "url": LLAMA_RAW + path,
            "lines": list(lines),
            "file_sha256": file_sha,
            "span_text": text,
            "span_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })
    return bindings


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
                   "install_links": SELFTEST_LINKS,
                   "install_links_sha256": install_links_sha(SELFTEST_LINKS),
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

def _selftest_receipt_v3():
    r = _selftest_receipt_v2()
    r["schema"] = RECEIPT_SCHEMA_V3
    r["model"]["arg"] = r["model"]["path"]
    r["source_binding"] = _selftest_source_binding()
    r["internal_fault"] = None
    r["outcome"] = "pass"
    r["captures"]["health"]["body_sha256"] = hashlib.sha256(
        r["captures"]["health"]["body"].encode("utf-8")).hexdigest()
    r["captures"]["models"]["body_sha256"] = hashlib.sha256(
        r["captures"]["models"]["body"].encode("utf-8")).hexdigest()
    r["loading_bodies_dropped"] = 0
    loading_sha = hashlib.sha256(ENVELOPE_BODY.encode("utf-8")).hexdigest()
    r["transitions"][1].update(body_sha256=loading_sha)
    r["loading_503"].update(body_sha256=loading_sha)
    r["loading_503_bodies"] = [{
        "path": "/v1/models",
        "body_sha256": loading_sha,
        "body": ENVELOPE_BODY,
        "repeats": r["transitions"][1]["repeats"],
    }]
    for check in r["checks"]:
        check["evaluated"] = True
        if check["id"] == "health_ready":
            check["observed"].update(
                body=HEALTH_READY_DOC, expected_body=HEALTH_READY_DOC)
        elif check["id"] in ("models_alias_id", "models_owned_by_llamacpp"):
            check["observed"]["status"] = r["captures"]["models"]["status"]
        elif check["id"] == "props_alias":
            check["observed"]["fields"] = copy.deepcopy(
                r["captures"]["props"]["fields"])
        elif check["id"] == "teardown_graceful":
            check["observed"].update(
                port_listener_ownership="child", error=None)
        elif check["id"] == "teardown_port_closed":
            check["observed"]["port_listener_ownership"] = "child"
        elif check["id"] == "loading_envelope_graded":
            check["observed"].update({
                "loading_observed": True,
                "distinct_bodies": 1,
                "bodies_dropped": 0,
                "total_503_responses": 13,
                "all_exact": True,
                "exact": True,
            })
    return r

def _selftest():
    base = _selftest_receipt()
    expects = ["--expect-model-sha256", MODEL_SHA,
               "--expect-server-sha256", SERVER_SHA,
               "--expect-server-impl-sha256", IMPL_SHA,
               "--expect-probe-sha256", PROBE_SHA,
               "--expect-tool-sha256", TOOL_SHA]
    base_tree = base["server"]["install_tree_sha256"]
    base_links = base["server"]["install_links_sha256"]
    cases = [("valid", base, expects, 0),
             ("tree-pin-valid", base,
              expects + ["--expect-install-tree-sha256", base_tree], 0),
             ("links-pin-valid", base,
              expects + ["--expect-install-links-sha256", base_links], 0)]
    legacy = copy.deepcopy(base)
    del legacy["server"]["install_links"]
    del legacy["server"]["install_links_sha256"]
    cases.append(("links-absent-legacy-valid", legacy, expects, 0))
    cases.append(("links-absent-with-pin", legacy,
                  expects + ["--expect-install-links-sha256", base_links], 1))
    # child_env_keys entries come from an untrusted receipt: a value after
    # '=' must never be echoed into gate output or collected diagnostics.
    env_secret = "kama-selftest-env-value-2f6b1d"


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
    mut("env-key-value-echo",
        lambda r: r["child_env_keys"].append("PATH=" + env_secret))
    mut("env-key-raw-value-echo",
        lambda r: r["child_env_keys"].append("SK_" + env_secret))
    mut("env-key-nonstring",
        lambda r: r["child_env_keys"].append({"v": env_secret}))
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
    mut("impl-sha-mismatch-expect",
        lambda r: r["server"].update(server_impl_sha256="0" * 64),
        extra=expects)
    mut("impl-digest-absent-expect",
        lambda r: r["server"].update(server_impl_sha256=None),
        extra=expects)
    mut("tree-sha-mismatch-expect",
        lambda r: r["server"].update(install_tree_sha256="0" * 64),
        extra=expects + ["--expect-install-tree-sha256", base_tree])
    mut("tree-empty-map-with-pin",
        lambda r: r["server"].update(install_tree={},
                                     install_tree_sha256=base_tree),
        extra=expects + ["--expect-install-tree-sha256", base_tree])
    mut("tree-sha-absent-expect",
        lambda r: r["server"].update(install_tree_sha256=None),
        extra=expects + ["--expect-install-tree-sha256", base_tree])
    mut("tree-sha-malformed-expect",
        lambda r: r["server"].update(install_tree_sha256="not-a-digest"),
        extra=expects + ["--expect-install-tree-sha256", base_tree])
    mut("tree-consistent-member-swap",
        lambda r: (r["server"]["install_tree"].update(
                       **{"libggml-base.so.0.27.0": "e" * 64}),
                   r["server"].update(install_tree_sha256=install_tree_sha(
                       r["server"]["install_tree"]))),
        extra=expects + ["--expect-install-tree-sha256", base_tree])
    mut("impl-field-tree-mismatch",
        lambda r: (r["server"]["install_tree"].update(
                       **{"libllama-server-impl.so": "e" * 64}),
                   r["server"].update(install_tree_sha256=install_tree_sha(
                       r["server"]["install_tree"]))),
        extra=expects)

    def relink(r, links):
        r["server"]["install_links"] = links
        r["server"]["install_links_sha256"] = install_links_sha(links)

    links_pin = ["--expect-install-links-sha256", base_links]
    # A consistent retarget onto another pinned member is VALID without a
    # links pin (documented limit) and INVALID with one.
    retargeted = copy.deepcopy(base)
    relink(retargeted, dict(SELFTEST_LINKS, **{"libllama.so.0": "llama-server"}))
    cases.append(("links-retarget-unpinned-valid", retargeted, expects, 0))
    cases.append(("links-retarget-pinned", retargeted,
                  expects + links_pin, 1))
    mut("links-sha-tampered",
        lambda r: r["server"].update(install_links_sha256="0" * 64))
    mut("links-sha-null-nonempty",
        lambda r: r["server"].update(install_links_sha256=None))
    mut("links-dangling", lambda r: relink(
        r, dict(SELFTEST_LINKS, **{"libllama.so.0": "libllama.so.9"})))
    mut("links-absolute-outside", lambda r: relink(
        r, dict(SELFTEST_LINKS, **{"libllama.so.0": "/usr/lib/libllama.so"})))
    mut("links-dotdot-outside", lambda r: relink(
        r, dict(SELFTEST_LINKS, **{"libllama.so.0": "../libllama.so"})))
    mut("links-loop", lambda r: relink(
        r, {"libllama.so.0": "libllama-alias.so",
            "libllama-alias.so": "libllama.so.0"}))
    mut("links-not-object",
        lambda r: r["server"].update(install_links="libllama.so.0"))
    mut("links-non-string-target", lambda r: r["server"].update(
        install_links={"libllama.so.0": 5}))
    mut("links-shadows-member", lambda r: relink(
        r, dict(SELFTEST_LINKS, **{"libllama.so": "llama-server"})))
    mut("links-pin-malformed", lambda r: None,
        extra=expects + ["--expect-install-links-sha256", "zz"])
    mut("links-dropped-pinned", lambda r: relink(r, {}),
        extra=expects + links_pin)
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

    base_v3 = _selftest_receipt_v3()
    cases.append(("v3-valid", base_v3, expects, 0))
    no_loading = copy.deepcopy(base_v3)
    no_loading["transitions"] = [
        row for row in no_loading["transitions"]
        if not (row.get("path") == "/v1/models"
                and row.get("status") == 503)]
    no_loading.update(loading_503=None, loading_503_bodies=[],
                      loading_bodies_dropped=0, loading_observed=False,
                      loading_envelope_exact=None, outcome="not-evaluated")
    load_check = next(c for c in no_loading["checks"]
                      if c["id"] == "loading_envelope_graded")
    load_check.update(passed=None, evaluated=False)
    load_check["observed"].update({
        "loading_observed": False,
        "distinct_bodies": 0,
        "bodies_dropped": 0,
        "total_503_responses": 0,
        "all_exact": None,
        "exact": None,
        "not_evaluated_reason": "no-loading-503-observed",
    })
    cases.append(("v3-no-loading-not-evaluated", no_loading, expects, 3))

    cases.extend([
        ("v1-require-schema-v1", base, expects
         + ["--require-schema", "v1"], 0),
        ("v1-require-schema-v2-rejects-v1", base, expects
         + ["--require-schema", "v2"], 1),
        ("v2-require-schema-v3-rejects-v2", base_v2, expects
         + ["--require-schema", "v3"], 1),
        ("v3-require-schema-v3", base_v3, expects
         + ["--require-schema", "v3"], 0),
    ])

    def mut3(name, fn, receipt=None, extra=None, want=1):
        r = copy.deepcopy(base_v3 if receipt is None else receipt)
        fn(r)
        cases.append((name, r, extra or [], want))

    mut3("v3-extra-server-argv-flag",
         lambda r: r["argv"].insert(-2, "--metrics"))
    mut3("v3-duplicate-server-argv-flag",
         lambda r: r["argv"].__setitem__(
             slice(-2, -2), ["--port", "45679"]))
    mut3("v3-model-arg-does-not-match-argv",
         lambda r: r["model"].update(arg="/other/model.gguf"))
    # Round-18 RevTriStateDesign P2: a 503 on the ready /v1/models capture
    # (ids intact) must not leave the run NOT-EVALUATED.
    mut3("v3-models-capture-503-ids-intact",
         lambda r: r["captures"]["models"].update(status=503),
         receipt=no_loading)
    for label, path, status in (
            ("route-alias", "/v1/models/", 503),
            ("status-string", "/v1/models", "503"),
            ("status-float", "/v1/models", 503.0),
            ("status-bool", "/v1/models", True)):
        mut3("v3-transition-encoding-" + label,
             lambda r, p=path, s=status: r["transitions"].append(
                 {"path": p, "status": s}), receipt=no_loading)
    mut3("v3-transition-503-nonexact",
         lambda r: r["transitions"][1].update(body='{"error":{}}'))
    # H1 (falsify GateCaptureHashes): a /health 503 carrying the exact loading
    # envelope contradicts loading_observed=false, whatever the route.
    mut3("v3-health-loading-envelope-null-license",
         lambda r: r["transitions"].append({
             "t_ms": 1100, "path": "/health", "status": 503,
             "error": None,
             "body_sha256": hashlib.sha256(
                 ENVELOPE_BODY.encode("utf-8")).hexdigest(),
             "body": ENVELOPE_BODY, "body_over_cap": False,
             "repeats": 3}), receipt=no_loading)
    mut3("v3-transition-503-truncated",
         lambda r: r["transitions"][1].update(body_over_cap=True))
    mut3("v3-teardown-port-close-unowned",
         lambda r: (r.update(port_listener_ownership="foreign"),
                    next(c for c in r["checks"]
                         if c["id"] == "teardown_port_closed")
                    ["observed"].update(
                        port_listener_ownership="foreign")))
    mut3("v3-source-binding-tampered",
         lambda r: r["source_binding"][0].update(row="S999"))
    mut3("v3-internal-fault-not-mirrored",
         lambda r: r.update(internal_fault="internal:KeyboardInterrupt",
                            outcome="setup-error"))
    mut3("v3-loading-observed-count-forged",
         lambda r: next(c for c in r["checks"]
                        if c["id"] == "loading_envelope_graded")
         ["observed"].update(total_503_responses=999))
    mut3("v3-health-observed-body-forged",
         lambda r: next(c for c in r["checks"]
                        if c["id"] == "health_ready")
         ["observed"].update(body={"status": "degraded"}))
    mut3("v3-probe-served-model-forged",
         lambda r: r["probes"][0]["result"]["rows"][0].update(
             served_model="ghost-model"))
    mut3("v3-nonboolean-evaluated",
         lambda r: next(c for c in r["checks"]
                        if c["id"] == "health_ready")
         .update(evaluated="yes"))
    mut3("v3-outcome-fail-with-all-true-checks",
         lambda r: r.update(outcome="fail"))
    mut3("v3-unobserved-loading-missing-reason",
         lambda r: next(c for c in r["checks"]
                        if c["id"] == "loading_envelope_graded")
         ["observed"].pop("not_evaluated_reason"),
         receipt=no_loading)
    mut3("v3-unobserved-loading-claimed-evaluated",
         lambda r: next(c for c in r["checks"]
                        if c["id"] == "loading_envelope_graded")
         .update(evaluated=True),
         receipt=no_loading)
    mut3("v3-nonloading-check-is-null",
         lambda r: (next(c for c in r["checks"]
                         if c["id"] == "health_ready")
                    .update(passed=None, evaluated=False),
                    next(c for c in r["checks"]
                         if c["id"] == "health_ready")
                    ["observed"].update(
                        not_evaluated_reason=
                        "no-loading-503-observed"),
                    r.update(outcome="not-evaluated")))
    mut3("v3-loading-check-null-although-503-present",
         lambda r: (next(c for c in r["checks"]
                         if c["id"] == "loading_envelope_graded")
                    .update(passed=None, evaluated=False),
                    next(c for c in r["checks"]
                         if c["id"] == "loading_envelope_graded")
                    ["observed"].update(
                        not_evaluated_reason=
                        "no-loading-503-observed"),
                    r.update(outcome="not-evaluated")))
    mut3("v3-outcome-pass-with-null",
         lambda r: r.update(outcome="pass"),
         receipt=no_loading)

    def drop_257th_loading_body(r):
        first = r["transitions"][1]
        rows = []
        bodies = []
        for i in range(257):
            body = ENVELOPE_BODY + (" " * i)
            digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
            row = copy.deepcopy(first)
            row.update(t_ms=40 + i, body=body, body_sha256=digest,
                       repeats=0, body_read_truncated=False,
                       body_over_cap=False)
            rows.append(row)
            if i < 256:
                bodies.append({
                    "path": "/v1/models", "body_sha256": digest,
                    "body": body, "repeats": 0,
                })
        r["transitions"] = [
            r["transitions"][0], *rows, r["transitions"][2]]
        r["loading_503"] = {
            "t_ms": rows[0]["t_ms"], "path": "/v1/models",
            "status": 503, "body_sha256": rows[0]["body_sha256"],
            "body": rows[0]["body"],
        }
        r["loading_503_bodies"] = bodies
        r["loading_bodies_dropped"] = 1
        check = next(c for c in r["checks"]
                     if c["id"] == "loading_envelope_graded")
        check["observed"].update(
            distinct_bodies=256, bodies_dropped=1,
            total_503_responses=256)

    mut3("v3-silently-dropped-257th-loading-body",
         drop_257th_loading_body)

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
            elif want == 0 and not proc.stdout.startswith("VALID "):
                failures.append(
                    f"{name}: exit 0 did not print a VALID verdict: "
                    f"{proc.stdout.strip()[:400]!r}")
            elif want == 1 and not proc.stdout.startswith("INVALID "):
                failures.append(
                    f"{name}: exit 1 did not print an INVALID verdict: "
                    f"{proc.stdout.strip()[:400]!r}")
            elif want == 3 and not proc.stdout.startswith("NOT-EVALUATED "):
                failures.append(
                    f"{name}: exit 3 did not print NOT-EVALUATED: "
                    f"{proc.stdout.strip()[:400]!r}")
            if env_secret in proc.stdout or env_secret in proc.stderr:
                failures.append(
                    f"{name}: gate echoed a child_env_keys value into "
                    "diagnostics")
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
    n_valid = sum(1 for c in cases if c[3] == 0)
    n_not_evaluated = sum(1 for c in cases if c[3] == 3)
    n_mut = sum(1 for c in cases if c[3] == 1)
    print(f"selftest: {n_valid} VALID and {n_not_evaluated} "
          f"NOT-EVALUATED receipts accepted; {n_mut} mutations + "
          "unreadable case rejected")
    return 0


# --------------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Validate kama-llamacpp-live/v1, /v2 and /v3 receipts.")
    ap.add_argument("receipt", nargs="?", help="receipt JSON path")
    ap.add_argument("--expect-model-sha256", metavar="HEX",
                    help="require the recorded model sha256")
    ap.add_argument("--expect-server-sha256", metavar="HEX",
                    help="require the recorded server sha256")
    ap.add_argument("--expect-server-impl-sha256", metavar="HEX",
                    help="require the recorded server implementation "
                         "library sha256")
    ap.add_argument("--expect-install-tree-sha256", metavar="HEX",
                    help="require the recorded install-tree sha256")
    ap.add_argument("--expect-install-links-sha256", metavar="HEX",
                    help="require the recorded install-links (symlink) "
                         "sha256")
    ap.add_argument("--expect-probe-sha256", metavar="HEX",
                    help="require the recorded probe sha256")
    ap.add_argument("--expect-tool-sha256", metavar="HEX",
                    help="require the recorded harness-tool sha256")
    ap.add_argument("--require-schema", choices=("v1", "v2", "v3"),
                    help="reject receipts below this schema version")

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
                        expect_server_impl=args.expect_server_impl_sha256,
                        expect_tree=args.expect_install_tree_sha256,
                        expect_links=args.expect_install_links_sha256,
                        expect_probe=args.expect_probe_sha256,
                        expect_tool=args.expect_tool_sha256)
    if args.require_schema and isinstance(receipt, dict):
        minimum = {"v1": 1, "v2": 2, "v3": 3}[args.require_schema]
        declared = receipt.get("schema")
        version = {
            RECEIPT_SCHEMA: 1,
            RECEIPT_SCHEMA_V2: 2,
            RECEIPT_SCHEMA_V3: 3,
        }.get(declared)
        if version is not None and version < minimum:
            problems.append(
                f"schema {declared!r} is below --require-schema "
                f"{args.require_schema}")
    if problems:
        print(f"INVALID {args.receipt}: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    if isinstance(receipt, dict) \
            and receipt.get("schema") == RECEIPT_SCHEMA_V3 \
            and receipt.get("outcome") == "not-evaluated":
        print(f"NOT-EVALUATED {args.receipt}")
        return 3
    print(f"VALID {args.receipt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
