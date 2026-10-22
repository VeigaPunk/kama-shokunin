#!/usr/bin/env python3
"""FinalConsumer06: inspect the constructed fixture of the
unselected-invalid-correction consumer (bypasses the driver's temp cleanup
by calling the committed driver's own scenario() builder).

Writes raw JSON under out/FinalConsumer06/.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer06")
CLONE = BASE / "clone"
DRIVER = CLONE / ".ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py"
AFTER = CLONE / "tools/report-landing-audit.py"
BEFORE = BASE / "insp/before-report-landing-audit.py"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/postfix/out/FinalConsumer06")
OUT.mkdir(parents=True, exist_ok=True)
TMP = BASE / "tmp"
TMP.mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(TMP)

spec = importlib.util.spec_from_file_location("replay3", DRIVER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
       "PATH": "/usr/bin:/bin"}


def g(repo, *args):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), *args],
                       capture_output=True, env=ENV)
    return {"argv": ["git", "-C", str(repo), *args],
            "rc": p.returncode,
            "out": p.stdout.decode("utf-8", "replace").strip(),
            "err": p.stderr.decode("utf-8", "replace").strip()}


def run_tool(tool, lane, fleet, draft, errata):
    cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"]
    cmd += ["--errata", str(errata)] if errata else ["--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=60)
    rec = {"argv": cmd, "exit": p.returncode,
           "stderr": p.stderr.decode("utf-8", "replace").strip()[:600]}
    try:
        rec["doc"] = json.loads(p.stdout.decode("utf-8", "replace"))
    except Exception:
        rec["stdout"] = p.stdout.decode("utf-8", "replace")[:2000]
    return rec


def main():
    fx = BASE / "fixture"
    if fx.exists():
        subprocess.run(["rm", "-rf", str(fx)], check=True)
    fx.mkdir(parents=True)
    lane, fleet, draft, errata = mod.scenario(fx, "unselected-invalid-correction")
    report = {"scenario": "unselected-invalid-correction",
              "driver": str(DRIVER),
              "driver_sha256": mod.hashlib.sha256(DRIVER.read_bytes()).hexdigest(),
              "lane": str(lane), "fleet": str(fleet),
              "draft_path": str(draft), "errata_path": str(errata),
              "draft_text": draft.read_text(encoding="utf-8"),
              "errata_text": errata.read_text(encoding="utf-8")}
    parts = errata.read_text(encoding="utf-8").rstrip("\n").split("\t")
    token, correction = parts[2], parts[3]
    report["errata_row"] = {"round": parts[0], "kind": parts[1],
                             "token": token, "correction": correction,
                             "evidence": parts[4]}
    # the valid work commit cited by the draft
    cited = draft.read_text(encoding="utf-8").split("`")[1]
    report["cited_commit"] = cited
    report["git_observation"] = {
        "token_cat_file_type_lane": g(lane, "cat-file", "-t", token),
        "token_cat_file_type_fleet": g(fleet, "cat-file", "-t", token),
        "token_rev_parse_lane": g(lane, "rev-parse", "--verify", token + "^{commit}"),
        "cited_type_lane": g(lane, "cat-file", "-t", cited),
        "cited_type_fleet": g(fleet, "cat-file", "-t", cited),
        "cited_rev_lane": g(lane, "rev-parse", cited),
        "cited_is_ancestor_of_lane_head": g(lane, "merge-base", "--is-ancestor",
                                            cited, "HEAD"),
        "lane_objects": g(lane, "cat-file", "--batch-all-objects",
                          "--batch-check=%(objectname) %(objecttype) %(objectsize)"),
        "fleet_objects": g(fleet, "cat-file", "--batch-all-objects",
                           "--batch-check=%(objectname) %(objecttype) %(objectsize)"),
        "lane_refs": g(lane, "show-ref"),
        "fleet_refs": g(fleet, "show-ref"),
        "lane_log": g(lane, "log", "--format=%H %T %s"),
        "fleet_log": g(fleet, "log", "--format=%H %T %s"),
    }
    report["after_with_ledger"] = run_tool(AFTER, lane, fleet, draft, errata)
    report["before_with_ledger"] = run_tool(BEFORE, lane, fleet, draft, errata)
    report["after_no_ledger"] = run_tool(AFTER, lane, fleet, draft, None)
    report["before_no_ledger"] = run_tool(BEFORE, lane, fleet, draft, None)
    (OUT / "fixture-inspection.json").write_text(
        json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "draft_text": report["draft_text"],
        "errata_text": report["errata_text"],
        "cited_commit": cited,
        "token_type_lane": report["git_observation"]["token_cat_file_type_lane"],
        "cited_type_lane": report["git_observation"]["cited_type_lane"],
        "cited_type_fleet": report["git_observation"]["cited_type_fleet"],
        "after_with_ledger_exit": report["after_with_ledger"]["exit"],
        "after_summary": report["after_with_ledger"].get("doc", {}).get("summary"),
        "after_defects": report["after_with_ledger"].get("doc", {}).get("results"),
        "after_errata_invalid": report["after_with_ledger"].get("doc", {}).get("errata_invalid"),
        "after_errata_unmatched": report["after_with_ledger"].get("doc", {}).get("errata_unmatched"),
        "before_with_ledger_exit": report["before_with_ledger"]["exit"],
        "before_summary": report["before_with_ledger"].get("doc", {}).get("summary"),
        "before_errata_invalid": report["before_with_ledger"].get("doc", {}).get("errata_invalid"),
        "before_errata_unmatched": report["before_with_ledger"].get("doc", {}).get("errata_unmatched"),
    }, indent=1, sort_keys=True))


main()
