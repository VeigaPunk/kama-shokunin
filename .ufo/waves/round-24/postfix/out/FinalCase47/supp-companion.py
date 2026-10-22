#!/usr/bin/env python3
"""FinalCase47 supplemental: PG48 promisor-marked vs FRESH plain companion.

OUTSIDE the frozen 47: no manifest edit, no twin link, no new grid cell.

The plain companion is produced by filesystem-copying the UNRUN fixture lane
(no git clone of a partial store), then removing ONLY the promisor metadata
the builder installed (config keys + paired .promisor markers).  Object,
pack and index bytes, branches, citations and the connected local origin
URL/availability are left untouched.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase47/clone")
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location(
    "promisor_grid", CLONE / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

AUDITOR = CLONE / "tools" / "report-landing-audit.py"
OUT = Path(sys.argv[1])


def file_digests(root: Path):
    """sha256 of every file under .git/objects plus .git/index."""
    out = {}
    gitdir = G.git_dir(root)
    for p in sorted((gitdir / "objects").rglob("*")):
        if p.is_file():
            out[str(p.relative_to(gitdir))] = hashlib.sha256(
                p.read_bytes()).hexdigest()
    idx = gitdir / "index"
    if idx.exists():
        out["index"] = hashlib.sha256(idx.read_bytes()).hexdigest()
    return out


def refs(repo):
    return G.git(repo, "for-each-ref",
                 "--format=%(refname) %(objectname)").strip()


def config_all(repo):
    entries = []
    for e in G.git(repo, "config", "--null", "--list").split("\0"):
        if e:
            entries.append(e)
    return sorted(entries)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    root = G.make_root()
    tmp = Path(root, "supp")
    tmp.mkdir(parents=True, exist_ok=True)
    built = G.BUILDERS["c_opaque_unused_tree_clean"](root, tmp)
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]

    # ---- fresh plain companion: filesystem copy of the UNRUN fixture lane
    plain = Path(tmp, "lane-plain")
    shutil.copytree(lane, plain, symlinks=True)
    # remove ONLY the promisor metadata the builder installed
    removed = []
    for key in ("remote.origin.promisor", "extensions.partialclone",
                "remote.origin.partialclonefilter"):
        p = subprocess.run(["git", "-C", str(plain), "config", "--unset-all",
                            key], capture_output=True, env=G.env())
        if p.returncode == 0:
            removed.append(key)
    packdir = G.git_dir(plain) / "objects" / "pack"
    markers = []
    if packdir.is_dir():
        for m in sorted(packdir.glob("*.promisor")):
            if m.with_suffix(".pack").exists():
                markers.append(m.name)
                m.unlink()
                removed.append("marker:" + m.name)

    # ---- attestation
    inv_marked = G.object_inventory(lane)
    inv_plain = G.object_inventory(plain)
    miss_marked = G.missing_objects(lane, "refs/heads/master")
    miss_plain = G.missing_objects(plain, "refs/heads/master")
    dig_marked = file_digests(lane)
    dig_plain = file_digests(plain)
    cfg_marked = config_all(lane)
    cfg_plain = config_all(plain)
    facts_marked = G.promisor_facts(lane)
    facts_plain = G.promisor_facts(plain)

    att = {
        "fixture_builder": "c_opaque_unused_tree_clean",
        "unrun_fixture_lane": str(lane),
        "plain_companion_lane": str(plain),
        "copy_method": "shutil.copytree of the unrun fixture lane "
                       "(filesystem copy, no git clone)",
        "removed_metadata": removed,
        "promisor_facts_marked": facts_marked,
        "promisor_facts_plain": facts_plain,
        "object_inventory_equal": inv_marked == inv_plain,
        "object_inventory_count": len(inv_marked),
        "object_pack_index_digests_equal": dig_marked == dig_plain,
        "object_pack_index_file_count": len(dig_marked),
        "missing_objects_marked": miss_marked,
        "missing_objects_plain": miss_plain,
        "missing_objects_equal": miss_marked == miss_plain,
        "refs_equal": refs(lane) == refs(plain),
        "refs": refs(lane),
        "config_marked": cfg_marked,
        "config_plain": cfg_plain,
        "origin_url_marked": G.git(lane, "config", "--get",
                                  "remote.origin.url").strip(),
        "origin_url_plain": G.git(plain, "config", "--get",
                                 "remote.origin.url").strip(),
        "origin_url_exists_on_disk": Path(G.git(
            plain, "config", "--get", "remote.origin.url").strip()).exists(),
        "missing_subtree_sha": shas.get("missing_subtree"),
        "lane_commit_sha": shas.get("lane_commit"),
    }
    att["origin_url_unchanged"] = (att["origin_url_marked"]
                                   == att["origin_url_plain"])

    # ---- run the pinned auditor on both metadata variants
    def run(lane_dir, cwd):
        cwd.mkdir(parents=True, exist_ok=True)
        before = {"lane": G.object_inventory(lane_dir),
                  "fleet": G.object_inventory(fleet)}
        code, out, err, timed = G.run_auditor(AUDITOR, lane_dir, fleet, cwd,
                                              False)
        after = {"lane": G.object_inventory(lane_dir),
                 "fleet": G.object_inventory(fleet)}
        acquired = {k: sorted(after[k] - before[k]) for k in after}
        doc = None
        try:
            doc = json.loads(out)
        except ValueError:
            pass
        return {"exit": code, "stdout": out, "stderr": err,
                "timed_out": timed, "objects_acquired": acquired,
                "document": doc}

    marked_run = run(lane, Path(tmp, "run-marked"))
    plain_run = run(plain, Path(tmp, "run-plain"))

    def norm(doc, lane_dir):
        if doc is None:
            return None
        text = json.dumps(doc, sort_keys=True)
        text = text.replace(str(fleet), "<fleet>")
        text = text.replace(str(lane_dir), "<lane>")
        return json.loads(text)

    dm = norm(marked_run["document"], lane)
    dp = norm(plain_run["document"], plain)
    supp = {
        "attestation": att,
        "marked_run": {k: v for k, v in marked_run.items()
                       if k != "document"},
        "plain_run": {k: v for k, v in plain_run.items()
                      if k != "document"},
        "marked_exit": marked_run["exit"],
        "plain_exit": plain_run["exit"],
        "both_exit_zero": (marked_run["exit"] == 0 and plain_run["exit"] == 0),
        "normalized_document_marked": dm,
        "normalized_document_plain": dp,
        "normalized_documents_equal": (dm is not None and dm == dp),
        "marked_status": (dm or {}).get("summary", {}).get("status"),
        "plain_status": (dp or {}).get("summary", {}).get("status"),
    }
    (OUT / "supplemental-companion.json").write_text(
        json.dumps(supp, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in supp.items()
                      if k not in ("attestation", "normalized_document_marked",
                                   "normalized_document_plain")},
                     indent=1, sort_keys=True))
    print("ATTESTATION:", json.dumps(att, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
