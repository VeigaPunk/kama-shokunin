#!/usr/bin/env python3
"""Capture and audit complete receipts for the round-32 registry gate.

Capture runs the gate code from a pinned lane revision against that revision and
three deterministic, disposable Git fixtures. Fixture Git writes stay under a
temporary directory. Audit reads only committed receipt blobs and replays each
case from its pinned source revision; the lane repository is never mutated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

FULL_REV = re.compile(r"^[0-9a-f]{40}$")
GATE_PATH = "tools/gate-registry-check.py"
RUNNER_PATH = "tools/round33-gate-receipts.py"
RECEIPT_ROOT = ".ufo/waves/round-33/c2"
CASES = {
    "gate-tip": ("gate-tip-r33.out", 0, "registered 10 unregistered 0 defective 0"),
    "thin-row": (
        "controls/thin-row-r33.out",
        1,
        "defective .ufo/waves/round-33/count-fixture.py: thin-row",
    ),
    "empty-exit-map": (
        "controls/empty-exit-map-r33.out",
        1,
        "defective .ufo/waves/round-33/count-fixture.py: empty-exit-map",
    ),
    "missing-path": (
        "controls/missing-path-r33.out",
        1,
        "defective .ufo/waves/round-33/count-fixture.py: missing-path:.ufo/waves/round-999/count-c999.py",
    ),
}
EXPECTED_STDOUT = {
    "gate-tip": ["registered 10 unregistered 0 defective 0"],
    "thin-row": [
        "defective .ufo/waves/round-33/count-fixture.py: thin-row",
        "defective .ufo/waves/round-33/count-fixture.py: empty-entry",
        "defective .ufo/waves/round-33/count-fixture.py: empty-exit-map",
        "registered 1 unregistered 0 defective 3",
    ],
    "empty-exit-map": [
        "defective .ufo/waves/round-33/count-fixture.py: empty-exit-map",
        "registered 1 unregistered 0 defective 1",
    ],
    "missing-path": [
        "defective .ufo/waves/round-33/count-fixture.py: missing-path:.ufo/waves/round-999/count-c999.py",
        "registered 1 unregistered 0 defective 1",
    ],
}

REGISTRY_HEADER = (
    "| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |\n"
    "|---|---|---|---|---|\n"
)


class ReceiptError(Exception):
    pass


def git(repo: str | Path, *args: str, env: dict[str, str] | None = None) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if proc.returncode:
        message = proc.stderr.decode("utf-8", "replace").strip()
        raise ReceiptError(f"git {' '.join(args)} failed ({proc.returncode}): {message}")
    return proc.stdout


def git_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_AUTHOR_NAME"] = "kama-round-33-control"
    env["GIT_AUTHOR_EMAIL"] = "kama-round-33-control@shokunin.local"
    env["GIT_COMMITTER_NAME"] = "kama-round-33-control"
    env["GIT_COMMITTER_EMAIL"] = "kama-round-33-control@shokunin.local"
    env["GIT_AUTHOR_DATE"] = "2000-01-01T00:00:00+00:00"
    env["GIT_COMMITTER_DATE"] = "2000-01-01T00:00:00+00:00"
    return env


def verify_revision(repo: str | Path, revision: str) -> None:
    if not FULL_REV.fullmatch(revision):
        raise ReceiptError("revision must be a full 40-character commit id")
    resolved = git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}").decode().strip()
    if resolved != revision:
        raise ReceiptError(f"revision did not resolve exactly: {revision}")


def read_blob(repo: str | Path, revision: str, path: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{revision}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        raise ReceiptError(f"missing blob at {revision}:{path}")
    return proc.stdout


def write_fixture(root: Path, kind: str, gate_bytes: bytes) -> None:
    (root / "tools").mkdir(parents=True, exist_ok=True)
    counter = ".ufo/waves/round-33/count-fixture.py"
    counter_path = root / counter
    counter_path.parent.mkdir(parents=True, exist_ok=True)
    counter_path.write_bytes(b"# deterministic registry fixture counter\n")
    (root / GATE_PATH).write_bytes(gate_bytes)

    if kind == "thin-row":
        row = f"| {counter} | | | | |\n"
    elif kind == "empty-exit-map":
        row = (
            f"| {counter} | python3 |   | "
            "fixed fixture values | no repository writes |\n"
        )
    elif kind == "missing-path":
        row = (
            f"| {counter} | .ufo/waves/round-999/count-c999.py | "
            "0 clean; 1 rejected | fixed fixture values | no repository writes |\n"
        )
    else:
        raise ReceiptError(f"unknown fixture kind: {kind}")
    (root / "SKILL.md").write_text(REGISTRY_HEADER + row, encoding="utf-8")


def create_fixture(tmp: Path, kind: str, gate_bytes: bytes) -> tuple[Path, str, str]:
    root = tmp / f"fixture-{kind}"
    root.mkdir()
    write_fixture(root, kind, gate_bytes)
    env = git_environment()
    git(root, "init", "-q", env=env)
    git(root, "add", "-A", env=env)
    git(
        root,
        "-c",
        "core.autocrlf=false",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-qm",
        f"round-33 {kind} control",
        env=env,
    )
    revision = git(root, "rev-parse", "HEAD", env=env).decode().strip()
    tree = git(root, "rev-parse", f"{revision}^{{tree}}", env=env).decode().strip()
    return root, revision, tree


def invoke_gate(
    script: Path,
    repo: Path,
    revision: str,
    *,
    cwd: Path,
) -> tuple[int, str, str, list[str]]:
    argv = [sys.executable, str(script), "--repo", str(repo), "--rev", revision]
    proc = subprocess.run(
        argv,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return (
        proc.returncode,
        proc.stdout.decode("utf-8", "replace"),
        proc.stderr.decode("utf-8", "replace"),
        argv,
    )


def receipt_text(
    *,
    case: str,
    source_rev: str,
    evaluated_rev: str,
    gate_hash: str,
    runner_hash: str,
    tree: str,
    command_argv: list[str],
    exit_code: int,
    stdout: str,
    stderr: str,
) -> str:
    replay = (
        f"python3 {GATE_PATH} --repo <lane> --rev {source_rev}"
        if case == "gate-tip"
        else f"python3 {GATE_PATH} --repo <fixture:{case}> --rev {evaluated_rev}"
    )
    lines = [
        "FORMAT=KAMA_GATE_RECEIPT_V1",
        f"FIXTURE={case}",
        f"COMMAND={replay}",
        f"COMMAND_ARGV_JSON={json.dumps(command_argv, ensure_ascii=False)}",
        f"SOURCE_REV={source_rev}",
        f"EVALUATED_REV={evaluated_rev}",
        f"EVALUATED_TREE={tree}",
        f"GATE_SHA256={gate_hash}",
        f"RUNNER_SHA256={runner_hash}",
        f"EXIT_CODE={exit_code}",
        "STDOUT_BEGIN",
    ]
    text = "\n".join(lines) + "\n" + stdout
    if stdout and not stdout.endswith("\n"):
        text += "\n"
    text += "STDOUT_END\nSTDERR_BEGIN\n" + stderr
    if stderr and not stderr.endswith("\n"):
        text += "\n"
    return text + "STDERR_END\n"


def expected_receipts(repo: Path, source_rev: str) -> dict[str, str]:
    verify_revision(repo, source_rev)
    gate_bytes = read_blob(repo, source_rev, GATE_PATH)
    gate_hash = hashlib.sha256(gate_bytes).hexdigest()
    runner_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    expected: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="kama-r33-gate-") as temp_name:
        temp = Path(temp_name)
        gate_dir = temp / "lane-gate"
        gate_dir.mkdir()
        gate_script = gate_dir / "gate-registry-check.py"
        gate_script.write_bytes(gate_bytes)
        code, stdout, stderr, argv = invoke_gate(
            gate_script, repo, source_rev, cwd=repo
        )
        tree = git(repo, "rev-parse", f"{source_rev}^{{tree}}").decode().strip()
        expected["gate-tip"] = receipt_text(
            case="gate-tip",
            source_rev=source_rev,
            evaluated_rev=source_rev,
            gate_hash=gate_hash,
            runner_hash=runner_hash,
            tree=tree,
            command_argv=argv,
            exit_code=code,
            stdout=stdout,
            stderr=stderr,
        )

        for kind in ("thin-row", "empty-exit-map", "missing-path"):
            fixture, revision, fixture_tree = create_fixture(temp, kind, gate_bytes)
            fixture_gate = fixture / GATE_PATH
            code, stdout, stderr, argv = invoke_gate(
                fixture_gate, fixture, revision, cwd=fixture
            )
            expected[kind] = receipt_text(
                case=kind,
                source_rev=source_rev,
                evaluated_rev=revision,
                gate_hash=gate_hash,
                runner_hash=runner_hash,
                tree=fixture_tree,
                command_argv=argv,
                exit_code=code,
                stdout=stdout,
                stderr=stderr,
            )
    return expected


def output_ok(case: str, receipt: str, expected_exit: int, expected_line: str,
              source_rev: str, gate_hash: str, runner_hash: str) -> bool:
    headers: dict[str, str] = {}
    try:
        before_stdout, stdout_and_tail = receipt.split("STDOUT_BEGIN\n", 1)
        stdout, _tail = stdout_and_tail.split("STDOUT_END\nSTDERR_BEGIN\n", 1)
    except ValueError:
        return False
    for line in before_stdout.splitlines():
        if "=" not in line:
            return False
        key, value = line.split("=", 1)
        if key in headers:
            return False
        headers[key] = value
    evaluated = headers.get("EVALUATED_REV", "")
    tree = headers.get("EVALUATED_TREE", "")
    try:
        argv = json.loads(headers.get("COMMAND_ARGV_JSON", ""))
    except (TypeError, json.JSONDecodeError):
        return False
    if (
        not isinstance(argv, list)
        or len(argv) != 6
        or not all(isinstance(arg, str) for arg in argv)
        or Path(argv[0]).name not in {"python", "python3"}
        or not argv[1].endswith("gate-registry-check.py")
        or argv[2] != "--repo"
        or not os.path.isabs(argv[3])
        or argv[4] != "--rev"
        or argv[5] != evaluated
    ):
        return False
    evaluated_for_command = source_rev if case == "gate-tip" else evaluated
    fixture_for_command = "<lane>" if case == "gate-tip" else f"<fixture:{case}>"
    expected_command = (
        f"python3 {GATE_PATH} --repo {fixture_for_command} --rev {evaluated_for_command}"
    )
    return (
        headers.get("FORMAT") == "KAMA_GATE_RECEIPT_V1"
        and headers.get("FIXTURE") == case
        and bool(re.fullmatch(r"[0-9a-f]{40}", evaluated))
        and bool(re.fullmatch(r"[0-9a-f]{40}", tree))
        and headers.get("SOURCE_REV") == source_rev
        and headers.get("GATE_SHA256") == gate_hash
        and headers.get("RUNNER_SHA256") == runner_hash
        and headers.get("EXIT_CODE") == str(expected_exit)
        and expected_line in stdout.splitlines()
        and stdout.splitlines() == EXPECTED_STDOUT[case]
        and headers.get("COMMAND") == expected_command
        and headers.get("COMMAND_ARGV_JSON")
    )


def lane_path(repo: Path, relative: str) -> Path:
    path = (repo / relative).resolve()
    try:
        path.relative_to(repo.resolve())
    except ValueError as exc:
        raise ReceiptError("output path escapes the lane repo") from exc
    if not relative.startswith(RECEIPT_ROOT + "/"):
        raise ReceiptError(f"output must be beneath {RECEIPT_ROOT}/")
    return path


def capture(repo: Path, source_rev: str, out_arg: str) -> int:
    verify_revision(repo, source_rev)
    out = lane_path(repo, out_arg)
    if out.exists():
        raise ReceiptError(f"refusing to overwrite existing output directory: {out_arg}")
    expected = expected_receipts(repo, source_rev)
    out.mkdir(parents=True)
    complete = 0
    for case, (relative, expected_exit, expected_line) in CASES.items():
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected[case], encoding="utf-8")
        gate_hash = hashlib.sha256(read_blob(repo, source_rev, GATE_PATH)).hexdigest()
        runner_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if output_ok(case, expected[case], expected_exit, expected_line,
                     source_rev, gate_hash, runner_hash):
            complete += 1
        print(
            f"CAPTURE case={case} source_rev={source_rev} "
            f"evaluated_rev={next(line[14:] for line in expected[case].splitlines() if line.startswith('EVALUATED_REV='))} "
            f"exit={expected_exit} path={out_arg}/{relative}"
        )
    met = complete == len(CASES)
    print(f"CAPTURE_COMPLETE={complete}/{len(CASES)} met={'True' if met else 'False'}")
    return 0 if met else 1


def receipt_blob(repo: Path, tip: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{tip}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        return None
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None

def parse_receipt(receipt: str) -> tuple[dict[str, str], str, str] | None:
    try:
        header_text, remainder = receipt.split("STDOUT_BEGIN\n", 1)
        stdout, remainder = remainder.split("STDOUT_END\nSTDERR_BEGIN\n", 1)
        stderr, ending = remainder.rsplit("STDERR_END\n", 1)
    except ValueError:
        return None
    if ending:
        return None
    headers: dict[str, str] = {}
    for line in header_text.splitlines():
        if "=" not in line:
            return None
        key, value = line.split("=", 1)
        if key in headers:
            return None
        headers[key] = value
    return headers, stdout, stderr


def known_runner_hashes(repo: Path, tip: str) -> set[str]:
    revisions = git(repo, "log", "--format=%H", tip, "--", RUNNER_PATH).decode().splitlines()
    return {
        hashlib.sha256(read_blob(repo, revision, RUNNER_PATH)).hexdigest()
        for revision in revisions
    }



def audit(repo: Path, tip: str, source_rev: str, receipt_dir: str) -> int:
    verify_revision(repo, tip)
    verify_revision(repo, source_rev)
    root = lane_path(repo, receipt_dir)
    relative_root = root.relative_to(repo.resolve()).as_posix()
    gate_hash = hashlib.sha256(read_blob(repo, source_rev, GATE_PATH)).hexdigest()
    runner_hashes = known_runner_hashes(repo, tip)

    # Rebuild the exact bounded inputs and re-run the pinned gate as the oracle.
    expected = expected_receipts(repo, source_rev)
    complete = 0
    missing = 0
    invalid = 0
    for case, (relative, expected_exit, expected_line) in CASES.items():
        path = f"{relative_root}/{relative}"
        receipt = receipt_blob(repo, tip, path)
        if receipt is None:
            missing += 1
            continue
        actual = parse_receipt(receipt)
        expected_record = parse_receipt(expected[case])
        if actual is None or expected_record is None:
            invalid += 1
            continue
        headers, stdout, stderr = actual
        expected_headers, expected_stdout, expected_stderr = expected_record
        runner_hash = headers.get("RUNNER_SHA256", "")
        stable_fields = (
            "FORMAT", "FIXTURE", "COMMAND", "SOURCE_REV", "EVALUATED_REV",
            "EVALUATED_TREE", "GATE_SHA256", "EXIT_CODE",
        )
        if (
            runner_hash in runner_hashes
            and all(headers.get(key) == expected_headers.get(key) for key in stable_fields)
            and stdout == expected_stdout
            and stderr == expected_stderr
            and output_ok(case, receipt, expected_exit, expected_line,
                          source_rev, gate_hash, runner_hash)
        ):
            complete += 1
        else:
            invalid += 1
    met = complete == len(CASES) and missing == 0 and invalid == 0
    print(
        f"R33_GATE_RECEIPT_AUDIT source_rev={source_rev} tip={tip} "
        f"complete={complete}/{len(CASES)} missing={missing} invalid={invalid} "
        f"met={'True' if met else 'False'}"
    )
    return 0 if met else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cap = sub.add_parser("capture", help="run the pinned gate and three isolated controls")
    cap.add_argument("--repo", default=".", help="lane Git repository")
    cap.add_argument("--source-rev", required=True, help="full revision supplying the gate code and lane tree")
    cap.add_argument("--out", required=True, help="new output directory beneath .ufo/waves/round-33/c2/")
    check = sub.add_parser("audit", help="re-run and compare the four committed receipts")
    check.add_argument("--repo", default=".", help="lane Git repository")
    check.add_argument("--tip", required=True, help="full revision whose receipts are audited")
    check.add_argument("--source-rev", required=True, help="full revision supplying the gate code and lane tree")
    check.add_argument("--receipt-dir", required=True, help="receipt directory beneath .ufo/waves/round-33/c2/")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    try:
        if args.command == "capture":
            return capture(repo, args.source_rev, args.out)
        return audit(repo, args.tip, args.source_rev, args.receipt_dir)
    except (ReceiptError, OSError, subprocess.SubprocessError) as exc:
        print(f"R33_GATE_RECEIPT_ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
