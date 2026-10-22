"""FinalCase46 supplemental metadata-only companion for PG47 (outside the 47).

Builds the UNRUN PG47 fixture with the pinned grid builder, filesystem-copies
it, removes only the builder-installed promisor metadata from the copy, attests
identical object/ref/missing premises, then runs the pinned auditor on both via
the pinned grid's own run_case.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase46")
CLONE = S / "clone"
CASE = "PG47-opaque-tree-with-unresolved-fabricated-token"
out_dir = Path(sys.argv[1])

spec = importlib.util.spec_from_file_location(
    "grid", CLONE / "tests/report-audit/promisor-grid.py")
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

table, digest = grid.load_manifest()
case = next(c for c in table["cases"] if c["case"] == CASE)
auditor = (CLONE / "tools/report-landing-audit.py").resolve()

root = grid.make_root()
orig_tmp = Path(root, "orig")
orig_tmp.mkdir()
built = grid.BUILDERS[case["builder"]](root, orig_tmp)
shas = built["shas"]


def tree_digest(path):
    h = hashlib.sha256()
    for p in sorted(Path(path).rglob("*")):
        if p.is_file() and not p.is_symlink():
            h.update(str(p.relative_to(path)).encode() + b"\0")
            h.update(p.read_bytes())
    return h.hexdigest()


def config_list(repo):
    return sorted(e for e in grid.git(repo, "config", "--local", "--null",
                                      "--list").split("\0") if e)


def facts(repo, ref):
    gd = grid.git_dir(repo)
    return {
        "inventory": sorted(grid.object_inventory(repo)),
        "objects_dir_sha256": tree_digest(gd / "objects"),
        "refs": grid.git(repo, "for-each-ref",
                         "--format=%(refname) %(objectname)").split("\n"),
        "missing_no_lazy": grid.missing_objects(repo, ref),
        "promisor": grid.promisor_facts(repo),
        "origin_url": grid.git(repo, "config", "--get", "remote.origin.url",
                               check=False).strip(),
        "config": config_list(repo),
        "markers": sorted(p.name for p in (gd / "objects/pack").glob(
            "*.promisor")),
    }


# filesystem copy of the unrun fixture (no auditor has run yet)
comp_tmp = Path(root, "companion")
comp_tmp.mkdir()
for name in ("lane", "fleet"):
    shutil.copytree(built[name], comp_tmp / name, symlinks=True)
comp = dict(built, lane=comp_tmp / "lane", fleet=comp_tmp / "fleet")

before_strip = {"orig_lane": facts(built["lane"], "refs/heads/master"),
                "comp_lane_pre": facts(comp["lane"], "refs/heads/master")}
removed = []
for key in ("remote.origin.promisor", "extensions.partialclone"):
    if grid.git(comp["lane"], "config", "--local", "--get", key,
                check=False).strip():
        grid.git(comp["lane"], "config", "--local", "--unset-all", key)
        removed.append(key)
for repo in (comp["lane"], comp["fleet"]):
    pack = grid.git_dir(repo) / "objects/pack"
    for m in pack.glob("*.promisor"):
        if m.with_suffix(".pack").exists():
            m.unlink()
            removed.append(str(m.relative_to(repo)))

att = {
    "orig": {"lane": facts(built["lane"], "refs/heads/master"),
             "fleet": facts(built["fleet"], "HEAD")},
    "comp": {"lane": facts(comp["lane"], "refs/heads/master"),
             "fleet": facts(comp["fleet"], "HEAD")},
}
missing_subtree = shas["missing_subtree"]
checks = {
    "removed_exactly": removed,
    "lane_inventory_equal": att["orig"]["lane"]["inventory"]
    == att["comp"]["lane"]["inventory"],
    "fleet_inventory_equal": att["orig"]["fleet"]["inventory"]
    == att["comp"]["fleet"]["inventory"],
    "lane_objects_bytes_equal": att["orig"]["lane"]["objects_dir_sha256"]
    == att["comp"]["lane"]["objects_dir_sha256"],
    "fleet_objects_bytes_equal": att["orig"]["fleet"]["objects_dir_sha256"]
    == att["comp"]["fleet"]["objects_dir_sha256"],
    "refs_equal": all(att["orig"][r]["refs"] == att["comp"][r]["refs"]
                      for r in ("lane", "fleet")),
    "missing_equal": all(att["orig"][r]["missing_no_lazy"]
                         == att["comp"][r]["missing_no_lazy"]
                         for r in ("lane", "fleet")),
    "missing_is_subtree_only": att["orig"]["lane"]["missing_no_lazy"]
    == [missing_subtree] and att["orig"]["fleet"]["missing_no_lazy"] == [],
    "subtree_is_lane_tip_d": grid.git(built["lane"], "rev-parse",
                                      f"{shas['lane_commit']}:d").strip()
    == missing_subtree,
    "subtree_absent_both": not grid.object_exists(built["lane"], missing_subtree)
    and not grid.object_exists(comp["lane"], missing_subtree),
    "fake_absent_all": not any(grid.object_exists(r, grid.FAKE) for r in (
        built["lane"], built["fleet"], comp["lane"], comp["fleet"])),
    "origin_url_equal": att["orig"]["lane"]["origin_url"]
    == att["comp"]["lane"]["origin_url"],
    "origin_url_target_exists": Path(att["orig"]["lane"]["origin_url"]).exists(),
    "orig_lane_promisor_backed": att["orig"]["lane"]["promisor"]["promisor_backed"],
    "comp_lane_promisor_backed": att["comp"]["lane"]["promisor"]["promisor_backed"],
    "config_diff_orig_minus_comp": sorted(set(att["orig"]["lane"]["config"])
                                          - set(att["comp"]["lane"]["config"])),
    "config_diff_comp_minus_orig": sorted(set(att["comp"]["lane"]["config"])
                                          - set(att["orig"]["lane"]["config"])),
    "fleet_config_equal": att["orig"]["fleet"]["config"]
    == att["comp"]["fleet"]["config"],
    "report_blob_equal": grid.git(built["fleet"], "rev-parse",
                                  f"HEAD:{grid.REL}").strip()
    == grid.git(comp["fleet"], "rev-parse", f"HEAD:{grid.REL}").strip(),
}
premise_ok = all(checks[k] for k in (
    "lane_inventory_equal", "fleet_inventory_equal", "lane_objects_bytes_equal",
    "fleet_objects_bytes_equal", "refs_equal", "missing_equal",
    "missing_is_subtree_only", "subtree_is_lane_tip_d", "subtree_absent_both",
    "fake_absent_all", "origin_url_equal", "orig_lane_promisor_backed",
    "fleet_config_equal", "report_blob_equal")) \
    and not checks["comp_lane_promisor_backed"] \
    and not checks["config_diff_comp_minus_orig"]

result = {"case": CASE, "grid_sha256": hashlib.sha256(
    (CLONE / "tests/report-audit/promisor-grid.py").read_bytes()).hexdigest(),
    "auditor_sha256": hashlib.sha256(auditor.read_bytes()).hexdigest(),
    "expectations_sha256": digest, "root": str(root),
    "builder_premise": built["premise"], "shas": shas,
    "checks": checks, "premise_ok": premise_ok}
if premise_ok:
    rows = {}
    for label, b, tmp in (("promisor", built, orig_tmp),
                          ("plain", comp, comp_tmp)):
        obs = grid.run_case(auditor, b, case, tmp, "current", shas)
        obs["stderr_normalised"] = obs["stderr_tail"].replace(
            str(b["lane"]), "<lane>").replace(str(b["fleet"]), "<fleet>")
        rows[label] = obs
    result["rows"] = rows
    p, q = rows["promisor"], rows["plain"]
    result["comparison"] = {
        "exits": [p["exit"], q["exit"]],
        "exit_class": ("diagnostic-only" if p["exit"] == q["exit"] == 2
                       else "other"),
        "documents": [p["document"], q["document"]],
        "document_equality": "not-applicable: refusal has no verdict document",
        "normalised_refusal_identical": p["stderr_normalised"]
        == q["stderr_normalised"],
    }
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "supplement.json").write_text(json.dumps(result, indent=1) + "\n")
print(json.dumps({"premise_ok": premise_ok, "checks": checks,
                  "comparison": result.get("comparison"),
                  "exits": {k: v["exit"] for k, v in result.get("rows", {}).items()},
                  "met": {k: v["met_amended"] for k, v in result.get("rows", {}).items()},
                  "acquired": {k: v["objects_acquired"] for k, v in result.get("rows", {}).items()},
                  "stderr": {k: v["stderr_normalised"] for k, v in result.get("rows", {}).items()}},
                 indent=1))
