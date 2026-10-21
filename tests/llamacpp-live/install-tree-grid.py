#!/usr/bin/env python3
"""install-tree-grid.py — consistent install-tree swap grid for the receipt gate.

Builds one mutant per named install-tree member: the member digest is replaced
and `install_tree_sha256` is recomputed over the mutated tree, so the receipt
stays internally consistent (the lane's round-18 residual: only the impl file
was pinned). Runs the gate on the unmutated baseline and on each mutant.

    install-tree-grid.py --gate PATH --receipt PATH \\
        --model-sha HEX --server-sha HEX --impl-sha HEX \\
        --probe-sha HEX --tool-sha HEX [--tree-sha HEX] [--members NAME ...]
    install-tree-grid.py --selftest

`--tree-sha` adds `--expect-install-tree-sha256` (the round-19 pin); without it
the grid measures the pre-pin boundary. Prints
`baseline=VALID|INVALID members=N rejected=K/N tree_pin=on|off`.
Exit: 0 baseline VALID and every mutant rejected (or, without --tree-sha, the
caller reads the count); 1 a mutant survived; 2 baseline invalid / bad input.
"""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_MEMBERS = ("libggml-base.so.0.27.0", "libllama-common.so.0.7.0",
                   "libllama.so.0.7.0")


def tree_sha(tree):
    lines = "".join(f"{name} {tree[name]}\n" for name in sorted(tree))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def pins(args, tree):
    out = ["--expect-model-sha256", args.model_sha,
           "--expect-server-sha256", args.server_sha,
           "--expect-server-impl-sha256", args.impl_sha,
           "--expect-probe-sha256", args.probe_sha,
           "--expect-tool-sha256", args.tool_sha]
    if tree:
        out += ["--expect-install-tree-sha256", tree]
    return out


def gate_exit(gate, receipt_path, argv):
    proc = subprocess.run([sys.executable, str(gate), str(receipt_path), *argv],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, timeout=300)
    return proc.returncode, proc.stdout.strip()[:200]


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    selftest = "--selftest" in argv
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gate", required=not selftest)
    ap.add_argument("--receipt", required=not selftest)
    for flag in ("model-sha", "server-sha", "impl-sha", "probe-sha",
                 "tool-sha"):
        ap.add_argument("--" + flag, required=not selftest)
    ap.add_argument("--tree-sha", default=None)
    ap.add_argument("--members", nargs="+", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="exercise baseline, mutation, absent-member and bad-receipt cases")
    args = ap.parse_args(argv)
    if args.selftest:
        return run_selftest()

    try:
        base = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"install-tree-grid: cannot read {args.receipt}: {exc}",
              file=sys.stderr)
        return 2
    tree = base["server"].get("install_tree")
    if not isinstance(tree, dict) or not tree:
        print("install-tree-grid: receipt has no install_tree", file=sys.stderr)
        return 2
    members = args.members or list(DEFAULT_MEMBERS)
    argv = pins(args, args.tree_sha)
    with tempfile.TemporaryDirectory(prefix="install-tree-grid-") as tmp:
        tmp = Path(tmp)
        base_path = tmp / "baseline.json"
        base_path.write_text(json.dumps(base), encoding="utf-8")
        exit_code, out = gate_exit(args.gate, base_path, argv)
        baseline = "VALID" if exit_code == 0 else "INVALID"
        rows = []
        # An invalid baseline makes every mutant "rejected" for the wrong
        # reason; do not run or count them (one gate call only).
        for member in (members if baseline == "VALID" else []):
            if member not in tree:
                rows.append({"member": member, "status": "absent"})
                continue
            mutant = copy.deepcopy(base)
            mutant["server"]["install_tree"][member] = "a" * 64
            mutant["server"]["install_tree_sha256"] = tree_sha(
                mutant["server"]["install_tree"])
            path = tmp / (member.replace("/", "_") + ".json")
            path.write_text(json.dumps(mutant), encoding="utf-8")
            code, text = gate_exit(args.gate, path, argv)
            # A kill is an INVALID verdict (exit 1), never an error (2) or
            # NOT-EVALUATED (3); tameshi's convention and the gate's own
            # selftest both require an emitted verdict.
            status = ("rejected" if code == 1 else
                      "error" if code in (2, 3) else "accepted")
            rows.append({"member": member, "gate_exit": code,
                         "status": status, "stdout": text})
    rejected = sum(1 for r in rows if r["status"] == "rejected")
    doc = {"schema": "kama-install-tree-grid/v1",
           "gate": str(args.gate), "receipt": str(args.receipt),
           "tree_pin": bool(args.tree_sha), "baseline": baseline,
           "members": len(rows), "rejected": rejected, "rows": rows}
    if args.json:
        print(json.dumps(doc, indent=1))
    else:
        print(f"baseline={baseline} members={len(rows)} "
              f"rejected={rejected}/{len(rows)} "
              f"tree_pin={'on' if args.tree_sha else 'off'}")
        for row in rows:
            print(f"  {row['status']:<8} {row['member']}")
    if baseline != "VALID":
        return 2
    return 0 if rejected == len(rows) else 1


def run_selftest():
    """Exercise valid and fail-capable install-tree grid outcomes."""
    from runpy import run_path

    gate = Path(__file__).with_name("check-receipt.py").resolve()
    fixture = run_path(str(gate))
    base = fixture["_selftest_receipt"]()
    member = "libllama.so"
    pins = [
        "--model-sha", fixture["MODEL_SHA"],
        "--server-sha", fixture["SERVER_SHA"],
        "--impl-sha", fixture["IMPL_SHA"],
        "--probe-sha", fixture["PROBE_SHA"],
        "--tool-sha", fixture["TOOL_SHA"],
        "--tree-sha", base["server"]["install_tree_sha256"],
    ]
    script = Path(__file__).resolve()
    failures = []

    with tempfile.TemporaryDirectory(prefix="install-tree-grid-selftest-") as tmp:
        tmp = Path(tmp)
        valid_path = tmp / "valid.json"
        valid_path.write_text(json.dumps(base), encoding="utf-8")
        bad = copy.deepcopy(base)
        bad["server"]["install_tree_sha256"] = "0" * 64
        bad_path = tmp / "bad.json"
        bad_path.write_text(json.dumps(bad), encoding="utf-8")

        def check_case(name, receipt_path, expected_exit, baseline,
                       status, rejected, members=None):
            command = [sys.executable, str(script), "--gate", str(gate),
                       "--receipt", str(receipt_path), *pins,
                       "--members", members or member, "--json"]
            try:
                proc = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, timeout=900)
                result = json.loads(proc.stdout)
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                failures.append(f"{name}: could not run grid: {exc}")
                return
            rows = result.get("rows")
            row = rows[0] if isinstance(rows, list) and rows else {}
            observed = (
                proc.returncode == expected_exit
                and result.get("baseline") == baseline
                and row.get("status") == status
                and result.get("rejected") == rejected
            )
            if not observed:
                failures.append(
                    f"{name}: exit={proc.returncode} "
                    f"baseline={result.get('baseline')!r} "
                    f"row={row.get('status')!r} "
                    f"rejected={result.get('rejected')!r}")

        check_case("baseline and pinned member mutation", valid_path,
                   0, "VALID", "rejected", 1)
        check_case("absent member", valid_path, 1, "VALID", "absent", 0,
                    members="absent-member.so")
        check_case("bad receipt", bad_path, 2, "INVALID", None, 0)

    if failures:
        for failure in failures:
            print(f"SELFTEST FAIL {failure}", file=sys.stderr)
        return 1
    print("selftest: baseline, member rejection, absent member and bad receipt passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
