#!/usr/bin/env python3
"""Build C2 (engine-pin-relations) fixtures under $S/fixtures/c2.

Uses the lane's real committed tag lists (copied, read-only source) plus register
variants:
  reg-good.tsv          lane register as-is
  reg-no-b7200.tsv      same register with the llama.cpp b7200 cross-lane row removed
                        (missing ref covered by the sibling llama.cpp commit row)
Also builds a synthetic git repo whose receipt is present in the worktree but not
committed at the tip (probes the module's receipt_committed fallback).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
LANE = Path(sys.argv[2])

TAGS = ROOT / "tags"
TAGS.mkdir(parents=True, exist_ok=True)
for engine in ("llama.cpp", "sglang", "vllm"):
    shutil.copyfile(LANE / ".ufo/waves/round-80/measured/after/c2-tags" / f"{engine}.txt",
                    TAGS / f"{engine}.txt")

register = (LANE / "registry/engine-pin-relations.tsv").read_text()
(ROOT / "reg-good.tsv").write_text(register)
kept = [line for line in register.splitlines(keepends=True)
        if not (line.startswith("llama.cpp\tb7200\t"))]
(ROOT / "reg-no-b7200.tsv").write_text("".join(kept))

# ---- synthetic git repo: uncommitted receipt at the tip -------------------------
git_root = ROOT / "git-uncommitted-receipt"
if git_root.exists():
    shutil.rmtree(git_root)
git_root.mkdir(parents=True)


def run(*args):
    proc = subprocess.run(["git", "-C", str(git_root), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout


run("init", "-q")
run("config", "user.name", "fixture")
run("config", "user.email", "fixture@example.invalid")
run("config", "commit.gpgsign", "false")
(git_root / "tags").mkdir()
(git_root / "tags/alpha.txt").write_text("a" * 40 + "\trefs/tags/a1\n" + "b" * 40 + "\trefs/tags/a2\n")
(git_root / "tags/llama.cpp.txt").write_text(
    "c" * 40 + "\trefs/tags/b11963\n"
    + "39febd2adb947b70da35e95f9351b3bf58ad170a" + "\trefs/tags/b11963^{}\n"
    + "d" * 40 + "\trefs/tags/b7200\n")
(git_root / "pins.tsv").write_text(
    "engine\trepo\ttag_regex\tpin\tsource\n"
    "alpha\t-\ta(\\d+)\ta1\tS1\n"
    "llama.cpp\t-\tb(\\d+)\tb7200\tS2\n")
(git_root / "register.tsv").write_text(
    "engine\tref\tkind\trole\trelation\tnewer\tnewest\treceipt\tdated\n"
    "alpha\ta1\ttag\tsynthetic\tbehind\t1\ta2\treceipts/alpha.txt\t2026-11-04\n"
    "llama.cpp\t39febd2adb947b70da35e95f9351b3bf58ad170a\tcommit\tsynthetic\ttag:b11963\t0\tb11963\ttags/alpha.txt\t2026-11-04\n"
    "llama.cpp\tb7200\ttag\tsynthetic\tbehind\t1\tb11963\ttags/alpha.txt\t2026-11-04\n")
run("add", "tags", "pins.tsv", "register.tsv")
run("commit", "-q", "-m", "committed files, receipt not committed")
tip = run("rev-parse", "HEAD").strip()
(git_root / "receipts").mkdir()
(git_root / "receipts/alpha.txt").write_text("tags\n")  # untracked: present, not committed

index = {
    "tags_dir": str(TAGS),
    "register_good": str(ROOT / "reg-good.tsv"),
    "register_no_b7200": str(ROOT / "reg-no-b7200.tsv"),
    "git_uncommitted_receipt": {"repo": str(git_root), "tip": tip,
                                "receipt": "receipts/alpha.txt"},
}
(ROOT / "index.json").write_text(json.dumps(index, indent=2) + "\n")
print(json.dumps(index, indent=2))
