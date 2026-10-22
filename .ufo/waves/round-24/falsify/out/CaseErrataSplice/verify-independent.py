#!/usr/bin/env python3
"""Independent re-derivation of PG29/PG30 (CaseErrataSplice).

Rebuilds the two fixtures with the pinned grid's own builders, then checks
the premises, the object presence/absence, the finding/token pairs, the
no-acquisition property and the twin document equality with plain git
plumbing, WITHOUT trusting the grid's own grading.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseErrataSplice/repo")
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "promisor_grid", REPO / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseErrataSplice/verify-root")
AUDIT = REPO / "tools" / "report-landing-audit.py"


def plain_git(repo, *args):
    p = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                        "-C", str(repo), *args], capture_output=True,
                       env=G.env())
    return p.returncode, p.stdout.decode(errors="replace").strip(), \
        p.stderr.decode(errors="replace").strip()


def inv(repo):
    rc, out, _ = plain_git(repo, "cat-file", "--batch-all-objects",
                           "--batch-check=%(objectname)")
    assert rc == 0
    return set(out.split())


def missing_of(repo, root):
    rc, out, _ = plain_git(repo, "rev-list", "--objects", "--missing=print",
                           "--no-object-names", root)
    assert rc == 0
    return sorted(l[1:] for l in out.split("\n") if l.startswith("?"))


def build(name, builder, **kw):
    tmp = Path(ROOT, name)
    tmp.mkdir(parents=True, exist_ok=True)
    built = G.BUILDERS[builder](ROOT, tmp, **kw) if kw else G.BUILDERS[builder](ROOT, tmp)
    return built, tmp


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)
    report = {"cases": {}}

    for name, builder in (("PG29", "c_errata_corrected_missing_sha_plain"),
                          ("PG30", "c_errata_corrected_missing_sha_promisor")):
        built, tmp = build(name, builder)
        lane, fleet = built["lane"], built["fleet"]
        shas = built["shas"]
        rec = {"builder": builder,
               "grid_premise": built["premise"],
               "errata_flag": built.get("errata")}
        # --- independent object presence/absence -----------------------
        lane_inv, fleet_inv = inv(lane), inv(fleet)
        rec["objects"] = {"lane": len(lane_inv), "fleet": len(fleet_inv)}
        rec["missing_over_tip"] = {
            "lane_master": missing_of(lane, "refs/heads/master"),
            "fleet_head": missing_of(fleet, "HEAD")}
        rec["missing_over_all_refs"] = {
            "lane": missing_of(lane, "--all"),
            "fleet": missing_of(fleet, "--all")}
        for label, sha in (("spliced", shas["spliced"]),
                           ("lane_commit", shas["lane_commit"]),
                           ("f_blob", shas["f_blob"]),
                           ("report_blob", shas["report_blob"]),
                           ("fake", G.FAKE)):
            rc_l, _, _ = plain_git(lane, "cat-file", "-e", sha + "^{object}")
            rc_f, _, _ = plain_git(fleet, "cat-file", "-e", sha + "^{object}")
            rec.setdefault("presence", {})[label] = {
                "sha": sha, "in_lane": rc_l == 0, "in_fleet": rc_f == 0}
        # spliced-token shape
        rec["spliced_shape"] = {
            "spliced": shas["spliced"],
            "equals_lane_commit_prefix15_plus_HIST_TAIL":
                shas["spliced"] == shas["lane_commit"][:15] + G.HIST_TAIL,
            "HIST_TAIL": G.HIST_TAIL,
            "len": len(shas["spliced"]),
            "is_40_hex": all(c in "0123456789abcdef" for c in shas["spliced"])}
        # errata ledger content actually in the lane object store
        rc, out, err = plain_git(lane, "show",
                                 "refs/heads/master:registry/"
                                 "report-landing-errata.tsv")
        rec["errata_file"] = {"rc": rc, "content": out, "stderr": err}
        # promisor marks, read straight from the repo config
        rc, out, _ = plain_git(lane, "config", "--list")
        rec["lane_config"] = [l for l in out.split("\n")
                              if "promisor" in l or "partialclone" in l]
        rc, out, _ = plain_git(fleet, "config", "--list")
        rec["fleet_config"] = [l for l in out.split("\n")
                               if "promisor" in l or "partialclone" in l]
        # lane commit list (author/subject) as the auditor sees it
        rc, out, _ = plain_git(lane, "log", "--format=%H%x00%an%x00%at%x00%s",
                               "refs/heads/master")
        rec["lane_log"] = out.split("\n")
        # --- run the auditor, pinned ------------------------------
        before = {"lane": lane_inv, "fleet": fleet_inv}
        argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
                "--fleet-repo", str(fleet), "--rounds", "1", "--json"]
        proc = subprocess.run(argv, capture_output=True, env=G.env(),
                              cwd=str(tmp), timeout=60)
        after = {"lane": inv(lane), "fleet": inv(fleet)}
        rec["auditor"] = {
            "argv": argv,
            "exit": proc.returncode,
            "stderr": proc.stderr.decode(errors="replace"),
            "stdout_len": len(proc.stdout),
            "objects_acquired": {
                "lane": sorted(after["lane"] - before["lane"]),
                "fleet": sorted(after["fleet"] - before["fleet"])},
            "objects_lost": {
                "lane": sorted(before["lane"] - after["lane"]),
                "fleet": sorted(before["fleet"] - after["fleet"])},
            "invariants": {
                "lane_config_after": plain_git(lane, "config", "--list")[1],
                "refs_after": plain_git(lane, "for-each-ref",
                                        "--format=%(refname)")[1],
            }}
        doc = json.loads(proc.stdout.decode(errors="replace")) \
            if proc.stdout.strip() else None
        rec["document"] = doc
        # --- exact finding/token pairs ----------------------------
        if doc:
            pairs = []
            for res in doc.get("results", []):
                for d in res.get("defects", []):
                    pairs.append({"kind": d.get("kind"), "token": d.get("token"),
                                  "corrected_by": d.get("corrected_by")})
            rec["finding_pairs"] = pairs
            rec["summary"] = doc.get("summary")
        # normalized document for twin comparison
        rec["normalised_document"] = G.normalise_document(
            proc.stdout.decode(errors="replace"), built)
        report["cases"][name] = rec

    a = report["cases"]["PG29"]
    b = report["cases"]["PG30"]
    report["twin_document_equal"] = \
        a["normalised_document"] == b["normalised_document"]
    report["twin_finding_pairs_equal"] = \
        a.get("finding_pairs") == b.get("finding_pairs")
    report["twin_exits"] = [a["auditor"]["exit"], b["auditor"]["exit"]]
    out = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseErrataSplice/verify.json")
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({
        "twin_document_equal": report["twin_document_equal"],
        "twin_finding_pairs_equal": report["twin_finding_pairs_equal"],
        "twin_exits": report["twin_exits"],
        "pg29_missing": a["missing_over_tip"],
        "pg30_missing": b["missing_over_tip"],
        "pg29_pairs": a.get("finding_pairs"),
        "pg30_pairs": b.get("finding_pairs"),
        "pg29_acquired": a["auditor"]["objects_acquired"],
        "pg30_acquired": b["auditor"]["objects_acquired"],
    }, indent=1))


if __name__ == "__main__":
    main()
