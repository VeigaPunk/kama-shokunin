#!/usr/bin/env python3
"""heldout-cells.py - round-91 C1 held-out cells (seat EX01HeldOutCells).

Not part of the C1 predicate. Reuses the frozen counter's Stub/jbody/ids_doc/run
helpers (imported from tools/round91-answer-time.py, read-only) so the stub
behaviour and the 120 s kill are byte-identical to the counter.

Each cell starts one lane-owned stub on a free 127.0.0.1 port, then runs the base
probe and the M probe (both given as files extracted from git) against it:
  check --port P --expect E --timeout 5 --connect-timeout 2 --json
(listeners cell: listeners --port P --expect E --registry <missing> ... --json).
Raw stdout is kept under <out>/raw with any JSON string value > 4096 bytes
replaced by <elided N bytes sha256=...> so receipts stay small; the full raw
stdout's sha256 and byte count are recorded in the TSV.

Usage: heldout-cells.py --base PROBE --m PROBE --out DIR --work DIR [--only cid]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

COUNTER = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round91-answer-time.py")
# Importing the lane counter must not write __pycache__ into the read-only lane tree.
sys.dont_write_bytecode = True


def load_counter(path: Path):
    spec = importlib.util.spec_from_file_location("r91counter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = load_counter(COUNTER)


def body(doc) -> bytes:
    return C.jbody(doc)


def doc_data(ids, status=None):
    return C.ids_doc(ids, status)


def cell_models_name(n=200000, present=True):
    names = [f"{p}{i:05d}" for p in "ab" for i in range(n // 2)]
    assert len(names) == n and len(set(names)) == n
    seq = [{"name": x} for x in names]
    if present:
        seq.append({"name": "good"})
    return {"models": seq}


def cell_dup():
    return doc_data(["dup"] * 199999 + ["good"])


def cell_crlf_lines():
    return "__raw__", (b'{\r\n  "object": "list",\r\n  "data": [\r\n    {"id": "good"}\r\n'
                       b'  ]\r\n}\r\n')


def cell_crlf_in_id(present):
    ids = ["good\r\n"] + (["good"] if present else [])
    return doc_data(ids)


def cell_router(n, expected_status):
    seq = [{"id": f"r{i:05d}", "status": {"value": "loaded"}} for i in range(n - 1)]
    seq.append({"id": "good", "status": {"value": expected_status}})
    return {"object": "list", "data": seq}


def cell_router_big_id():
    return {"object": "list", "data": [
        {"id": "a" * 3900000, "status": {"value": "loaded"}},
        {"id": "good", "status": {"value": "loaded"}}]}


def cell_router_backslash():
    return {"object": "list", "data": [
        {"id": "q\\b", "status": {"value": "loaded"}},
        {"id": "other", "status": {"value": "loaded"}}]}


def cell_num(ids, expect):
    return doc_data(ids)


def cell_router_custom(entries):
    return {"object": "list", "data": entries}


def cell_router_path_gguf_80k():
    seq = [{"id": f"r{i:05d}", "status": {"value": "loaded"}} for i in range(79999)]
    seq.append({"id": "/models/sub/good.gguf", "status": {"value": "unloaded"}})
    return cell_router_custom(seq)


CELLS = [
    # cid, routes(fn -> dict), expect, kind, expected verdict, expected reason (or None)
    ("H1-models-name-200k-last", lambda: {"/v1/models": {"body": body(cell_models_name())}},
     "good", "check", "MODEL_OK", "matched"),
    ("H1b-models-name-200k-absent", lambda: {"/v1/models": {"body": body(cell_models_name(present=False))}},
     "good", "check", "MODEL_MISMATCH", "served-id-mismatch"),
    ("H2-dup-200k", lambda: {"/v1/models": {"body": body(cell_dup())}},
     "good", "check", "MODEL_OK", "matched"),
    ("H3a-crlf-body", lambda: {"/v1/models": {"body": cell_crlf_lines()[1]}},
     "good", "check", "MODEL_OK", "matched"),
    ("H3b-crlf-in-id-plus-plain", lambda: {"/v1/models": {"body": body(cell_crlf_in_id(True))}},
     "good", "check", "MODEL_OK", "matched"),
    ("H3c-crlf-in-id-only", lambda: {"/v1/models": {"body": body(cell_crlf_in_id(False))}},
     "good", "check", "MODEL_MISMATCH", "served-id-mismatch"),
    ("H4-router-80k-wildcard", lambda: {"/v1/models": {"body": body(cell_router(80000, "loaded"))}},
     "*", "check", "MODEL_OK", "expected-wildcard"),
    ("H5-router-80k-unloaded-autoload",
     lambda: {"/v1/models": {"body": body(cell_router(80000, "unloaded"))},
              "/props": {"body": b'{"role":"router","models_autoload":true}'}},
     "good", "check", "MODEL_OK", "router-unloaded-autoload"),
    ("H6-router-3.9m-id", lambda: {"/v1/models": {"body": body(cell_router_big_id())}},
     "good", "check", "MODEL_OK", "matched"),
    ("H7-expect-abs-path", lambda: {"/v1/models": {"body": body(doc_data(["/models/good.gguf"]))}},
     "/models/good.gguf", "check", "MODEL_OK", "matched"),
    ("H8a-numeric-both", lambda: {"/v1/models": {"body": body(cell_num(["1.0", "1"], "1"))}},
     "1", "check", "MODEL_OK", "matched"),
    ("H8b-numeric-1.0-only", lambda: {"/v1/models": {"body": body(cell_num(["1.0"], "1"))}},
     "1", "check", "MODEL_MISMATCH", "served-id-mismatch"),
    ("H8c-numeric-1-vs-1.0", lambda: {"/v1/models": {"body": body(cell_num(["1"], "1.0"))}},
     "1.0", "check", "MODEL_MISMATCH", "served-id-mismatch"),
    ("H9-listeners-port-stub", lambda: {"/v1/models": {"body": body(doc_data(["good"]))}},
     "good", "listeners", "MODEL_OK", "matched"),
    ("H10-router-backslash-id", lambda: {"/v1/models": {"body": body(cell_router_backslash())}},
     "q\\b", "check", "MODEL_OK", "matched"),
    ("H11-expect-unresolvable", lambda: {"/v1/models": {"body": body(doc_data(["good"]))}},
     "/", "check", "MODEL_MISMATCH", "unresolvable-id"),
    # H12-H15: the router_match filter must apply normalize_id's rule (drop through last '/',
    # strip ONE .gguf) to the raw entry field. A filter bug that drops the expected entry is a
    # FALSE GREEN (status refinement silently skipped), so each cell's expected verdict depends
    # on the matched entry's status.
    ("H12-router-path-gguf-unloaded-autoload",
     lambda: {"/v1/models": {"body": body(cell_router_path_gguf_80k())},
              "/props": {"body": b'{"role":"router","models_autoload":true}'}},
     "good", "check", "MODEL_OK", "router-unloaded-autoload"),
    ("H12b-router-path-gguf-unloaded-small",
     lambda: {"/v1/models": {"body": body(cell_router_custom([
         {"id": "/models/sub/good.gguf", "status": {"value": "unloaded"}}]))},
              "/props": {"body": b'{"role":"router","models_autoload":true}'}},
     "good", "check", "MODEL_OK", "router-unloaded-autoload"),
    ("H13-router-one-gguf-only",
     lambda: {"/v1/models": {"body": body(cell_router_custom([
         {"id": "good.gguf.gguf", "status": {"value": "loading"}},
         {"id": "good", "status": {"value": "unloaded"}}]))},
              "/props": {"body": b'{"role":"router","models_autoload":true}'}},
     "good", "check", "MODEL_OK", "router-unloaded-autoload"),
    ("H14-router-loading-path-gguf",
     lambda: {"/v1/models": {"body": body(cell_router_custom([
         {"id": "/models/sub/good.gguf", "status": {"value": "loading"}}]))}},
     "good", "check", "MODEL_LOADING", "router-loading"),
    ("H15-router-numeric-compare",
     lambda: {"/v1/models": {"body": body(cell_router_custom([
         {"id": "1.0", "status": {"value": "loaded"}},
         {"id": "1", "status": {"value": "unloaded"}}]))},
              "/props": {"body": b'{"role":"router","models_autoload":true}'}},
     "1", "check", "MODEL_OK", "router-unloaded-autoload"),
]


def elide_raw(raw: bytes, limit: int = 4096):
    """Return (elided_text, elided_count, raw_sha256, raw_len)."""
    sha = hashlib.sha256(raw).hexdigest()
    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception:
        return raw[:limit].decode("utf-8", "replace"), 0, sha, len(raw)
    n = 0

    def walk(o):
        nonlocal n
        if isinstance(o, dict):
            return {k: walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(v) for v in o]
        if isinstance(o, str) and len(o.encode()) > limit:
            n += 1
            b = o.encode()
            return f"<elided {len(b)} bytes sha256={hashlib.sha256(b).hexdigest()}>"
        return o

    return json.dumps(walk(doc), indent=1), n, sha, len(raw)


def run_cell(probe: Path, cid, routes, expect, kind, workroot: Path):
    pcwd = workroot / f"cwd-{cid}"
    pcwd.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TMPDIR=str(pcwd))
    with C.Stub(routes) as stub:
        if kind == "listeners":
            cmd = ["bash", str(probe), "listeners", "--port", str(stub.port), "--expect", expect,
                   "--timeout", "5", "--connect-timeout", "2", "--json",
                   "--registry", str(workroot / "no-such-registry.tsv")]
            t0 = time.monotonic()
            try:
                p = C.subprocess.run(cmd, capture_output=True, timeout=C.KILL, env=env, cwd=pcwd)
                rc, out, dt = p.returncode, p.stdout, time.monotonic() - t0
            except C.subprocess.TimeoutExpired:
                rc, out, dt = None, b"", time.monotonic() - t0
        else:
            rc, out, dt = C.run(probe, stub.port, expect, env, pcwd)
    return rc, out, dt


def parse(out: bytes, kind: str):
    try:
        doc = json.loads(out.decode("utf-8"))
    except Exception:
        return None
    if kind == "listeners":
        try:
            return doc["listeners"][0]
        except Exception:
            return None
    return C.parse_row(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--m", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--only")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "raw").mkdir(parents=True, exist_ok=True)
    a.work.mkdir(parents=True, exist_ok=True)
    probes = [("base", a.base), ("m", a.m)]
    rows = []
    for cid, routes_fn, expect, kind, want_v, want_r in CELLS:
        if a.only and cid not in a.only.split(","):
            continue
        try:
            routes = routes_fn()
        except C.CannotEvaluate as e:
            print(f"CELL_SKIP {cid} {e}")
            continue
        for label, probe in probes:
            load = " ".join(f"{x:.2f}" for x in os.getloadavg())
            rc, out, dt = run_cell(probe, cid, routes, expect, kind, a.work)
            row = parse(out, kind)
            v = row.get("verdict") if row else ("killed" if rc is None else f"unparsed(rc={rc})")
            r = (row.get("reason") if row else "-") or "-"
            served = row.get("served_model") if row else None
            sbytes = len(served.encode()) if isinstance(served, str) else 0
            ok = v == want_v and (want_r is None or r == want_r)
            text, nelided, rsha, rlen = elide_raw(out)
            (a.out / "raw" / f"{cid}.{label}.json").write_text(
                f"# probe={probe} sha256={C.sha256(probe)} rc={rc} seconds={dt:.2f} "
                f"verdict={v} reason={r} raw_len={rlen} raw_sha256={rsha} elided={nelided}\n{text}\n")
            rows.append((cid, label, rc, v, r, f"{dt:.2f}", ok, sbytes, rlen, load))
            print(f"CELL {cid} probe={label} rc={rc} verdict={v} reason={r} seconds={dt:.2f} "
                  f"ok={int(ok)} served_bytes={sbytes} raw_bytes={rlen} load={load}", flush=True)
    tsv = a.out / "heldout.tsv"
    with tsv.open("w") as f:
        f.write("cell\tprobe\trc\tverdict\treason\tseconds\tmeets_expected\tserved_bytes\traw_bytes\tload\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    load = " ".join(f"{x:.2f}" for x in os.getloadavg())
    print(f"HELDOUT cells={len(rows)//2} runs={len(rows)} load={load}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
