#!/usr/bin/env python3
"""Bounded, offline probe of the apply_errata / refuse_unknown boundary.

Scope (one assigned check, no full grid):
  * an ordinary absent fake corrected by an authorized ledger row stays a
    real corrected finding (clean exit 0, uncorrected defects empty);
  * actual unavailable content is NOT rescued by a ledger row: the refusal
    wins and the reason is content-derived;
  * the errata ledger's verdict path (errata-invalid) is compared with its
    refusal path for the same content, selected vs unselected round.

Fixtures come from the round-24 grid's own builder (tests/report-audit/
promisor-grid.py), so the shapes are the oracle's shapes (PG29/PG30/PG34).
No network, no transport, no repository program, no lazy fetch.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary")
GRID_PATH = BASE / "tests/report-audit/promisor-grid.py"
AUDITOR = BASE / "tools/report-landing-audit.py"
ROOT = BASE / "fx"
OUT = BASE / "out"
FAKE = "0123456789abcdef0123456789abcdef01234567"

os.environ["TMPDIR"] = str(BASE / "tmp")
Path(os.environ["TMPDIR"]).mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("grid", GRID_PATH)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def add_errata(lane, row):
    """Commit one ledger row into the lane's committed errata file."""
    grid.commit(lane, "fixture", 1600, "errata",
                "registry/report-landing-errata.tsv", row)


def run_arm(name, opts, rows=(), drops=(), note="", use_errata=None):
    """One bounded arm: build the fixture, apply the ledger rows and the
    object drops, run the candidate auditor once, record the observation."""
    tmp = ROOT / name
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    built = grid.build(ROOT, tmp, **opts)
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    for row in rows:
        add_errata(lane, row.replace("@BLOB@", shas["f_blob"])
                   .replace("@COMMIT@", shas["lane_commit"]))
    for key in drops:
        grid.drop_object(lane, shas[key])
    if use_errata is None:
        use_errata = bool(rows) or bool(opts.get("errata"))
    code, out, err, timed_out = grid.run_auditor(AUDITOR, lane, fleet, tmp,
                                                 use_errata=use_errata)
    uncorrected, raw = grid.observed_defects(out)
    try:
        summary = json.loads(out).get("summary")
    except ValueError:
        summary = None
    obs = {
        "arm": name,
        "note": note,
        "exit": code,
        "timed_out": timed_out,
        "stderr": err.strip(),
        "uncorrected_defects": uncorrected,
        "raw_defects": raw,
        "summary": summary,
        "rows": [r.strip() for r in rows],
        "dropped": [shas.get(k) for k in drops],
        "lane_commit": shas.get("lane_commit"),
        "premise": built["premise"],
    }
    (OUT / f"{name}.json").write_text(json.dumps(obs, indent=1, sort_keys=True),
                                      encoding="utf-8")
    print(json.dumps({k: obs[k] for k in
                      ("arm", "exit", "stderr", "uncorrected_defects",
                       "raw_defects", "summary")}, indent=1, sort_keys=True))
    return obs


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {a for a in args.only.split(",") if a}
    OUT.mkdir(parents=True, exist_ok=True)
    ROOT.mkdir(parents=True, exist_ok=True)
    arms = {}

    def want(name):
        return not only or name in only

    # A1 control, PG34 plain shape: the report cites a blob the store
    # references but cannot serve; no ledger row.
    if want("A1"):
        arms["A1_control_pg34_plain"] = run_arm(
            "A1_control_pg34_plain", dict(cited_blob=True), drops=("f_blob",),
            note="PG34 plain shape: the report cites a blob the store "
                 "references but cannot serve; no ledger row. Expected exit "
                 "2 with a content-derived reason naming the blob.")

    # A2 COUNTEREXAMPLE: the same unavailable cited blob, plus an authorized
    # ledger row that claims to correct exactly that citation.
    if want("A2"):
        arms["A2_counterexample_unavailable_rescued"] = run_arm(
            "A2_counterexample_unavailable_rescued", dict(cited_blob=True),
            rows=("1\tunresolved-full-hash\t@BLOB@\t@COMMIT@\tev\n",),
            drops=("f_blob",),
            note="COUNTEREXAMPLE: the same unavailable cited blob, with an "
                 "authorized errata row (round 1, unresolved-full-hash, "
                 "token=<cited blob>, correction=<real lane commit>). "
                 "Expected: exit 2 -- a ledger row must not rescue "
                 "unavailable content. Exit 0 would be a false clean.")

    # A3 positive control, PG29 plain shape: ordinary absent fake + ledger.
    if want("A3"):
        arms["A3_pg29_errata_corrected_plain"] = run_arm(
            "A3_pg29_errata_corrected_plain", dict(errata=True),
            note="PG29 plain shape: the report cites a spliced 40-hex that "
                 "no audited repository holds; the lane ledger carries the "
                 "correcting row. Expected exit 0, no uncorrected defect; "
                 "the defect stays in the raw list as corrected.")

    # A4 PG30 shape: the same fixture with a promisor-marked lane.
    if want("A4"):
        arms["A4_pg30_errata_corrected_promisor"] = run_arm(
            "A4_pg30_errata_corrected_promisor",
            dict(errata=True, lane_mark="config"),
            note="PG30 shape: the same fixture with a promisor-marked lane. "
                 "Expected exit 0: promisor metadata alone changes no "
                 "verdict and the authorized errata still corrects the "
                 "ordinary absent fake.")

    # A5 ledger scope: an out-of-scope (unselected round) row with an
    # unresolvable correction.
    if want("A5"):
        arms["A5_unselected_round_unresolvable_correction"] = run_arm(
            "A5_unselected_round_unresolvable_correction", dict(),
            rows=(f"2\tunresolved-full-hash\t{FAKE}\t"
                  "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\tev\n",),
            note="The audited population is round 1 only; the ledger carries "
                 "a round-2 row whose correction is a fabricated absent hex. "
                 "Expected: no effect on the verdict (exit 0). "
                 "errata-unmatched is scoped to selected rounds since round "
                 "21; errata-invalid is not.")

    # A6/A7: the ledger's own path. The report is CLEAN (it does not cite
    # the unavailable object), and only the ledger row names it: as the
    # correction in an unselected round, and as the correction in the
    # audited round. The same content must not be a verdict in one case and
    # a refusal in the other.
    if want("A6"):
        arms["A6_unavailable_correction_unselected_round"] = run_arm(
            "A6_unavailable_correction_unselected_round", dict(),
            rows=(f"2\tunresolved-full-hash\t{FAKE}\t@BLOB@\tev\n",),
            drops=("f_blob",),
            note="The report is clean; only the ledger row names the "
                 "unavailable object, as the correction of a round-2 "
                 "(unselected) row. Expected: no effect on the verdict, or a "
                 "refusal that names the object -- never a verdict that the "
                 "correction is not a commit.")
    if want("A7"):
        arms["A7_unavailable_correction_selected_round"] = run_arm(
            "A7_unavailable_correction_selected_round", dict(),
            rows=(f"1\tunresolved-full-hash\t{FAKE}\t@BLOB@\tev\n",),
            drops=("f_blob",),
            note="The report is clean; only the ledger row names the "
                 "unavailable object, as the correction of a round-1 "
                 "(audited) row. Expected exit 2 with a content-derived "
                 "reason naming it.")

    meta = {
        "auditor": str(AUDITOR),
        "auditor_sha256": sha256(AUDITOR),
        "grid": str(GRID_PATH),
        "grid_sha256": sha256(GRID_PATH),
        "base": "2e254a1763a9c08aa07fc53081287f506c447d84",
        "arms": {k: {"exit": v["exit"], "stderr": v["stderr"],
                     "uncorrected_defects": v["uncorrected_defects"],
                     "raw_defects": v["raw_defects"],
                     "summary": v["summary"]}
                 for k, v in arms.items()},
    }
    (OUT / "summary.json").write_text(json.dumps(meta, indent=1, sort_keys=True),
                                      encoding="utf-8")
    print(json.dumps(meta["arms"], indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
