#!/usr/bin/env python3
"""Bounded probe for the CodeLocalScope lane (round 24, commit 2e254a1).

Scope: negative diagnosis (missing cited object behind another ref / dangling
tree) versus ordinary object resolution (a present but unreachable object).

Scenarios
  A  PG40 exactly as the grid builder builds it (c_missing_cited_unselected_
     branch_promisor): does the report actually cite the missing side blob?
  B  the same fixture, but the report cites the missing side blob (the
     premise PG40's name claims): the missing cited object behind another
     ref must be exit 2 (could-not-evaluate), content-derived.
  B2 same as B, but the side ref is deleted: the hole is behind a dangling
     tree/commit instead of a live ref.
  C  a present but unreachable commit is cited: it must resolve normally
     (no refusal).
  C2 a present but unreachable blob is cited in the landed section: it must
     resolve as a present object (wrong type), never as missing.

No network, no transport, no repository program: local git plumbing only.
"""
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

WORK = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/work")
GRID = WORK / "tests/report-audit/promisor-grid.py"
AUDITOR = WORK / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/grid-root")
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

os.environ["TMPDIR"] = "/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/tmp"
Path(os.environ["TMPDIR"]).mkdir(parents=True, exist_ok=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


grid = load("grid", GRID)
aud = load("aud", AUDITOR)

report = {"scenarios": {}}


def fresh(name):
    root = ROOT / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    return root


def run_auditor(lane, fleet, tmp):
    code, out, err, timed_out = grid.run_auditor(AUDITOR, lane, fleet, tmp)
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    defects = []
    if doc:
        for res in doc.get("results", []):
            for d in res.get("defects", []):
                defects.append([d.get("kind"), d.get("token")])
    return {"exit": code, "timed_out": timed_out,
            "stderr": err.strip()[-600:], "stdout_nonempty": bool(out.strip()),
            "defects": sorted(defects)}


def diagnosis(lane):
    """The auditor's own store-wide diagnosis (missing, opaque)."""
    tip = grid.git(lane, "rev-parse", "HEAD").strip()
    missing, opaque = aud.missing_reachable(lane, tip)
    return {"tip": tip, "missing": sorted(missing), "opaque": sorted(opaque)}


# ---------------------------------------------------------------- scenario A
def scenario_a():
    root = fresh("A")
    tmp = root / "t"
    built = grid.BUILDERS["c_missing_cited_unselected_branch_promisor"](
        root, tmp)
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    text = grid.git(fleet, "show", f"HEAD:{grid.REL}")
    side = shas.get("unselected_blob")
    obs = {
        "builder": "c_missing_cited_unselected_branch_promisor",
        "options": "lane_mark=config, unselected_hole=True, fake_landed=True, "
                   "drop=('unselected_blob',)",
        "report_text": text,
        "cited_tokens_in_report": sorted(set(aud.FULL.findall(text))),
        "missing_side_blob_sha": side,
        "side_blob_cited_in_report": bool(side and side in text),
        "fabricated_token": grid.FAKE,
        "fabricated_token_cited_in_report": grid.FAKE in text,
        "side_ref_exists": bool(grid.git(lane, "for-each-ref",
                                         "--format=%(refname)",
                                         "refs/heads/side").strip()),
        "premise": built["premise"],
        "diagnosis": diagnosis(lane),
        "audit": run_auditor(lane, fleet, tmp),
    }
    report["scenarios"]["A_pg40_as_built"] = obs
    return obs


# ---------------------------------------------------------------- scenario B
def scenario_b(name, delete_side_ref):
    root = fresh(name)
    tmp = root / "t"
    built = grid.build(root, tmp, lane_mark="config", unselected_hole=True,
                       fake_landed=True, drop=("unselected_blob",))
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    side = shas["unselected_blob"]
    # the intended premise: the report cites the missing side blob
    text = grid.report_text(cites=[shas["lane_commit"], side])
    publish_if_changed(fleet, text, 2100)
    if delete_side_ref:
        grid.git(lane, "update-ref", "-d", "refs/heads/side")
    obs = {
        "side_ref_deleted": delete_side_ref,
        "report_text": text,
        "cited_missing_side_blob": side,
        "side_blob_present": grid.object_exists(lane, side),
        "diagnosis": diagnosis(lane),
        "audit": run_auditor(lane, fleet, tmp),
    }
    report["scenarios"][name] = obs
    return obs


# ---------------------------------------------------------------- scenario C
def scenario_c(name, cite_blob):
    root = fresh(name)
    tmp = root / "t"
    built = grid.build(root, tmp, lane_mark="config", unselected_hole=True)
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    # the side commit, its tree and its blob are present but unreachable
    side_commit = grid.git(lane, "rev-parse", "refs/heads/side").strip()
    grid.git(lane, "update-ref", "-d", "refs/heads/side")
    dangling_commit = side_commit
    dangling_blob = shas.get("unselected_blob")
    cite = dangling_blob if cite_blob else dangling_commit
    text = grid.report_text(cites=[shas["lane_commit"], cite])
    publish_if_changed(fleet, text, 2100)
    obs = {
        "cited_object": cite,
        "cited_object_present": grid.object_exists(lane, cite),
        "cited_object_reachable_from_ref": cite in {
            line.split()[0] for line in
            grid.git(lane, "rev-list", "--objects", "--all").split("\n")
            if line.strip()},
        "side_ref_exists": bool(grid.git(lane, "for-each-ref",
                                         "--format=%(refname)",
                                         "refs/heads/side").strip()),
        "diagnosis": diagnosis(lane),
        "audit": run_auditor(lane, fleet, tmp),
    }
    report["scenarios"][name] = obs
    return obs


def publish_if_changed(fleet, text, when):
    """Publish only when the committed report differs (an identical text
    would be an empty commit)."""
    current = grid.git(fleet, "show", f"HEAD:{grid.REL}")
    if current == text:
        return False
    grid.publish(fleet, text, when)
    return True


def scenario_e(name, lane_mark):
    """Plain (no promisor) twin of the cited-missing-behind-a-ref case."""
    root = fresh(name)
    tmp = root / "t"
    built = grid.build(root, tmp, lane_mark=lane_mark, unselected_hole=True,
                       fake_landed=True, drop=("unselected_blob",))
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    side = shas["unselected_blob"]
    text = grid.report_text(cites=[shas["lane_commit"], side])
    publish_if_changed(fleet, text, 2100)
    obs = {
        "lane_mark": lane_mark,
        "cited_missing_side_blob": side,
        "side_blob_present": grid.object_exists(lane, side),
        "diagnosis": diagnosis(lane),
        "audit": run_auditor(lane, fleet, tmp),
    }
    report["scenarios"][name] = obs
    return obs


def scenario_f(name, lane_mark):
    """No-harm row: a fabricated token is cited and a missing blob is
    uncited: the fabricated token is a proved absence (exit 1), the
    uncited hole blocks nothing."""
    root = fresh(name)
    tmp = root / "t"
    built = grid.build(root, tmp, lane_mark=lane_mark, unselected_hole=True,
                       fake_landed=True, drop=("unselected_blob",))
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    text = grid.report_text(cites=[shas["lane_commit"], grid.FAKE])
    publish_if_changed(fleet, text, 2100)
    obs = {
        "lane_mark": lane_mark,
        "fabricated_token": grid.FAKE,
        "missing_uncited_blob": shas["unselected_blob"],
        "diagnosis": diagnosis(lane),
        "audit": run_auditor(lane, fleet, tmp),
    }
    report["scenarios"][name] = obs
    return obs


a = scenario_a()
b = scenario_b("B_cited_missing_behind_ref", False)
b2 = scenario_b("B2_cited_missing_behind_dangling_tree", True)
c = scenario_c("C_present_unreachable_commit", False)
c2 = scenario_c("C2_present_unreachable_blob", True)
e_plain = scenario_e("E_cited_missing_behind_ref_plain", None)
f_plain = scenario_f("F_no_harm_fabricated_plus_uncited_hole_plain", None)
e_prom = scenario_e("E2_cited_missing_behind_ref_promisor", "config")
f_prom = scenario_f("F2_no_harm_fabricated_plus_uncited_hole_promisor",
                    "config")

(OUT / "probe-result.json").write_text(
    json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")
print(json.dumps(report, indent=1, sort_keys=True))
