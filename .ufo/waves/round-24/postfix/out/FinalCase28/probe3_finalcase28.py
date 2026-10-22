#!/usr/bin/env python3
"""FinalCase28 probe 3: in-process accounting of the diagnosis path for the
absent-citation (E) and required-hole (F) surfaces of the blobless lane.

probe2 ran E and F as subprocesses, so its call counters for those two were
empty by construction (a separate module instance).  Here both run in-process
under the same spies, so the counters are meaningful.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase28/clone")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase28/probe3")
AUDIT = CLONE / "tools" / "report-landing-audit.py"
GRID = CLONE / "tests" / "report-audit" / "promisor-grid.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pg = load(GRID, "pg_grid3")
aud = load(AUDIT, "pg_audit3")
OUT = {}


def instrument():
    state = {"missing": [], "unknown": [], "opaque": []}
    orig_missing = aud.RepoStore.missing
    orig_unc = aud.unknown_citation
    orig_op = aud.opaque_hole

    def spy_missing(self):
        state["missing"].append(str(self.path))
        return orig_missing(self)

    def spy_unc(stores, token):
        res = orig_unc(stores, token)
        state["unknown"].append({"token": token,
                                 "matched_store": str(res.path) if res
                                 else None})
        return res

    def spy_op(stores):
        res = orig_op(stores)
        state["opaque"].append({"store": str(res[0].path) if res[0] else None,
                                 "oid": res[1]})
        return res

    aud.RepoStore.missing = spy_missing
    aud.unknown_citation = spy_unc
    aud.opaque_hole = spy_op
    return state


def run_in_process(lane, fleet):
    state = instrument()
    buf, errbuf = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(errbuf):
        status = aud.main(["--lane-repo", str(lane), "--fleet-repo", str(fleet),
                           "--rounds", "1", "--json", "--no-errata"])
    out = buf.getvalue()
    doc = None
    if out.strip():
        try:
            doc = json.loads(out)
        except ValueError:
            doc = None
    return {"exit": status, "stdout_len": len(out),
            "stderr": errbuf.getvalue().strip()[-400:],
            "verdict_document": doc is not None,
            "defects": sorted((d["kind"], d["token"])
                              for r in (doc["results"] if doc else [])
                              for d in r["defects"]),
            "summary_status": doc["summary"]["status"] if doc else None,
            "calls": state}


root = SCRATCH
root.mkdir(parents=True, exist_ok=True)

tmp_e = root / "e3"
tmp_e.mkdir(parents=True, exist_ok=True)
built_e = pg.build(root, tmp_e, lane_mark="config", sources=False,
                   blobless_lane=True, fake_landed=True)
OUT["E3_absent_citation_in_process"] = run_in_process(built_e["lane"],
                                                       built_e["fleet"])

tmp_f = root / "f3"
tmp_f.mkdir(parents=True, exist_ok=True)
built_f = pg.build(root, tmp_f, lane_mark="config", blobless_lane=True)
OUT["F3_required_hole_in_process"] = run_in_process(built_f["lane"],
                                                     built_f["fleet"])

print(json.dumps(OUT, indent=1, sort_keys=True))
