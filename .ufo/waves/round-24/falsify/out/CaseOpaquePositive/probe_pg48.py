#!/usr/bin/env python3
"""Independent probe of fixture family OpaquePositive / PG48.

Bounded, offline, benign: builds the same fixture family the grid builds
(tests/report-audit/promisor-grid.py builders), then
  1. asserts the actual missing/present object state,
  2. runs the pinned auditor and records exit/stdout/stderr/defect pairs,
  3. records the object inventory delta (no acquisition),
  4. builds the two twins the manifest leaves null (unmarked twin, and
     the same fixture with the opaque subtree present) and compares the
     normalised verdict documents field by field.
No network, no transport, no execution payloads.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo")
GRID = REPO / "tests/report-audit/promisor-grid.py"
AUDIT = REPO / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/probe-root")


def load_grid():
    spec = importlib.util.spec_from_file_location("pggrid", GRID)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clean_root():
    shutil.rmtree(ROOT, ignore_errors=True)
    ROOT.mkdir(parents=True, exist_ok=True)


def run_auditor(lane, fleet, tmp, trace=None):
    env = dict(os.environ)
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
               GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    if trace:
        env["GIT_TRACE"] = str(trace)
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=env, cwd=str(tmp),
                       timeout=60)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def inventory(repo):
    out = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                          "cat-file", "--batch-all-objects",
                          "--batch-check=%(objectname) %(objecttype)"],
                         capture_output=True)
    d = {}
    for line in out.stdout.decode().split("\n"):
        if not line:
            continue
        name, _, kind = line.partition(" ")
        d[name] = kind
    return d


def normalise(doc, lane, fleet):
    if doc is None:
        return None
    text = json.dumps(doc, sort_keys=True)
    text = text.replace(str(fleet), "<fleet>").replace(str(lane), "<lane>")
    return json.loads(text)


def main():
    g = load_grid()
    out = {"repo_head": subprocess.run(["git", "-C", str(REPO), "rev-parse",
                                        "HEAD"], capture_output=True,
                                       text=True).stdout.strip(),
           "auditor_sha256": subprocess.run(
               ["sha256sum", str(AUDIT)], capture_output=True,
               text=True).stdout.split()[0],
           "grid_sha256": subprocess.run(
               ["sha256sum", str(GRID)], capture_output=True,
               text=True).stdout.split()[0]}
    clean_root()

    # ---- A: the graded PG48 fixture exactly as the grid builds it
    tmpA = ROOT / "A"
    tmpA.mkdir(parents=True)
    builtA = g.BUILDERS["c_opaque_unused_tree_clean"](ROOT, tmpA)
    laneA, fleetA, shasA = builtA["lane"], builtA["fleet"], builtA["shas"]
    premA = builtA["premise"]
    invA_lane_before = inventory(laneA)
    invA_fleet_before = inventory(fleetA)
    traceA = tmpA / "git-trace.log"
    codeA, outA, errA = run_auditor(laneA, fleetA, tmpA, trace=traceA)
    invA_lane_after = inventory(laneA)
    invA_fleet_after = inventory(fleetA)
    docA = json.loads(outA) if outA.strip().startswith("{") else None

    subtree = shasA.get("missing_subtree") or shasA.get("opaque_tree")
    present = {}
    for name, kind in invA_lane_after.items():
        present[name] = kind

    def exists(repo, sha):
        p = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                            "-C", str(repo), "cat-file", "-e",
                            sha + "^{object}"], capture_output=True)
        return p.returncode == 0

    A = {
        "premise": premA,
        "lane_commit": shasA["lane_commit"],
        "missing_subtree_oid": subtree,
        "missing_subtree_present_in_store": exists(laneA, subtree),
        "lane_commit_present": exists(laneA, shasA["lane_commit"]),
        "tip_tree_present": exists(laneA, shasA["tip_tree"]),
        "f_blob_present": exists(laneA, shasA["f_blob"]),
        "sources_blob_present": exists(laneA, shasA["sources_blob"]),
        "lane_object_count": len(invA_lane_after),
        "fleet_object_count": len(invA_fleet_after),
        "lane_objects_acquired": sorted(set(invA_lane_after)
                                        - set(invA_lane_before)),
        "fleet_objects_acquired": sorted(set(invA_fleet_after)
                                         - set(invA_fleet_before)),
        "exit": codeA,
        "stdout_len": len(outA),
        "stderr": errA.strip()[:400],
        "document": normalise(docA, laneA, fleetA),
        "defect_pairs": sorted(
            (d["kind"], d["token"])
            for r in (docA or {}).get("results", []) for d in r.get("defects", [])),
        "trace": traceA.read_text(errors="replace") if traceA.exists() else "",
    }

    # ---- B: unmarked twin (identical fixture, no promisor metadata)
    tmpB = ROOT / "B"
    tmpB.mkdir(parents=True)
    builtB = g.build(ROOT, tmpB, opaque_tree=True, drop=("opaque_tree",))
    laneB, fleetB = builtB["lane"], builtB["fleet"]
    invB_before = inventory(laneB)
    codeB, outB, errB = run_auditor(laneB, fleetB, tmpB)
    invB_after = inventory(laneB)
    docB = json.loads(outB) if outB.strip().startswith("{") else None
    B = {
        "premise_promisor": builtB["premise"]["lane_promisor"],
        "exit": codeB,
        "stderr": errB.strip()[:400],
        "document": normalise(docB, laneB, fleetB),
        "defect_pairs": sorted(
            (d["kind"], d["token"])
            for r in (docB or {}).get("results", []) for d in r.get("defects", [])),
        "lane_objects_acquired": sorted(set(invB_after) - set(invB_before)),
        "missing_subtree_oid": builtB["shas"].get("missing_subtree"),
    }

    # ---- C: complete twin (same fixture, opaque subtree PRESENT)
    tmpC = ROOT / "C"
    tmpC.mkdir(parents=True)
    builtC = g.build(ROOT, tmpC, lane_mark="config", opaque_tree=True)
    laneC, fleetC = builtC["lane"], builtC["fleet"]
    codeC, outC, errC = run_auditor(laneC, fleetC, tmpC)
    docC = json.loads(outC) if outC.strip().startswith("{") else None
    C = {
        "exit": codeC,
        "stderr": errC.strip()[:400],
        "document": normalise(docC, laneC, fleetC),
        "defect_pairs": sorted(
            (d["kind"], d["token"])
            for r in (docC or {}).get("results", []) for d in r.get("defects", [])),
        "lane_missing": builtC["premise"]["lane_missing"],
    }

    A["twin_B_document_equal"] = A["document"] == B["document"]
    A["twin_C_document_equal"] = A["document"] == C["document"]
    A["twin_B_exit_equal"] = A["exit"] == B["exit"]
    A["twin_C_exit_equal"] = A["exit"] == C["exit"]
    # field-level diff for C
    diff = []
    if isinstance(A["document"], dict) and isinstance(C["document"], dict):
        def walk(a, b, path=""):
            if type(a) is not type(b):
                diff.append((path, a, b)); return
            if isinstance(a, dict):
                for k in sorted(set(a) | set(b)):
                    if k not in a or k not in b:
                        diff.append((path + "/" + k, a.get(k), b.get(k)))
                    else:
                        walk(a[k], b[k], path + "/" + k)
            elif isinstance(a, list):
                if len(a) != len(b):
                    diff.append((path, a, b)); return
                for i, (x, y) in enumerate(zip(a, b)):
                    walk(x, y, f"{path}[{i}]")
            elif a != b:
                diff.append((path, a, b))
        walk(A["document"], C["document"])
    A["twin_C_field_diff"] = diff

    out["A_pg48_graded_fixture"] = A
    out["B_unmarked_twin"] = B
    out["C_complete_twin"] = C
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
