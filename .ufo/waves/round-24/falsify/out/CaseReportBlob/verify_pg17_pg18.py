#!/usr/bin/env python3
"""Bounded, offline verification of the two assigned ReportBlob rows.

Rebuilds exactly the PG17 and PG18 fixtures with the pinned grid's own
builders (tests/report-audit/promisor-grid.py, sha256 b034e159...), asserts
the missing/present objects directly, runs the pinned auditor
(tools/report-landing-audit.py, sha256 ea51bc35...), and prints the full
stderr, the object-acquisition delta and the twin-document comparison.

No network, no transport, no repository program, no execution marker.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRID = HERE / "tests" / "report-audit" / "promisor-grid.py"
AUDIT = HERE / "tools" / "report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"

spec = importlib.util.spec_from_file_location("pggrid", GRID)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

ROOT = Path(tempfile.mkdtemp(prefix="verify-pg17-18-", dir=str(HERE)))
out = {"root": str(ROOT)}


def raw_git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=G.env())
    if check and p.returncode:
        raise SystemExit(f"git {args} in {repo}: rc={p.returncode} "
                         f"{p.stderr.decode(errors='replace').strip()}")
    return p


def describe(repo, label, sha):
    p = raw_git(repo, "cat-file", "-e", sha + "^{object}", check=False)
    present = p.returncode == 0
    q = raw_git(repo, "cat-file", "-t", sha, check=False)
    kind = q.stdout.decode().strip() if present else None
    ls = raw_git(repo, "ls-tree", "HEAD", "--", REL, check=False)
    return {"label": label, "sha": sha, "present": present, "type": kind,
            "ls_tree_head_rel": ls.stdout.decode().strip()}


cases = [("PG17-missing-fleet-report-promisor", "c_missing_fleet_report_promisor"),
         ("PG18-missing-fleet-report-plain", "c_missing_fleet_report_plain")]
results = []
for name, builder in cases:
    tmp = ROOT / name
    tmp.mkdir(parents=True)
    built = G.BUILDERS[builder](ROOT, tmp)
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    prem = built["premise"]
    before = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
    code, sout, serr, timed_out = G.run_auditor(AUDIT, lane, fleet, tmp,
                                                use_errata=False)
    after = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    rb = shas["report_blob"]
    fleet_ls = raw_git(fleet, "ls-tree", "HEAD", check=False).stdout.decode()
    fleet_show = raw_git(fleet, "show", f"HEAD:{REL}", check=False)
    row = {
        "case": name,
        "fleet_promisor": prem["fleet_promisor"],
        "lane_promisor": prem["lane_promisor"],
        "lane_missing": prem["lane_missing"],
        "fleet_missing": prem["fleet_missing"],
        "fleet_missing_count": len(prem["fleet_missing"]),
        "report_blob": rb,
        "report_blob_is_missing": rb in prem["fleet_missing"],
        "report_blob_present_in_fleet": describe(fleet, "fleet", rb),
        "report_blob_present_in_lane": describe(lane, "lane", rb),
        "fleet_head_tree": shas["fleet_tip_tree"],
        "fleet_head_tree_present": describe(fleet, "tree", shas["fleet_tip_tree"]),
        "fleet_ls_tree_HEAD": fleet_ls,
        "fleet_show_report_rc": fleet_show.returncode,
        "fleet_show_report_err": fleet_show.stderr.decode(errors="replace").strip(),
        "lane_commit_present": describe(lane, "lane_commit", shas["lane_commit"]),
        "exit": code,
        "stdout_bytes": len(sout),
        "stdout": sout[:400],
        "stderr_full": serr.strip(),
        "stderr_starts_cne": serr.startswith("could-not-evaluate:"),
        "stdout_is_json": (lambda t: (lambda: True)() if False else None)(sout),
        "timed_out": timed_out,
        "objects_acquired": acquired,
        "forbidden_reason_present": [f for f in ("partial clone (", "promisor pack")
                                    if f in serr],
        "names_any_of_match": {n: (n in serr) for n in (rb, REL)},
        "reason_class_unavailable_term": [t for t in G.REASON_CLASSES["unavailable"]
                                           if t in serr.lower()],
    }
    try:
        json.loads(sout)
        row["stdout_is_json"] = True
    except ValueError:
        row["stdout_is_json"] = False
    results.append(row)

out["rows"] = results
a, b = results
out["twin"] = {
    "document_a_is_none": a["document"] if False else None,
    "stdout_a": a["stdout"], "stdout_b": b["stdout"],
    "stdout_equal": a["stdout"] == b["stdout"],
    "stdout_empty_both": (not a["stdout"].strip()) and (not b["stdout"].strip()),
    "stderr_equal_raw": a["stderr_full"] == b["stderr_full"],
}
print(json.dumps(out, indent=1))
