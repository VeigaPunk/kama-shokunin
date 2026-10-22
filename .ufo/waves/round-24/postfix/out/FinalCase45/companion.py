#!/usr/bin/env python3
"""FinalCase45 supplemental: metadata-only companion for PG46.

Builds the PG46 fixture with the PINNED grid's own builder, filesystem-copies
the UNRUN fixture, strips ONLY the promisor metadata from the copy, attests
equal no-lazy object inventories and the same missing-object premise, then runs
the PINNED auditor on both metadata variants.  No manifest edit, no cell.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase45/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase45/companion")
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase45/out")

spec = importlib.util.spec_from_file_location("pgrid", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

doc = {"pin": {"clone": str(CLONE),
               "head": subprocess.run(["git", "-C", str(CLONE), "rev-parse",
                                       "HEAD"], capture_output=True,
                                      text=True).stdout.strip(),
               "grid_sha256": hashlib.sha256(GRID.read_bytes()).hexdigest(),
               "auditor_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest()},
       "builder": "c_opaque_tree_hides_cited_blob"}


def copytree(src, dst):
    shutil.copytree(src, dst, symlinks=False)


def strip_promisor(repo):
    """Remove ONLY the promisor metadata the builder installed.

    Configuration keys that declare promisor/partial-clone state and paired
    .promisor markers.  remote.origin.url (the local origin) is left alone.
    """
    removed = []
    for key in ("remote.origin.promisor", "extensions.partialclone",
                "remote.origin.partialclonefilter"):
        p = subprocess.run(["git", "-C", str(repo), "config", "--unset-all",
                            key], capture_output=True, text=True)
        if p.returncode == 0:
            removed.append(key)
    pack = pg.git_dir(repo) / "objects" / "pack"
    if pack.is_dir():
        for marker in sorted(pack.glob("*.promisor")):
            marker.unlink()
            removed.append(marker.name)
    return removed


def config_dump(repo):
    p = subprocess.run(["git", "-C", str(repo), "config", "--null", "--list"],
                       capture_output=True)
    return sorted(e for e in p.stdout.decode(errors="replace").split("\0") if e)


def refs_dump(repo):
    p = subprocess.run(["git", "-C", str(repo), "for-each-ref",
                        "--format=%(refname) %(objectname)"], capture_output=True)
    return sorted(p.stdout.decode(errors="replace").split("\n"))


def run_auditor(lane, fleet, cwd):
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, cwd=str(cwd), env=pg.env(),
                          timeout=60)
    return {"argv": argv, "exit": proc.returncode,
            "stdout": proc.stdout.decode(errors="replace"),
            "stderr": proc.stderr.decode(errors="replace")}


def norm(text, subs):
    for a, b in subs:
        text = text.replace(a, b)
    return text


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)
    tmp = ROOT / "case"
    tmp.mkdir()
    built = pg.BUILDERS["c_opaque_tree_hides_cited_blob"](ROOT, tmp)
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    doc["shas"] = {k: v for k, v in shas.items()}
    doc["premise_builder"] = built["premise"]

    # the UNRUN fixture is copied now, before any auditor runs
    plain = ROOT / "plain"
    plain.mkdir()
    copytree(lane, plain / "lane")
    copytree(fleet, plain / "fleet")
    doc["removed_promisor_metadata"] = strip_promisor(plain / "lane")
    strip_promisor(plain / "fleet")

    # ---------------- attestations
    inv = {}
    for label, a, b in (("lane", lane, plain / "lane"),
                        ("fleet", fleet, plain / "fleet")):
        inv[label] = {
            "marked_inventory": sorted(pg.object_inventory(a)),
            "plain_inventory": sorted(pg.object_inventory(b)),
            "inventory_equal": pg.object_inventory(a) == pg.object_inventory(b),
            "marked_missing": pg.missing_objects(a, "refs/heads/master")
            if label == "lane" else pg.missing_objects(a, "HEAD"),
            "plain_missing": pg.missing_objects(b, "refs/heads/master")
            if label == "lane" else pg.missing_objects(b, "HEAD"),
            "marked_promisor": pg.promisor_facts(a),
            "plain_promisor": pg.promisor_facts(b),
            "marked_refs": refs_dump(a),
            "plain_refs": refs_dump(b),
            "refs_equal": refs_dump(a) == refs_dump(b),
            "marked_config": config_dump(a),
            "plain_config": config_dump(b),
        }
        inv[label]["missing_equal"] = (inv[label]["marked_missing"]
                                       == inv[label]["plain_missing"])
    doc["attestations"] = inv

    # the premise the cell is about
    doc["premise_check"] = {
        "hidden_blob_present_lane": pg.object_exists(lane, shas["hidden_blob"]),
        "hidden_blob_present_plain_lane": pg.object_exists(plain / "lane",
                                                           shas["hidden_blob"]),
        "hidden_blob_present_fleet": pg.object_exists(fleet, shas["hidden_blob"]),
        "missing_subtree_present_lane": pg.object_exists(lane,
                                                         shas["missing_subtree"]),
        "missing_subtree_present_plain_lane": pg.object_exists(plain / "lane",
                                                               shas["missing_subtree"]),
        "lane_commit_present_lane": pg.object_exists(lane, shas["lane_commit"]),
        "lane_commit_present_plain_lane": pg.object_exists(plain / "lane",
                                                           shas["lane_commit"]),
        "report_blob_present_fleet": pg.object_exists(fleet,
                                                      shas["report_blob"]),
        "origin_url": [e for e in config_dump(lane) if "origin" in e],
        "origin_url_plain": [e for e in config_dump(plain / "lane")
                             if "origin" in e],
    }
    url_marked = [e for e in config_dump(lane) if e.startswith("remote.origin.url")]
    url_plain = [e for e in config_dump(plain / "lane")
                 if e.startswith("remote.origin.url")]
    doc["premise_check"]["origin_url_equal"] = url_marked == url_plain
    doc["premise_check"]["origin_url_on_disk_exists"] = [
        (e.split("\n", 1)[1], Path(e.split("\n", 1)[1]).exists())
        for e in url_plain]
    # the report text the audit reads
    rel = ".ufo/reports/round-1/kama.md"
    p = subprocess.run(["git", "-C", str(fleet), "show", f"HEAD:{rel}"],
                       capture_output=True, text=True)
    doc["report_text"] = p.stdout
    doc["report_cites_hidden_blob"] = shas["hidden_blob"] in p.stdout

    # ---------------- two metadata variants, same pinned auditor
    before = {"marked": {"lane": pg.object_inventory(lane),
                         "fleet": pg.object_inventory(fleet)},
              "plain": {"lane": pg.object_inventory(plain / "lane"),
                        "fleet": pg.object_inventory(plain / "fleet")}}
    runs = {}
    runs["marked"] = run_auditor(lane, fleet, tmp)
    runs["plain"] = run_auditor(plain / "lane", plain / "fleet", ROOT / "plain")
    after = {"marked": {"lane": pg.object_inventory(lane),
                        "fleet": pg.object_inventory(fleet)},
             "plain": {"lane": pg.object_inventory(plain / "lane"),
                       "fleet": pg.object_inventory(plain / "fleet")}}
    for k in runs:
        runs[k]["objects_acquired"] = {
            side: sorted(after[k][side] - before[k][side]) for side in after[k]}
        runs[k]["stdout_is_json"] = None
        try:
            json.loads(runs[k]["stdout"])
            runs[k]["stdout_is_json"] = True
        except ValueError:
            runs[k]["stdout_is_json"] = False
        runs[k]["has_verdict_document"] = bool(runs[k]["stdout"].strip())
        runs[k]["stderr_normalized"] = norm(
            runs[k]["stderr"], [(str(lane), "<lane>"), (str(fleet), "<fleet>"),
                                (str(plain / "lane"), "<lane>"),
                                (str(plain / "fleet"), "<fleet>")])
    doc["runs"] = runs
    doc["comparison"] = {
        "exit_equal": runs["marked"]["exit"] == runs["plain"]["exit"],
        "exit_marked": runs["marked"]["exit"],
        "exit_plain": runs["plain"]["exit"],
        "stderr_normalized_equal": (runs["marked"]["stderr_normalized"]
                                     == runs["plain"]["stderr_normalized"]),
        "no_verdict_document_either": (not runs["marked"]["has_verdict_document"]
                                       and not runs["plain"]["has_verdict_document"]),
        "document_equality": "not applicable: both variants refuse, so no "
                              "verdict document exists on either side",
        "objects_acquired_empty": all(
            not runs[k]["objects_acquired"][s] for k in runs
            for s in runs[k]["objects_acquired"]),
    }
    (OUT / "companion.json").write_text(json.dumps(doc, indent=1,
                                                    sort_keys=False) + "\n")
    print(json.dumps({k: doc[k] for k in ("comparison", "premise_check")},
                     indent=1))
    print("marked stderr:", runs["marked"]["stderr"].strip()[:400])
    print("plain  stderr:", runs["plain"]["stderr"].strip()[:400])


if __name__ == "__main__":
    main()
