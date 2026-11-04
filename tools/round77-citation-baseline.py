#!/usr/bin/env python3
"""Round-77 C1: frozen receipt scope plus reproducible baseline receipts.

Only measured/before receipts use introduction ancestry and byte stability.
All other citations retain the imported round-76 classification rules.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PREDICATE = (
    "`python3 tools/round77-citation-baseline.py --repo <lane> --round 75` prints one "
    "`CITATION_BASELINE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0 "
    "nonreceipt=0 unclassified=0` line and exits 0 only when the round-75 self-record's citation "
    "population is classified under the frozen fence scope (a citation inside a CommonMark fenced "
    "block is quoted history; an unclosed fence is could-not-evaluate) and the frozen record-path "
    "scope (a delta between a receipt's recorded revision and the tip that touches only "
    "`PROVINCE.md`, `SKILL.md` or `corpus/**` does not shift that receipt), and under the declared "
    "baseline-receipt class — a citation whose path lies under a `measured/before/` directory is "
    "bound when its first five lines name one 40-hex revision that is an ancestor of the commit "
    "that introduced the receipt file and the file's bytes are identical at that introducing "
    "commit and at the tip — with the two legacy header-less wave receipts named individually as "
    "`CITATION_BASELINE_UNBOUND <path> :: <reason>`; it exits 1 naming "
    "`CITATION_BASELINE_FINDING <shifted|stale|nonreceipt>` for a live non-receipt citation, a "
    "receipt shifted by a non-self-description delta, a baseline receipt whose recorded revision is "
    "not an ancestor of its introduction, a baseline receipt whose bytes changed after "
    "introduction, or a stale receipt, and 2 on could-not-evaluate (a missing self-record, an "
    "unclosed fence, an empty live population, an unreadable receipt at the tip, CLI misuse)."
)

spec = importlib.util.spec_from_file_location(
    "round77_receipt_scope", os.path.join(HERE, "round76-receipt-scope.py"))
if spec is None or spec.loader is None:
    raise ImportError("cannot import round76-receipt-scope.py")
scope = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scope)
_load_module = scope._load_module
base_mod = scope.base_mod
CouldNotEvaluate = scope.CouldNotEvaluate
_original_classify = scope._classify_receipt


def _classify_receipt(repo, tip, path, specs):
    if "/measured/before/" not in "/" + path:
        return _original_classify(repo, tip, path, specs)
    kind = base_mod._obj_type(repo, tip, path)
    if kind is None:
        return "stale", "absent at " + tip
    if kind != "blob":
        raise CouldNotEvaluate("unreadable receipt at tip: " + path)
    blob = base_mod._blob(repo, tip, path)
    if blob is None:
        raise CouldNotEvaluate("unreadable receipt at tip: " + path)
    rev, problem = base_mod._header_rev(blob)
    if rev is None:
        return "shifted", "baseline header leg: " + problem
    introductions = base_mod._text(base_mod._git(
        repo, "log", "--diff-filter=A", "--format=%H", tip, "--", path)).splitlines()
    if not introductions:
        raise CouldNotEvaluate("baseline introduction missing: " + path)
    introduction = introductions[-1]
    if base_mod._commit_sha(repo, rev) is None or not base_mod._is_ancestor(repo, rev, introduction):
        return "shifted", "baseline ancestry leg: header rev {} is not an ancestor of introduction {}".format(rev, introduction)
    original = base_mod._blob(repo, introduction, path)
    if original is None:
        raise CouldNotEvaluate("unreadable baseline at introduction: " + path)
    if hashlib.sha256(original).digest() != hashlib.sha256(blob).digest():
        return "shifted", "baseline sha256 leg: bytes changed since introduction " + introduction
    return "bound", "baseline rev={} introduction={} sha256={}".format(
        rev, introduction, hashlib.sha256(blob).hexdigest())


def audit(repo, tip, round_no, all_findings=False):
    # This private module instance is used synchronously; restore its hook even on error.
    previous = scope._classify_receipt
    scope._classify_receipt = _classify_receipt
    try:
        result = scope.audit(repo, tip, round_no, all_findings)
    finally:
        scope._classify_receipt = previous
    result["line"] = result["line"].replace("RECEIPT_SCOPE", "CITATION_BASELINE", 1)
    return result


def render(result):
    return scope.render(result).replace("RECEIPT_SCOPE", "CITATION_BASELINE")


def _run_arm(fx, tip, name, expected, marker, outcomes):
    proc = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--repo", fx.path,
         "--round", "75", "--tip", tip], capture_output=True, text=True,
        timeout=base_mod.TIMEOUT)
    output = proc.stdout + proc.stderr
    outcomes.append((name, proc.returncode == expected and marker in output,
                     proc.returncode, expected, output))


def _selftest_arms(scratch, outcomes):
    receipt = ".ufo/waves/round-75/measured/x.out"
    nonreceipt = ".ufo/waves/round-75/controls/build-spec.py"
    cases = (
        ("fence-none-live", 2, "empty live population", "```\n`" + receipt + "`\n```\n", False),
        ("fence-unclosed", 2, "unclosed fence", "```\n`" + nonreceipt + "`\n", True),
        ("fence-live-nonreceipt", 1, "CITATION_BASELINE_FINDING nonreceipt", "`" + nonreceipt + "`\n", True),
        ("shift-tools", 1, "CITATION_BASELINE_FINDING shifted", "", True),
    )
    for name, expected, marker, body, live in cases:
        fx = scope._Fixture(scratch, name)
        fx.write("tools/input.py", "original\n")
        rev = fx.commit("fixture instrument")
        fx.write(receipt, "# rev={}\n".format(rev))
        fx.write("SCORECARD.md", "# Fixture\n\n## Round 75\n\n" +
                 ("`" + receipt + "`\n" if live else "No live citation.\n"))
        fx.write("corpus/lessons/round-75.md", "# Lesson\n\n" + body)
        tip = fx.commit("fixture record")
        if name == "shift-tools":
            fx.write("tools/input.py", "changed\n")
            tip = fx.commit("fixture tools delta")
        _run_arm(fx, tip, name, expected, marker, outcomes)
    receipt = ".ufo/waves/round-75/measured/before/baseline.out"
    for name in ("baseline-bound", "baseline-nonancestor", "baseline-edited"):
        fx = scope._Fixture(scratch, name)
        fx.write("tools/input.py", "original\n")
        rev = fx.commit("fixture instrument")
        fx.write(receipt, "# rev={}\nmeasurement=1\n".format(rev))
        fx.write("SCORECARD.md", "# Fixture\n\n## Round 75\n\n`" + receipt + "`\n")
        fx.write("corpus/lessons/round-75.md", "# Lesson\n")
        tip = fx.commit("fixture baseline introduction")
        fx.write("tools/input.py", "changed\n")
        later = fx.commit("fixture tools delta")
        tip = later
        if name == "baseline-nonancestor":
            fx.write(receipt, "# rev={}\nmeasurement=1\n".format(later))
            tip = fx.commit("fixture nonancestor header")
        elif name == "baseline-edited":
            fx.write(receipt, "# rev={}\nmeasurement=2\n".format(rev))
            tip = fx.commit("fixture edited baseline")
        expected = 0 if name == "baseline-bound" else 1
        marker = {"baseline-bound": "bound=1 unbound=0 shifted=0",
                  "baseline-nonancestor": "baseline ancestry leg:",
                  "baseline-edited": "baseline sha256 leg:"}[name]
        _run_arm(fx, tip, name, expected, marker, outcomes)


def run_selftest(args):
    # Scratch discipline (round-77 §7): honour TMPDIR; --work is optional and the
    # default root is removed with the fixture it holds.
    owned = not args.work
    root = (os.path.abspath(args.work) if args.work else
            tempfile.mkdtemp(prefix="citation-baseline-root-",
                             dir=os.environ.get("TMPDIR") or tempfile.gettempdir()))
    os.makedirs(root, exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="citation-baseline-", dir=root)
    outcomes = []
    try:
        _selftest_arms(scratch, outcomes)
    finally:
        shutil.rmtree(scratch)
        if owned:
            shutil.rmtree(root, ignore_errors=True)
    for name, ok, rc, expected, output in outcomes:
        print("CITATION_BASELINE_SELFTEST {} {}".format(name, "PASS" if ok else "FAIL"))
        print("CITATION_BASELINE_ARM {} expect={} got={}".format(name, expected, rc))
        print(output.rstrip())
    passed = sum(ok for _, ok, _, _, _ in outcomes)
    failed = len(outcomes) - passed
    print("CITATION_BASELINE_SELFTEST pass={} fail={}".format(passed, failed))
    return int(failed != 0)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CouldNotEvaluate(message)


def main(argv=None):
    ap = _Parser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--round", dest="round_no", type=int)
    ap.add_argument("--tip")
    ap.add_argument("--base-rev")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--work")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all-findings", action="store_true")
    try:
        args = ap.parse_args(argv)
        if args.selftest:
            return run_selftest(args)
        if args.round_no is None or args.round_no < 1:
            raise CouldNotEvaluate("--round must be a positive integer")
        tip = args.tip or args.base_rev
        source = "explicit:--tip" if args.tip else "explicit:--base-rev"
        if not tip:
            plan_path = "plans/round-{}-claims.md".format(args.round_no + 1)
            plan = base_mod._blob(args.repo, "HEAD", plan_path)
            if plan is None:
                tip, source = "HEAD", "default:head (no " + plan_path + " yet)"
            else:
                match = re.search(r"Base revision `([0-9a-f]{40})`", plan.decode("utf-8", "replace"))
                if match is None:
                    raise CouldNotEvaluate("population plan lacks Base revision: " + plan_path)
                tip, source = match.group(1), "plan:" + plan_path
        result = audit(args.repo, tip, args.round_no, args.all_findings)
        result["population_source"] = source
    except (CouldNotEvaluate, OSError, subprocess.SubprocessError) as exc:
        print("CITATION_BASELINE CouldNotEvaluate: {}".format(exc), file=sys.stderr)
        return 2
    if not args.json:
        print("CITATION_BASELINE_POP round={} tip={} source={}".format(
            args.round_no, result["tip_commit"], source))
    print(json.dumps(result, indent=1, sort_keys=True) if args.json else render(result))
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
