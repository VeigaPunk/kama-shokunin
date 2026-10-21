#!/usr/bin/env python3
"""End-to-end check that the live producer refuses an unpinnable install
before launching anything.

Usage: unpinnable-e2e.py [--tree DIR] [--model PATH --model-sha256 HEX]

Copies the install directory (symlinks preserved) to a temporary directory
three times and adds one unpinnable entry per copy: a `glibc-hwcaps/`
directory, a `glibc-hwcaps` symlink to a directory, and a soname link that
dangles. For each, runs `tools/kama-llamacpp-live.py` against the copy and
requires exit 2, `setup_error` starting `install-tree-unpinnable:`, no child
PID and no argv (nothing launched). A pristine copy must pass the same
pre-launch scan (`install_links` problems empty) without being run.

Exit: 0 every case refused before launch; 1 a case launched or was not
refused; 2 could-not-evaluate (missing tree/model, copy failure).
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types

LANE = Path(__file__).resolve().parents[2]
PRODUCER = LANE / "tools/kama-llamacpp-live.py"
TREE = Path.home() / ".local/opt/llama-b11755"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"


def copy_tree(src, dst):
    dst.mkdir()
    for entry in sorted(os.listdir(src)):
        full = src / entry
        if full.is_symlink():
            os.symlink(os.readlink(full), dst / entry)
        elif full.is_file():
            shutil.copy2(full, dst / entry)
        else:
            raise RuntimeError(f"{full}: unexpected entry type")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tree", type=Path, default=TREE)
    ap.add_argument("--model", type=Path, default=MODEL)
    ap.add_argument("--model-sha256", default=MODEL_SHA)
    args = ap.parse_args()
    try:
        if not (args.tree / "llama-server").is_file() or not args.model.is_file():
            raise RuntimeError("tree or model missing")
        producer = types.ModuleType("producer")
        producer.__file__ = str(PRODUCER)
        exec(compile(PRODUCER.read_text(encoding="utf-8"), str(PRODUCER),
                     "exec"), producer.__dict__)
        cases = {
            "hwcaps-directory": lambda d: (d / "glibc-hwcaps" / "x86-64-v3")
            .mkdir(parents=True),
            "hwcaps-symlink-to-dir": lambda d: os.symlink(
                tempfile.gettempdir(), d / "glibc-hwcaps"),
            "dangling-soname": lambda d: (os.unlink(d / "libggml.so.0"),
                                          os.symlink("libggml.so.9",
                                                     d / "libggml.so.0")),
        }
        failures, rows = [], []
        with tempfile.TemporaryDirectory(prefix="kama-unpinnable-") as tmp:
            pristine = Path(tmp) / "pristine"
            copy_tree(args.tree, pristine)
            try:
                tree, _ = producer.install_tree(str(pristine / "llama-server"))
            except producer.SetupError as exc:
                raise RuntimeError(f"pristine identity unavailable: {exc.code}") from exc
            problems = producer.install_links(str(pristine / "llama-server"),
                                              tree)[2]
            rows.append({"case": "pristine-scan", "problems": problems})
            if problems:
                failures.append(f"pristine copy has problems {problems}")
            for name, mutate in cases.items():
                d = Path(tmp) / name
                copy_tree(args.tree, d)
                mutate(d)
                out = Path(tmp) / f"{name}.json"
                proc = subprocess.run(
                    [sys.executable, str(PRODUCER), "--server",
                     str(d / "llama-server"), "--model", str(args.model),
                     "--model-sha256", args.model_sha256, "--out", str(out)],
                    capture_output=True, text=True, timeout=120)
                receipt = json.loads(out.read_text()) if out.is_file() else {}
                setup = receipt.get("setup_error") or ""
                ok = (proc.returncode == 2
                      and setup.startswith("install-tree-unpinnable:")
                      and receipt.get("child_pid") is None
                      and receipt.get("argv") is None)
                rows.append({"case": name, "exit": proc.returncode,
                             "setup_error": setup,
                             "child_pid": receipt.get("child_pid"),
                             "argv": receipt.get("argv"), "refused": ok})
                if not ok:
                    failures.append(name)
        for row in rows:
            print(json.dumps(row, sort_keys=True))
        print(f"summary cases={len(cases)} refused={len(cases) - len([f for f in failures if f in cases])} "
              f"failures={len(failures)}")
        return 0 if not failures else 1
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
