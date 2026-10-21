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
`baseline=VALID|INVALID|ERROR members=N rejected=K/N tree_pin=on|off`.
Only the gate's own verdict counts (check-receipt.py `main`): a mutant is
`rejected` on exit 1 with stdout starting `INVALID `, `accepted` on exit 0
with stdout starting `VALID `. Any other exit, a signal, a traceback, a
timeout or a launch failure is `error`: no verdict was observed.
Exit: 0 baseline VALID and every mutant rejected (or, without --tree-sha, the
caller reads the count); 1 a mutant survived (accepted) or a member is
absent; 2 could not evaluate: baseline not VALID, any `error` row, bad
input, or the grid's own fault.
"""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import traceback
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


GATE_TIMEOUT = 300  # seconds per gate run


def _excerpt(text):
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    text = text or ""
    marker = "Traceback (most recent call last):"
    position = text.find(marker)
    if position >= 0:
        text = text[position:]
    return text.strip()[:200]


def gate_verdict(gate, receipt_path, argv, timeout=GATE_TIMEOUT):
    """Return (verdict, exit, stdout, stderr, reason) for one gate run."""
    try:
        proc = subprocess.run(
            [sys.executable, str(gate), str(receipt_path), *argv],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        return ("ERROR", None, _excerpt(exc.stdout), _excerpt(exc.stderr),
                f"timeout after {timeout}s")
    except OSError as exc:
        return "ERROR", None, "", "", f"cannot run gate: {exc}"
    code, out, err = proc.returncode, proc.stdout, proc.stderr
    if ("Traceback (most recent call last):" in out
            or "Traceback (most recent call last):" in err):
        verdict, reason = "ERROR", f"traceback in gate output (exit {code})"
    elif code < 0:
        verdict, reason = "ERROR", f"killed by signal {-code}"
    elif code == 1 and out.startswith("INVALID "):
        verdict, reason = "INVALID", None
    elif code == 0 and out.startswith("VALID "):
        verdict, reason = "VALID", None
    else:
        verdict, reason = "ERROR", f"no verdict line for exit {code}"
    return verdict, code, _excerpt(out), _excerpt(err), reason


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
                    help="exercise baseline, mutations, errors and bad receipts")
    args = ap.parse_args(argv)
    if args.selftest:
        return run_selftest()

    try:
        base = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"install-tree-grid: cannot read {args.receipt}: {exc}",
              file=sys.stderr)
        return 2
    if not isinstance(base, dict) or not isinstance(base.get("server"), dict):
        print("install-tree-grid: receipt has no server object", file=sys.stderr)
        return 2
    tree = base["server"].get("install_tree")
    if not isinstance(tree, dict) or not tree:
        print("install-tree-grid: receipt has no install_tree", file=sys.stderr)
        return 2
    members = args.members or list(DEFAULT_MEMBERS)
    pin_argv = pins(args, args.tree_sha)
    rows = []
    baseline = "ERROR"
    baseline_reason = None
    with tempfile.TemporaryDirectory(prefix="install-tree-grid-") as tmp:
        tmp = Path(tmp)
        base_path = tmp / "baseline.json"
        base_path.write_text(json.dumps(base), encoding="utf-8")
        (baseline, _, _, baseline_err, baseline_reason) = gate_verdict(
            args.gate, base_path, pin_argv)
        # An invalid or unobserved baseline makes every mutant uninformative.
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
            verdict, code, text, stderr, reason = gate_verdict(
                args.gate, path, pin_argv)
            status = {"INVALID": "rejected", "VALID": "accepted"}.get(
                verdict, "error")
            row = {"member": member, "gate_exit": code, "status": status,
                   "stdout": text, "stderr": stderr}
            if reason is not None:
                row["error"] = reason
            rows.append(row)
    rejected = sum(1 for r in rows if r["status"] == "rejected")
    errors = sum(1 for r in rows if r["status"] == "error")
    doc = {"schema": "kama-install-tree-grid/v1",
           "gate": str(args.gate), "receipt": str(args.receipt),
           "tree_pin": bool(args.tree_sha), "baseline": baseline,
           "members": len(rows), "rejected": rejected, "errors": errors,
           "rows": rows}
    if args.json:
        print(json.dumps(doc, indent=1))
    else:
        print(f"baseline={baseline} members={len(rows)} "
              f"rejected={rejected}/{len(rows)} "
              f"tree_pin={'on' if args.tree_sha else 'off'}")
        for row in rows:
            suffix = f" ({row['error']})" if "error" in row else ""
            print(f"  {row['status']:<8} {row['member']}{suffix}")
    if baseline == "ERROR":
        detail = f": {baseline_err}" if baseline_err else ""
        print(f"install-tree-grid: baseline gate error: "
              f"{baseline_reason}{detail}", file=sys.stderr)
        return 2
    if baseline != "VALID" or errors:
        if errors:
            print(f"install-tree-grid: {errors} member gate run(s) "
                  "gave no verdict", file=sys.stderr)
        return 2
    return 0 if rejected == len(rows) else 1


def run_selftest():
    """Exercise genuine verdicts and gate failures against the grid."""
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
                       status, rejected, gate_path=gate, members=None,
                       errors=0):
            command = [sys.executable, str(script), "--gate", str(gate_path),
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
                and result.get("errors") == errors
            )
            if not observed:
                failures.append(
                    f"{name}: exit={proc.returncode} "
                    f"baseline={result.get('baseline')!r} "
                    f"row={row.get('status')!r} "
                    f"rejected={result.get('rejected')!r} "
                    f"errors={result.get('errors')!r}")

        def stub_gate(name, mutant_body):
            path = tmp / f"{name}-gate.py"
            path.write_text(
                "import json, os, signal, sys\n"
                f"base_sha = {base['server']['install_tree_sha256']!r}\n"
                "receipt = json.load(open(sys.argv[1], encoding='utf-8'))\n"
                "if receipt['server']['install_tree_sha256'] == base_sha:\n"
                "    print('VALID synthetic baseline')\n"
                "    raise SystemExit(0)\n"
                + mutant_body,
                encoding="utf-8")
            return path

        check_case("baseline and genuine INVALID member", valid_path,
                   0, "VALID", "rejected", 1)
        check_case("absent member", valid_path, 1, "VALID", "absent", 0,
                   members="absent-member.so")
        check_case("bad receipt", bad_path, 2, "INVALID", None, 0)

        cases = (
            ("crash gate", "raise RuntimeError('injected gate crash')\n"),
            ("silent exit 1", "raise SystemExit(1)\n"),
            ("signal gate", "os.kill(os.getpid(), signal.SIGTERM)\n"),
            ("unknown exit", "raise SystemExit(7)\n"),
            ("INVALID followed by traceback",
             "print('INVALID synthetic')\n"
             "raise RuntimeError('injected after INVALID')\n"),
            ("stdout traceback after INVALID",
             "print('INVALID synthetic')\n"
             "print('Traceback (most recent call last):')\n"
             "raise SystemExit(1)\n"),
            ("stderr-only INVALID",
             "print('INVALID synthetic', file=sys.stderr)\n"
             "raise SystemExit(1)\n"),
        )
        for name, body in cases:
            check_case(name, valid_path, 2, "VALID", "error", 0,
                       gate_path=stub_gate(name.replace(" ", "-"), body),
                       errors=1)

        timeout_gate = tmp / "timeout-gate.py"
        timeout_gate.write_text("import time\ntime.sleep(10)\n", encoding="utf-8")
        verdict = gate_verdict(timeout_gate, valid_path, [], timeout=0.1)
        if verdict[0] != "ERROR" or not verdict[4].startswith("timeout after"):
            failures.append(f"gate timeout classification: {verdict!r}")

    if failures:
        for failure in failures:
            print(f"SELFTEST FAIL {failure}", file=sys.stderr)
        return 1
    print("selftest: genuine verdicts, absent/bad input, crash, silent exit 1, "
          "signal, unknown exit, post-INVALID tracebacks, stderr-only INVALID "
          "and timeout passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"install-tree-grid: internal error: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)
