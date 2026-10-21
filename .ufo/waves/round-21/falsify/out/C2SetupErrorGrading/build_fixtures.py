#!/usr/bin/env python3
"""C2SetupErrorGrading (round 21, FALSIFY): hand-built receipt fixtures.

BASE: committed kama-llamacpp-live/v3 receipt
  .ufo/waves/round-21/runs/b76727f3/live-receipt.json
  at a6617149722c73d90e142fbdc8154d6967055f7e.
PRODUCER: tools/kama-llamacpp-live.py at the same commit. It is parsed with
  ast only (never imported or run). No server, port, model or producer code
  runs here; every fixture is a pure JSON edit of BASE.

Usage: build_fixtures.py BASE PRODUCER OUT_DIR
"""
import ast
import copy
import hashlib
import json
import os
import sys

ABSENT = object()
SETUP_ERROR = "install-tree-unpinnable:glibc-hwcaps:not-regular-or-symlink"
# Producer fields assigned before the install_links() SetupError
# (main() lines 1353-1367 and 1375-1379 at a6617149). The raise skips
# server.update() (line 1387), so all other fields keep initial-dict values.
PRE_RAISE_TOP = {"schema", "started_utc", "ended_utc", "model", "probe",
                 "alias", "ctx", "threads", "tool", "server"}
PRE_RAISE_SERVER = {"arg"}
SKIP_LITERAL = {"setup_error"}


def initial_receipt_node(path):
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    for fn in ast.walk(tree):
        if not (isinstance(fn, ast.FunctionDef) and fn.name == "main"):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict) \
                    and any(isinstance(t, ast.Name) and t.id == "receipt"
                            for t in node.targets):
                return node.value
    raise SystemExit("initial receipt dict not found in main()")


def items(node):
    return {k.value: v for k, v in zip(node.keys, node.values)}


def literal(node):
    try:
        return ast.literal_eval(node)
    except ValueError:
        return ABSENT


def faithful_setup_error(base, setup_error):
    """The receipt main() holds when install_links() raises SetupError."""
    return {
        "schema": base["schema"],
        "started_utc": base["started_utc"],
        "ended_utc": base["ended_utc"],
        "server": {"arg": base["server"]["arg"], "realpath": None,
                   "sha256": None, "install_tree": {},
                   "install_tree_sha256": None, "install_links": {},
                   "install_links_sha256": None,
                   "server_impl_sha256": None},
        "model": copy.deepcopy(base["model"]),
        "model_sha256_post": None,
        "probe": {"path": base["probe"]["path"], "sha256": None},
        "alias": base["alias"], "ctx": base["ctx"],
        "threads": base["threads"],
        "port": None, "port_refusal_set": [], "child_env_keys": [],
        "argv": None, "transitions": [], "loading_503": None,
        "loading_503_bodies": [], "loading_bodies_dropped": 0,
        "loading_observed": False, "loading_envelope_exact": None,
        "captures": {}, "probes": [], "teardown": None, "checks": [],
        "setup_error": setup_error, "internal_fault": None,
        "child_pid": None, "port_listener_ownership": "unproven",
        "source_binding": [],
        "tool": {"path": base["tool"]["path"], "sha256": None},
        "outcome": "setup-error",
    }


def ast_check(fixture, node):
    top = items(node)
    if set(fixture) != set(top):
        raise AssertionError(
            f"top-level keys differ: {sorted(set(fixture) ^ set(top))}")
    srv = items(top["server"])
    if set(fixture["server"]) != set(srv):
        raise AssertionError(
            f"server keys differ: {sorted(set(fixture['server']) ^ set(srv))}")
    compared = []
    for key, value in top.items():
        lit = literal(value)
        if key in PRE_RAISE_TOP or key in SKIP_LITERAL or lit is ABSENT:
            continue
        if fixture[key] != lit:
            raise AssertionError(
                f"{key}: fixture {fixture[key]!r} != producer {lit!r}")
        compared.append(key)
    for key, value in srv.items():
        lit = literal(value)
        if key in PRE_RAISE_SERVER or lit is ABSENT:
            continue
        if fixture["server"][key] != lit:
            raise AssertionError(
                f"server.{key}: fixture {fixture['server'][key]!r} "
                f"!= producer {lit!r}")
        compared.append("server." + key)
    return len(top), len(srv), compared


def top_diff(base, variant):
    def fmt(v):
        if v is ABSENT:
            return "<absent>"
        s = json.dumps(v, sort_keys=True, ensure_ascii=True)
        return s if len(s) <= 90 else s[:87] + "..."
    lines = []
    for key in sorted(set(base) | set(variant)):
        bv = base.get(key, ABSENT)
        vv = variant.get(key, ABSENT)
        if key == "server" and isinstance(bv, dict) and isinstance(vv, dict):
            for sk in sorted(set(bv) | set(vv)):
                b2, v2 = bv.get(sk, ABSENT), vv.get(sk, ABSENT)
                if b2 != v2:
                    lines.append(f"server.{sk}: {fmt(b2)} -> {fmt(v2)}")
            continue
        if bv != vv:
            lines.append(f"{key}: {fmt(bv)} -> {fmt(vv)}")
    return lines


def main():
    base_path, producer_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(base_path, "rb") as fh:
        base_digest = hashlib.sha256(fh.read()).hexdigest()
    with open(base_path, encoding="utf-8") as fh:
        base = json.load(fh)
    os.makedirs(out, exist_ok=True)

    variants = {}
    variants["setup-error-faithful.json"] = faithful_setup_error(
        base, SETUP_ERROR)
    v = copy.deepcopy(base)
    v["setup_error"] = SETUP_ERROR
    v["outcome"] = "setup-error"
    variants["setup-error-only.json"] = v
    v = copy.deepcopy(variants["setup-error-only.json"])
    v["server"]["install_links"] = {}
    v["server"]["install_links_sha256"] = None
    variants["setup-error-null-links.json"] = v
    v = copy.deepcopy(base)
    v["server"]["install_links"] = {}
    v["server"]["install_links_sha256"] = None
    variants["complete-null-links.json"] = v
    v = copy.deepcopy(base)
    v["setup_error"] = SETUP_ERROR
    v["outcome"] = "pass"
    variants["setup-error-outcome-pass.json"] = v
    v = copy.deepcopy(base)
    v["checks"] = []
    v["outcome"] = "setup-error"
    variants["empty-checks-setup-null.json"] = v
    v = copy.deepcopy(base)
    v["server"]["install_tree_sha256"] = None
    variants["complete-null-tree-digest.json"] = v
    v = copy.deepcopy(base)
    v["internal_fault"] = 5
    v["setup_error"] = 5
    v["outcome"] = "setup-error"
    variants["internal-fault-nonstring.json"] = v
    variants["base-copy.json"] = copy.deepcopy(base)

    n_top, n_srv, compared = ast_check(
        variants["setup-error-faithful.json"], initial_receipt_node(
            producer_path))
    print(f"ast-check ok: producer initial dict has {n_top} top-level and "
          f"{n_srv} server keys; faithful fixture matches both sets; "
          f"{len(compared)} literal defaults equal")
    print(f"base sha256 {base_digest}")

    manifest = [f"{base_digest}  base (committed blob, unmodified)"]
    diffs = []
    for name, receipt in variants.items():
        text = json.dumps(receipt, indent=2, ensure_ascii=True) + "\n"
        with open(os.path.join(out, name), "w", encoding="ascii") as fh:
            fh.write(text)
        digest = hashlib.sha256(text.encode("ascii")).hexdigest()
        manifest.append(f"{digest}  {name}")
        changed = top_diff(base, receipt)
        diffs.append(f"## {name}")
        diffs.extend("  " + line for line in changed)
        if not changed:
            diffs.append("  (identical to base)")
    with open(os.path.join(out, "MANIFEST.sha256"), "w",
              encoding="ascii") as fh:
        fh.write("\n".join(manifest) + "\n")
    with open(os.path.join(out, "DIFFS-vs-base.txt"), "w",
              encoding="ascii") as fh:
        fh.write("\n".join(diffs) + "\n")
    print("\n".join(manifest))
    print("\n".join(diffs))


if __name__ == "__main__":
    main()
