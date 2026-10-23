#!/usr/bin/env python3
"""Run real frozen/mutant counters on isolated fixture lanes; no transport mocks.

Stages: pristine, mutants, restored, summarize. Run restored only after replacing
sandbox mutant copies with the saved frozen bytes. Evidence mutant copies stay
intact. Every invocation acquires the shared counter lock independently.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

SHA = "382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6"
SANDBOX = Path("/fast/scratch/hyaku/kama-r27/KamaR27CtlCounterMutants")
EVIDENCE = Path(__file__).resolve().parent
LOCK = "/fast/scratch/hyaku/kama-r27/counter.lock"
FROZEN = SANDBOX / ".ufo/waves/round-27/count-c1.py"
FIXTURES = json.loads((EVIDENCE / "fixtures.json").read_text())["cases"]
MUTANTS = json.loads((EVIDENCE / "mutants.json").read_text())["mutants"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1, sort_keys=True) + "\n")


def limits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, 8 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
    _, hard = resource.getrlimit(resource.RLIMIT_NPROC)
    cap = 32768 if hard == resource.RLIM_INFINITY else min(hard, 32768)
    resource.setrlimit(resource.RLIMIT_NPROC, (cap, cap))


def clean_owned_orphans():
    """Only our adopted children; never scan or terminate other seats' servers."""
    children = Path(f"/proc/{os.getpid()}/task/{os.getpid()}/children")
    pids = [int(s) for s in children.read_text().split()]
    killed = []
    for pid in pids:
        try:
            os.killpg(pid, signal.SIGKILL)
            killed.append(pid)
        except ProcessLookupError:
            pass
    for pid in pids:
        try:
            os.waitpid(pid, 0)
        except ChildProcessError:
            pass
    return killed


def run_one(stage, variant, counter, wanted, case):
    assert digest(FROZEN) == SHA, "frozen counter changed"
    assert digest(counter) == wanted, "wrong counter copy bytes"
    root = EVIDENCE / "runs" / stage / variant
    root.mkdir(parents=True, exist_ok=True)
    name = case["name"]
    receipt_path = root / (name + ".receipt.json")
    assert not receipt_path.exists(), "refusing to replace existing run evidence"
    lane = "." if name == "pilot" else case["counter_lane"]
    command = ["flock", LOCK, "timeout", "-k", "15", "900", "python3",
               str(counter), "--lane", lane, "--repo", ".", "--out", str(receipt_path)]
    started = time.time()
    env = dict(os.environ)
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    proc = subprocess.Popen(command, cwd=SANDBOX, env=env, start_new_session=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            preexec_fn=limits)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=1020)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
    finally:
        orphan_groups = clean_owned_orphans()
    stdout_text, stderr_text = stdout.decode("utf-8", "replace"), stderr.decode("utf-8", "replace")
    (root / (name + ".stdout.txt")).write_text(stdout_text)
    (root / (name + ".stderr.txt")).write_text(stderr_text)
    (root / (name + ".exit-code.txt")).write_text(str(proc.returncode) + "\n")
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    result = {"stage": stage, "variant": variant, "fixture": name,
              "command": command, "cwd": str(SANDBOX), "exit_code": proc.returncode,
              "stdout": stdout_text, "stderr": stderr_text, "timed_out": timed_out,
              "started_unix": started, "duration_seconds": round(time.time() - started, 3),
              "counter_sha256_before": wanted, "counter_sha256_after": digest(counter),
              "frozen_sha256_after": digest(FROZEN), "cleaned_owned_orphan_groups": orphan_groups,
              "receipt": receipt}
    emit(root / (name + ".run.json"), result)
    print(json.dumps({k: result[k] for k in ("stage", "variant", "fixture", "exit_code", "stdout", "duration_seconds")}), flush=True)
    return result


def load(stage, variant, name):
    return json.loads((EVIDENCE / "runs" / stage / variant / (name + ".run.json")).read_text())


def observable(result):
    return result["exit_code"], result["stdout"], result["stderr"]


def summarize():
    rows, valid, fixture_results = [], [], []
    for case in FIXTURES:
        before = load("pristine", "frozen", case["name"])
        restored = load("restored", "frozen", case["name"])
        rec = before["receipt"] or {}
        reasons = {r["id"]: r["why"] for r in rec.get("rows", [])}
        expected = {rid: [case["expected_reason"]] for rid in case["bad_ids"]}
        clean = (before["exit_code"] == 0 and "could_not_evaluate" not in rec and
                 all(reasons.get(rid) == why for rid, why in expected.items()) and
                 all(not why for rid, why in reasons.items() if rid not in expected) and
                 rec.get("counted") == case["registered"] - len(case["bad_ids"]))
        restored_same = observable(before) == observable(restored)
        if clean and restored_same:
            valid.append(case["name"])
        fixture_results.append({"fixture": case["name"], "registered": rec.get("registered"),
                                "counted": rec.get("counted"), "met": rec.get("met"),
                                "why": reasons, "single_clause_expected": expected,
                                "baseline_valid": clean, "restored_output_matches": restored_same,
                                "frozen_output": before["stdout"].strip(),
                                "restored_output": restored["stdout"].strip()})
    for mutant in MUTANTS:
        differences, all_outputs = [], []
        for case in FIXTURES:
            before = load("pristine", "frozen", case["name"])
            after = load("mutants", mutant["name"], case["name"])
            changed = observable(before) != observable(after)
            item = {"fixture": case["name"], "frozen_output": before["stdout"].strip(),
                    "mutant_output": after["stdout"].strip(),
                    "frozen_exit": before["exit_code"], "mutant_exit": after["exit_code"],
                    "output_changed": changed, "baseline_usable": case["name"] in valid,
                    "frozen_why": {r["id"]: r["why"] for r in (before["receipt"] or {}).get("rows", [])},
                    "mutant_why": {r["id"]: r["why"] for r in (after["receipt"] or {}).get("rows", [])}}
            all_outputs.append(item)
            if changed and case["name"] in valid:
                differences.append(item)
        verdict = "killed" if differences else ("survived" if len(valid) == len(FIXTURES) else "inconclusive")
        rows.append({"mutant": mutant["name"], "clause": mutant["clause"], "verdict": verdict,
                     "changed_usable_cases": differences, "all_case_outputs": all_outputs,
                     "before_sha256": SHA, "mutant_sha256": mutant["mutant_sha256"],
                     "restored_sha256": digest(Path(mutant["counter_path"]))})
    summary = {"schema": "kama-r27-counter-mutation-summary/v1", "fixtures": fixture_results,
               "usable_baseline_cases": valid, "mutants": rows,
               "killed": [r["mutant"] for r in rows if r["verdict"] == "killed"],
               "survived": [r["mutant"] for r in rows if r["verdict"] == "survived"],
               "inconclusive": [r["mutant"] for r in rows if r["verdict"] == "inconclusive"],
               "frozen_sha256_after": digest(FROZEN),
               "restored_all_exact": all(r["restored_sha256"] == SHA for r in rows)}
    emit(EVIDENCE / "summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("killed", "survived", "inconclusive", "restored_all_exact")}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("pristine", "mutants", "restored", "summarize"))
    args = parser.parse_args()
    # Servers create their own process groups. Become their subreaper so timeout
    # cleanup can kill our adopted groups without touching another seat.
    if ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "cannot become child subreaper")
    assert digest(FROZEN) == SHA
    if args.stage == "summarize":
        summarize()
        return
    variants = [("frozen", FROZEN, SHA)]
    if args.stage == "mutants":
        variants = [(m["name"], Path(m["counter_path"]), m["mutant_sha256"]) for m in MUTANTS]
    elif args.stage == "restored":
        # All restored scratch copies have identical SHA; exercise one actual
        # restored copy on the full detector instead of repeating identical work.
        variants = [("frozen", Path(MUTANTS[0]["counter_path"]), SHA)]
        assert all(digest(Path(m["counter_path"])) == SHA for m in MUTANTS)
    for variant, counter, wanted in variants:
        for case in FIXTURES:
            run_one(args.stage, variant, counter, wanted, case)


if __name__ == "__main__":
    main()
