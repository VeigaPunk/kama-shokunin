#!/usr/bin/env python3
"""Assemble the machine-readable oracle spec for the round-24 case."""
import hashlib
import json
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "build/out/CaseMissingLaneTree")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseMissingLaneTree")
BASE = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    return json.loads((SCRATCH / name).read_text(encoding="utf-8"))


base = load("measure-base.json")
ref = load("measure-ref.json")
ref_na = load("measure-ref-noavail.json")
ref_tol = load("measure-ref-tolerant.json")

spec = {
    "case": "F20-promisor-missing-lane-tree",
    "lane": "CaseMissingLaneTree",
    "round": 24,
    "axis": "C1 calibration 7->7 (promisor metadata vs unavailable evidence)",
    "base_commit": BASE,
    "title": "promisor-marked lane with an unavailable reachable tree, all "
             "commit objects present locally",
    "expected": {
        "exit": 2,
        "kinds": None,
        "verdict": None,
        "stdout_is_verdict": False,
        "stderr_must_contain": ["could-not-evaluate:"],
        "stderr_any": ["missing", "not a tree object", "unable to read",
                       "unavailable", "not available", "no such"],
        "stderr_must_not_contain": [
            "partial clone (promisor pack)",
            "partial clone (extensions.partialclone",
            "partial clone (remote.",
        ],
        "no_traceback": True,
        "no_timeout": True,
        "no_command_executed": True,
        "object_store_unchanged": True,
        "tree_still_unavailable": True,
    },
    "soft_recommendations": [
        "the refusal should name the unavailable object (40-hex tree id)",
        "use a read-only availability probe (git rev-list --objects "
        "--missing=print) instead of a promisor-metadata refusal",
    ],
    "premise": [
        {"check": "cited commit object present",
         "command": "git cat-file -t <c1>", "expect": "commit"},
        {"check": "tip commit object present",
         "command": "git cat-file -t <c2>", "expect": "commit"},
        {"check": "tip tree unavailable",
         "command": "git --no-lazy-fetch cat-file -e <tree>",
         "expect": "non-zero exit"},
        {"check": "tree is reachable from the audited tip",
         "command": "git rev-list --objects --missing=print master",
         "expect": "a line starting with '?' naming the tree"},
        {"check": "promisor metadata present",
         "command": "git config --list",
         "expect": "extensions.partialclone=origin, remote.origin.promisor=true"},
        {"check": "no remote target exists",
         "command": "test -e <tmp>/absent-promisor.git",
         "expect": "absent: a lazy fetch could not succeed"},
    ],
    "paired_controls": [
        {"variant": "control-promisor-complete",
         "promisor": True, "missing_tree": False,
         "expect_exit_after_repair": 0, "expect_kinds": [],
         "note": "same lane and fleet, every object present: the same "
                 "substantive verdict as a full clone, not exit 2"},
        {"variant": "control-plain-missing-tree",
         "promisor": False, "missing_tree": True,
         "expect_exit_after_repair": 2,
         "note": "the unavailable tree alone forces exit 2, with or without "
                 "promisor metadata"},
        {"variant": "control-plain-complete",
         "promisor": False, "missing_tree": False,
         "expect_exit_after_repair": 0, "expect_kinds": [],
         "note": "sanity: the fixture itself is clean"},
    ],
    "measured": {
        "base_r23": {k: {"exit": v["exit"], "kinds": v["kinds"],
                         "verdict": v["verdict"],
                         "stderr": v["stderr"][:300]}
                     for k, v in base["variants"].items()},
        "scratch_reference_repair": {
            k: {"exit": v["exit"], "kinds": v["kinds"], "verdict": v["verdict"],
                "stderr": v["stderr"][:300]}
            for k, v in ref["variants"].items()},
        "scratch_reference_repair_tolerant_read": {
            k: {"exit": v["exit"], "kinds": v["kinds"], "verdict": v["verdict"],
                "stderr": v["stderr"][:300]}
            for k, v in ref_tol["variants"].items()},
        "scratch_reference_repair_without_availability_check": {
            k: {"exit": v["exit"], "kinds": v["kinds"], "verdict": v["verdict"],
                "stderr": v["stderr"][:300]}
            for k, v in ref_na["variants"].items()},
    },
    "notes": [
        "the base refusal reason is the promisor metadata, not the missing "
        "object; the reason must change, the exit code must not",
        "the r23 grid already refuses promisor repositories wholesale "
        "(tools/report-landing-audit.py:457 and :465); the r24 repair must "
        "replace that metadata refusal with an evidence-availability check",
        "the tip tree is required evidence: the auditor reads the lane tip "
        "tree to find corpus/SOURCES.md "
        "(tools/report-landing-audit.py:258-268), and that registry decides "
        "how 40-hex tokens in the report are classified",
        "the fixture uses no network, no clone transport and no configured "
        "program; the promisor remote URL is a non-existent local path",
    ],
    "artifacts": {
        "builder": "case_missing_lane_tree.py",
        "grid_fragment": "grid-fragment.py",
        "measurement_base": "measure-base.json",
        "measurement_scratch_reference_repair": "measure-ref-repair.json",
        "measurement_scratch_reference_repair_no_availability":
            "measure-ref-no-availability.json",
        "measurement_scratch_reference_repair_tolerant":
            "measure-ref-tolerant-read.json",
        "scratch_proof": "scratch-proof.txt",
    },
    "hashes": {
        "builder_sha256": sha(OUT / "case_missing_lane_tree.py"),
        "grid_fragment_sha256": sha(OUT / "grid-fragment.py"),
        "base_auditor_sha256": sha(SCRATCH / "base-audit.py"),
        "scratch_reference_auditor_sha256": sha(SCRATCH / "ref-audit.py"),
        "scratch_reference_noavail_auditor_sha256":
            sha(SCRATCH / "ref-audit-noavail.py"),
        "scratch_reference_tolerant_auditor_sha256":
            sha(SCRATCH / "ref-audit-tolerant.py"),
    },
}

(OUT / "case_missing_lane_tree.json").write_text(
    json.dumps(spec, indent=1, sort_keys=True) + "\n", encoding="utf-8")
for src, dst in (("measure-base.json", "measure-base.json"),
                 ("measure-ref.json", "measure-ref-repair.json"),
                 ("measure-ref-noavail.json",
                  "measure-ref-no-availability.json")):
    (OUT / dst).write_bytes((SCRATCH / src).read_bytes())
print("wrote", OUT / "case_missing_lane_tree.json")
print(json.dumps(spec["hashes"], indent=1, sort_keys=True))
