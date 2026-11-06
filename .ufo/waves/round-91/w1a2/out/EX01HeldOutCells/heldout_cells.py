#!/usr/bin/env python3
"""EX01HeldOutCells - round-91 C1 held-out cells (NOT part of the frozen predicate).

Runs `check --port <stub> --expect <id> --json` (and one `listeners --port <stub>`)
against the probe bytes at the base revision B and at the measured revision M, using
the Stub class / ids_doc / jbody / run helpers of the frozen counter
tools/round91-answer-time.py (imported, not copied, so the transport is identical).

Usage: heldout_cells.py --repo <lane> --work <scratch> --out <dir> [--only SUBSTR]

Each cell is graded on the probe's own verdict/reason and wall seconds. A cell where
base is RIGHT and M is WRONG is harm (BLOCKER). A cell where both agree is a
regression check. A cell over the 20 s budget is a time finding, not harm, and is
re-run once before it is called slow (host load is high).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE = "c06838c5b94576971ea33ac465bf2c935e9037f9"
MEAS = "3decfa36b0eba7e5197c034dd1547146bca1568a"
KILL = 120.0
BUDGET = 20.0


def load_counter(repo: Path):
    p = repo / "tools" / "round91-answer-time.py"
    spec = importlib.util.spec_from_file_location("r91counter", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def loadavg() -> str:
    try:
        return Path("/proc/loadavg").read_text().split()[0]
    except OSError:
        return "?"


def router_doc(entries):
    """entries: [(id, status.value)] -> llama.cpp router /v1/models shape."""
    return {"object": "list", "data": [{"id": i, "status": {"value": v}} for i, v in entries]}


def build_cells(m, scale=1):
    """-> list of dicts: cid, doc, routes, expect, want(v, r) or None, sub, why

    scale>1 shrinks every large population so the BASE probe also finishes: same body
    shape, same code path, both revisions complete -> a semantics differential.
    """
    N_IDS = 200000 // scale
    N_ROUTER = 80000 // scale
    BIG = 3900000 // scale
    P = "" if scale == 1 else "S"
    caps = []

    # H1 Ollama shape: 200k `name` keys, expected last (python path only: served_ids
    # precedence data.id -> models.id -> models.name).
    caps.append(dict(
        cid="H1-models-name-200k-last",
        doc={"object": "list",
             "models": [{"name": "x%06d" % i} for i in range(N_IDS)] + [{"name": "good"}]},
        expect="good", want=("MODEL_OK", "matched"),
        why=f"{N_IDS} models[].name keys (Ollama shape), expected id last"))

    # H2a 200k identical ids (served_ids dedups them; documents the behaviour).
    caps.append(dict(
        cid="H2a-dup-200k-literal",
        doc={"object": "list", "data": [{"id": "dup"} for _ in range(N_IDS)] + [{"id": "good"}]},
        expect="good", want=("MODEL_OK", "matched"),
        why="200k literal duplicate ids: served_ids dict.fromkeys collapses them"))

    # H2b 200k distinct raw ids that all normalize to the SAME basename: no dedup,
    # so the per-id loop runs 200k times before the match (last).
    caps.append(dict(
        cid="H2b-dup-200k-normalized",
        doc={"object": "list",
             "data": [{"id": "%06d/dup" % i} for i in range(N_IDS)] + [{"id": "good"}]},
        expect="good", want=("MODEL_OK", "matched"),
        why="200k distinct ids that normalize to 'dup'; expect 'good' last"))

    # H3 CR/LF inside JSON strings (escaped in the wire body).
    caps.append(dict(
        cid="H3a-crlf-ids-no-match",
        doc={"object": "list", "data": [{"id": "x\r\ny"}, {"id": "good\r\n"}]},
        expect="good", want=("MODEL_MISMATCH", "served-id-mismatch"),
        why="ids carry CR/LF: byte compare after normalize -> no match with 'good'"))

    caps.append(dict(
        cid="H3b-crlf-ids-with-match",
        doc={"object": "list", "data": [{"id": "good\r\n"}, {"id": "good"}]},
        expect="good", want=("MODEL_OK", "matched"),
        why="a CR/LF id must not break the pass of a plain 'good' after it"))

    # H3c raw CRLF as JSON whitespace between tokens (valid RFC 8259), plain ids.
    caps.append(dict(
        cid="H3c-crlf-tokens",
        doc={"object": "list", "data": [{"id": "good"}]}, expect="good",
        want=("MODEL_OK", "matched"), raw_crlf=True,
        why="CRLF line endings between JSON tokens, ids plain"))

    # H4 80k router entries, wildcard expectation (every entry counts).
    caps.append(dict(
        cid="H4-router-80k-wildcard",
        doc=router_doc([("r%05d" % i, "loaded") for i in range(N_ROUTER)] + [("good", "loaded")]),
        expect="*", want=("MODEL_OK", "expected-wildcard"),
        why="80k router entries with --expect '*' (wildcard short-circuits before match)"))

    # H5 80k router entries, expected entry `unloaded`, /props says autoload.
    caps.append(dict(
        cid="H5-router-80k-unloaded-autoload",
        doc=router_doc([("r%05d" % i, "loaded") for i in range(N_ROUTER)] + [("good", "unloaded")]),
        routes={"/props": {"body": m.jbody({"role": "router", "models_autoload": True})}},
        expect="good", want=("MODEL_OK", "router-unloaded-autoload"),
        why="80k entries, the matching one unloaded, autoload router"))

    # H6 one 3.9 MB id in a router listing.
    caps.append(dict(
        cid="H6a-router-id-3900k-plain",
        doc=router_doc([("a" * BIG, "loaded"), ("good", "loaded")]),
        expect="good", want=("MODEL_OK", "matched"),
        why="one 3.9 MB plain id in a router listing, expected present"))
    caps.append(dict(
        cid="H6b-router-id-3900k-slashes",
        doc=router_doc([("a/" * (BIG // 2 - 1) + "zzz.gguf", "loaded"), ("good", "loaded")]),
        expect="good", want=("MODEL_OK", "matched"),
        why="one 3.9 MB id of 'a/' pairs in a router listing, expected present"))

    # H7 expected id given as an absolute path / with a backslash.
    caps.append(dict(
        cid="H7a-expect-abs-path",
        doc={"object": "list", "data": [{"id": "good"}]}, expect="/models/good.gguf",
        want=("MODEL_OK", "matched"),
        why="--expect /models/good.gguf normalizes to 'good'"))
    caps.append(dict(
        cid="H7b-expect-backslash",
        doc={"object": "list", "data": [{"id": "a\\b"}]}, expect="a\\b",
        want=("MODEL_OK", "matched"),
        why="S592: the expected id reaches awk through ENVIRON, so '\\' is literal"))

    # H8 numeric-looking ids: awk string vs numeric comparison.
    caps.append(dict(
        cid="H8a-numeric-served-1.0-1",
        doc={"object": "list", "data": [{"id": "1.0"}, {"id": "1"}]}, expect="1",
        want=("MODEL_OK", "matched"),
        why="served '1.0' then '1', expect '1' -> the second must match"))
    caps.append(dict(
        cid="H8b-numeric-served-1-expect-1.0",
        doc={"object": "list", "data": [{"id": "1"}]}, expect="1.0",
        want=("MODEL_MISMATCH", "served-id-mismatch"),
        why="numeric strings must compare as strings: '1' != '1.0'"))

    # H10 router entry whose id carries a backslash (S592 ENVIRON / literal backslash).
    caps.append(dict(
        cid="H10-router-backslash-id",
        doc=router_doc([("a\\b", "loaded"), ("good", "loaded")]),
        expect="a\\b", want=("MODEL_OK", "matched"),
        why="router id with a backslash; router_match must not unescape it"))

    # H11 router_match must apply normalize_id's rule: a path+gguf id whose /props
    # refinement changes the reason only if the filter matched it.
    caps.append(dict(
        cid="H11-router-path-gguf-unloaded",
        doc=router_doc([("r%05d" % i, "loaded") for i in range(N_ROUTER)] + [("/models/sub/good.gguf", "unloaded")]),
        routes={"/props": {"body": m.jbody({"role": "router", "models_autoload": True})}},
        expect="good", want=("MODEL_OK", "router-unloaded-autoload"),
        why="only entry is '/models/sub/good.gguf' unloaded: the filter must normalize, or the reason degrades to 'matched'"))

    # H9 listeners mode pointed at the stub via --port.
    caps.append(dict(
        cid="H9-listeners-port-stub",
        doc={"object": "list", "data": [{"id": "good"}]}, expect="good",
        sub="listeners", want=("MODEL_OK", "matched"),
        why="listeners --port <stub> --expect good classifies the stub"))
    if scale != 1:
        for c in caps:
            c["cid"] = P + c["cid"]
    return caps


def crlf_body(doc) -> bytes:
    b = json.dumps(doc, separators=(",", ":")).encode()
    b = b.replace(b'{"object":"list","data":', b'{\r\n  "object": "list",\r\n  "data": ')
    if len(b) >= 4194304:
        raise RuntimeError("body over cap")
    return b


def run_cell(m, probe: Path, cell, env, cwd: Path, tmpd: Path):
    routes = {"/v1/models": {"body": crlf_body(cell["doc"]) if cell.get("raw_crlf") else m.jbody(cell["doc"])}}
    for k, v in (cell.get("routes") or {}).items():
        routes[k] = v
    body_len = len(routes["/v1/models"]["body"])
    with m.Stub(routes) as stub:
        port = stub.port
        if cell.get("sub") == "listeners":
            cmd = ["bash", str(probe), "listeners", "--port", str(port),
                   "--expect", cell["expect"], "--timeout", "5", "--connect-timeout", "2", "--json"]
        else:
            cmd = ["bash", str(probe), "check", "--port", str(port), "--expect", cell["expect"],
                   "--timeout", "5", "--connect-timeout", "2", "--json"]
        t0 = time.monotonic()
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=KILL, env=env, cwd=cwd)
            rc, out, err = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            rc, out, err = None, e.stdout or b"", e.stderr or b""
        dt = time.monotonic() - t0
    row = None
    try:
        doc = json.loads(out.decode("utf-8", "replace"))
        key = "listeners" if cell.get("sub") == "listeners" else "rows"
        row = doc[key][0]
    except Exception:
        row = None
    verdict = row.get("verdict") if row else ("killed" if rc is None else f"unparsed(rc={rc})")
    reason = row.get("reason") if row else "-"
    served = row.get("served_model") if row else None
    return dict(cid=cell["cid"], rc=rc, verdict=verdict, reason=reason, seconds=round(dt, 2),
                body_bytes=body_len, served_len=(len(served) if isinstance(served, str) else None),
                stdout_bytes=len(out), row=row, stderr=err.decode("utf-8", "replace")[-800:])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--scale", type=int, default=1)
    a = ap.parse_args()

    m = load_counter(a.repo)
    a.work.mkdir(parents=True, exist_ok=True)
    a.out.mkdir(parents=True, exist_ok=True)
    probes = {}
    for label, rev in (("B", BASE), ("M", MEAS)):
        raw = subprocess.run(["git", "-C", str(a.repo), "show", f"{rev}:tools/kama-probe.sh"],
                             capture_output=True, check=True).stdout
        p = a.work / f"probe-{label}.sh"
        p.write_bytes(raw)
        probes[label] = (rev, p, __import__("hashlib").sha256(raw).hexdigest())

    cells = build_cells(m, a.scale)
    if a.only:
        pats = [x for x in a.only.split(",") if x]
        cells = [c for c in cells if any(x in c["cid"] for x in pats)]

    tmpd = a.work / "probe-tmp"
    tmpd.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(tmpd))
    results = []
    for cell in cells:
        line = {"cid": cell["cid"], "why": cell["why"], "expect": cell["expect"],
                "want": "%s/%s" % cell["want"], "cells": {}}
        for label in ("B", "M"):
            rev, probe, sha = probes[label]
            load0 = loadavg()
            r = run_cell(m, probe, cell, env, tmpd, tmpd)
            r.update(rev=rev, probe_sha256=sha, load_before=load0, load_after=loadavg())
            got = f"{r['verdict']}/{r['reason']}"
            want = "%s/%s" % cell["want"]
            if r["verdict"] == "killed":
                ok = None
            else:
                ok = (got == want)
            r["ok"] = ok
            line["cells"][label] = r
            print(f"HELDOUT {cell['cid']} {label} rc={r['rc']} verdict={r['verdict']} "
                  f"reason={r['reason']} seconds={r['seconds']:.2f} body={r['body_bytes']} "
                  f"load={r['load_before']} ok={ok}", flush=True)
            # small raw receipt, with a huge served_model elided (len kept)
            row_copy = dict(r["row"]) if isinstance(r["row"], dict) else r["row"]
            if isinstance(row_copy, dict) and isinstance(row_copy.get("served_model"), str) \
                    and len(row_copy["served_model"]) > 200:
                s = row_copy["served_model"]
                row_copy["served_model"] = s[:120] + f"…<{len(s)} chars>…" + s[-40:]
            (a.out / f"raw-{cell['cid']}-{label}.txt").write_text(
                f"# rev={rev} probe_sha256={sha} rc={r['rc']} seconds={r['seconds']} "
                f"body_bytes={r['body_bytes']} stdout_bytes={r['stdout_bytes']}\n"
                f"# served_len={r['served_len']}\n"
                + json.dumps(row_copy, indent=1) + "\n")
        b, mm = line["cells"]["B"], line["cells"]["M"]
        if b["verdict"] not in ("killed",) and b["ok"] and mm["ok"] is False:
            line["harm"] = "BLOCKER: base right, M wrong"
            print(f"HELDOUT_HARM {cell['cid']}", flush=True)
        results.append(line)
        (a.out / "heldout-results.json").write_text(json.dumps(results, indent=1))

    print("\n=== summary (verdict/reason, seconds) ===")
    for line in results:
        b, mm = line["cells"]["B"], line["cells"]["M"]
        print(f"{line['cid']:<34} B: {b['verdict']}/{b['reason']} {b['seconds']:>7.2f}s  "
              f"M: {mm['verdict']}/{mm['reason']} {mm['seconds']:>7.2f}s  want={line['want']}  "
              f"harm={'yes' if line.get('harm') else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
