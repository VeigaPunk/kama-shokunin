#!/usr/bin/env python3
"""Inspect only registered PM08 source bytes; never import or execute the auditor."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def syntax_ok(text):
    try:
        compile(text, "<PM08-static-only>", "exec")
        return True
    except SyntaxError:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch", required=True)
    parser.add_argument("--stage", required=True, choices=("pristine", "mutated", "restored"))
    args = parser.parse_args()
    scratch = Path(args.scratch).resolve()
    auditor = scratch / "tools/report-landing-audit.py"
    inventory = scratch / "tests/report-audit/promisor-mutants.py"
    source_bytes = auditor.read_bytes()
    source = source_bytes.decode("utf-8")
    inventory_bytes = inventory.read_bytes()
    inventory_tree = ast.parse(inventory_bytes.decode("utf-8"))
    declarations = [node.value for node in inventory_tree.body
                    if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "MUTANTS"
                            for target in node.targets)]
    assert len(declarations) == 1 and isinstance(declarations[0], ast.List)
    registered_id = "PM08-remove-no-lazy-fetch-gate"
    matches = []
    for element in declarations[0].elts:
        if not isinstance(element, ast.Dict):
            continue
        if any(isinstance(key, ast.Constant) and key.value == "id"
               and isinstance(value, ast.Constant) and value.value == registered_id
               for key, value in zip(element.keys, element.values)):
            matches.append(ast.literal_eval(element))
    assert len(matches) == 1
    spec = matches[0]
    assert spec["execution"] == "static-only" and spec["expect_rows"] == []
    assert all(alt["kind"] == "replace" for alt in spec["alternatives"])
    counts = [source.count(alt["old"]) for alt in spec["alternatives"]]
    selected = next((index for index, count in enumerate(counts) if count == 1), None)
    predicted = None
    if selected is not None:
        alt = spec["alternatives"][selected]
        predicted = source.replace(alt["old"], alt["new"])

    tree = ast.parse(source)
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "GIT_ISOLATION"
                           for target in node.targets)]
    assert len(assignments) == 1
    isolation = ast.literal_eval(assignments[0].value)
    wrappers = [node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == "git"]
    assert len(wrappers) == 1
    git_calls = [node for node in ast.walk(wrappers[0])
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute)
                 and isinstance(node.func.value, ast.Name)
                 and node.func.value.id == "subprocess" and node.func.attr == "run"]
    assert len(git_calls) == 1
    argv = git_calls[0].args[0]
    forwarded = isinstance(argv, ast.List) and any(
        isinstance(element, ast.Starred) and isinstance(element.value, ast.Name)
        and element.value.id == "GIT_ISOLATION" for element in argv.elts)
    flag = spec["static_check"]
    marker_expressions = {}
    for node in ast.walk(inventory_tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("present_before", "present_after"):
                    marker_expressions[target.id] = ast.unparse(node.value)
    expressions_confirmed = marker_expressions == {
        "present_before": "marker in source", "present_after": "marker in applied"}
    assert expressions_confirmed
    compiled = syntax_ok(source)
    gate_present = flag in isolation
    passed = compiled and forwarded and gate_present
    record = {
        "stage": args.stage,
        "registered_id": registered_id,
        "registered_execution": spec["execution"],
        "registered_expected_graded_rows": spec["expect_rows"],
        "source_sha256": digest(source_bytes),
        "inventory_sha256": digest(inventory_bytes),
        "grid_sha256": digest((scratch / "tests/report-audit/promisor-grid.py").read_bytes()),
        "manifest_sha256": digest((scratch / "tests/report-audit/promisor-grid-expectations.json").read_bytes()),
        "registered_alternative_match_counts": counts,
        "registered_selected_alternative": selected,
        "registered_predicted_mutant_sha256": digest(predicted.encode("utf-8")) if predicted is not None else None,
        "registered_predicted_mutant_compiles": syntax_ok(predicted) if predicted is not None else None,
        "source_compiles_without_execution": compiled,
        "git_wrapper_forwards_isolation": forwarded,
        "git_isolation_contains_no_lazy_fetch": gate_present,
        "registered_marker_expressions_confirmed": expressions_confirmed,
        "registered_substring_marker_present": flag in source,
        "registered_substring_marker_occurrences": source.count(flag),
        "static_detector_passed": passed,
        "target_executed": False,
        "grid_executed": False,
        "transport_executed": False,
        "behavioral_kill_credit": 0,
    }
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
