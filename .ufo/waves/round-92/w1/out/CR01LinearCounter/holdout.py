#!/usr/bin/env python3
"""Held-out cells for the frozen round-92 C2 counter (CR01 review, not part of the claim).

Each cell is a legal answer the frozen counter's 15 cells do not contain. The harness imports the
frozen counter and reuses its Stub, Runner, jbody/ids_doc/router_doc and served_col, so the probe
environment (installed at <work>/probe/kama-probe.sh, cwd, TMPDIR, --timeout 5 / --connect-timeout
2) is exactly the counter's.

Cells
  H1-mixed-<n>        check, one id of n/2 `\\` then n/2 `"` (n/2+n/2 = n chars): the escape kinds
                      the L1/L2 cells test one at a time, mixed in one value.
  H2-router-90001     check, 90 000 unloaded `g` entries then one loaded `g` (L3 has 80 000,
                      L4 60 001): the loaded entry is the last line.
  H3-deep-20000       snapshot, 20 000 ids /srv/models/xNNNNN.gguf (L5: 16 000 /m/xNNNNN.gguf).
  H3-deep-12          the same rule at 12 ids (fast enough for BASE too; the rule anchor).
  H4-trailing-space   check, ids ["x ", "y"], expect "x " (no frozen cell has a trailing space).
  H5-snap-30000       snapshot, 30 000 ids /srv/xNNNNN.gguf (L5: 16 000).

Usage: holdout.py --counter FILE --work DIR --cell NAME --probe FILE --label NAME [--kill S]
Prints one JSON line: cell, label, bytes, rc, seconds, verdict, reason, served_len, served_sha256,
n_served, rule (snapshot). Exit 0 when the cell ran (the probe may still be killed: rc=null).
"""
import argparse
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


def load(path):
    spec = importlib.util.spec_from_file_location("r92counter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--cell", required=True)
    ap.add_argument("--probe", type=Path, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--kill", type=float, default=240.0)
    a = ap.parse_args()
    m = load(a.counter)
    m.KILL = a.kill
    probe = a.probe.read_bytes()
    w = a.work / f"{a.cell}-{a.label}"
    shutil.rmtree(w, ignore_errors=True)
    w.mkdir(parents=True)
    R = m.Runner(w)
    R.install(probe)
    out = {"cell": a.cell, "label": a.label, "probe_sha256": hashlib.sha256(probe).hexdigest()}

    if a.cell.startswith("H1-mixed-"):
        n = int(a.cell.rsplit("-", 1)[1])
        ids = ["\\" * (n // 2) + '"' * (n // 2)]
        body = m.jbody(m.ids_doc(ids))
        with m.Stub({"/v1/models": body}) as s:
            rc, so, dt = R.check(s.port, "good")
        row = m.row_of(so)
        served = row.get("served_model") if row else None
        out.update(bytes=len(body), rc=rc, seconds=round(dt, 2),
                   verdict=row.get("verdict") if row else None,
                   reason=row.get("reason") if row else None,
                   served_len=len(served) if isinstance(served, str) else -1,
                   served_sha256=hashlib.sha256(served.encode()).hexdigest()[:16] if isinstance(served, str) else None)
    elif a.cell == "H2-router-90001":
        entries = [("g", "unloaded", None, None)] * 90000 + [("g", "loaded", None, None)]
        body = m.jbody(m.router_doc(entries))
        with m.Stub({"/v1/models": body}) as s:
            rc, so, dt = R.check(s.port, "g")
        row = m.row_of(so)
        out.update(bytes=len(body), rc=rc, seconds=round(dt, 2), entries=len(entries),
                   verdict=row.get("verdict") if row else None,
                   reason=row.get("reason") if row else None)
    elif a.cell in ("H3-deep-20000", "H3-deep-12", "H5-snap-30000"):
        if a.cell == "H3-deep-12":
            ids = [f"/srv/models/x{i:05d}.gguf" for i in range(12)]
            expect = "x00000"
        elif a.cell == "H3-deep-20000":
            ids = [f"/srv/models/x{i:05d}.gguf" for i in range(20000)]
            expect = "x00000"
        else:
            ids = [f"/srv/x{i:05d}.gguf" for i in range(30000)]
            expect = "x00000"
        body = m.jbody(m.ids_doc(ids))
        with m.Stub({"/v1/models": body}) as s:
            rc, so, dt, tsv = R.snapshot(s.port, expect)
        col = m.served_col(tsv)
        ncol = len(col.split(",")) if col is not None else -1
        out.update(bytes=len(body), ids=len(ids), rc=rc, seconds=round(dt, 2), n_served=ncol,
                   served_len=len(col) if col is not None else -1,
                   served_sha256=hashlib.sha256(col.encode()).hexdigest()[:16] if col is not None else None,
                   served_head=(col or "")[:40])
    elif a.cell == "H4-trailing-space":
        body = m.jbody(m.ids_doc(["x ", "y"]))
        with m.Stub({"/v1/models": body}) as s:
            rc, so, dt = R.check(s.port, "x ")
        row = m.row_of(so)
        out.update(bytes=len(body), rc=rc, seconds=round(dt, 2),
                   verdict=row.get("verdict") if row else None,
                   reason=row.get("reason") if row else None,
                   served_model=repr(row.get("served_model")) if row else None)
    else:
        print(f"HOLDOUT unknown cell {a.cell}")
        return 2
    print("HOLDOUT " + json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
