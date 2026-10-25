#!/usr/bin/env python3
"""Round-33 W1 mutation probe for the C2 gate-receipt audit.

Applies one behaviour-bearing receipt mutation at a time in a disposable clone of
the lane repo, commits it (the audit reads receipt blobs at a tip commit, never the
working tree), runs the exact C2 audit command, then restores the clone to the
pristine baseline commit and proves the bytes are identical.

Lane repo itself is never written.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys

BASELINE = "7c35289da5f4b94e062cd900eb086919e5094003"
SOURCE_REV = "967d88528c1d83535563f971863f7855f76b4849"
RECEIPT_DIR = ".ufo/waves/round-33/c2/final"
GATE_TIP = f"{RECEIPT_DIR}/gate-tip-r33.out"
THIN_ROW = f"{RECEIPT_DIR}/controls/thin-row-r33.out"
EMPTY_MAP = f"{RECEIPT_DIR}/controls/empty-exit-map-r33.out"
MISSING_PATH = f"{RECEIPT_DIR}/controls/missing-path-r33.out"
RECEIPTS = [GATE_TIP, THIN_ROW, EMPTY_MAP, MISSING_PATH]
GATE_PATH = "tools/gate-registry-check.py"

RESULTS: list[dict] = []


def run(cwd: pathlib.Path, argv: list[str], env: dict[str, str] | None = None):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, env=env)


def commit_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        GIT_AUTHOR_NAME="kama-round-33-mutant",
        GIT_AUTHOR_EMAIL="kama-round-33-mutant@shokunin.local",
        GIT_COMMITTER_NAME="kama-round-33-mutant",
        GIT_COMMITTER_EMAIL="kama-round-33-mutant@shokunin.local",
        GIT_AUTHOR_DATE="2000-01-01T00:00:00+00:00",
        GIT_COMMITTER_DATE="2000-01-01T00:00:00+00:00",
    )
    return env


def git(repo: pathlib.Path, *args: str) -> str:
    proc = run(repo, ["git", "-C", str(repo), *args])
    if proc.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout


def audit(repo: pathlib.Path, tip: str) -> tuple[int, str]:
    proc = run(
        repo,
        [
            sys.executable,
            "tools/round33-gate-receipts.py",
            "audit",
            "--repo",
            ".",
            "--tip",
            tip,
            "--source-rev",
            SOURCE_REV,
            "--receipt-dir",
            RECEIPT_DIR,
        ],
    )
    return proc.returncode, (proc.stdout + proc.stderr).rstrip("\n")


def header_bounds(text: str) -> tuple[list[str], str]:
    head, rest = text.split("STDOUT_BEGIN\n", 1)
    return head.splitlines(keepends=True), "STDOUT_BEGIN\n" + rest


def join(head: list[str], rest: str) -> str:
    return "".join(head) + rest


def set_header(head: list[str], key: str, old_prefix: str, new_value: str) -> list[str]:
    hits = [i for i, line in enumerate(head) if line.startswith(key + "=")]
    assert len(hits) == 1, f"{key}: {len(hits)} header lines"
    i = hits[0]
    assert head[i].startswith(old_prefix), f"{key} unexpected: {head[i]!r}"
    assert head[i].endswith("\n")
    head[i] = f"{key}={new_value}\n"
    return head


def set_argv_rev(head: list[str], new_rev: str) -> list[str]:
    hits = [i for i, line in enumerate(head) if line.startswith("COMMAND_ARGV_JSON=")]
    assert len(hits) == 1
    i = hits[0]
    argv = json.loads(head[i].split("=", 1)[1])
    assert argv[4] == "--rev"
    argv[5] = new_rev
    head[i] = "COMMAND_ARGV_JSON=" + json.dumps(argv, ensure_ascii=False) + "\n"
    return head


def sub_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, f"expected one occurrence of {old!r}, got {text.count(old)}"
    return text.replace(old, new)


def mutate_shorten_hash(repo: pathlib.Path) -> dict:
    path = repo / GATE_TIP
    text = path.read_text(encoding="utf-8")
    short = SOURCE_REV[:12]
    head, rest = header_bounds(text)
    head = set_header(
        head,
        "COMMAND",
        f"COMMAND=python3 tools/gate-registry-check.py --repo <lane> --rev {SOURCE_REV}",
        f"python3 tools/gate-registry-check.py --repo <lane> --rev {short}",
    )
    head = set_header(head, "EVALUATED_REV", f"EVALUATED_REV={SOURCE_REV}", short)
    head = set_argv_rev(head, short)
    path.write_text(join(head, rest), encoding="utf-8")
    return {"file": GATE_TIP, "field": "EVALUATED_REV (+COMMAND, argv)", "old": SOURCE_REV,
            "new": short, "kind": "shortened 40-hex hash to 12 hex chars"}


def mutate_hex_digit(repo: pathlib.Path) -> dict:
    path = repo / THIN_ROW
    text = path.read_text(encoding="utf-8")
    head, rest = header_bounds(text)
    evaluated = [l for l in head if l.startswith("EVALUATED_REV=")][0].strip().split("=", 1)[1]
    flipped = evaluated[:-1] + ("4" if evaluated[-1] != "4" else "5")
    head = set_header(
        head,
        "COMMAND",
        f"COMMAND=python3 tools/gate-registry-check.py --repo <fixture:thin-row> --rev {evaluated}",
        f"python3 tools/gate-registry-check.py --repo <fixture:thin-row> --rev {flipped}",
    )
    head = set_header(head, "EVALUATED_REV", f"EVALUATED_REV={evaluated}", flipped)
    head = set_argv_rev(head, flipped)
    path.write_text(join(head, rest), encoding="utf-8")
    return {"file": THIN_ROW, "field": "EVALUATED_REV (+COMMAND, argv)",
            "old": evaluated, "new": flipped, "kind": "one hex digit changed"}


def mutate_source_digit(repo: pathlib.Path) -> dict:
    path = repo / GATE_TIP
    text = path.read_text(encoding="utf-8")
    head, rest = header_bounds(text)
    flipped = SOURCE_REV[:-1] + ("a" if SOURCE_REV[-1] != "a" else "b")
    head = set_header(
        head,
        "COMMAND",
        f"COMMAND=python3 tools/gate-registry-check.py --repo <lane> --rev {SOURCE_REV}",
        f"python3 tools/gate-registry-check.py --repo <lane> --rev {flipped}",
    )
    head = set_header(head, "SOURCE_REV", f"SOURCE_REV={SOURCE_REV}", flipped)
    head = set_argv_rev(head, flipped)
    path.write_text(join(head, rest), encoding="utf-8")
    return {"file": GATE_TIP, "field": "SOURCE_REV (+COMMAND, argv)", "old": SOURCE_REV,
            "new": flipped, "kind": "one hex digit changed in source revision"}


def mutate_alt_digest(repo: pathlib.Path) -> dict:
    gate_bytes = repo.joinpath(GATE_PATH).read_bytes()
    alternate = hashlib.sha256(gate_bytes + b"\n").hexdigest()
    actual = hashlib.sha256(gate_bytes).hexdigest()
    text = (repo / GATE_TIP).read_text(encoding="utf-8")
    head, rest = header_bounds(text)
    head = set_header(head, "GATE_SHA256", f"GATE_SHA256={actual}", alternate)
    (repo / GATE_TIP).write_text(join(head, rest), encoding="utf-8")
    return {"file": GATE_TIP, "field": "GATE_SHA256", "old": actual, "new": alternate,
            "kind": "alternate gate digest: sha256(gate bytes + trailing LF)"}


def restore(repo: pathlib.Path) -> None:
    git(repo, "reset", "--hard", "--quiet", BASELINE)
    git(repo, "clean", "-fdq")


def file_hashes(repo: pathlib.Path) -> dict[str, str]:
    return {
        rel: hashlib.sha256((repo / rel).read_bytes()).hexdigest() for rel in RECEIPTS
    }


def main() -> int:
    repo = pathlib.Path(sys.argv[1]).resolve()
    if not (repo / ".git").is_dir():
        raise SystemExit(f"not a clone root: {repo}")
    if git(repo, "rev-parse", "HEAD").strip() != BASELINE:
        raise SystemExit("scratch clone is not at the pristine baseline commit")

    pristine = file_hashes(repo)
    code, output = audit(repo, BASELINE)
    RESULTS.append({"mutant": "BASELINE (pristine receipts, no mutation)", "tip": BASELINE,
                    "exit": code, "audit": output, "diff": "", "bytes": pristine})
    print(f"### BASELINE tip={BASELINE} exit={code}\n{output}\n")

    for name, fn in (
        ("M1-shorten-evaluated-rev", mutate_shorten_hash),
        ("M2-flip-one-hex-digit-evaluated-rev", mutate_hex_digit),
        ("M3-flip-one-hex-digit-source-rev", mutate_source_digit),
        ("M4-alternate-gate-digest", mutate_alt_digest),
    ):
        detail = fn(repo)
        git(repo, "add", "-A")
        env = commit_env()
        proc = run(
            repo,
            ["git", "-c", "commit.gpgsign=false", "commit", "-qm", f"mutant {name}"],
            env=env,
        )
        if proc.returncode:
            raise SystemExit(f"commit failed: {proc.stderr}")
        tip = git(repo, "rev-parse", "HEAD").strip()
        diff = git(repo, "diff", "--unified=0", BASELINE, tip, "--", *RECEIPTS)
        code, output = audit(repo, tip)
        print(f"### {name} tip={tip} exit={code}\n{output}")
        print(diff)
        RESULTS.append({"mutant": name, "detail": detail, "tip": tip, "exit": code,
                        "audit": output, "diff": diff, "bytes": file_hashes(repo)})
        restore(repo)

    restored = file_hashes(repo)
    code, output = audit(repo, BASELINE)
    ok = restored == pristine
    print(f"### RESTORED tip={BASELINE} exit={code} bytes_identical={ok}\n{output}")
    RESULTS.append({"mutant": "RESTORED baseline bytes", "tip": BASELINE, "exit": code,
                    "audit": output, "diff": "", "bytes": restored,
                    "restored_identical": ok})

    report = {
        "baseline_commit": BASELINE,
        "source_rev": SOURCE_REV,
        "receipt_dir": RECEIPT_DIR,
        "pristine_sha256": pristine,
        "restored_sha256": restored,
        "restored_identical": ok,
        "results": RESULTS,
    }
    out = pathlib.Path(__file__).with_name("mutants.json")
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
