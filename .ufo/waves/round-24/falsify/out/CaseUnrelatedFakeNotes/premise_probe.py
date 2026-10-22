#!/usr/bin/env python3
"""Independent premise/observation probe for the UnrelatedFakeNotes family.

Read-only against the pinned clone; builds its own offline fixtures under the
scratch root.  It does NOT change any expected cell and does not touch the
lane's production .jj/index, fleet or routing.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

GRID = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/repo"
            "/tests/report-audit/promisor-grid.py")
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes"
            "/probe-root")
REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/repo")
AUDIT = REPO / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)


def sh(*args, cwd=None):
    p = subprocess.run(args, capture_output=True, cwd=cwd,
                       env={k: v for k, v in os.environ.items()
                            if not k.startswith("GIT_")})
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def probe(builder_name, tag):
    tmp = ROOT / tag
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    built = pg.BUILDERS[builder_name](ROOT, tmp)
    lane, fleet, shas = built["lane"], built["fleet"], built["shas"]
    out = {"builder": builder_name, "lane": str(lane), "fleet": str(fleet)}
    prem = built["premise"]
    out["premise"] = prem
    out["shas"] = shas
    # --- actual missing / present objects, independently computed
    def inv(repo):
        rc, so, _ = sh("git", "-C", str(repo), "cat-file",
                       "--batch-all-objects", "--batch-check=%(objectname)")
        return set(so.split())
    def types(repo):
        rc, so, _ = sh("git", "-C", str(repo), "cat-file",
                       "--batch-all-objects",
                       "--batch-check=%(objectname) %(objecttype)")
        return dict(l.split() for l in so.split("\n") if l.strip())
    out["lane_objects"] = len(inv(lane))
    out["fleet_objects"] = len(inv(fleet))
    tmap = types(lane)
    # the blob hole: which object id is missing
    out["missing_oids"] = prem["lane_missing"]
    out["missing_types_in_store"] = {oid: tmap.get(oid, "<absent>")
                                     for oid in prem["lane_missing"]}
    out["missing_is_blob"] = all(tmap.get(oid) is None for oid in
                                 prem["lane_missing"])
    # opaque classification as the auditor computes it: blob:none walk
    rc, so, se = sh("git", "-C", str(lane), "--no-lazy-fetch",
                    "-c", "core.commitGraph=false", "rev-list", "--objects",
                    "--missing=print", "--no-object-names",
                    "--filter=blob:none", "--stdin",
                    stdin=None) if False else (0, "", "")
    roots = "\n".join(sorted(tmap)) + "\n"
    p = subprocess.run(["git", "-C", str(lane), "--no-lazy-fetch",
                        "-c", "core.commitGraph=false", "rev-list", "--objects",
                        "--missing=print", "--no-object-names",
                        "--filter=blob:none", "--stdin"],
                       input=roots.encode(), capture_output=True)
    opaque = sorted(l[1:] for l in p.stdout.decode().split("\n")
                    if l.startswith("?"))
    out["opaque_missing_nonleaf"] = opaque
    out["opaque_empty"] = not opaque
    # present/absent of the tokens that matter
    for label, oid in (("fake", pg.FAKE),
                       ("lane_commit", shas["lane_commit"]),
                       ("unused_blob", shas.get("unused_blob")),
                       ("fleet_commit", shas.get("fleet_commit")),
                       ("report_blob", shas.get("report_blob"))):
        present = []
        for repo in (lane, fleet):
            rc, so, se = sh("git", "-C", str(repo), "--no-lazy-fetch",
                            "--no-replace-objects", "cat-file", "-e",
                            oid + "^{object}") if oid else (1, "", "")
            present.append(rc == 0)
        out[f"{label}_present"] = present
    # promisor marking facts
    out["lane_promisor_facts"] = pg.promisor_facts(lane)
    out["fleet_promisor_facts"] = pg.promisor_facts(fleet)
    # --- run the auditor and observe
    before = {"lane": inv(lane), "fleet": inv(fleet)}
    code, so, se, to = pg.run_auditor(AUDIT, lane, fleet, tmp, False)
    after = {"lane": inv(lane), "fleet": inv(fleet)}
    out["auditor_exit"] = code
    out["auditor_stderr"] = se.strip()
    out["auditor_stdout_len"] = len(so)
    out["timed_out"] = to
    out["objects_acquired"] = {k: sorted(after[k] - before[k]) for k in after}
    try:
        doc = json.loads(so)
    except ValueError:
        doc = None
    out["document"] = doc
    out["defects"] = pg.observed_defects(so)[0]
    return built, out


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    results = {}
    for builder, tag in (("c_unused_missing_blob_fabricated_notes_promisor",
                          "PG41"),
                         ("c_unused_missing_blob_fabricated_notes_plain",
                          "PG42")):
        built, res = probe(builder, tag)
        results[tag] = res
        (ROOT / f"{tag}.json").write_text(
            json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps(results, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
