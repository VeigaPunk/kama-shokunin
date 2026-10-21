#!/usr/bin/env python3
"""Capture one frozen-grid detector phase, without editing the detector or gate."""
import argparse
import concurrent.futures
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

SCRATCH = Path("/tmp/kama-r20-MutGridRedBefore")
LANE = SCRATCH / "lane"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/MutGridRedBefore")
RECEIPT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live-recovery/receipt-1.json")
GRID = LANE / "tests/llamacpp-live/install-tree-grid.py"
GATE = SCRATCH / "gate-stub.py"
FROZEN_RECEIPT = LANE / ".ufo/waves/round-18/live-recovery/receipt-1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    return {str(path): sha(path) for path in (GRID, GATE, RECEIPT, FROZEN_RECEIPT)}


def capture(argv):
    proc = subprocess.Popen(argv, cwd=LANE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
    return {"argv": argv, "cwd": str(LANE), "exit": proc.returncode,
            "stdout": stdout, "stderr": stderr, "timed_out": timed_out}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("pristine", "mutated", "restored"))
    phase = parser.parse_args().phase
    before = snapshot()
    base = json.loads(RECEIPT.read_text(encoding="utf-8"))
    fields = [("model", base["model_sha256_post"]),
              ("server", base["server"]["sha256"]),
              ("server-impl", base["server"]["server_impl_sha256"]),
              ("probe", base["probe"]["sha256"]),
              ("tool", base["tool"]["sha256"]),
              ("install-tree", base["server"]["install_tree_sha256"])]
    grid_flags = ("model", "server", "impl", "probe", "tool", "tree")
    grid_argv = [sys.executable, str(GRID), "--gate", str(GATE),
                 "--receipt", str(RECEIPT)]
    direct_flags = []
    for (field, value), grid_flag in zip(fields, grid_flags):
        grid_argv += ["--" + grid_flag + "-sha", value]
        direct_flags += ["--expect-" + field + "-sha256", value]
    grid_argv += ["--json"]
    mutant = copy.deepcopy(base)
    mutant["server"]["install_tree"]["libggml-base.so.0.27.0"] = "a" * 64
    tree = mutant["server"]["install_tree"]
    material = "".join(f"{name} {tree[name]}\n" for name in sorted(tree))
    mutant["server"]["install_tree_sha256"] = hashlib.sha256(material.encode()).hexdigest()
    subject_path = SCRATCH / "direct-member.json"
    subject_path.write_text(json.dumps(mutant), encoding="utf-8")
    direct_argv = [sys.executable, str(GATE), str(subject_path), *direct_flags]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        grid_future = executor.submit(capture, grid_argv)
        direct_future = executor.submit(capture, direct_argv)
        grid_result, direct_result = grid_future.result(), direct_future.result()
    try:
        document = json.loads(grid_result["stdout"])
    except ValueError:
        document = None
    record = {"phase": phase, "frozen_commit": "37bd4c5bd456a2f8a54d3312c28495c321715856",
              "hashes_before": before, "hashes_after": snapshot(),
              "grid": grid_result, "direct_gate": direct_result,
              "grid_document": document,
              "processes_reaped": True}
    output_path = OUT / (phase + ".json")
    with output_path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    print(f"phase={phase} grid_exit={grid_result['exit']} direct_gate_exit={direct_result['exit']}")
    print(f"gate_sha256={before[str(GATE)]}")
    print("GRID STDOUT:\n" + grid_result["stdout"], end="")
    print("GRID STDERR:\n" + grid_result["stderr"], end="")
    print("DIRECT GATE STDOUT:\n" + direct_result["stdout"], end="")
    print("DIRECT GATE STDERR:\n" + direct_result["stderr"], end="")
    print(f"evidence={output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
