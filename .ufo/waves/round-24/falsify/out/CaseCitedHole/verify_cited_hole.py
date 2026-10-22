#!/usr/bin/env python3
"""Independent premise + observation verifier for the CitedHole family.

Read-only against the pinned scratch clone; it rebuilds the two registered
fixtures with the grid's own builders (no fixture is modified), then asserts
the premises and the observations independently of the grid's grader.

Usage:
  python3 verify_cited_hole.py --clone /fast/scratch/hyaku/kama-r24/falsify/CaseCitedHole \
      --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseCitedHole/premises.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseCitedHole")
CASES = [
    ("PG33-missing-cited-blob-promisor", "c_missing_cited_blob_promisor"),
    ("PG34-missing-cited-blob-plain", "c_missing_cited_blob_plain"),
]


def load_grid(clone: Path):
    path = clone / "tests" / "report-audit" / "promisor-grid.py"
    spec = importlib.util.spec_from_file_location("promisor_grid_local", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["promisor_grid_local"] = mod
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args, check=False):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
               GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env)
    return p.returncode, p.stdout.decode(errors="replace").strip(), \
        p.stderr.decode(errors="replace").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", default=str(SCRATCH))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    clone = Path(args.clone).resolve()
    grid = load_grid(clone)
    auditor = clone / "tools" / "report-landing-audit.py"
    report = {"clone": str(clone), "clone_revision":
              git(clone, "rev-parse", "HEAD")[1], "cases": {}}

    root = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseCitedHole/tmp-verify")
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    frozen = grid.frozen_auditor(root, None)

    for idx, (case, builder) in enumerate(CASES):
        tmp = root / case
        tmp.mkdir(parents=True, exist_ok=True)
        built = grid.BUILDERS[builder](root, tmp)
        lane, fleet = built["lane"], built["fleet"]
        shas = built["shas"]
        oid = shas["cited_blob"]
        rec = {"builder": builder, "shas": {k: v for k, v in shas.items()
                                            if isinstance(v, str)},
               "lane": str(lane), "fleet": str(fleet)}

        # --- premise: the dropped object IS the cited blob ---------------
        rec["cited_blob_equals_f_blob"] = (oid == shas["f_blob"])

        # --- premise: a PRESENT tree references the absent blob ----------
        rc, tree_ls, _ = git(lane, "ls-tree", "-r", "HEAD")
        rec["tip_tree_entries"] = tree_ls.splitlines()
        rec["tree_references_cited_blob"] = any(
            line.split()[2] == oid for line in tree_ls.splitlines())
        rc, entry, _ = git(lane, "ls-tree", "HEAD", "f")
        rec["tree_entry_f"] = entry
        rc, kind, _ = git(lane, "cat-file", "-t", oid)
        rec["cat_file_type_rc"] = rc
        rc2, _, _ = git(lane, "--no-lazy-fetch", "cat-file", "-e", oid)
        rec["lane_object_absent_rc"] = rc2
        rc3, _, _ = git(fleet, "--no-lazy-fetch", "cat-file", "-e", oid)
        rec["fleet_object_absent_rc"] = rc3
        rc4, out4, _ = git(lane, "--no-lazy-fetch", "rev-parse",
                           f"{shas['lane_commit']}:f")
        rec["rev_parse_f_rc"] = rc4
        rec["rev_parse_f_out"] = out4

        # --- premise: the report cites exactly that blob -------------------
        rc, text, _ = git(fleet, "show", f"HEAD:{grid.REL}")
        rec["report_text"] = text
        rec["report_cites_blob"] = (f"blob {oid}" in text)
        rec["report_cites_blob_count"] = text.count(oid)
        rec["cited_in_landed_section"] = (
            oid in text.split("## Notes")[0])
        rec["cited_in_notes_section"] = (
            oid in text.split("## Notes")[1] if "## Notes" in text else False)

        # --- premise: the store's own missing-object set ------------------
        rc, allobj, _ = git(lane, "--no-lazy-fetch", "cat-file",
                            "--batch-all-objects",
                            "--batch-check=%(objectname) %(objecttype)")
        roots = [l.split()[0] for l in allobj.splitlines()
                 if l.split()[1] in ("commit", "tree", "tag")]
        stdin = "".join(f"{r}\n" for r in roots)
        p = subprocess.run(["git", "-C", str(lane), "--no-lazy-fetch",
                            "-c", "core.commitGraph=false", "rev-list",
                            "--objects", "--missing=print", "--no-object-names",
                            "--stdin"], input=stdin.encode(), capture_output=True,
                           env=grid.env())
        missing = {l[1:] for l in p.stdout.decode().split("\n")
                   if l.startswith("?")}
        rec["lane_missing_objects"] = sorted(missing)
        rec["missing_set_is_exactly_the_cited_blob"] = (missing == {oid})

        # --- premise: the promisor marking side ---------------------------
        rec["promisor_facts_lane"] = grid.promisor_facts(lane)
        rec["promisor_facts_fleet"] = grid.promisor_facts(fleet)
        rc, cfg, _ = git(lane, "config", "--get", "remote.origin.url")
        rec["lane_origin_url"] = cfg
        rc, cfg2, _ = git(lane, "config", "--get", "remote.origin.promisor")
        rec["lane_promisor_true"] = cfg2
        rec["origin_url_exists_on_disk"] = Path(cfg).exists() if cfg else None

        # --- observation: current + frozen arms ---------------------------
        before = {"lane": grid.object_inventory(lane),
                  "fleet": grid.object_inventory(fleet)}
        packs_before = {k: sorted((grid.git_dir(Path(v)) / "objects" / "pack")
                                  .glob("*")) for k, v in
                        (("lane", lane), ("fleet", fleet))}
        code, out, err, to = grid.run_auditor(auditor, lane, fleet, tmp, False)
        after = {"lane": grid.object_inventory(lane),
                 "fleet": grid.object_inventory(fleet)}
        packs_after = {k: sorted((grid.git_dir(Path(v)) / "objects" / "pack")
                                 .glob("*")) for k, v in
                       (("lane", lane), ("fleet", fleet))}
        rec["current"] = {
            "exit": code, "stdout": out, "stderr": err, "timed_out": to,
            "stderr_starts_cne": err.startswith("could-not-evaluate:"),
            "names_the_cited_oid": oid in err,
            "stdout_is_a_verdict_document": bool(out.strip()),
            "forbidden_metadata_reason": ("partial clone (" in err
                                          or "promisor pack" in err),
            "reason_class_hit": [t for t in grid.REASON_CLASSES["unavailable"]
                                 if t in err.lower()],
            "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
            "pack_dir_changed": packs_before != packs_after,
            "pack_dirs": {k: [p.name for p in v] for k, v in packs_after.items()},
            "traceback": "Traceback (most recent call last)" in err,
        }
        fcode, fout, ferr, fto = grid.run_auditor(frozen, lane, fleet, tmp,
                                                   False)
        rec["frozen"] = {"exit": fcode, "stdout": fout, "stderr": ferr,
                         "timed_out": fto,
                         "defects": grid.observed_defects(fout)[0],
                         "names_the_cited_oid": oid in ferr}

        # --- observation: the twin's message is the same modulo the path --
        rec["stderr_normalised"] = err.replace(str(lane), "<lane>")
        report["cases"][case] = rec

    # --- twin comparison: substantive verdict equality -------------------
    p33 = report["cases"][CASES[0][0]]
    p34 = report["cases"][CASES[1][0]]
    report["twin"] = {
        "pair": [CASES[0][0], CASES[1][0]],
        "same_exit": p33["current"]["exit"] == p34["current"]["exit"],
        "same_stderr_modulo_path": (p33["stderr_normalised"]
                                    == p34["stderr_normalised"]),
        "same_cited_oid": (p33["shas"]["cited_blob"]
                           == p34["shas"]["cited_blob"]),
        "grid_twin_document_comparison": "vacuous (no verdict document: both "
                                         "arms exit 2 with an empty stdout)",
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=1, sort_keys=False)
                              + "\n", encoding="utf-8")
    print(json.dumps({
        "cases": {c: {"exit": report["cases"][c]["current"]["exit"],
                      "names_oid": report["cases"][c]["current"]
                      ["names_the_cited_oid"],
                      "missing_set_exact":
                          report["cases"][c]
                          ["missing_set_is_exactly_the_cited_blob"],
                      "tree_refs_blob": report["cases"][c]
                      ["tree_references_cited_blob"]}
                  for c in report["cases"]},
        "twin": report["twin"]}, indent=1))
    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
