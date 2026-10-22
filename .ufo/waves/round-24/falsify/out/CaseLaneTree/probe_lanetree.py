#!/usr/bin/env python3
"""CaseLaneTree independent probe.

Builds the PG15 (promisor) and PG16 (plain) fixtures with the grid's own
builders (read-only import), then independently asserts:
  * which objects are actually missing / present,
  * the exact auditor exit / stdout / stderr for current and frozen arms,
  * that the refusal reason is content-derived and names the missing tree,
  * that no object was acquired and no transport command ran (git trace),
  * the PG15/PG16 twin comparison of the refusal text (no verdict document
    exists for either row, so the comparison is textual).
Offline, local, no network: the promisor remote url points at a nonexistent
directory by construction.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent / "repo"
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "promisor_grid", REPO / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree/work")
SCRATCH.mkdir(parents=True, exist_ok=True)

FROZEN_REV = G.FROZEN


def frozen_auditor(dest):
    p = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob",
                        f"{FROZEN_REV}:{G.AUDIT}"], capture_output=True)
    if p.returncode:
        raise SystemExit("cannot read frozen auditor")
    dest.write_bytes(p.stdout)
    return dest


def present(repo, sha):
    return G.object_exists(repo, sha)


def run_auditor(auditor, lane, fleet, tmp, trace=None):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
    env = G.env()
    if trace:
        env["GIT_TRACE"] = "1"
        env["GIT_TRACE_FILE"] = str(trace)
    proc = subprocess.run(argv, capture_output=True, env=env, cwd=str(tmp),
                          timeout=60)
    return proc.returncode, proc.stdout.decode(errors="replace"), \
        proc.stderr.decode(errors="replace")


def case(name, builder, auditor_current, auditor_frozen, tag):
    tmp = SCRATCH / tag
    if tmp.exists():
        import shutil
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    built = G.BUILDERS[builder](SCRATCH, tmp)
    lane, fleet, shas = built["lane"], built["fleet"], built["shas"]
    prem = built["premise"]

    # ---- independent object census (not the builder's own report)
    lane_inv = G.object_inventory(lane)
    fleet_inv = G.object_inventory(fleet)
    census = {}
    for label, sha in (("lane_commit", shas["lane_commit"]),
                       ("tip_tree", shas["tip_tree"]),
                       ("f_blob", shas["f_blob"]),
                       ("sources_blob", shas["sources_blob"]),
                       ("report_blob", shas["report_blob"]),
                       ("fleet_tip_tree", shas["fleet_tip_tree"])):
        census[label] = {"oid": sha,
                         "in_lane": sha in lane_inv,
                         "in_fleet": sha in fleet_inv,
                         "cat_file_lane": present(lane, sha),
                         "cat_file_fleet": present(fleet, sha)}
    facts = {"promisor_facts_lane": G.promisor_facts(lane),
             "promisor_facts_fleet": G.promisor_facts(fleet),
             "premise": prem,
             "census": census,
             "missing_by_revlist": {
                 "lane": G.missing_objects(lane, "refs/heads/master"),
                 "fleet": G.missing_objects(fleet, "HEAD")},
             "lane_config": subprocess.run(
                 ["git", "-C", str(lane), "config", "--list"],
                 capture_output=True, env=G.env()).stdout.decode(
                     errors="replace").split(),
             }
    # the missing set must be exactly the dropped tip tree
    facts["missing_set_is_exactly_tip_tree"] = (
        facts["missing_by_revlist"]["lane"] == [shas["tip_tree"]])
    facts["fleet_has_no_missing"] = facts["missing_by_revlist"]["fleet"] == []

    before = {"lane": set(lane_inv), "fleet": set(fleet_inv)}
    trace = SCRATCH / f"{tag}-trace.txt"
    code_c, out_c, err_c = run_auditor(auditor_current, lane, fleet, tmp,
                                       trace=trace)
    after = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    trace_c = trace.read_text(errors="replace") if trace.exists() else ""
    trace.unlink(missing_ok=True)

    code_f, out_f, err_f = run_auditor(auditor_frozen, lane, fleet, tmp)

    facts["current"] = {"exit": code_c, "stdout": out_c, "stderr": err_c,
                        "objects_acquired": acquired}
    facts["frozen"] = {"exit": code_f, "stdout": out_f, "stderr": err_f}
    facts["trace_git_commands"] = [
        ln for ln in trace_c.splitlines()
        if "trace: built-in:" in ln or "exec" in ln]
    facts["trace_mentions_fetch_or_transport"] = [
        ln for ln in trace_c.splitlines()
        if ("fetch" in ln or "transport" in ln or "upload-pack" in ln
            or "remote-https" in ln or "http" in ln)]
    facts["stdout_is_json_verdict"] = False
    try:
        json.loads(out_c)
        facts["stdout_is_json_verdict"] = bool(out_c.strip())
    except ValueError:
        pass
    facts["stderr_has_metadata_refusal"] = any(
        s in err_c for s in G.METADATA_REFUSAL)
    facts["stderr_names_tip_tree"] = shas["tip_tree"] in err_c
    facts["stderr_reason_class_terms"] = [
        t for t in G.REASON_CLASSES["unavailable"] if t in err_c.lower()]
    facts["stderr_starts_cne"] = err_c.startswith(G.CNE_PREFIX)
    facts["stderr_names_missing_object_text"] = (
        "unavailable required object" in err_c)
    return facts


def main():
    current = REPO / G.AUDIT
    frozen = frozen_auditor(SCRATCH / "frozen-audit.py")
    report = {
        "pinned_commit": subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"],
            capture_output=True).stdout.decode().strip(),
        "frozen_revision": FROZEN_REV,
        "current_auditor_sha256": subprocess.run(
            ["sha256sum", str(current)], capture_output=True).stdout.decode().split()[0],
        "frozen_auditor_sha256": subprocess.run(
            ["sha256sum", str(frozen)], capture_output=True).stdout.decode().split()[0],
        "expectations_sha256": subprocess.run(
            ["sha256sum", str(REPO / "tests/report-audit/promisor-grid-expectations.json")],
            capture_output=True).stdout.decode().split()[0],
        "cases": {},
    }
    report["cases"]["PG15-missing-lane-tree-promisor"] = case(
        "PG15", "c_missing_lane_tree_promisor", current, frozen, "pg15")
    report["cases"]["PG16-missing-lane-tree-plain"] = case(
        "PG16", "c_missing_lane_tree_plain", current, frozen, "pg16")

    # ---- twin comparison: the verdict documents are both absent (exit 2),
    # so compare the normalised refusal text instead.
    def norm(text, key):
        rep = report["cases"][key]
        lane = str(rep["census"]["lane_commit"])  # unused placeholder
        return text
    p15 = report["cases"]["PG15-missing-lane-tree-promisor"]
    p16 = report["cases"]["PG16-missing-lane-tree-plain"]
    import re as _re
    def canon(text, case_key):
        t = text
        for key in ("PG15-missing-lane-tree-promisor", "PG16-missing-lane-tree-plain"):
            t = t.replace(str(SCRATCH / ("pg15" if key.startswith("PG15") else "pg16")), "<case>")
        t = _re.sub(r"/fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree/work/pg1[56]", "<case>", t)
        return t
    report["twin"] = {
        "verdict_document_present_pg15": p15["current"]["stdout"].strip() != "",
        "verdict_document_present_pg16": p16["current"]["stdout"].strip() != "",
        "current_stderr_equal_after_path_normalisation":
            canon(p15["current"]["stderr"], "PG15") == canon(p16["current"]["stderr"], "PG16"),
        "pg15_current_stderr": p15["current"]["stderr"],
        "pg16_current_stderr": p16["current"]["stderr"],
        "pg15_frozen_stderr": p15["frozen"]["stderr"],
        "pg16_frozen_stderr": p16["frozen"]["stderr"],
        "frozen_exit_pg15": p15["frozen"]["exit"],
        "frozen_exit_pg16": p16["frozen"]["exit"],
    }
    out = OUT / "probe.json"
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "cases": {k: {
            "exit_current": v["current"]["exit"],
            "exit_frozen": v["frozen"]["exit"],
            "stderr_current": v["current"]["stderr"].strip()[:400],
            "stderr_frozen": v["frozen"]["stderr"].strip()[:200],
            "missing_set_is_exactly_tip_tree": v["missing_set_is_exactly_tip_tree"],
            "fleet_has_no_missing": v["fleet_has_no_missing"],
            "acquired": v["current"]["objects_acquired"],
            "names_tip_tree": v["stderr_names_tip_tree"],
            "metadata_refusal": v["stderr_has_metadata_refusal"],
            "stdout_json": v["stdout_is_json_verdict"],
            "transport": v["trace_mentions_fetch_or_transport"],
        } for k, v in report["cases"].items()},
        "twin": {k: v for k, v in report["twin"].items()
                 if not k.endswith("_stderr")},
    }, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
