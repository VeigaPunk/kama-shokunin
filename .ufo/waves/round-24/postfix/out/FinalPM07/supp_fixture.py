#!/usr/bin/env python3
"""FinalPM07 supplementary, PRIVATE fixture (outside the frozen 47).

Shape (as tasked):
  * complete SELECTED master / audit inputs - the lane master closure and
    the fleet report are fully present;
  * an ordinary fabricated citation in the report (the grid family's $fake
    full-hash token), which the local-object contract grades as an ordinary
    failed finding (exit 1);
  * an UNSELECTED ref that points at an ABSENT commit which is not among
    the present roots of the store.

Three auditors are measured on the SAME fixture (no fixture is rebuilt
between measurements; the object inventory is snapshotted at build time and
before and after every run):
  1. pristine pinned auditor,
  2. the canonical PM07 operator (roots.append("--all") in the store-wide
     missing walk) applied to a private copy,
  3. SUPPLEMENT-OPAQUE-ALLREFS: a separately named variant that broadens
     ONLY the opacity (name-hiding) walk to the actual Git --all argv.
     NOT the canonical operator, no primary-population credit.

All git observations use the auditor's own isolation flags
(--no-lazy-fetch, --no-replace-objects, ...): no fetch, no network.
"""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM07")
CLONE = S / "clone"
WORK = S / "work"
FIXTURES = S / "out/fixtures"
FAKE = "0123456789abcdef0123456789abcdef01234567"

spec = importlib.util.spec_from_file_location(
    "promisor_grid", CLONE / "tests/report-audit/promisor-grid.py")
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

aspec = importlib.util.spec_from_file_location(
    "pinned_auditor", CLONE / "tools/report-landing-audit.py")
auditor_mod = importlib.util.module_from_spec(aspec)
aspec.loader.exec_module(auditor_mod)

FIXTURES.mkdir(parents=True, exist_ok=True)
tmp = FIXTURES / "supp-unselected-absent-commit"
if tmp.exists():
    shutil.rmtree(tmp)
tmp.mkdir(parents=True)

# ---------------------------------------------------------------- fixture
built = grid.build(FIXTURES, tmp, lane_mark="config", fake_landed=True)
lane, fleet = built["lane"], built["fleet"]
shas = built["shas"]

# an unselected branch whose commit object is then removed: the ref stays,
# its target does not, so the ref points at an absent commit.
grid.git(lane, "checkout", "-q", "-b", "unselected")
side = grid.commit(lane, "kama-shokunin", 1200, "unselected: file",
                    "unselected.txt", "unselected\n")
grid.git(lane, "checkout", "-q", "master")
Path(lane, "unselected.txt").unlink(missing_ok=True)
absent = side
grid.drop_object(lane, absent)          # the loose commit object is removed
ref_target = (Path(grid.git_dir(lane)) / "refs/heads/unselected").read_text().strip()

build_inventory = {"lane": grid.object_inventory(lane),
                   "fleet": grid.object_inventory(fleet)}

premise = {
    "lane": str(lane), "fleet": str(fleet),
    "lane_promisor": built["premise"]["lane_promisor"],
    "unselected_ref": "refs/heads/unselected",
    "unselected_ref_target": ref_target,
    "absent_commit": absent,
    "absent_commit_served": grid.object_exists(lane, absent),
    "absent_commit_in_present_roots": absent in auditor_mod.present_roots(lane),
    "selected_master_closure_missing":
        grid.missing_objects(lane, "refs/heads/master"),
    "fleet_report_closure_missing": grid.missing_objects(fleet, "HEAD"),
    "fake_token": FAKE,
    "fake_token_present": grid.object_exists(lane, FAKE)
    or grid.object_exists(fleet, FAKE),
    "selected_master_commit": shas["lane_commit"],
    "fleet_report_blob": shas["report_blob"],
    "build_inventory_lane_count": len(build_inventory["lane"]),
    "build_inventory_fleet_count": len(build_inventory["fleet"]),
}
print(json.dumps(premise, indent=1))

# ---------------------------------------------- what the two walks see
# the auditor's own isolated git(): --no-lazy-fetch, --no-replace-objects
def walk(extra, roots):
    out = auditor_mod.git(lane, "-c", "core.commitGraph=false", "rev-list",
                          "--objects", "--missing=print", "--no-object-names",
                          *extra, "--stdin",
                          stdin="".join(f"{r}\n" for r in roots))
    return sorted(l[1:] for l in out.split("\n") if l.startswith("?"))

pr = auditor_mod.present_roots(lane)
walk_facts = {
    "pristine_store_wide_missing": walk((), pr + [shas["lane_commit"]]),
    "canonical_pm07_store_wide_missing":
        walk((), pr + [shas["lane_commit"], "--all"]),
    "pristine_opacity_missing": walk(("--filter=blob:none",),
                                     [shas["lane_commit"]]),
    "supplement_opaque_allrefs_opacity_missing":
        walk(("--filter=blob:none",), ["--all"]),
    "present_roots_count": len(pr),
    "present_roots_contains_absent": absent in pr,
}
print(json.dumps(walk_facts, indent=1))

# ------------------------------------------------------------ measurement
auditors = {
    "pristine": CLONE / "tools/report-landing-audit.py",
    "PM07-canonical": WORK / "auditor-PM07-canonical.py",
    "SUPPLEMENT-OPAQUE-ALLREFS": WORK / "auditor-SUPPLEMENT-OPAQUE-ALLREFS.py",
}

results = {}
for label, path in auditors.items():
    before = {"lane": grid.object_inventory(lane),
              "fleet": grid.object_inventory(fleet)}
    code, out, err, timed_out = grid.run_auditor(str(path), lane, fleet, tmp,
                                                  use_errata=False)
    after = {"lane": grid.object_inventory(lane),
             "fleet": grid.object_inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    defects, raw = grid.observed_defects(out)
    results[label] = {
        "auditor": str(path),
        "auditor_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "exit": code,
        "timed_out": timed_out,
        "traceback": "Traceback (most recent call last)" in err,
        "internal_error": "could-not-evaluate: internal:" in err,
        "stderr": err.strip()[:600],
        "stdout_len": len(out),
        "document": doc,
        "defects": defects,
        "raw_defects": raw,
        "objects_acquired": acquired,
        "inventory_unchanged_during_run":
            before["lane"] == after["lane"] and before["fleet"] == after["fleet"],
        "inventory_matches_build_snapshot":
            after["lane"] == build_inventory["lane"]
            and after["fleet"] == build_inventory["fleet"],
    }
    (S / "out" / f"supp-{label}.json").write_text(
        json.dumps(results[label], indent=1, sort_keys=True) + "\n")
    print(f"[{label}] exit={code} defects={defects} acquired={acquired} "
          f"inventory_unchanged={results[label]['inventory_unchanged_during_run']} "
          f"stderr={err.strip()[:220]!r}")

summary = {
    "fixture": str(tmp),
    "premise": premise,
    "walk_facts": walk_facts,
    "results": {k: {kk: vv for kk, vv in v.items() if kk != "document"}
                for k, v in results.items()},
    "documents_identical": {
        "PM07-canonical": results["pristine"]["document"]
        == results["PM07-canonical"]["document"],
        "SUPPLEMENT-OPAQUE-ALLREFS":
            results["pristine"]["document"]
            == results["SUPPLEMENT-OPAQUE-ALLREFS"]["document"],
    },
    "exit_map": {k: v["exit"] for k, v in results.items()},
}
(S / "out" / "supp-summary.json").write_text(
    json.dumps(summary, indent=1, sort_keys=True) + "\n")
print(json.dumps(summary["documents_identical"], indent=1))
print(json.dumps(summary["exit_map"], indent=1))
