#!/usr/bin/env python3
"""Grade the pinned finite error-versus-verdict regression set.

Usage: error-verdict-census.py --cells PATH [--lane PATH] [--json]
       error-verdict-census.py --selftest [--cells PATH] [--lane PATH]

Only the named grid, citation, and survivor-arm cells are accepted. Their
fixtures and expected before/after classes are pinned; no shell argv schema.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import signal
import subprocess
import sys
import tempfile

FROZEN_REV = "37bd4c5bd456a2f8a54d3312c28495c321715856"
MANIFEST_SHA256 = "ff3b7da9c060a7f12a7ca081c79db06899a4f5c9418d26ffe4a88bc6c607f469"
EVIDENCE_SHA256 = "846025bcb24be004c3953fb9c2ae1b38ad024a294294986b5c58a4f451e5769b"
FIXTURE_SHA256 = {
    "grid-gate.py": "0e65e584fe9d7bda52af233c7fd189555d4314b1b7ae6267b12cbf1e2d3bbb5f",
    "sitecustomize.py": "6a467c6306862d740416a34b22178d3aae3f72812a43de0387df91bbd5e06ab1",
    "survivor-arm-probe.py": "bf031256913317e688362adc0f663f6fce77228eba00a265c11adfc8deb95014",
}
GRID = "tests/llamacpp-live/install-tree-grid.py"
CITATION = "tools/citation-provenance.py"
SURVIVORS = ".ufo/waves/round-18/c2/survivors.py"
FROZEN_SOURCE_SHA256 = {
    GRID: "6f51803c47db597e2f6778b492bfaba14735a23c599bc972f8d33ab477a68f05",
    CITATION: "5c887572b37a80c0757b59a7735da386be2885e463ec2682c1d59f8e9b55110b",
    SURVIVORS: "ac934794af1eee8067ea11f7f8cc31702ea7dfad257fec2649f2d638477bac75",
}
CELL_IDS = (
    "grid-exit1-traceback", "grid-exit1-silent", "grid-signal",
    "grid-timeout", "grid-unknown-exit", "grid-clean-baseline",
    "grid-real-invalid-verdict", "grid-invalid-then-traceback",
    "citation-git-unavailable", "citation-document-unreadable",
    "citation-nonexistent-revision", "citation-missing-token",
    "citation-valid-token", "survivor-selftest-early-abort",
    "survivor-selftest-complete-target-failure",
)
RED_IDS = (
    "grid-exit1-traceback", "grid-exit1-silent", "grid-signal",
    "grid-unknown-exit", "grid-invalid-then-traceback",
    "survivor-selftest-early-abort",
)
CLASSES = {"accepted", "rejected", "failed", "killed", "error",
           "could-not-evaluate"}
MODES = {
    GRID: {"crash", "silent1", "signal", "timeout", "unknown", "accept",
           "invalid", "invalid-then-traceback"},
    CITATION: {"git-unavailable", "document-unreadable",
               "nonexistent-revision", "missing-token", "valid-token"},
    SURVIVORS: {"early-abort", "complete-target-failure"},
}
CELL_TIMEOUT = 30


class CensusFault(Exception):
    pass


def env_for(work):
    return {"PATH": os.environ.get("PATH", os.defpath), "HOME": str(work),
            "TMPDIR": str(work), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_OPTIONAL_LOCKS": "0", "PYTHONDONTWRITEBYTECODE": "1"}


def child(argv, cwd, env, timeout=CELL_TIMEOUT):
    try:
        proc = subprocess.Popen(argv, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
    except OSError as exc:
        return False, None, "", str(exc)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
        return False, proc.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")
    return True, proc.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def validate_registry(rows):
    if not isinstance(rows, list) or not rows or tuple(
            row.get("id") if isinstance(row, dict) else None for row in rows) != CELL_IDS:
        raise CensusFault("registry IDs/order differ from the pinned denominator")
    if tuple(row["id"] for row in rows if row.get("known_red") is True) != RED_IDS:
        raise CensusFault("registry known-red vector differs from the pinned red set")
    keys = {"id", "instrument", "mode", "expected_frozen_class",
            "expected_current_class", "known_red"}
    for row in rows:
        if set(row) != keys:
            raise CensusFault(f"unexpected registry fields for {row['id']}")
        if row["instrument"] not in MODES or row["mode"] not in MODES[row["instrument"]]:
            raise CensusFault(f"unsupported instrument/mode: {row['id']}")
        if row["expected_frozen_class"] not in CLASSES or row["expected_current_class"] not in CLASSES:
            raise CensusFault(f"invalid expected class: {row['id']}")
        if row["known_red"] != (row["expected_frozen_class"] != row["expected_current_class"]):
            raise CensusFault(f"known-red bit disagrees with classes: {row['id']}")
    if {row["expected_current_class"] for row in rows} != CLASSES:
        raise CensusFault("registry must retain both verdict and error classes")
    return rows


def load_registry(path, fixture_dir):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise CensusFault(f"cannot read registry: {type(exc).__name__}") from exc
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise CensusFault("registry digest differs from the runner-pinned digest")
    try:
        rows = validate_registry(json.loads(raw.decode("utf-8")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CensusFault(f"invalid registry: {type(exc).__name__}") from exc
    root, fixtures = Path(fixture_dir).resolve(), {}
    for name, expected in FIXTURE_SHA256.items():
        try:
            source = (root / name).resolve(strict=True)
            source.relative_to(root)
            data = source.read_bytes()
        except (OSError, ValueError) as exc:
            raise CensusFault(f"fixture unavailable: {name}") from exc
        if hashlib.sha256(data).hexdigest() != expected:
            raise CensusFault(f"fixture digest mismatch: {name}")
        fixtures[name] = data
    return rows, fixtures, raw


def git_show(lane, revision, path):
    try:
        proc = subprocess.run(["git", "-C", str(lane), "show", f"{revision}:{path}"],
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=env_for(Path(lane)),
                              timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CensusFault(f"git show failed for {path}: {type(exc).__name__}") from exc
    if proc.returncode:
        raise CensusFault(f"git show failed for {path}: exit {proc.returncode}")
    if hashlib.sha256(proc.stdout).hexdigest() != FROZEN_SOURCE_SHA256.get(path):
        raise CensusFault(f"frozen instrument digest mismatch: {path}")
    return proc.stdout


def doc(output):
    try:
        value = json.loads(output)
    except (json.JSONDecodeError, RecursionError):
        return None
    return value if isinstance(value, dict) else None


def classify_grid(run):
    ran, rc, stdout, stderr = run
    if not ran:
        return "could-not-evaluate"
    result = doc(stdout)
    if result is not None:
        if result.get("baseline") == "ERROR":
            return "error"
        if result.get("baseline") != "VALID":
            return "could-not-evaluate"
        rows = result.get("rows")
        status = rows[0].get("status") if isinstance(rows, list) and len(rows) == 1 \
            and isinstance(rows[0], dict) else None
        return status if status in {"accepted", "rejected", "error"} else "could-not-evaluate"
    return "error" if "Traceback (most recent call last):" in stderr else \
        "could-not-evaluate"


def classify_citation(run):
    ran, rc, stdout, stderr = run
    if not ran:
        return "could-not-evaluate"
    result = doc(stdout)
    counts = result.get("counts") if result else None
    if isinstance(counts, dict):
        nums = [counts.get(key) for key in
                ("docs_unreadable", "missing", "mismatch", "off_ref")]
        if any(not isinstance(n, int) or isinstance(n, bool) for n in nums):
            return "could-not-evaluate"
        unreadable, missing, mismatch, off_ref = nums
        if unreadable:
            return "error"
        # A nonexistent revision is a row mismatch verdict, not unusable Git.
        if missing or mismatch or off_ref:
            return "failed"
        return "accepted" if rc == 0 else "error"
    if rc == 2 or "citation-provenance:" in stderr or \
            "Traceback (most recent call last):" in stdout + stderr:
        return "error"
    return "could-not-evaluate"


def classify_survivor(run):
    if not run[0]:
        return "could-not-evaluate"
    result = doc(run[2])
    status = result.get("outcome") if result else None
    if status in {"killed", "survived", "error"}:
        return status
    return "could-not-evaluate"


def run_grid(cell, program, fixtures):
    with tempfile.TemporaryDirectory(prefix="error-verdict-grid-") as temp:
        work = Path(temp)
        script = work / GRID
        script.parent.mkdir(parents=True)
        script.write_bytes(program)
        gate, receipt = work / "grid-gate.py", work / "receipt.json"
        gate.write_bytes(fixtures["grid-gate.py"])
        receipt.write_text(json.dumps({"server": {"install_tree": {
            "libllama.so.0.7.0": "a" * 64}}}), encoding="utf-8")
        env = env_for(work)
        env["CENSUS_GATE_MODE"] = cell["mode"]
        if cell["mode"] == "timeout":
            (work / "sitecustomize.py").write_bytes(fixtures["sitecustomize.py"])
            env["PYTHONPATH"] = str(work)
        args = ["--gate", str(gate), "--receipt", str(receipt),
                "--model-sha", "model", "--server-sha", "server",
                "--impl-sha", "impl", "--probe-sha", "probe",
                "--tool-sha", "tool", "--members", "libllama.so.0.7.0", "--json"]
        run = child([sys.executable, str(script), *args], work, env)
        return classify_grid(run), run[0]


def git_fixture(work, env):
    evidence = work / "evidence.txt"
    evidence.write_text("census evidence\n", encoding="utf-8")
    cmds = (["git", "init", "-q", "--template="],
            ["git", "add", "--", "evidence.txt"],
            ["git", "-c", "user.name=census fixture", "-c",
             "user.email=fixture@example.invalid", "commit", "-q", "-m", "fixture"],
            ["git", "rev-parse", "HEAD"])
    for command in cmds:
        run = child(list(command), work, env, timeout=20)
        if not run[0] or run[1] != 0:
            raise CensusFault("cannot create citation fixture repository")
    return run[2].strip()


def run_citation(cell, program):
    with tempfile.TemporaryDirectory(prefix="error-verdict-citation-") as temp:
        work = Path(temp)
        script = work / CITATION
        script.parent.mkdir(parents=True)
        script.write_bytes(program)
        env = env_for(work)
        env.update(GIT_AUTHOR_DATE="2000-01-01T00:00:00Z",
                   GIT_COMMITTER_DATE="2000-01-01T00:00:00Z")
        head = git_fixture(work, env)
        revision = "f" * 40 if cell["mode"] == "nonexistent-revision" else head
        registry = work / "registry.json"
        registry.write_text(json.dumps([{"id": "fixture", "rev": revision,
                                         "path": "evidence.txt",
                                         "sha256": EVIDENCE_SHA256}]), encoding="utf-8")
        doc_path = work / "doc.md"
        token = f"cite({revision}, evidence.txt, sha256={EVIDENCE_SHA256})\n"
        doc_path.write_text("no citation token\n" if cell["mode"] == "missing-token"
                            else token, encoding="utf-8")
        docs = work / "absent.md" if cell["mode"] == "document-unreadable" else doc_path
        if cell["mode"] == "git-unavailable":
            env["PATH"] = ""
        args = [sys.executable, str(script), "--lane", str(work),
                "--registry", str(registry), "--docs", str(docs),
                "--allow-off-ref", "--json"]
        run = child(args, work, env)
        return classify_citation(run), run[0]


def run_survivor(cell, program, fixture):
    with tempfile.TemporaryDirectory(prefix="error-verdict-survivor-") as temp:
        work = Path(temp)
        module = work / SURVIVORS
        module.parent.mkdir(parents=True)
        module.write_bytes(program)
        wrapper = work / "survivor-arm-probe.py"
        wrapper.write_bytes(fixture)
        run = child([sys.executable, str(wrapper), str(module), cell["mode"]],
                    work, env_for(work))
        return classify_survivor(run), run[0]


def run_cell(cell, program, fixtures):
    if cell["instrument"] == GRID:
        return run_grid(cell, program, fixtures)
    if cell["instrument"] == CITATION:
        return run_citation(cell, program)
    return run_survivor(cell, program, fixtures["survivor-arm-probe.py"])


def census(lane, rows, fixtures, arm):
    lane = Path(lane).resolve()
    results, unrun, frozen = [], [], {}
    for cell in rows:
        path = cell["instrument"]
        if arm != "current" and path not in frozen:
            frozen[path] = git_show(lane, FROZEN_REV, path)
        old_class = new_class = None
        old_ran = new_ran = None
        if arm != "current":
            old_class, old_ran = run_cell(cell, frozen[path], fixtures)
        if arm != "frozen":
            source = lane.joinpath(*PurePosixPath(path).parts)
            try:
                current = source.resolve(strict=True)
                current.relative_to(lane)
                if not current.is_file():
                    raise OSError("not a regular file")
                current_bytes = current.read_bytes()
            except (OSError, ValueError) as exc:
                raise CensusFault(f"cannot read current instrument {path}") from exc
            new_class, new_ran = run_cell(cell, current_bytes, fixtures)
        if old_ran is False or new_ran is False:
            unrun.append(cell["id"])
        results.append({
            "id": cell["id"], "frozen_class": old_class,
            "current_class": new_class,
            "expected_frozen_class": cell["expected_frozen_class"],
            "expected_current_class": cell["expected_current_class"],
            "known_red": cell["known_red"],
            "frozen_witness_match": (old_class == cell["expected_frozen_class"])
                if old_class is not None else None,
            "frozen_ran": old_ran, "current_ran": new_ran,
        })
    frozen_bad = (sum(r["frozen_class"] != r["expected_current_class"] for r in results)
                  if arm != "current" else None)
    current_bad = (sum(r["current_class"] != r["expected_current_class"] for r in results)
                   if arm != "frozen" else None)
    witness_bad = (sum(not r["frozen_witness_match"] for r in results)
                   if arm != "current" else None)
    red_bad = (sum(r["known_red"] !=
                   (r["frozen_class"] != r["expected_current_class"]) for r in results)
               if arm != "current" else None)
    return {
        "arm": arm, "cells": len(results),
        "frozen_misclassified": frozen_bad, "current_misclassified": current_bad,
        "frozen_witness_mismatches": witness_bad, "red_vector_mismatches": red_bad,
        "frozen_errors": (sum(r["frozen_class"] == "error" for r in results)
                          if arm != "current" else None),
        "current_errors": (sum(r["current_class"] == "error" for r in results)
                           if arm != "frozen" else None),
        "unrun": unrun, "results": results,
    }


def emit(result, as_json):
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        frozen = result["frozen_misclassified"]
        current = result["current_misclassified"]
        print(f"cells={result['cells']} frozen_misclassified="
              f"{frozen if frozen is not None else 'NA'} "
              f"current_misclassified={current if current is not None else 'NA'}")
        print(f"errors frozen={result['frozen_errors'] if result['frozen_errors'] is not None else 'NA'} "
              f"current={result['current_errors'] if result['current_errors'] is not None else 'NA'}")


def default_cells():
    here = Path(__file__).resolve().parent
    for path in (here / "error-injection-cells.json",
                 here.parent / "registry" / "error-injection-cells.json"):
        if path.is_file():
            return path
    return here / "error-injection-cells.json"


def selftest(rows, fixtures, raw, lane):
    failures, original = [], json.loads(raw.decode("utf-8"))
    mutants = [[], original[:-1], original + [dict(original[0])],
               [dict(row, id="renamed") if i == 0 else row
                for i, row in enumerate(original)]]
    for candidate in mutants:
        if hashlib.sha256(json.dumps(candidate, separators=(",", ":")).encode()).hexdigest() == MANIFEST_SHA256:
            failures.append("mutated manifest digest collision")
        try:
            validate_registry(candidate)
        except (CensusFault, AttributeError):
            continue
        failures.append("empty/deleted/duplicate/relabeled manifest accepted")
    launderer = "import json; print(json.dumps({'baseline':'VALID','rows':[{'status':'rejected'}]}))"
    honest = ("import json,sys; s='error' if sys.argv[1]=='error' else 'rejected'; "
              "print(json.dumps({'baseline':'VALID','rows':[{'status':s}]}))")
    def stub(source, mode):
        run = child([sys.executable, "-c", source, mode], Path.cwd(), env_for(Path.cwd()))
        return classify_grid(run)
    if (stub(launderer, "error") != "rejected" or stub(honest, "error") != "error"
            or stub(launderer, "verdict") != "rejected"
            or stub(honest, "verdict") != "rejected"):
        failures.append("stub error/verdict directions")
    synthetic = (True, 1, json.dumps({"counts": {"docs_unreadable": 0,
                   "missing": 0, "mismatch": 1, "off_ref": 0},
                   "results": [{"status": "mismatch", "error": "missing rev"}]}), "")
    if classify_citation(synthetic) != "failed":
        failures.append("nonexistent revision must stay a failed verdict")
    frozen = git_show(Path(lane).resolve(), FROZEN_REV, SURVIVORS)
    for cell in (r for r in rows if r["instrument"] == SURVIVORS):
        outcome, ran = run_survivor(cell, frozen, fixtures["survivor-arm-probe.py"])
        if not ran or outcome != "killed":
            failures.append(f"frozen survivor selftest-arm control: {cell['id']}")
    if failures:
        for item in failures:
            print(f"selftest: FAIL {item}", file=sys.stderr)
        return 1
    print(f"selftest: ok ({len(rows)} pinned cells; manifest guards; error/verdict controls; survivor arm only)")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cells")
    parser.add_argument("--lane", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--fixtures")
    parser.add_argument("--arm", choices=("both", "frozen", "current"),
                        default="both",
                        help="both exits 0 only on a clean current arm and exact frozen red witness; frozen exits 1 for its expected errors; current exits 0 only with no current misclassification")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    cells = Path(args.cells) if args.cells else default_cells()
    fixtures_dir = Path(args.fixtures) if args.fixtures else \
        cells.resolve().parent / "error-injection-fixtures"
    if not args.selftest and not args.cells:
        parser.error("--cells is required unless --selftest is used")
    try:
        rows, fixtures, raw = load_registry(cells, fixtures_dir)
        if args.selftest:
            return selftest(rows, fixtures, raw, args.lane)
        result = census(args.lane, rows, fixtures, args.arm)
    except (OSError, CensusFault, subprocess.TimeoutExpired) as exc:
        print(f"error-verdict-census: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    emit(result, args.json)
    if result["unrun"]:
        return 2
    if args.arm != "current" and (
            result["frozen_witness_mismatches"] or result["red_vector_mismatches"]):
        return 2
    if args.arm == "frozen":
        return 1 if result["frozen_misclassified"] else 0
    return 0 if result["current_misclassified"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
