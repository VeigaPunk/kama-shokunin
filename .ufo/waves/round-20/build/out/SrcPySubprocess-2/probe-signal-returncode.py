#!/usr/bin/env python3
"""probe-signal-returncode.py - executed evidence for the SrcPySubprocess draft.

Observes, on the host interpreter, what the Python 3.14 `subprocess` docs say
about `returncode` (negative -N = terminated by signal N, POSIX; a shell may
map signals to 128+N), the `sys.exit(p.returncode)` re-exit idiom used by
tests/probe-verdicts/fault-controls.py:432,443,506, and four error-injection
cells against the frozen tests/llamacpp-live/install-tree-grid.py bytes at
the round-start pin (a stub gate killed by a signal emits no verdict).

    probe-signal-returncode.py --out PATH.json

Stdlib only. Every child is waited for; no server, no network. Writes only
--out and a temporary directory it removes. Prints one line per cell.
Exit: 0 every cell matched its expectation; 1 a cell differed; 2 harness fault.
"""
import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
PIN = "37bd4c5bd456a2f8a54d3312c28495c321715856"
GRID = "tests/llamacpp-live/install-tree-grid.py"
SLEEP = "31.7"           # unusual length so a leftover child is findable
MEMBER = "libllama.so.0.7.0"
TIMEOUT = 60

SELF_KILL = ("import os, signal\n"
             "os.kill(os.getpid(), signal.SIGKILL)\n")
VERDICT_THEN_KILL = ("import os, signal\n"
                     "print('INVALID would-be verdict', flush=True)\n"
                     "os.kill(os.getpid(), signal.SIGKILL)\n")
REEXIT = ("import subprocess, sys\n"
          "p = subprocess.run([sys.executable, '-c', " + repr(SELF_KILL) + "])\n"
          "print(p.returncode, flush=True)\n"
          "sys.exit(p.returncode)\n")
GATE_STUB = r'''import json, os, signal, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    tree = json.load(fh)["server"]["install_tree"]
mutant = any(v == "a" * 64 for v in tree.values())
sig = os.environ.get("STUB_MUTANT_SIG" if mutant else "STUB_BASE_SIG", "")
if sig:
    os.kill(os.getpid(), getattr(signal, sig))
print("INVALID stub verdict" if mutant else "VALID stub verdict", flush=True)
sys.exit(1 if mutant else 0)
'''


def run(argv, **kw):
    return subprocess.run(argv, capture_output=True, text=True,
                          timeout=TIMEOUT, **kw)


def cell(cid, expect, observed, source):
    ok = all(observed.get(k) == v for k, v in expect.items())
    print(f"cell={cid} ok={ok} expect={json.dumps(expect, sort_keys=True)} "
          f"observed={json.dumps(observed, sort_keys=True)}")
    return {"id": cid, "ok": ok, "expect": expect, "observed": observed,
            "grounds": source}


def doc_cells():
    cells = []
    p = subprocess.Popen(["sleep", SLEEP])
    p.kill()
    cells.append(cell("popen-kill", {"returncode": -signal.SIGKILL},
                      {"returncode": p.wait(timeout=TIMEOUT)},
                      "subprocess.rst@v3.14.8:958-959"))
    p = subprocess.Popen(["sleep", SLEEP])
    p.terminate()
    cells.append(cell("popen-terminate", {"returncode": -signal.SIGTERM},
                      {"returncode": p.wait(timeout=TIMEOUT)},
                      "subprocess.rst@v3.14.8:958-959"))
    cp = run([sys.executable, "-c", VERDICT_THEN_KILL])
    cells.append(cell("run-verdict-text-then-sigkill",
                      {"returncode": -9, "stdout": "INVALID would-be verdict\n"},
                      {"returncode": cp.returncode, "stdout": cp.stdout},
                      "subprocess.rst@v3.14.8:136-142"))
    try:
        run([sys.executable, "-c", SELF_KILL], check=True)
        observed = {"raised": False}
    except subprocess.CalledProcessError as exc:
        observed = {"raised": True, "returncode": exc.returncode,
                    "str": str(exc).split(" died with ", 1)[-1]}
    cells.append(cell("check-true-calledprocesserror",
                      {"raised": True, "returncode": -9,
                       "str": "<Signals.SIGKILL: 9>."}, observed,
                      "subprocess.rst@v3.14.8:240-243"))
    cp = run(f"sleep {SLEEP} & kill -KILL $!; wait $!", shell=True)
    cells.append(cell("shell-true-child-sigkill", {"returncode": 128 + 9},
                      {"returncode": cp.returncode},
                      "subprocess.rst@v3.14.8:961-964"))
    cp = run("kill -KILL $$", shell=True)
    cells.append(cell("shell-true-shell-itself-sigkill", {"returncode": -9},
                      {"returncode": cp.returncode},
                      "subprocess.rst@v3.14.8:958-959"))
    cp = run(["bash", "-c", f"sleep {SLEEP} & kill -TERM $!; wait $!"])
    cells.append(cell("bash-argv-child-sigterm", {"returncode": 128 + 15},
                      {"returncode": cp.returncode},
                      "bash.1 EXIT STATUS (bash 5.3.20-1)"))
    cp = run([sys.executable, "-c", REEXIT])
    cells.append(cell("python-reexit-sys-exit-returncode",
                      {"returncode": 256 - 9, "stdout": "-9\n"},
                      {"returncode": cp.returncode, "stdout": cp.stdout},
                      "fault-controls.py@37bd4c5:432,443,506 idiom"))
    return cells


def tree_sha(tree):
    lines = "".join(f"{name} {tree[name]}\n" for name in sorted(tree))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def grid_cells(tmp):
    blob = subprocess.run(["git", "-C", str(LANE), "show", f"{PIN}:{GRID}"],
                          capture_output=True, timeout=TIMEOUT, check=True).stdout
    grid = tmp / "install-tree-grid.py"
    grid.write_bytes(blob)
    gate = tmp / "gate-stub.py"
    gate.write_text(GATE_STUB, encoding="utf-8")
    tree = {MEMBER: "b" * 64}
    receipt = tmp / "receipt.json"
    receipt.write_text(json.dumps({"server": {
        "install_tree": tree, "install_tree_sha256": tree_sha(tree)}}),
        encoding="utf-8")
    argv = [sys.executable, str(grid), "--gate", str(gate),
            "--receipt", str(receipt)]
    for flag in ("--model-sha", "--server-sha", "--impl-sha", "--probe-sha",
                 "--tool-sha"):
        argv += [flag, "0" * 64]
    argv += ["--members", MEMBER, "--json"]
    plan = (
        ("frozen-grid-mutant-honest-reject", {}, {
            "grid_exit": 0, "baseline": "VALID", "gate_exit": 1,
            "status": "rejected", "rejected": 1}),
        ("frozen-grid-mutant-sigkill", {"STUB_MUTANT_SIG": "SIGKILL"}, {
            "grid_exit": 1, "baseline": "VALID", "gate_exit": -9,
            "status": "accepted", "rejected": 0}),
        ("frozen-grid-mutant-sigterm", {"STUB_MUTANT_SIG": "SIGTERM"}, {
            "grid_exit": 1, "baseline": "VALID", "gate_exit": -15,
            "status": "accepted", "rejected": 0}),
        ("frozen-grid-baseline-sigkill", {"STUB_BASE_SIG": "SIGKILL"}, {
            "grid_exit": 2, "baseline": "INVALID", "members": 0}),
    )
    cells = []
    for cid, extra, expect in plan:
        env = {k: v for k, v in os.environ.items() if not k.startswith("STUB_")}
        env.update(extra)
        cp = run(argv, env=env)
        doc = json.loads(cp.stdout)
        row = doc["rows"][0] if doc.get("rows") else {}
        observed = {"grid_exit": cp.returncode, "baseline": doc.get("baseline"),
                    "members": doc.get("members"),
                    "rejected": doc.get("rejected"),
                    "gate_exit": row.get("gate_exit"),
                    "status": row.get("status"), "stdout": row.get("stdout")}
        cells.append(cell(cid, expect, observed,
                          f"{GRID}@{PIN[:7]}:49-53,92,110-111"))
    return cells, hashlib.sha256(blob).hexdigest(), len(blob)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    try:
        cells = doc_cells()
        with tempfile.TemporaryDirectory(prefix="kama-r20-srcpysub-") as tmp:
            more, grid_sha, grid_len = grid_cells(Path(tmp))
        cells += more
        left = subprocess.run(["pgrep", "-f", f"sleep {SLEEP}"],
                              capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"harness fault: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    leftover = left.stdout.split()
    doc = {"schema": "kama-r20-srcpysubprocess-probe/v1",
           "python": sys.version, "executable": sys.executable,
           "frozen_grid": {"rev": PIN, "path": GRID, "sha256": grid_sha,
                           "bytes": grid_len},
           "cells": cells, "leftover_sleep_pids": leftover,
           "ok": sum(c["ok"] for c in cells), "total": len(cells)}
    Path(args.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(f"cells={len(cells)} ok={doc['ok']} leftover={len(leftover)} "
          f"frozen_grid_sha256={grid_sha}")
    return 0 if doc["ok"] == len(cells) and not leftover else 1


if __name__ == "__main__":
    sys.exit(main())
