#!/usr/bin/env python3
"""Isolate which audit predicates reject each round-33 C2 receipt mutant.

Reuses the audit tool's own functions (parse_receipt, output_ok, expected_receipts)
against mutant receipts committed in the disposable clone, and reports the
oracle-side stable-field diffs plus resolution/tree evidence for the mutated
revision strings. Read-only on the lane repo.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = pathlib.Path(sys.argv[1]).resolve() / "lane"
BASE = "7c35289da5f4b94e062cd900eb086919e5094003"
SOURCE = "967d88528c1d83535563f971863f7855f76b4849"
RD = ".ufo/waves/round-33/c2/final"
STABLE = ("FORMAT", "FIXTURE", "COMMAND", "SOURCE_REV", "EVALUATED_REV",
          "EVALUATED_TREE", "GATE_SHA256", "EXIT_CODE")


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "r33gate", LANE / "tools/round33-gate-receipts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def blob(repo: pathlib.Path, rev: str, path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        capture_output=True, text=True, check=True).stdout


def resolves(repo: pathlib.Path, rev: str) -> bool:
    if not re.fullmatch(r"[0-9a-f]{40}", rev):
        return False
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", f"{rev}^{{commit}}"],
        capture_output=True, text=True).returncode == 0


def git_out(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def main() -> int:
    mod = load_tool()
    expected = mod.expected_receipts(LANE, SOURCE)
    gate_hash = hashlib.sha256(mod.read_blob(LANE, SOURCE, mod.GATE_PATH)).hexdigest()
    baseline = {
        relative: blob(SCRATCH, BASE, f"{RD}/{relative}")
        for relative, _exit, _line in mod.CASES.values()
    }
    report = json.loads(
        (LANE / ".ufo/waves/round-33/w1/out/MutReceiptRevision-evidence/mutants.json")
        .read_text(encoding="utf-8"))
    findings = []
    for entry in report["results"]:
        tip = entry["tip"]
        if entry["mutant"].startswith(("BASELINE", "RESTORED")):
            continue
        per_case = []
        for case, (relative, expected_exit, expected_line) in mod.CASES.items():
            receipt = blob(SCRATCH, tip, f"{RD}/{relative}")
            actual = mod.parse_receipt(receipt)
            exp = mod.parse_receipt(expected[case])
            headers = actual[0]
            runner_hash = headers.get("RUNNER_SHA256", "")
            evaluated = headers.get("EVALUATED_REV", "")
            oracle_command = (
                f"python3 {mod.GATE_PATH} --repo <lane> --rev {SOURCE}"
                if case == "gate-tip"
                else f"python3 {mod.GATE_PATH} --repo <fixture:{case}> --rev "
                     f"{exp[0]['EVALUATED_REV']}")
            tree_of_evaluated = None
            if resolves(SCRATCH, evaluated):
                tree_of_evaluated = git_out(SCRATCH, "rev-parse", f"{evaluated}^{{tree}}")
            per_case.append({
                "case": case,
                "mutated_vs_baseline": receipt != baseline[relative],
                "oracle_stable_fields_differing": sorted(
                    k for k in STABLE if headers.get(k) != exp[0].get(k)),
                "evaluated_rev": evaluated,
                "evaluated_rev_is_40_hex": bool(re.fullmatch(r"[0-9a-f]{40}", evaluated)),
                "evaluated_rev_resolves_to_commit": resolves(SCRATCH, evaluated),
                "evaluated_tree_matches_reported_tree":
                    tree_of_evaluated == headers.get("EVALUATED_TREE"),
                "reported_command_matches_oracle_command":
                    headers.get("COMMAND") == oracle_command,
                "stdout_matches_oracle": actual[1] == exp[1],
                "stderr_matches_oracle": actual[2] == exp[2],
                "exit_code_matches_oracle": headers.get("EXIT_CODE") == str(expected_exit),
                "runner_hash_known": runner_hash in mod.known_runner_hashes(LANE, BASE),
                "output_ok": bool(mod.output_ok(case, receipt, expected_exit,
                                                expected_line, SOURCE, gate_hash,
                                                runner_hash)),
            })
        findings.append({"mutant": entry["mutant"], "tip": tip,
                         "mutation": entry.get("detail"), "cases": per_case})
    out = LANE / ".ufo/waves/round-33/w1/out/MutReceiptRevision-evidence/isolate.json"
    out.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    for item in findings:
        for case in item["cases"]:
            if case["mutated_vs_baseline"]:
                slim = {k: v for k, v in case.items() if k != "mutated_vs_baseline"}
                print(json.dumps({"mutant": item["mutant"], **slim}))
    print(f"WROTE {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
