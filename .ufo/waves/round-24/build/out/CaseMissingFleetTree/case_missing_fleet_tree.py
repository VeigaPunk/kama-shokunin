#!/usr/bin/env python3
"""CaseMissingFleetTree - offline oracle fixture builder, premise checks and runner.

One oracle family: the fleet history traversal that establishes a report's
first-add cutoff needs an ancestor tree that is absent from the fleet object
store.

Four rows (2x2: promisor-marked/unmarked x missing-tree/complete):

  MFT-1  marked + missing ancestor tree   -> expected exit 2 (could-not-evaluate)
  MFT-2  unmarked + missing ancestor tree -> expected exit 2 (could-not-evaluate)
  MFT-3  marked + complete                -> expected exit 0 (clean)
  MFT-4  unmarked + complete              -> expected exit 0 (clean)

Everything is local and offline. The promisor remote url points at a local
canary repository, so a lazy fetch would be observable there; no network
transport exists in the fixture and none is attempted.

Usage:
  case_missing_fleet_tree.py build     # build fixtures + premise checks
  case_missing_fleet_tree.py measure   # git-behavior measurements (no auditor)
  case_missing_fleet_tree.py audit     # run an auditor on every row
  case_missing_fleet_tree.py all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BASE_COMMIT = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
LANE_DIR = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
AUDIT_REL = "tools/report-landing-audit.py"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseMissingFleetTree")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "build/out/CaseMissingFleetTree")
REL = ".ufo/reports/round-1/kama.md"
ISOLATION = ["--no-replace-objects", "--no-lazy-fetch"]
TIMEOUT = 60


class Premise(Exception):
    """The fixture did not establish its state: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def git(repo, *args, data=None, check=True, isolation=True, **extra):
    argv = ["git", *(ISOLATION if isolation else []), "-C", str(repo), *args]
    p = subprocess.run(argv, input=data, capture_output=True, env=env(**extra),
                       timeout=TIMEOUT)
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))} rc={p.returncode}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p


def out(repo, *args, **kw):
    p = git(repo, *args, **kw)
    return p.stdout.decode(errors="surrogateescape")


def init(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    git(path.parent, "init", "-q", "-b", "master", str(path))
    git(path, "config", "gc.auto", "0")
    git(path, "config", "maintenance.auto", "false")
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    git(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
        GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
        GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return out(repo, "rev-parse", "HEAD").strip()


def build_variant(root: Path, marked: bool, missing_tree: bool):
    """lane + fleet (+ canary) for one variant."""
    root.mkdir(parents=True, exist_ok=True)
    lane = init(root / "lane")
    fleet = init(root / "fleet")
    canary = init(root / "canary")
    commit(canary, "canary", 500, "canary sentinel")

    lane_commit = commit(lane, "kama-shokunin", 1000, "round-1: work")
    body = (f"# kama round 1\n\n## Landed changes\n\n- {lane_commit}\n"
            ).encode()
    f1 = commit(fleet, "fleet", 2000, "round-1: report", REL, body)
    f2 = commit(fleet, "fleet", 2100, "later note", "notes.txt", b"note\n")

    tree1 = out(fleet, "rev-parse", f"{f1}^{{tree}}").strip()
    if marked:
        git(fleet, "config", "remote.origin.url", str(canary))
        git(fleet, "config", "remote.origin.promisor", "true")
        git(fleet, "config", "remote.origin.partialclonefilter", "blob:none")
        git(fleet, "config", "extensions.partialclone", "origin")

    removed = None
    if missing_tree:
        loose = Path(fleet, ".git/objects", tree1[:2], tree1[2:])
        if not loose.is_file():
            raise Premise(f"F1 root tree {tree1} is not a loose object; "
                          "the deletion premise cannot be established")
        loose.unlink()
        removed = tree1
        if git(fleet, "cat-file", "-e", tree1, check=False).returncode == 0:
            raise Premise(f"tree {tree1} still resolvable after deletion")
    return {"lane": lane, "fleet": fleet, "canary": canary,
            "lane_commit": lane_commit, "f1": f1, "f2": f2,
            "f1_tree": tree1, "removed_tree": removed}


def snapshot(repo: Path):
    gitdir = Path(out(repo, "rev-parse", "--absolute-git-dir").strip())
    pack = gitdir / "objects" / "pack"
    return {
        "fetch_head": (gitdir / "FETCH_HEAD").exists(),
        "packs": sorted(p.name for p in pack.iterdir()) if pack.is_dir() else [],
        "canary_head": out(repo.parent / "canary",
                           "rev-parse", "HEAD").strip()
        if (repo.parent / "canary").exists() else None,
        "canary_refs": sorted(
            out(repo.parent / "canary", "for-each-ref",
                "--format=%(refname) %(objectname)").split("\n"))
        if (repo.parent / "canary").exists() else [],
    }


def premise(variant):
    """Every fixture premise that must hold before the auditor is run."""
    fleet, lane = variant["fleet"], variant["lane"]
    checks = {}

    # report bytes readable at fleet HEAD
    p = git(fleet, "show", f"HEAD:{REL}", check=False)
    checks["report_readable_at_head"] = p.returncode == 0
    checks["report_bytes"] = p.stdout.decode(errors="replace")

    # HEAD tree present
    head_tree = out(fleet, "rev-parse", "HEAD^{tree}").strip()
    checks["head_tree_present"] = (
        git(fleet, "cat-file", "-e", head_tree, check=False).returncode == 0)

    # F1 root tree absent (only for the missing variants)
    if variant["removed_tree"]:
        checks["f1_tree_absent"] = (
            git(fleet, "cat-file", "-e", variant["f1_tree"],
                check=False).returncode != 0)
    else:
        checks["f1_tree_absent"] = False
        checks["f1_tree_present"] = (
            git(fleet, "cat-file", "-e", variant["f1_tree"],
                check=False).returncode == 0)

    # the traversal that establishes the first-add cutoff
    t = git(fleet, "log", "--diff-filter=A", "--format=%at", "--", REL,
            check=False)
    checks["cutoff_traversal_rc"] = t.returncode
    checks["cutoff_traversal_stderr"] = t.stderr.decode(errors="replace")
    checks["cutoff_traversal_stdout"] = t.stdout.decode(errors="replace")

    if not checks["report_readable_at_head"]:
        raise Premise("fleet HEAD does not carry the report blob")
    if not checks["head_tree_present"]:
        raise Premise("fleet HEAD tree is absent")
    if variant["removed_tree"] and not checks["f1_tree_absent"]:
        raise Premise("F1 root tree is still resolvable")
    if variant["removed_tree"] and checks["cutoff_traversal_rc"] == 0:
        raise Premise("the report traversal completed without the missing "
                      "ancestor tree: the case would be vacuous")
    return checks


def build_all():
    variants = {}
    for name, marked, missing in (
            ("MFT-1-marked-missing-tree", True, True),
            ("MFT-2-unmarked-missing-tree", False, True),
            ("MFT-3-marked-complete", True, False),
            ("MFT-4-unmarked-complete", False, False)):
        root = SCRATCH / "fixtures" / name
        if root.exists():
            shutil.rmtree(root)
        variants[name] = build_variant(root, marked, missing)
    return variants


def measure(variants, unsafe_probe=False):
    """git-behavior measurements, no auditor involved.

    unsafe_probe (opt-in, off by default) repeats ONE cat-file lookup with
    the isolation flags dropped, in a throwaway copy, to document that a
    promisor-marked repository really would contact its remote without
    --no-lazy-fetch. It runs git's own upload-pack against a LOCAL canary
    repository (file transport, no network, no fixture-configured program).
    It is not part of any graded row.
    """
    result = {}
    for name, v in variants.items():
        fleet = v["fleet"]
        m = {"variant": name, "f1": v["f1"], "f2": v["f2"],
             "f1_tree": v["f1_tree"], "removed_tree": v["removed_tree"],
             "lane_commit": v["lane_commit"]}
        # closure listings
        for label, args in (
                ("rev_list_missing_print",
                 ["rev-list", "--objects", "--missing=print", "--no-object-names",
                  "HEAD"]),
                ("rev_list_plain",
                 ["rev-list", "--objects", "--no-object-names", "HEAD"]),
                ("rev_list_missing_print_lane",
                 ["rev-list", "--objects", "--missing=print", "--no-object-names",
                  "master"])):
            repo = fleet if "lane" not in label else v["lane"]
            p = git(repo, *args, check=False)
            body = p.stdout.decode(errors="replace")
            m[label] = {"rc": p.returncode,
                         "stderr": p.stderr.decode(errors="replace"),
                         "missing_lines": [ln for ln in body.split("\n")
                                           if ln.startswith("?")],
                         "lines": len(body.split("\n"))}
        p = git(fleet, "cat-file", "--batch-check",
                data=f"{v['f1_tree']}\n".encode(), check=False)
        m["cat_file_batch_check_f1_tree"] = {
            "rc": p.returncode,
            "stdout": p.stdout.decode(errors="replace"),
            "stderr": p.stderr.decode(errors="replace")}
        p = git(fleet, "log", "--format=%H", "HEAD", check=False)
        m["commit_traversal"] = {"rc": p.returncode,
                                 "stdout": p.stdout.decode(errors="replace")}
        p = git(fleet, "fsck", "--no-progress", "--no-dangling", check=False)
        m["fsck"] = {"rc": p.returncode,
                     "stderr": p.stderr.decode(errors="replace")[-800:]}
        if unsafe_probe:
            # what happens WITHOUT the isolation flags, in a throwaway copy,
            # to document that the promisor remote would be contacted if git
            # were allowed to fetch (the canary proves it)
            copy = SCRATCH / "probes" / name
            if copy.exists():
                shutil.rmtree(copy)
            copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(v["fleet"], copy)
            before = snapshot(copy)
            p = git(copy, "cat-file", "-e", v["f1_tree"], check=False,
                    isolation=False)
            after = snapshot(copy)
            m["unsuppressed_cat_file"] = {
                "rc": p.returncode,
                "stderr": p.stderr.decode(errors="replace"),
                "fetch_head_before": before["fetch_head"],
                "fetch_head_after": after["fetch_head"],
                "canary_refs_before": before["canary_refs"],
                "canary_refs_after": after["canary_refs"]}
            shutil.rmtree(copy)
        result[name] = m
    return result


def audit(variants, auditor: Path):
    rows = []
    for name, v in variants.items():
        before = snapshot(v["fleet"])
        argv = [sys.executable, str(auditor),
                "--lane-repo", str(v["lane"]), "--fleet-repo", str(v["fleet"]),
                "--rounds", "1", "--no-errata", "--json"]
        p = subprocess.run(argv, capture_output=True, env=env(),
                           cwd=str(v["fleet"]), timeout=TIMEOUT)
        after = snapshot(v["fleet"])
        doc = None
        try:
            doc = json.loads(p.stdout.decode(errors="replace"))
        except ValueError:
            pass
        rows.append({
            "row": name,
            "auditor": str(auditor),
            "auditor_sha256": hashlib.sha256(auditor.read_bytes()).hexdigest(),
            "argv": argv,
            "exit": p.returncode,
            "stdout": p.stdout.decode(errors="replace")[:4000],
            "stderr": p.stderr.decode(errors="replace")[:4000],
            "verdict_document": doc is not None,
            "summary": (doc or {}).get("summary"),
            "defects": ([d for r in (doc or {}).get("results", [])
                         for d in r.get("defects", [])] if doc else None),
            "traceback": "Traceback (most recent call last)" in
            p.stderr.decode(errors="replace"),
            "fetch_head_before": before["fetch_head"],
            "fetch_head_after": after["fetch_head"],
            "packs_before": before["packs"],
            "packs_after": after["packs"],
            "canary_refs_before": before["canary_refs"],
            "canary_refs_after": after["canary_refs"],
        })
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command",
                    choices=("build", "measure", "audit", "all"))
    ap.add_argument("--auditor", default=str(LANE_DIR / AUDIT_REL))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--unsafe-probe", action="store_true",
                    help="also run the isolated unsuppressed cat-file probe "
                         "(local canary only; not a graded row)")
    args = ap.parse_args(argv)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    try:
        if args.command in ("build", "all"):
            variants = build_all()
            premises = {name: premise(v) for name, v in variants.items()}
            (outdir / "fixture.json").write_text(json.dumps({
                "base_commit": BASE_COMMIT,
                "scratch": str(SCRATCH),
                "variants": {
                    name: {"lane": str(v["lane"]), "fleet": str(v["fleet"]),
                           "canary": str(v["canary"]),
                           "lane_commit": v["lane_commit"],
                           "f1": v["f1"], "f2": v["f2"],
                           "f1_tree": v["f1_tree"],
                           "removed_tree": v["removed_tree"]}
                    for name, v in variants.items()},
                "premises": premises,
            }, indent=1, sort_keys=True), encoding="utf-8")
            print("premises ok:", json.dumps(
                {k: {kk: vv for kk, vv in p.items()
                     if kk in ("report_readable_at_head", "head_tree_present",
                               "f1_tree_absent", "f1_tree_present",
                               "cutoff_traversal_rc")}
                 for k, p in premises.items()}, indent=1))
        if args.command in ("measure", "all"):
            variants = build_all()
            data = measure(variants, unsafe_probe=args.unsafe_probe)
            name = ("measurements.json" if not args.unsafe_probe
                    else "measurements-unsafe-probe.json")
            (outdir / name).write_text(
                json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
            print(json.dumps(data, indent=1, sort_keys=True))
        if args.command in ("audit", "all"):
            variants = build_all()
            rows = audit(variants, Path(args.auditor))
            (outdir / "audit.json").write_text(
                json.dumps({"base_commit": BASE_COMMIT, "rows": rows},
                           indent=1, sort_keys=True), encoding="utf-8")
            for r in rows:
                print(f"{r['row']} exit={r['exit']} "
                      f"verdict={r['verdict_document']} "
                      f"summary={(r['summary'] or {}).get('status')} "
                      f"defects={len(r['defects'] or [])} "
                      f"traceback={r['traceback']} "
                      f"fetch_head={r['fetch_head_after']} "
                      f"canary_changed="
                      f"{r['canary_refs_before'] != r['canary_refs_after']}")
                if r["stderr"]:
                    print("   stderr:", r["stderr"].strip()[:300])
        return 0
    except Premise as exc:
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # errors are never verdicts
        print(f"could-not-evaluate: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
