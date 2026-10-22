#!/usr/bin/env python3
"""FinalCase33 premise probe: PG33-missing-cited-blob-promisor (+ graded twin
PG34-missing-cited-blob-plain) against the pinned auditor
tools/report-landing-audit.py @ 92063cfc60e217fa7e2098c568578119b16a1b95.

Read-only against the grid-kept fixtures (the grid root is NOT removed: the
promisor origin must stay in place).  Every git probe uses --no-lazy-fetch.
"""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase33/clone")
AUDIT = CLONE / "tools" / "report-landing-audit.py"
GRID_ROOT = Path(sys.argv[1]).resolve()
REL = ".ufo/reports/round-1/kama.md"

spec = importlib.util.spec_from_file_location("pinned_audit", AUDIT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def sh(repo, *args, data=None):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), *args],
                       input=None if data is None else data.encode(),
                       capture_output=True,
                       env={k: v for k, v in os.environ.items()
                            if not k.startswith("GIT_")},
                       timeout=30)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


def inventory(repo):
    rc, out, _ = sh(repo, "cat-file", "--batch-all-objects",
                    "--batch-check=%(objectname)")
    return sorted(out.split())


def case_report(case_dir, lane, fleet):
    tip = sh(lane, "rev-parse", "refs/heads/master")[1].strip()
    fleet_head = sh(fleet, "rev-parse", "HEAD")[1].strip()
    report = sh(fleet, "show", f"HEAD:{REL}")[1]
    tree = sh(lane, "ls-tree", tip)[1]
    # the cited blob token in the report notes
    tokens = re.findall(r"\b[0-9a-f]{40}\b", report)
    blob = None
    for t in tokens:
        rc, out, _ = sh(lane, "cat-file", "--batch-check",
                        data=f"{t}\n")
        if out.strip().endswith("missing"):
            blob = t
    # presence probes
    def present(repo, oid):
        _, out, _ = sh(repo, "cat-file", "--batch-check", data=f"{oid}\n")
        return out.strip()

    store = audit.RepoStore(str(lane), tip)
    missing, opaque = store.missing()
    # what a ROOT-SCOPED known-missing set would be (the scoping the
    # hypothesis is about): only the pinned root as walk root
    rooted = audit.git(str(lane), "-c", "core.commitGraph=false", "rev-list",
                       "--objects", "--missing=print", "--no-object-names",
                       "--stdin", stdin=tip + "\n")
    rooted_missing = {ln[1:] for ln in rooted.split("\n") if ln.startswith("?")}
    present_roots = audit.present_roots(str(lane))
    return {
        "case_dir": str(case_dir),
        "lane": str(lane),
        "fleet": str(fleet),
        "lane_tip": tip,
        "fleet_head": fleet_head,
        "report_text": report,
        "cited_tokens_in_report": tokens,
        "cited_blob_missing_oid": blob,
        "cited_blob_in_tip_tree": (blob in tree) if blob else None,
        "tip_tree_listing": tree,
        "lane_cat_file_cited_blob": present(lane, blob) if blob else None,
        "fleet_cat_file_cited_blob": present(fleet, blob) if blob else None,
        "auditor_missing_set_size": len(missing),
        "cited_blob_in_auditor_missing_set": (blob in missing) if blob else None,
        "auditor_opaque_set": sorted(opaque),
        "cited_blob_in_auditor_opaque_set": (blob in opaque) if blob else None,
        "root_scoped_missing_set": sorted(rooted_missing),
        "cited_blob_in_root_scoped_missing_set":
            (blob in rooted_missing) if blob else None,
        "present_roots_count": len(present_roots),
        "tip_is_present_root": tip in present_roots,
        "lane_config": dict(
            line.split("=", 1)
            for line in sh(lane, "config", "--list")[1].splitlines()
            if "=" in line),
    }


def direct_audit(lane, fleet):
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    p = subprocess.run([sys.executable, str(AUDIT), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1", "--json"],
                       capture_output=True, timeout=60,
                       env={k: v for k, v in os.environ.items()
                            if not k.startswith("GIT_")})
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    return {
        "argv": [sys.executable, str(AUDIT), "--lane-repo", str(lane),
                 "--fleet-repo", str(fleet), "--rounds", "1", "--json"],
        "exit": p.returncode,
        "stdout": p.stdout.decode("utf-8", "replace"),
        "stderr": p.stderr.decode("utf-8", "replace"),
        "objects_acquired": {k: sorted(set(after[k]) - set(before[k]))
                             for k in after},
    }


out = {"auditor_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
       "clone_head": sh(CLONE, "rev-parse", "HEAD")[1].strip(),
       "grid_root": str(GRID_ROOT),
       "cases": {}}
for label, sub in (("PG33-missing-cited-blob-promisor", "000"),
                   ("PG34-missing-cited-blob-plain", "001")):
    d = GRID_ROOT / "current" / sub
    lane, fleet = d / "lane", d / "fleet"
    rec = case_report(d, lane, fleet)
    rec["direct_audit"] = direct_audit(lane, fleet)
    out["cases"][label] = rec

a = out["cases"]["PG33-missing-cited-blob-promisor"]
b = out["cases"]["PG34-missing-cited-blob-plain"]


def norm(s, sub):
    return s.replace(str(GRID_ROOT / "current" / sub), "<CASE>")


out["twin_refusal_comparison"] = {
    "note": "both refusals have NO verdict document; the grid twin field is "
            "null, not false. This is a refusal-to-refusal comparison, NOT a "
            "twin document equality.",
    "same_exit": a["direct_audit"]["exit"] == b["direct_audit"]["exit"],
    "same_cited_oid":
        a["cited_blob_missing_oid"] == b["cited_blob_missing_oid"],
    "same_stderr_modulo_case_path":
        norm(a["direct_audit"]["stderr"], "000")
        == norm(b["direct_audit"]["stderr"], "001"),
    "stderr_pg33": a["direct_audit"]["stderr"],
    "stderr_pg34": b["direct_audit"]["stderr"],
    "stdout_empty_both": (a["direct_audit"]["stdout"].strip() == ""
                          and b["direct_audit"]["stdout"].strip() == ""),
}
print(json.dumps(out, indent=1, sort_keys=False))
