#!/usr/bin/env python3
"""Independent replay of the four round-33 gate-receipt cases.

Rebuilds each documented V1 fixture from its raw inputs (it does not import
tools/round33-gate-receipts.py), runs the pinned r32 gate once per case as its
own process, and compares the measured exit code, stdout and stderr byte for
byte against the captured receipts.

Inputs are hardcoded to the isolated run directory used for this wave:
  /tmp/kama-r33-execgate-replay/lane   (disposable clone of the lane)
  /tmp/kama-r33-execgate-replay/lane/.ufo/waves/round-33/c2/execgate-replay-1
Output:
  /tmp/kama-r33-execgate-replay/verify/independent-results.json
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
REPLAY = Path("/tmp/kama-r33-execgate-replay")
CLONE = REPLAY / "lane"
SRC = "967d88528c1d83535563f971863f7855f76b4849"
OUT = REPLAY / "verify"
HEADER = (
    "| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |\n"
    "|---|---|---|---|---|\n"
)
COUNTER = ".ufo/waves/round-33/count-fixture.py"
ROWS = {
    "thin-row": f"| {COUNTER} | | | | |\n",
    "empty-exit-map": f"| {COUNTER} | python3 |   | fixed fixture values | no repository writes |\n",
    "missing-path": f"| {COUNTER} | .ufo/waves/round-999/count-c999.py | 0 clean; 1 rejected | fixed fixture values | no repository writes |\n",
}
CASES = {
    "gate-tip": (0, "gate-tip-r33.out"),
    "thin-row": (1, "controls/thin-row-r33.out"),
    "empty-exit-map": (1, "controls/empty-exit-map-r33.out"),
    "missing-path": (1, "controls/missing-path-r33.out"),
}


def run(argv, cwd=None, env=None):
    p = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, check=False)
    return p.returncode, p.stdout, p.stderr


def parse(receipt):
    head, rest = receipt.split("STDOUT_BEGIN\n", 1)
    stdout, rest = rest.split("STDOUT_END\nSTDERR_BEGIN\n", 1)
    stderr, end = rest.rsplit("STDERR_END\n", 1)
    assert end == "", repr(end)
    return dict(line.split("=", 1) for line in head.splitlines()), stdout, stderr


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    base = CLONE / ".ufo/waves/round-33/c2/execgate-replay-1"
    gate_bytes = run(["git", "-C", str(LANE), "show",
                      f"{SRC}:tools/gate-registry-check.py"])[1]
    gate_hash = hashlib.sha256(gate_bytes).hexdigest()
    genv = os.environ.copy()
    genv.update({
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "kama-round-33-control",
        "GIT_AUTHOR_EMAIL": "kama-round-33-control@shokunin.local",
        "GIT_COMMITTER_NAME": "kama-round-33-control",
        "GIT_COMMITTER_EMAIL": "kama-round-33-control@shokunin.local",
        "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
        "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
    })

    results = {}
    gt = OUT / "gate-tip"
    gt.mkdir()
    (gt / "gate-registry-check.py").write_bytes(gate_bytes)
    rc, stdout, stderr = run(
        [sys.executable, str(gt / "gate-registry-check.py"),
         "--repo", str(CLONE), "--rev", SRC], cwd=CLONE)
    results["gate-tip"] = {
        "rc": rc, "stdout": stdout.decode(), "stderr": stderr.decode(),
        "evaluated_rev": SRC,
        "tree": run(["git", "-C", str(CLONE), "rev-parse",
                     f"{SRC}^{{tree}}"])[1].decode().strip(),
    }

    for kind in ("thin-row", "empty-exit-map", "missing-path"):
        root = OUT / f"fixture-{kind}"
        root.mkdir()
        (root / "tools").mkdir()
        (root / COUNTER).parent.mkdir(parents=True)
        (root / COUNTER).write_text("# deterministic registry fixture counter\n")
        (root / "tools/gate-registry-check.py").write_bytes(gate_bytes)
        (root / "SKILL.md").write_text(HEADER + ROWS[kind])
        run(["git", "-C", str(root), "init", "-q"], env=genv)
        run(["git", "-C", str(root), "add", "-A"], env=genv)
        run(["git", "-C", str(root), "-c", "core.autocrlf=false",
             "-c", "commit.gpgsign=false", "commit", "-qm",
             f"round-33 {kind} control"], env=genv)
        rev = run(["git", "-C", str(root), "rev-parse", "HEAD"])[1].decode().strip()
        tree = run(["git", "-C", str(root), "rev-parse",
                    f"{rev}^{{tree}}"])[1].decode().strip()
        rc, stdout, stderr = run(
            [sys.executable, str(root / "tools/gate-registry-check.py"),
             "--repo", str(root), "--rev", rev], cwd=root)
        results[kind] = {"rc": rc, "stdout": stdout.decode(),
                         "stderr": stderr.decode(), "evaluated_rev": rev,
                         "tree": tree}

    summary = []
    for case, (expected_exit, relative) in CASES.items():
        headers, rso, rse = parse((base / relative).read_text())
        got = results[case]
        checks = {
            "source_rev": headers.get("SOURCE_REV") == SRC,
            "evaluated_rev": headers.get("EVALUATED_REV") == got["evaluated_rev"],
            "evaluated_tree": headers.get("EVALUATED_TREE") == got["tree"],
            "gate_sha256": headers.get("GATE_SHA256") == gate_hash,
            "exit_numeric": bool(re.fullmatch(r"[0-9]+", headers.get("EXIT_CODE", ""))),
            "exit_matches_expected": headers.get("EXIT_CODE") == str(expected_exit) == str(got["rc"]),
            "stdout_byte_exact": rso == got["stdout"],
            "stderr_byte_exact": rse == got["stderr"],
            "argv_isolated": all("/tmp/" in a for a in json.loads(headers["COMMAND_ARGV_JSON"])[1:2]),
            "format_v1": headers.get("FORMAT") == "KAMA_GATE_RECEIPT_V1",
        }
        summary.append({"case": case, "receipt": relative, "headers": headers,
                        "measured": got, "checks": checks,
                        "all": all(checks.values())})
    (OUT / "independent-results.json").write_text(json.dumps(summary, indent=2) + "\n")
    for row in summary:
        print(row["case"], "ALL=" + str(row["all"]),
              "exit=" + row["headers"]["EXIT_CODE"], row["checks"])
    return 0 if all(row["all"] for row in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
