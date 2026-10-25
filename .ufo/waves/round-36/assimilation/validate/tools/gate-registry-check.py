#!/usr/bin/env python3
"""gate-registry-check.py -- instrument-registry gate: occurrence + meaning.

Every tracked round counter is a lane instrument; an instrument that SKILL.md
never names cannot be graded, re-run or retired by a reader. Round 32 repairs
the round-28 occurrence-only gate (routed by the round-31 closure: a thin row
with empty cells, a row with an empty exit map, and a row citing a
nonexistent path all flipped the gate to exit 0).

Contract:
    - Population: every tracked path matching ``.ufo/waves/round-*/count-*.py``
      (one directory level below ``.ufo/waves/``, extension ``.py``) or
      ``tools/round<N>-*.py`` (a round-scoped counter kept in ``tools/``).
      Round 34 widens the rule: the round-33 counters live in ``tools/`` and
      were invisible to this gate (routed defect of the round-33 closure).
    - Registry: the ``| Name | Kind / entry command | Exit map |
      Self-test / pinned values | Write scope |`` tables in SKILL.md at the
      evaluated revision. A path is ``registered`` iff it occurs in a cell of
      a row of such a table. A prose mention (a wave-artifact paragraph, a
      lesson pointer) does not register; that weaker class is reported
      ``unregistered`` even though the raw text occurs.
    - Meaning, graded per registered row (defects; a row with a defect is
      still registered, so a defective row does not also read unregistered):
        * ``thin-row``        fewer than two non-empty cells;
        * ``empty-entry``     the Kind / entry command cell is empty;
        * ``empty-exit-map``  the Exit map cell is empty;
        * ``missing-path:PATH`` a repo-relative path token (containing at
          least one slash) in the entry / self-test / write-scope cells does
          not exist at the evaluated revision. The counter's own path is
          exempt; ``<placeholder>`` and bare-filename tokens are not paths.

Output lines:
    unregistered <path>              (sorted; prose-only occurrences land here)
    defective <path>: <reason>       (sorted; one line per defect)
    registered R unregistered U defective D

Exit codes:
    0  U == 0 and D == 0
    1  U > 0 or D > 0
    2  could not evaluate (not a git repo, bad revision, missing SKILL.md,
       git failure/timeout)

Read-only: the tool issues only ``git rev-parse``, ``git ls-tree``,
``git ls-files``, ``git show`` and ``git cat-file -e``; it never writes to
the repository. ``--selftest`` builds sandbox fixtures under a temporary
directory (hermetic arms 1-5) and then evaluates this lane's own tree at its
branch tip (arm 6); it writes nothing inside any repository.

Usage:
    gate-registry-check.py [--repo DIR] [--rev REV] [--selftest]

    --repo DIR   Repository to evaluate (default: current directory).
    --rev REV    Git revision whose tree and SKILL.md are evaluated.
                 Default: the working tree (tracked files from the index,
                 SKILL.md from the filesystem).
    --selftest   Run the fixture matrix; print ``GATE_SELFTEST pass=N fail=M``
                 and exit 0 only if every arm holds and the lane arm is clean.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

COUNTER_RE = re.compile(
    r"^(?:\.ufo/waves/round-[^/]+/count-[^/]+|tools/round[0-9]+-[A-Za-z0-9._-]+)\.py$"
)
SKILL_PATH = "SKILL.md"
RE_PATH = re.compile(
    r"(?<![\w./~:<])((?:[\w.-]+/)+[\w.-]+\."
    r"(?:md|py|sh|json|jsonl|tsv|txt|out|conf|cpp|hpp|h|yml|yaml|toml|err|log|gguf|so))"
    r"(?![\w])"
)

EXIT_CLEAN = 0
EXIT_UNREGISTERED = 1
EXIT_ERROR = 2

GIT_TIMEOUT = 30


def run_git(root: str, args: list[str]) -> tuple[int, bytes, str]:
    try:
        p = subprocess.run(
            ["git", "-C", root, *args],
            capture_output=True,
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, b"", str(e)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace").strip()


def git_root(repo: str) -> tuple[str | None, str]:
    rc, out, err = run_git(repo, ["rev-parse", "--show-toplevel"])
    if rc != 0:
        return None, f"not a git working tree at {repo!r}: {err or f'rc={rc}'}"
    root = out.decode("utf-8", "surrogateescape").strip()
    if not root:
        return None, f"empty repository root for {repo!r}"
    return root, ""


def tracked_counters(root: str, rev: str | None) -> tuple[list[str] | None, str]:
    if rev is None:
        rc, out, err = run_git(root, ["ls-files", "-z"])
    else:
        rc, out, err = run_git(root, ["ls-tree", "-r", "-z", "--name-only", "--full-tree", rev])
    if rc != 0:
        what = "git ls-files" if rev is None else f"git ls-tree {rev}"
        return None, f"{what} failed: {err or f'rc={rc}'}"
    paths = [
        p.decode("utf-8", "surrogateescape")
        for p in out.split(b"\0")
        if p
    ]
    return sorted(p for p in paths if COUNTER_RE.match(p)), ""


def skill_text(root: str, rev: str | None) -> tuple[str | None, str]:
    if rev is None:
        path = Path(root) / SKILL_PATH
        try:
            return path.read_text(encoding="utf-8", errors="surrogateescape"), ""
        except OSError as e:
            return None, f"cannot read {path}: {e}"
    rc, out, err = run_git(root, ["show", f"{rev}:{SKILL_PATH}"])
    if rc != 0:
        return None, f"git show {rev}:{SKILL_PATH} failed: {err or f'rc={rc}'}"
    return out.decode("utf-8", "surrogateescape"), ""


def path_exists(root: str, rev: str | None, path: str) -> bool:
    if rev is None:
        return (Path(root) / path).exists()
    rc, _, _ = run_git(root, ["cat-file", "-e", f"{rev}:{path}"])
    return rc == 0


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def registry_rows(text: str) -> list[list[str]]:
    """Rows of every five-column registry-format table in SKILL.md."""
    lines = text.split("\n")
    rows: list[list[str]] = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].lstrip().startswith("|"):
            j = i
            block = []
            while j < n and lines[j].lstrip().startswith("|"):
                block.append(lines[j])
                j += 1
            if len(block) >= 2:
                hdr = cells(block[0])
                sep = cells(block[1])
                if (len(hdr) == 5
                        and all(set(s) <= set(":- ") for s in sep)
                        and hdr[0].lower() == "name"
                        and ("kind" in hdr[1].lower() or "entry" in hdr[1].lower())
                        and "exit" in hdr[2].lower()
                        and ("self-test" in hdr[3].lower() or "selftest" in hdr[3].lower())
                        and "write" in hdr[4].lower()):
                    for ln in block[2:]:
                        cs = cells(ln)
                        if any(cs):
                            rows.append(cs)
            i = j
            continue
        i += 1
    return rows


def evaluate(repo: str, rev: str | None) -> tuple[int, list[str], str]:
    root, err = git_root(repo)
    if root is None:
        return EXIT_ERROR, [], err
    counters, err = tracked_counters(root, rev)
    if counters is None:
        return EXIT_ERROR, [], err
    text, err = skill_text(root, rev)
    if text is None:
        return EXIT_ERROR, [], err

    rows = registry_rows(text)
    unregistered: list[str] = []
    defective: list[str] = []
    for path in counters:
        matched = [r for r in rows if any(path in c for c in r)]
        if not matched:
            unregistered.append(path)
            continue
        for row in matched:
            nonempty = [c for c in row if c]
            reasons: list[str] = []
            if len(nonempty) < 2:
                reasons.append("thin-row")
            if not row[1]:
                reasons.append("empty-entry")
            if not row[2]:
                reasons.append("empty-exit-map")
            cited = set()
            for c in (row[1], row[3], row[4]):
                for tok in RE_PATH.findall(c or ""):
                    if tok == path or tok.startswith("/") or tok.startswith("~"):
                        continue
                    cited.add(tok)
            for tok in sorted(cited):
                if not path_exists(root, rev, tok):
                    reasons.append(f"missing-path:{tok}")
            for r in reasons:
                defective.append(f"{path}: {r}")

    lines = [f"unregistered {p}" for p in unregistered]
    lines += [f"defective {d}" for d in defective]
    lines.append(
        f"registered {len(counters) - len(unregistered)} "
        f"unregistered {len(unregistered)} defective {len(defective)}"
    )
    bad = bool(unregistered or defective)
    return (EXIT_UNREGISTERED if bad else EXIT_CLEAN), lines, ""


REGISTRY_HEADER = (
    "| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |\n"
    "|---|---|---|---|---|\n"
)


def sandbox_fixture(tmp: str, name: str, skill_body: str, counter: str = ".ufo/waves/round-98/count-selftest.py") -> str:
    repo = os.path.join(tmp, name)
    os.makedirs(os.path.join(repo, os.path.dirname(counter)), exist_ok=True)
    Path(os.path.join(repo, counter)).write_text("# fixture counter\n")
    Path(os.path.join(repo, "tools")).mkdir(exist_ok=True)
    Path(os.path.join(repo, "tools/real-tool.py")).write_text("# real\n")
    Path(os.path.join(repo, SKILL_PATH)).write_text(skill_body)
    run_git(repo, ["init", "-q"])
    run_git(repo, ["add", "-A"])
    p = subprocess.run(
        ["git", "-C", repo, "-c", "user.name=gate-selftest",
         "-c", "user.email=gate-selftest@local", "commit", "-qm", name],
        capture_output=True, timeout=GIT_TIMEOUT,
    )
    if p.returncode != 0:
        raise RuntimeError(f"sandbox commit failed: {p.stderr.decode()[:200]}")
    rc, out, _ = run_git(repo, ["rev-parse", "HEAD"])
    return out.decode().strip()


def selftest() -> int:
    passed = 0
    failed = 0
    arms = []

    def arm(label: str, want_code: int, want_line: str, repo: str, rev: str | None):
        nonlocal passed, failed
        code, lines, err = evaluate(repo, rev)
        summary = lines[-1] if lines else f"ERROR {err}"
        hit = want_line in lines
        ok = code == want_code and hit
        if ok:
            passed += 1
        else:
            failed += 1
        arms.append(
            f"{'PASS' if ok else 'FAIL'} {label}: exit={code} "
            f"(want {want_code}) line={summary!r} want-line={want_line!r}"
        )

    with tempfile.TemporaryDirectory(prefix="gate-selftest-") as tmp:
        counter = ".ufo/waves/round-98/count-selftest.py"
        valid_body = (
            REGISTRY_HEADER
            + f"| selftest counter | measurement: `python3 {counter} --out r.json` "
              "| 0 ran; 2 could not evaluate | pins `.ufo/waves/round-98/preregistration.json` "
              "(see lesson); receipt `tools/real-tool.py` | read-only git |\n"
        )
        prereg = sandbox_fixture(tmp, "valid", valid_body)
        Path(os.path.join(tmp, "valid", ".ufo/waves/round-98/preregistration.json")).write_text("{}")
        run_git(os.path.join(tmp, "valid"), ["add", "-A"])
        subprocess.run(["git", "-C", os.path.join(tmp, "valid"), "-c", "user.name=g",
                        "-c", "user.email=g@l", "commit", "-qm", "prereg"],
                       capture_output=True, timeout=GIT_TIMEOUT)
        rc, out, _ = run_git(os.path.join(tmp, "valid"), ["rev-parse", "HEAD"])
        valid_tip = out.decode().strip()
        arm("valid-row", EXIT_CLEAN, "registered 1 unregistered 0 defective 0",
            os.path.join(tmp, "valid"), valid_tip)

        thin_body = REGISTRY_HEADER + f"| {counter} | | | | |\n"
        thin_tip = sandbox_fixture(tmp, "thin", thin_body)
        arm("thin-row", EXIT_UNREGISTERED,
            f"defective {counter}: thin-row", os.path.join(tmp, "thin"), thin_tip)

        noexit_body = (
            REGISTRY_HEADER
            + f"| selftest counter | measurement: `python3 {counter}` |  "
              "| pins `.ufo/waves/round-98/preregistration.json` | read-only git |\n"
        )
        Path(os.path.join(tmp, "noexit", ".ufo/waves/round-98/preregistration.json")).parent.mkdir(
            parents=True, exist_ok=True)
        noexit_tip = sandbox_fixture(tmp, "noexit", noexit_body)
        Path(os.path.join(tmp, "noexit", ".ufo/waves/round-98/preregistration.json")).write_text("{}")
        arm("empty-exit-map", EXIT_UNREGISTERED,
            f"defective {counter}: empty-exit-map", os.path.join(tmp, "noexit"), None)

        badpath_body = (
            REGISTRY_HEADER
            + f"| {counter} | .ufo/waves/round-999/count-c999.py "
              "| 0 ran; 2 could not evaluate | pins `.ufo/waves/round-98/preregistration.json` "
              "| read-only git |\n"
        )
        badpath_tip = sandbox_fixture(tmp, "badpath", badpath_body)
        Path(os.path.join(tmp, "badpath", ".ufo/waves/round-98/preregistration.json")).write_text("{}")
        arm("missing-path", EXIT_UNREGISTERED,
            f"defective {counter}: missing-path:.ufo/waves/round-999/count-c999.py",
            os.path.join(tmp, "badpath"), None)

        prose_body = (
            "Wave artifacts mention the counter in prose only: "
            f"`{counter}` is not a registry row here.\n"
        )
        prose_tip = sandbox_fixture(tmp, "prose", prose_body)
        arm("prose-only", EXIT_UNREGISTERED, f"unregistered {counter}",
            os.path.join(tmp, "prose"), prose_tip)

    # Arm 6: this lane's own tree at its branch tip.
    lane_root = Path(__file__).resolve().parent.parent
    rc, out, err = run_git(str(lane_root), ["rev-parse", "--verify", "master"])
    if rc != 0:
        failed += 1
        arms.append(f"FAIL lane-tip: cannot resolve master: {err}")
    else:
        tip = out.decode().strip()
        code, lines, lerr = evaluate(str(lane_root), tip)
        summary = lines[-1] if lines else f"ERROR {lerr}"
        ok = code == EXIT_CLEAN
        if ok:
            passed += 1
        else:
            failed += 1
        arms.append(
            f"{'PASS' if ok else 'FAIL'} lane-tip {tip[:12]}: exit={code} line={summary!r}"
        )

    for a in arms:
        print(a)
    print(f"GATE_SELFTEST pass={passed} fail={failed}")
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Report tracked round counters whose SKILL.md registry rows are absent or meaningless.",
    )
    ap.add_argument("--repo", default=".", help="repository to evaluate (default: current directory)")
    ap.add_argument(
        "--rev",
        default=None,
        help="git revision to evaluate (default: the working tree)",
    )
    ap.add_argument("--selftest", action="store_true",
                    help="run the fail-capable fixture matrix and the lane-tip check")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    code, lines, err = evaluate(args.repo, args.rev)
    if code == EXIT_ERROR:
        print(f"ERROR could not evaluate: {err}", file=sys.stderr)
        return EXIT_ERROR
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
