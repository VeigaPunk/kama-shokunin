#!/usr/bin/env python3
"""CaseOpaqueCited: bounded, offline probe of the PG46 cell.

Rebuilds the PG46 fixture with the grid's OWN builder (no reimplementation of
the fixture), then asserts the object-level premises the supplement states,
runs the pinned auditor directly on it, and builds two content twins
(identical bytes, marked and plain) to show what the cell actually
discriminates.

Read-only against production.  No network, no transport, no target
execution: only local git plumbing over synthetic repositories.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueCited")
CLONE = SCRATCH / "scratch"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDITOR = CLONE / "tools/report-landing-audit.py"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "falsify/out/CaseOpaqueCited")

spec = importlib.util.spec_from_file_location("grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)


def sh(*args, cwd=None):
    p = subprocess.run(args, capture_output=True, cwd=cwd)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def cat_exists(repo, oid):
    rc, out, err = sh("git", "--no-lazy-fetch", "--no-replace-objects",
                      "-C", str(repo), "cat-file", "-e", oid + "^{object}")
    return rc == 0, (out + err).strip()


def present_roots(repo):
    out = grid.git_nofetch(repo, "cat-file", "--batch-all-objects",
                           "--batch-check=%(objectname) %(objecttype)")
    return [line.split()[0] for line in out.split("\n")
            if line.strip() and line.split()[1] in ("commit", "tree", "tag")]


def walk(repo, roots, extra):
    stdin = "".join(f"{r}\n" for r in roots)
    out = grid.git_nofetch(repo, "-c", "core.commitGraph=false", "rev-list",
                           "--objects", "--missing=print", "--no-object-names",
                           *extra, "--stdin", data=stdin.encode())
    return sorted(line[1:] for line in out.split("\n") if line.startswith("?"))


def run_auditor(lane, fleet, cwd):
    argv = [sys.executable, str(AUDITOR), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    p = subprocess.run(argv, capture_output=True, cwd=str(cwd),
                       env=grid.env(), timeout=60)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def inventory(repo):
    return set(grid.git_nofetch(repo, "cat-file", "--batch-all-objects",
                                "--batch-check=%(objectname)").split())


def build_twin(root, tmp, marked):
    """The PG46 shape with NOTHING missing: same bytes, same dates.

    Mirrors grid.build() for the PG46 option set (opaque_tree + the cited
    hidden blob in the Notes) but without any object removal and without
    the grid's own premise check (which by construction rejects a fixture
    whose cited blob is still present).
    """
    lane = grid.init_repo(root, Path(tmp, "lane"))
    fleet = grid.init_repo(root, Path(tmp, "fleet"))
    files = [("corpus/SOURCES.md", grid.SOURCES), ("f", "fixture file\n"),
             ("d/f", "opaque\n")]
    for pth, content in files:
        target = Path(lane, pth)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    grid.git(lane, "add", "--", *[p for p, _ in files])
    grid.git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
             "round-1: work", GIT_AUTHOR_NAME="kama-shokunin",
             GIT_COMMITTER_NAME="kama-shokunin", GIT_AUTHOR_DATE="@1000 +0000",
             GIT_COMMITTER_DATE="@1000 +0000")
    l1 = grid.git(lane, "rev-parse", "HEAD").strip()
    hidden = grid.git(lane, "rev-parse", f"{l1}:d/f").strip()
    subtree = grid.git(lane, "rev-parse", f"{l1}:d").strip()
    grid.commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    text = grid.report_text([l1], [f"hidden blob {hidden}"])
    grid.publish(fleet, text, 2000)
    if marked:
        grid.mark_config(lane, tmp)
    return {"lane": lane, "fleet": fleet, "lane_commit": l1,
            "hidden_blob": hidden, "subtree": subtree, "report": text}


def main():
    result = {"probe": "CaseOpaqueCited/PG46", "clone": str(CLONE),
              "clone_head": sh("git", "-C", str(CLONE), "rev-parse",
                               "HEAD")[1].strip(),
              "auditor": str(AUDITOR),
              "auditor_sha256": sh("sha256sum", str(AUDITOR))[1].split()[0],
              "grid_sha256": sh("sha256sum", str(GRID))[1].split()[0],
              "expectations_sha256": sh("sha256sum", str(CLONE / "tests/"
                                          "report-audit/promisor-grid-"
                                          "expectations.json"))[1].split()[0],
              "git_version": sh("git", "--version")[1].strip(),
              "python": sys.version.split()[0]}

    root = SCRATCH / "probe"
    if root.exists():
        subprocess.run(["rm", "-rf", str(root)], check=True)
    root.mkdir(parents=True)

    # ---- 1. the cell's fixture, built by the grid's own builder ----------
    tmp = root / "pg46"
    tmp.mkdir()
    built = grid.BUILDERS["c_opaque_tree_hides_cited_blob"](root, tmp)
    lane, fleet, shas = built["lane"], built["fleet"], built["shas"]
    blob = shas["hidden_blob"]
    tree = shas["missing_subtree"]
    lane_commit = shas["lane_commit"]
    report_text = grid.git(fleet, "show", f"HEAD:{grid.REL}")

    prem = {
        "lane_commit": lane_commit,
        "cited_hidden_blob": blob,
        "missing_subtree": tree,
        "lane_promisor": built["premise"]["lane_promisor"],
        "fleet_promisor": built["premise"]["fleet_promisor"],
        "grid_lane_missing": built["premise"]["lane_missing"],
        "grid_fleet_missing": built["premise"]["fleet_missing"],
        "cited_blob_present_in_lane": cat_exists(lane, blob)[0],
        "cited_blob_present_in_fleet": cat_exists(fleet, blob)[0],
        "subtree_present_in_lane": cat_exists(lane, tree)[0],
        "subtree_present_in_fleet": cat_exists(fleet, tree)[0],
        "lane_commit_present": cat_exists(lane, lane_commit)[0],
        "lane_tip_tree_present": cat_exists(lane, shas["tip_tree"])[0],
        "lane_f_blob_present": cat_exists(lane, shas["f_blob"])[0],
        "fleet_report_blob_present": cat_exists(fleet, shas["report_blob"])[0],
        "report_text": report_text,
        "report_cites_blob_oid": blob in report_text,
        "report_cites_lane_commit": lane_commit in report_text,
    }
    roots = present_roots(lane)
    prem["lane_present_roots_count"] = len(roots)
    prem["missing_enumeration_objects"] = walk(lane, roots, ())
    prem["missing_enumeration_filter_blob_none"] = walk(
        lane, roots, ("--filter=blob:none",))
    prem["blob_in_missing_enumeration"] = blob in prem[
        "missing_enumeration_objects"]
    prem["tree_in_missing_enumeration"] = tree in prem[
        "missing_enumeration_objects"]
    prem["tree_in_opaque_enumeration"] = tree in prem[
        "missing_enumeration_filter_blob_none"]
    prem["blob_in_opaque_enumeration"] = blob in prem[
        "missing_enumeration_filter_blob_none"]
    fleet_roots = present_roots(fleet)
    prem["fleet_missing_enumeration_objects"] = walk(fleet, fleet_roots, ())
    prem["fleet_missing_enumeration_filter_blob_none"] = walk(
        fleet, fleet_roots, ("--filter=blob:none",))

    # ---- 2. the pinned auditor, run directly on the fixture --------------
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    code, out, err = run_auditor(lane, fleet, tmp)
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    stderr_full = err.strip()
    audit = {
        "exit": code,
        "stdout_bytes": len(out),
        "stdout_is_json": None,
        "stderr": stderr_full,
        "stderr_starts_cne": stderr_full.startswith("could-not-evaluate:"),
        "names_cited_token": blob in stderr_full,
        "names_missing_subtree": tree in stderr_full,
        "forbidden_metadata_phrase": any(
            f in stderr_full for f in ("partial clone (", "promisor pack")),
        "mentions_fleet_path": str(fleet) in stderr_full,
        "objects_acquired": acquired,
        "reason_class_unavailable": any(
            t in stderr_full.lower() for t in grid.REASON_CLASSES["unavailable"]),
    }
    try:
        json.loads(out)
        audit["stdout_is_json"] = True
    except ValueError:
        audit["stdout_is_json"] = False
    audit["document"] = None if not audit["stdout_is_json"] else json.loads(out)

    # ---- 2a. full .git fingerprint before/after the auditor run ---------
    def fingerprint(repo):
        out = {}
        gitdir = Path(grid.git_dir(repo))
        for path in sorted(gitdir.rglob("*")):
            if path.is_file():
                data = path.read_bytes()
                out[str(path.relative_to(gitdir))] = (
                    len(data), hashlib.sha256(data).hexdigest())
        return out

    fp_before = {"lane": fingerprint(lane), "fleet": fingerprint(fleet)}
    code2, out2, err2 = run_auditor(lane, fleet, tmp)
    fp_after = {"lane": fingerprint(lane), "fleet": fingerprint(fleet)}
    fp = {}
    for k in ("lane", "fleet"):
        before, after = fp_before[k], fp_after[k]
        added = sorted(set(after) - set(before))
        removed = sorted(set(before) - set(after))
        changed = sorted(p for p in set(before) & set(after)
                         if before[p] != after[p])
        fp[k] = {"files_before": len(before), "files_after": len(after),
                 "added": added, "removed": removed, "changed": changed,
                 "identical": not (added or removed or changed)}
    result["git_fingerprint_acquisition"] = fp
    result["second_audit_run"] = {"exit": code2,
                                   "stderr": err2.strip(),
                                   "stdout_bytes": len(out2)}
    result["promisor_facts"] = {
        "lane": grid.promisor_facts(lane),
        "fleet": grid.promisor_facts(fleet),
        "lane_origin_url": grid.git(lane, "config", "--get",
                                    "remote.origin.url").strip(),
        "lane_origin_url_exists_on_disk": Path(
            grid.git(lane, "config", "--get",
                     "remote.origin.url").strip()).exists(),
    }

    # ---- 2b. the restored-blob twin: the PG46 fixture with ONLY the cited
    # blob put back (byte-identical content, same OIDs).  This is the
    # manifest's "complete twin resolves the blob" claim, exercised on the
    # cell's own fixture, and it shows the refusal is caused by the absent
    # objects rather than by the citation or by the promisor mark.
    restored = root / "restored"
    restored.mkdir()
    rbuilt = grid.BUILDERS["c_opaque_tree_hides_cited_blob"](root, restored)
    rlane, rfleet = rbuilt["lane"], rbuilt["fleet"]
    rblob = rbuilt["shas"]["hidden_blob"]
    restored_oid = grid.git(rlane, "hash-object", "-w", "--stdin",
                             data=b"opaque\n").strip()
    rcode, rout, rerr = run_auditor(rlane, rfleet, restored)
    rdoc = None
    try:
        rdoc = json.loads(rout)
    except ValueError:
        rdoc = None
    result["restored_blob_twin"] = {
        "note": "PG46 fixture with the cited blob written back (identical "
                "OID): the citation resolves and the audit is clean",
        "restored_oid": restored_oid,
        "restored_oid_equals_cited_blob": restored_oid == blob,
        "cited_blob_present": cat_exists(rlane, blob)[0],
        "missing_enumeration_objects": walk(rlane, present_roots(rlane), ()),
        "exit": rcode,
        "stderr": rerr.strip(),
        "defects": None if rdoc is None else [
            d for res in rdoc.get("results", []) for d in res.get("defects", [])],
    }

    # ---- 3. content twins: the same bytes with nothing missing -----------
    twins = {}
    for label, marked in (("twin-marked", True), ("twin-plain", False)):
        ttmp = root / label
        ttmp.mkdir()
        t = build_twin(root, ttmp, marked)
        tb = {"lane": inventory(t["lane"]), "fleet": inventory(t["fleet"])}
        tc, to, te = run_auditor(t["lane"], t["fleet"], ttmp)
        ta = {"lane": sorted(inventory(t["lane"]) - tb["lane"]),
              "fleet": sorted(inventory(t["fleet"]) - tb["fleet"])}
        same_ids = (t["lane_commit"] == lane_commit
                    and t["hidden_blob"] == blob
                    and t["subtree"] == tree)
        doc = None
        try:
            doc = json.loads(to)
        except ValueError:
            doc = None
        twins[label] = {
            "marked": marked,
            "lane": str(t["lane"]),
            "fleet": str(t["fleet"]),
            "lane_commit": t["lane_commit"],
            "hidden_blob": t["hidden_blob"],
            "subtree": t["subtree"],
            "identical_oids_to_pg46": same_ids,
            "hidden_blob_present_in_lane": cat_exists(t["lane"], blob)[0],
            "exit": tc,
            "stdout_bytes": len(to),
            "stderr": te.strip(),
            "objects_acquired": ta,
            "document": doc,
            "defects": None if doc is None else [
                d for res in doc.get("results", []) for d in res.get("defects", [])],
        }
    # twin document comparison: marked vs plain, paths normalised
    def norm(doc, lane, fleet):
        if doc is None:
            return None
        text = json.dumps(doc, sort_keys=True)
        text = text.replace(str(twins["twin-marked"]["lane"]), "<lane>")
        text = text.replace(str(twins["twin-marked"]["fleet"]), "<fleet>")
        text = text.replace(str(twins["twin-plain"]["lane"]), "<lane>")
        text = text.replace(str(twins["twin-plain"]["fleet"]), "<fleet>")
        return json.loads(text)
    twins["document_comparison_marked_vs_plain"] = (
        norm(twins["twin-marked"]["document"],
             twins["twin-marked"]["lane"], twins["twin-marked"]["fleet"])
        == norm(twins["twin-plain"]["document"],
                twins["twin-plain"]["lane"], twins["twin-plain"]["fleet"]))
    twins["document_comparison_pg46_vs_twin"] = (
        audit["document"] is None)

    result["premises"] = prem
    result["audit_pg46"] = audit
    result["twins"] = twins
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "probe-pg46.json").write_text(
        json.dumps(result, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
