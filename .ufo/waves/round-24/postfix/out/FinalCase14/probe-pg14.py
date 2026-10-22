#!/usr/bin/env python3
"""Independent probe for PG14-missing-lane-blob-plain (current arm only).

Builds the pinned grid's OWN fixture (builder c_missing_lane_blob_plain),
records the premise facts, runs the pinned auditor directly with the same
argv the grid uses, and captures the FULL stdout/stderr (the grid keeps only
a 300 character tail).  A discrimination control builds the same fixture
WITHOUT the dropped blob so a blanket refusal (a precondition introduced by
the new scoped missing cache) would show up as a refusal instead of a
verdict.

Nothing here grades a grid cell: the graded cell is PG14 only, and it is
graded by the pinned grid itself (see grid-current-PG14.json).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase14/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDITOR = CLONE / "tools/report-landing-audit.py"
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase14/out")


def load_grid():
    spec = importlib.util.spec_from_file_location("pg_grid", GRID)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_auditor(grid, lane, fleet, tmp):
    argv = [sys.executable, str(AUDITOR), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    before = {"lane": grid.object_inventory(lane),
              "fleet": grid.object_inventory(fleet)}
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=grid.env(),
                            cwd=str(tmp), start_new_session=True)
    try:
        out, err = proc.communicate(timeout=grid.TIMEOUT)
        code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired:
        code, timed_out, out, err = None, True, b"", b""
    finally:
        try:
            os.killpg(proc.pid, 15)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    after = {"lane": grid.object_inventory(lane),
             "fleet": grid.object_inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    return {
        "argv": argv,
        "exit": code,
        "timed_out": timed_out,
        "stdout": out.decode(errors="replace"),
        "stderr": err.decode(errors="replace"),
        "objects_acquired": acquired,
        "survivors": grid.survivors(tmp),
    }


def identity_checks(res, names, forbidden):
    err = res["stderr"]
    out = res["stdout"]
    stdout_is_json = None
    try:
        json.loads(out)
        stdout_is_json = True
    except ValueError:
        stdout_is_json = False
    return {
        "exit": res["exit"],
        "stderr_starts_cne": err.startswith(grid_cne_prefix()),
        "stderr_full": err,
        "stderr_is_metadata_flavoured": any(f in err for f in forbidden),
        "stderr_has_internal_error": "could-not-evaluate: internal:" in err,
        "stderr_has_traceback": "Traceback (most recent call last)" in err,
        "names_present": [n for n in names if n and n in err],
        "names_any_present": any(n and n in err for n in names),
        "stdout_len": len(out),
        "stdout_is_json_document": stdout_is_json,
        "stdout_full": out,
        "objects_acquired": res["objects_acquired"],
        "timed_out": res["timed_out"],
        "survivors": res["survivors"],
    }


def grid_cne_prefix():
    return "could-not-evaluate:"


def main():
    grid = load_grid()
    root = grid.make_root()
    names = ["051975b0ced83169116c235e7691c0a1a8313300", "corpus/SOURCES.md"]
    forbidden = ["partial clone (", "promisor pack"]
    report = {
        "probe": "FinalCase14 independent premise+identity probe",
        "clone": str(CLONE),
        "clone_head": subprocess.run(["git", "-C", str(CLONE), "rev-parse",
                                      "HEAD"], capture_output=True,
                                     text=True).stdout.strip(),
        "grid_sha256": sha(GRID),
        "auditor_sha256": sha(AUDITOR),
        "expectations_sha256": sha(CLONE / "tests/report-audit" /
                                   "promisor-grid-expectations.json"),
        "tmpdir": os.environ.get("TMPDIR"),
        "grid_root": str(root),
        "cases": {},
    }

    # ---- the graded cell: PG14-missing-lane-blob-plain
    tmp = Path(root, "probe", "pg14")
    tmp.mkdir(parents=True, exist_ok=True)
    built = grid.BUILDERS["c_missing_lane_blob_plain"](root, tmp)
    lane, fleet, shas = built["lane"], built["fleet"], built["shas"]
    premise = {
        "builder": "c_missing_lane_blob_plain",
        "grid_premise": built["premise"],
        "lane_promisor_facts": grid.promisor_facts(lane),
        "fleet_promisor_facts": grid.promisor_facts(fleet),
        "lane_missing_objects": grid.missing_objects(lane, "refs/heads/master"),
        "fleet_missing_objects": grid.missing_objects(fleet, "HEAD"),
        "sources_blob_oid": shas["sources_blob"],
        "sources_blob_present": grid.object_exists(lane, shas["sources_blob"]),
        "lane_commit_oid": shas["lane_commit"],
        "lane_commit_present": grid.object_exists(lane, shas["lane_commit"]),
        "report_blob_present": grid.object_exists(fleet, shas["report_blob"]),
        "lane_branch": subprocess.run(
            ["git", "-C", str(lane), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True).stdout.strip(),
        "lane_config_promisor_keys": subprocess.run(
            ["git", "-C", str(lane), "config", "--list"], capture_output=True,
            text=True).stdout.strip().splitlines(),
    }
    res = run_auditor(grid, lane, fleet, tmp)
    report["cases"]["PG14-missing-lane-blob-plain"] = {
        "premise": premise,
        "observation": identity_checks(res, names, forbidden),
    }

    # ---- discrimination control: same fixture, blob NOT dropped
    tmp2 = Path(root, "probe", "control-complete-lane")
    tmp2.mkdir(parents=True, exist_ok=True)
    built2 = grid.BUILDERS["c_complete_lane_plain"](root, tmp2)
    lane2, fleet2, shas2 = built2["lane"], built2["fleet"], built2["shas"]
    premise2 = {
        "builder": "c_complete_lane_plain",
        "note": "diagnostic control only, NOT a graded grid cell",
        "sources_blob_present": grid.object_exists(lane2,
                                                    shas2["sources_blob"]),
        "lane_missing_objects": grid.missing_objects(lane2,
                                                      "refs/heads/master"),
        "fleet_missing_objects": grid.missing_objects(fleet2, "HEAD"),
        "same_sources_blob_oid": shas2["sources_blob"] == shas["sources_blob"],
        "same_lane_commit_oid": shas2["lane_commit"] == shas["lane_commit"],
    }
    res2 = run_auditor(grid, lane2, fleet2, tmp2)
    report["cases"]["control-complete-lane-plain"] = {
        "premise": premise2,
        "observation": identity_checks(res2, names, forbidden),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "probe-pg14.json").write_text(
        json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v["observation"] for k, v in
                      report["cases"].items()}, indent=1, sort_keys=True))
    print("probe written:", OUT / "probe-pg14.json")


if __name__ == "__main__":
    main()
