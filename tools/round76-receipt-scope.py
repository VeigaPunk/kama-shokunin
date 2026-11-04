#!/usr/bin/env python3
"""Round-76 C1: fence-scoped citations and explicitly widened record paths.

Read committed blobs, not working-tree records. Legacy header-less receipts remain
named unbound classifications, not failures. Stale paths are named findings and
count as unclassified because there are no receipt bytes to bind.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
PREDICATE = (
    "`python3 tools/round76-receipt-scope.py --repo <lane> --round 75` prints one "
    "`RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0 "
    "nonreceipt=0 unclassified=0` line and exits 0 only when the round-75 self-record's citation "
    "population is classified under the declared fence scope — a citation inside a CommonMark "
    "fenced block is quoted history, never a citation, and an unclosed fence is "
    "could-not-evaluate — and under the declared record-path scope — a delta between a receipt's "
    "recorded revision and the tip that touches only the self-description paths `PROVINCE.md`, "
    "`SKILL.md` and `corpus/**` does not shift that receipt — with the two legacy header-less wave "
    "receipts named individually as `RECEIPT_SCOPE_UNBOUND <path> :: <reason>` findings; it exits 1 "
    "naming `RECEIPT_SCOPE_FINDING` for a live non-receipt citation, a receipt shifted by a "
    "non-self-description delta or a stale receipt, and 2 on could-not-evaluate (a missing "
    "self-record, an unclosed fence, an empty live population, an unreadable receipt at the tip, "
    "CLI misuse)."
)


def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
    if spec is None or spec.loader is None:
        raise ImportError("cannot import " + filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r73 = _load_module("round76_r73", "round73-receipt-claim-binding.py")
base_mod = r73._load_base(os.path.join(HERE, "round72-receipt-tip-binding.py"))
audit_mod = _load_module("round76_append_audit", "append-only-audit.py")
CouldNotEvaluate = base_mod.CouldNotEvaluate
RECEIPT_EXTS = base_mod.RECEIPT_EXTS


def _fence_flags(lines):
    """Use the audit's v5 functions directly; reject an unterminated block."""
    flags, fence = [], None
    for line in lines:
        raw = line.encode("utf-8").rstrip(b"\r")
        quoted = fence is not None
        if fence is not None:
            if audit_mod.fence_close(raw, fence):
                fence = None
        else:
            fence = audit_mod.fence_open(raw)
            quoted = fence is not None
        flags.append(quoted)
    if fence is not None:
        raise CouldNotEvaluate("unclosed fence")
    return flags


def _resolve_citation(repo, tip, round_no, token, where):
    """Keep r72 scope/expansion; also retain non-receipt leaves as findings.

    Only leaf type admission differs from the frozen resolver. Directories and
    glob/brace receipt populations still use its expansion and scope helpers.
    """
    tok = token.strip()
    while tok.startswith("./"):
        tok = tok[2:]
    tok = tok.rstrip(",;:")
    if not tok or re.search(r"\s", tok) or "..." in tok:
        return []
    if any(ch in tok for ch in base_mod.SKIP_CHARS):
        return []
    prefix = ".ufo/waves/round-{}/".format(round_no)
    qualified = tok == prefix.rstrip("/") or tok.startswith(prefix)
    if qualified:
        full = tok
    elif tok.startswith(".ufo/"):
        return []
    else:
        if base_mod._obj_type(repo, tip, tok.split("/", 1)[0]) is not None:
            return []
        full = prefix + tok
    paths = []
    for candidate in base_mod._brace_expand(full.rstrip("/")):
        if not qualified and not base_mod._in_scope(repo, tip, candidate):
            continue
        is_dir = tok.endswith("/") or base_mod._obj_type(repo, tip, candidate) == "tree"
        if not base_mod.GLOB_CHARS.search(candidate) and not is_dir and not base_mod.is_receipt(candidate):
            paths.append(candidate)
        else:
            paths.extend(base_mod._expand_one(repo, tip, candidate, is_dir, where))
    return paths


def _classify_receipt(repo, tip, path, specs):
    kind = base_mod._obj_type(repo, tip, path)
    if kind is not None and kind != "blob":
        raise CouldNotEvaluate("unreadable receipt at tip: " + path)
    return base_mod._evaluate(repo, tip, path, specs)


def summary_line(result):
    keys = ("round", "fenced_quoted", "live_citations", "bound", "unbound",
            "shifted", "nonreceipt", "unclassified")
    return "RECEIPT_SCOPE " + " ".join("{}={}".format(k, result[k]) for k in keys)


def audit(repo, tip, round_no, all_findings=False):
    repo = os.path.abspath(repo)
    tip_sha = base_mod._commit_sha(repo, tip)
    if tip_sha is None:
        raise CouldNotEvaluate("tip is not a commit: " + tip)
    try:
        records = r73._read_records(repo, tip_sha, round_no, base_mod)
    except r73.CouldNotEvaluate as exc:
        raise CouldNotEvaluate(str(exc)) from exc
    live, quoted = {}, set()
    for filename, lines, offset in records:
        flags = _fence_flags(lines)
        for token, _, lineno in base_mod._citations(lines, offset, filename):
            fenced = flags[lineno - offset - 1]
            # Fenced history never needs directory expansion or receipt reads.
            if fenced:
                normalized = token
                while normalized.startswith("./"):
                    normalized = normalized[2:]
                normalized = normalized.rstrip(",;:")
                prefix = ".ufo/waves/round-{}/".format(round_no)
                if (normalized.startswith(prefix) and not re.search(r"\s", normalized)
                        and not any(ch in normalized for ch in base_mod.SKIP_CHARS)
                        and "..." not in normalized
                        and not base_mod.is_receipt(normalized)
                        and not normalized.endswith("/")):
                    quoted.update(base_mod._brace_expand(normalized))
                continue
            where = "{}:{}".format(filename, lineno)
            for path in _resolve_citation(repo, tip_sha, round_no, token, where):
                live.setdefault(path, where)
    if not live:
        raise CouldNotEvaluate("self-record cites no live receipt path; empty live population")
    specs = base_mod.default_record_paths(round_no) + ["PROVINCE.md", "SKILL.md", "corpus/**"]
    result = dict(round=round_no, tip_commit=tip_sha, fenced_quoted=0,
                  live_citations=len(live), bound=0, unbound=0, shifted=0,
                  nonreceipt=0, unclassified=0, findings=[], record_paths=specs)
    result["quoted_paths"] = sorted(quoted - live.keys())
    result["fenced_quoted"] = len(result["quoted_paths"])
    for path in sorted(live):
        if not base_mod.is_receipt(path):
            cls, detail = "nonreceipt", "live citation at " + live[path]
        else:
            cls, detail = _classify_receipt(repo, tip_sha, path, specs)
        result[cls if cls != "stale" else "unclassified"] += 1
        if cls != "bound":
            result["findings"].append(dict(kind=cls, path=path, detail=detail))
        if all_findings and cls == "shifted":
            blob = base_mod._blob(repo, tip_sha, path)
            rev, _ = base_mod._header_rev(blob)
            if rev and base_mod._commit_sha(repo, rev) and base_mod._is_ancestor(repo, rev, tip_sha):
                for commit in base_mod._rev_list(repo, rev, tip_sha):
                    for changed in base_mod._diff_paths(repo, commit):
                        if not base_mod._record_match(changed, specs):
                            result.setdefault("delta_findings", []).append(
                                dict(receipt=path, commit=commit, path=changed))
    result["exit"] = int(any(f["kind"] != "unbound" for f in result["findings"]))
    result["line"] = summary_line(result)
    return result


def render(result):
    lines = ["RECEIPT_SCOPE_QUOTED " + path for path in result["quoted_paths"]]
    for finding in result["findings"]:
        label = ("RECEIPT_SCOPE_UNBOUND" if finding["kind"] == "unbound"
                 else "RECEIPT_SCOPE_FINDING " + finding["kind"])
        lines.append("{} {} :: {}".format(label, finding["path"], finding["detail"]))
    for delta in result.get("delta_findings", []):
        lines.append("RECEIPT_SCOPE_DELTA {} :: {} touched by {}".format(
            delta["receipt"], delta["path"], delta["commit"]))
    return "\n".join(lines + [result["line"]])


class _Fixture(base_mod._Fixture):
    """Assert fixture ownership before every mutating git operation."""
    def commit(self, message):
        top = base_mod._text(base_mod._git(self.path, "rev-parse", "--show-toplevel")).strip()
        if os.path.realpath(top) != os.path.realpath(self.path):
            raise CouldNotEvaluate("fixture root mismatch")
        return super().commit(message)


def _selftest_arms(scratch, outcomes):
    receipt = ".ufo/waves/round-75/measured/x.out"
    nonreceipt = ".ufo/waves/round-75/controls/build-spec.py"
    cases = (
        ("fence-quoted-skip", 0, "fenced_quoted=1", "```\n`" + nonreceipt + "`\n```\n", True),
        ("fence-live-nonreceipt", 1, "RECEIPT_SCOPE_FINDING nonreceipt", "`" + nonreceipt + "`\n", True),
        ("fence-none-live", 2, "empty live population", "```\n`" + receipt + "`\n```\n", False),
        ("fence-unclosed", 2, "unclosed fence", "```\n`" + nonreceipt + "`\n", True),
        ("shift-selfdesc", 0, "bound=1 unbound=0 shifted=0", "", True),
        ("shift-tools", 1, "RECEIPT_SCOPE_FINDING shifted", "", True),
        ("unbound-named", 0, "RECEIPT_SCOPE_UNBOUND " + receipt + " :: no tip=/rev= header", "", True),
    )
    for name, expected, marker, body, live in cases:
        fx = _Fixture(scratch, name)
        fx.write("tools/input.py", "original\n")
        rev = fx.commit("fixture instrument")
        header = "legacy receipt\n" if name == "unbound-named" else "# rev={}\n".format(rev)
        fx.write(receipt, header)
        fx.write("SCORECARD.md", "# Fixture\n\n## Round 75\n\n" +
                 ("`" + receipt + "`\n" if live else "No live citation.\n"))
        fx.write("corpus/lessons/round-75.md", "# Lesson\n\n" + body)
        tip = fx.commit("fixture record")
        if name in ("shift-selfdesc", "shift-tools"):
            fx.write("PROVINCE.md" if name == "shift-selfdesc" else "tools/input.py", "changed\n")
            tip = fx.commit("fixture delta")
        proc = subprocess.run([sys.executable, os.path.abspath(__file__), "--repo", fx.path,
                               "--round", "75", "--tip", tip], capture_output=True,
                              text=True, timeout=base_mod.TIMEOUT)
        output = proc.stdout + proc.stderr
        ok = proc.returncode == expected and marker in output
        outcomes.append((name, ok, proc.returncode, expected, output))


def run_selftest(args):
    if not args.work:
        print("RECEIPT_SCOPE CouldNotEvaluate: --selftest requires --work", file=sys.stderr)
        return 2
    os.makedirs(os.path.abspath(args.work), exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="receipt-scope-", dir=os.path.abspath(args.work))
    outcomes = []
    try:
        _selftest_arms(scratch, outcomes)
    finally:
        shutil.rmtree(scratch)
    for name, ok, rc, expected, output in outcomes:
        print("RECEIPT_SCOPE_ARM {} expect={} got={} {}".format(name, expected, rc, "ok" if ok else "FAIL"))
        if not ok:
            print(output.rstrip())
    passed = sum(ok for _, ok, _, _, _ in outcomes)
    failed = len(outcomes) - passed
    print("RECEIPT_SCOPE_SELFTEST pass={} fail={}".format(passed, failed))
    return int(failed != 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--round", dest="round_no", type=int)
    ap.add_argument("--tip", help="override the round's population tip")
    ap.add_argument("--base-rev", help="population revision (default: next round's frozen plan base)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--work")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all-findings", action="store_true",
                    help="show every non-record path/commit in shifted receipts' deltas")
    args = ap.parse_args(argv)
    if args.selftest:
        return run_selftest(args)
    if args.round_no is None or args.round_no < 1:
        ap.error("--round must be a positive integer")
    try:
        source = "explicit:--tip" if args.tip else "explicit:--base-rev"
        tip = args.tip or args.base_rev
        if not tip:
            plan_path = "plans/round-{}-claims.md".format(args.round_no + 1)
            plan = base_mod._blob(args.repo, "HEAD", plan_path)
            if plan is None:
                raise CouldNotEvaluate("missing population plan: " + plan_path)
            match = re.search(r"Base revision `([0-9a-f]{40})`", plan.decode("utf-8", "replace"))
            if match is None:
                raise CouldNotEvaluate("population plan lacks Base revision: " + plan_path)
            tip = match.group(1)
            source = "plan:" + plan_path
        result = audit(args.repo, tip, args.round_no, args.all_findings)
        result["population_source"] = source
    except (CouldNotEvaluate, OSError, subprocess.SubprocessError) as exc:
        print("RECEIPT_SCOPE CouldNotEvaluate: {}".format(exc), file=sys.stderr)
        return 2
    if not args.json:
        print("RECEIPT_SCOPE_POP round={} tip={} source={}".format(
            args.round_no, result["tip_commit"], source))
    print(json.dumps(result, indent=1, sort_keys=True) if args.json else render(result))
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
