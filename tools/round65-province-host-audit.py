#!/usr/bin/env python3
"""round65-province-host-audit.py - PROVINCE.md must match the observed host.

Round 65 moved the lane to a new Windows host. PROVINCE.md's "Owns" table and
round notes name concrete artifacts on "this box" that the former Linux host
held. Calibration contract: every named host surface is either present on the
current host or recorded absent in PROVINCE.md with its host-census date.

For each declared surface this audit checks the host and requires, for an
absent surface, that PROVINCE.md's bytes carry the surface's marker tag
(`province-host:<tag>`), which the round-65 corrections attach to the
recorded-absent lines. A present surface needs no marker.

    PROVINCE_HOST_AUDIT surfaces=N present=P absent=A stale=S
    stale <tag>: absent on this host and unmarked in PROVINCE.md

Exit: 0 stale == 0; 1 otherwise. Read-only: it stats host paths, may spawn the
declared interpreter once, and reads PROVINCE.md; it writes nothing.

Round 67 extends the declared set to the serving-side surfaces the lane-owned
live fixtures need (round-16 llama.cpp fixture, round-60 Ollama fixture —
paths as pinned in `registry/ollama-live-pin.tsv`) and to the interpreter
precondition every registered ``python3 tools/...`` command carries: on this
host ``python3`` is the Microsoft Store app-execution alias stub, and a PATH
hit for it is not a usable interpreter (S539 — the alias can report
"command not found" or open the Store instead of running Python), so the
``spawn`` kind grades a real run (``python3 -c "import sys"``, exit 0) rather
than existence; a spawn that errors or exceeds the 30 s budget grades absent.
"""
import os
import subprocess
import sys
from pathlib import Path

LANE = Path(__file__).resolve().parent.parent
PROVINCE = LANE / "PROVINCE.md"

# (tag, kind, path/env; kind: file|dir|env|spawn)
SURFACES = [
    ("omp-binary", "file", "~/.local/bin/omp"),
    ("llama-b11755-install", "dir", "~/.local/opt/llama-b11755"),
    ("llama-server-link", "file", "~/.local/bin/llama-server"),
    ("kama-cache-gguf", "dir", "~/.cache/kama-shokunin"),
    ("llama-b11755-archive", "file", "~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz"),
    ("qwen-coder-unit", "file", "~/.config/systemd/user/qwen-coder.service"),
    ("opencode-json", "file", "~/.config/opencode/opencode.json"),
    ("janitor-md", "file", "~/.config/opencode/agents/janitor.md"),
    ("ufo-src", "env", "UFO_SRC"),
    ("omp-dir", "dir", "~/.omp"),
    ("ollama-v04011-install", "dir", "~/.local/opt/ollama-v0.40.11"),
    ("fixture-gguf-model", "file", "~/.cache/kama-shokunin/models/stories260K.gguf"),
    ("python3-interpreter", "spawn", "python3"),
]

SPAWN_TIMEOUT = 30


def host_has(kind, target):
    if kind == "env":
        return bool(os.environ.get(target))
    if kind == "spawn":
        try:
            proc = subprocess.run(
                [target, "-c", "import sys"], capture_output=True,
                timeout=SPAWN_TIMEOUT)
        except (OSError, subprocess.TimeoutExpired):
            return False
        return proc.returncode == 0
    full = Path(os.path.expanduser(target))
    return full.exists() and (full.is_dir() if kind == "dir" else full.is_file())


def main():
    try:
        province = PROVINCE.read_bytes().decode("utf-8")
    except OSError as exc:
        print(f"PROVINCE_HOST_AUDIT could-not-evaluate: cannot read PROVINCE.md: {exc}")
        return 2
    present = absent = stale = 0
    for tag, kind, target in SURFACES:
        if host_has(kind, target):
            present += 1
            print(f"present {tag} ({target})")
            continue
        absent += 1
        if f"province-host:{tag}" in province:
            print(f"absent-recorded {tag} ({target})")
        else:
            stale += 1
            print(f"stale {tag}: absent on this host and unmarked in PROVINCE.md")
    print(f"PROVINCE_HOST_AUDIT surfaces={len(SURFACES)} present={present} "
          f"absent={absent} stale={stale}")
    return 0 if stale == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
