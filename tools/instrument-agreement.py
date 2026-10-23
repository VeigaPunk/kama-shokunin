#!/usr/bin/env python3
"""instrument-agreement.py — run a lane instrument N times over one tree and report agreement.

Why: a counter's target means something only when its output is reproducible for the same
tree. This tool re-runs one instrument N times in isolated temp dirs, normalizes only the
volatile fields the caller declares, and reports agreement as a counter:
`IA runs=N agree=A disagree=D digest=<sha256 prefix>`.

Usage:
  python3 tools/instrument-agreement.py --runs 3 --out RECEIPT.json -- CMD [ARG...]
  python3 tools/instrument-agreement.py --selftest

Options:
  --runs N            number of runs (default 3)
  --cwd DIR           working directory for each run (default: the directory holding tools/)
  --normalize REGEX=REPL   declared volatile field, repeatable; applied to stdout and stderr
  --out FILE          receipt path (refused if it exists)
  --selftest          offline fixture arms; prints `IA_SELFTEST pass=N fail=0`

Semantics:
  * Every run gets a fresh temp dir; TMPDIR points at it. The temp path itself is always
    normalized to `<TMP>`, because it is the tool's own artifact, not the instrument's.
  * Nothing else is normalized unless the caller declares it. An undeclared volatile field
    is a disagreement by design.
  * A run's digest = sha256(exit code, 0x00, normalized stdout, 0x00, normalized stderr).
  * Agreement = all runs share digest. Exit 0 agree, 1 disagree, 2 setup error
    (bad usage, missing command, unresolvable cwd, undecodable output).

What it does not show: that the instrument is correct, or that its normalized fields are
irrelevant to the claim. Those stay the caller's burden (corpus/knowledge/instrument-run-agreement.md).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

DEFAULT_NORMALIZE = ((r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z", "<ISOUTCDATE>"),)


def normalize(text: str, tmpdir: str, rules) -> str:
    out = text.replace(tmpdir, "<TMP>")
    for pattern, repl in rules:
        out = re.sub(pattern, repl, out)
    return out


def one_run(cmd, cwd, rules):
    d = tempfile.mkdtemp(prefix="ia-run-")
    env = dict(os.environ)
    env["TMPDIR"] = d
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, env=env, timeout=300)
    except FileNotFoundError:
        raise SystemExit(f"instrument-agreement: command not found: {cmd[0]}")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    stdout = normalize(p.stdout.decode(errors="replace"), d, rules)
    stderr = normalize(p.stderr.decode(errors="replace"), d, rules)
    digest = hashlib.sha256(f"{p.returncode}\0{stdout}\0{stderr}".encode()).hexdigest()
    return {"exit": p.returncode, "digest": digest,
            "stdout_head": stdout.split("\n")[0][:200],
            "stderr_head": stderr.split("\n")[0][:200]}


def measure(cmd, cwd, runs, rules):
    results = [one_run(cmd, cwd, rules) for _ in range(runs)]
    digests = {r["digest"] for r in results}
    agree = sum(1 for r in results if r["digest"] == results[0]["digest"])
    return results, agree, len(results) - agree


def selftest() -> int:
    checks = []
    root = tempfile.mkdtemp(prefix="ia-selftest-")

    def check(name, ok, note):
        checks.append({"name": name, "ok": bool(ok), "note": note})

    det = os.path.join(root, "det.py")
    open(det, "w").write("import sys\nprint('value=42')\nprint('file=fixture', file=sys.stderr)\nsys.exit(0)\n")
    r, a, d = measure([sys.executable, det], root, 3, DEFAULT_NORMALIZE)
    check("deterministic", a == 3 and d == 0 and r[0]["exit"] == 0, f"agree={a} disagree={d}")

    nd = os.path.join(root, "nd.py")
    open(nd, "w").write("import os, sys\nm = os.path.join(sys.argv[1], 'marker')\n"
                        "n = int(open(m).read()) if os.path.exists(m) else 0\n"
                        "open(m, 'w').write(str(n + 1))\n"
                        "print('phase=deviant' if n == 1 else 'phase=stable')\n")
    r, a, d = measure([sys.executable, nd, root], root, 3, DEFAULT_NORMALIZE)
    check("nondeterministic", a == 2 and d == 1 and r[0]["exit"] == 0, f"agree={a} disagree={d}")

    vol = os.path.join(root, "vol.py")
    open(vol, "w").write("import time\nprint('at 2026-10-23T12:00:00Z ok')\n")
    r, a, d = measure([sys.executable, vol], root, 3, DEFAULT_NORMALIZE)
    check("declared-volatile", a == 3 and d == 0, f"agree={a} disagree={d}")

    ex = os.path.join(root, "ex.py")
    open(ex, "w").write("import os, sys\nm = os.path.join(sys.argv[1], 'exitmarker')\n"
                        "n = int(open(m).read()) if os.path.exists(m) else 0\n"
                        "open(m, 'w').write(str(n + 1))\n"
                        "print('same stdout')\nsys.exit(1 if n == 1 else 0)\n")
    r, a, d = measure([sys.executable, ex, root], root, 3, DEFAULT_NORMALIZE)
    check("exit-disagreement", a == 2 and d == 1 and r[0]["exit"] == 0, f"agree={a} disagree={d}")

    shutil.rmtree(root, ignore_errors=True)
    fails = [c for c in checks if not c["ok"]]
    for c in checks:
        print(f"[{'PASS' if c['ok'] else 'FAIL'}] {c['name']}: {c['note']}")
    print(f"IA_SELFTEST pass={len(checks) - len(fails)} fail={len(fails)}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--cwd")
    ap.add_argument("--normalize", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    o = ap.parse_args()
    if o.selftest:
        return selftest()
    cmd = o.cmd[1:] if o.cmd[:1] == ["--"] else o.cmd
    if not cmd:
        print("instrument-agreement: missing command after --", file=sys.stderr)
        return 2
    if o.runs < 2:
        print("instrument-agreement: --runs must be >= 2", file=sys.stderr)
        return 2
    cwd = o.cwd or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isdir(cwd):
        print(f"instrument-agreement: cwd unavailable: {cwd}", file=sys.stderr)
        return 2
    rules = list(DEFAULT_NORMALIZE)
    for spec in o.normalize:
        if "=" not in spec:
            print(f"instrument-agreement: --normalize needs REGEX=REPL: {spec}", file=sys.stderr)
            return 2
        pattern, repl = spec.split("=", 1)
        try:
            re.compile(pattern)
        except re.error as e:
            print(f"instrument-agreement: bad regex {pattern!r}: {e}", file=sys.stderr)
            return 2
        rules.append((pattern, repl))
    try:
        results, agree, disagree = measure(cmd, cwd, o.runs, rules)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    receipt = {"tool": "instrument-agreement/v1", "command": cmd, "cwd": cwd,
               "runs": o.runs, "agree": agree, "disagree": disagree,
               "normalize": [list(r) for r in rules], "results": results,
               "verdict": "agree" if disagree == 0 else "disagree"}
    text = json.dumps(receipt, indent=1, sort_keys=True)
    if o.out:
        if os.path.exists(o.out):
            print(f"instrument-agreement: refusing to overwrite {o.out}", file=sys.stderr)
            return 2
        open(o.out, "w").write(text + "\n")
    print(f"IA runs={o.runs} agree={agree} disagree={disagree} "
          f"digest={results[0]['digest'][:12]} exit={results[0]['exit']}")
    return 0 if disagree == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
