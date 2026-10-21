#!/usr/bin/env python3
"""ExecOldGitRun, step 2 of 2 (round-23 falsify): the committed auditor on the
grid's C01-clean fixture with PATH pointing at official git 2.44.0-1 and
2.45.0-1 (extracted by fetch-old-git.sh; never installed).

- Fixture: grid.c_clean (tests/report-audit/repo-state-grid.py), built with the
  system git exactly as the grid builds it, in a fresh /tmp directory.
- Each auditor run: PATH = only the old bin dir; argv and env as the grid's
  run_case (--lane-repo, --fleet-repo, --json, --rounds 1, --no-errata; env from
  grid.env()).
- Each run is repeated under strace -f -e trace=execve to record which git
  binaries executed; the traced run must match the plain run.
- Fixture tree digest must be unchanged across every run (auditor is read-only).
- Grid harness: repo-state-grid.py --arm current --case C01-clean --json under
  each PATH (fixture builder and auditor both run with that git).
- Controls: system git on the same fixture; /tmp mutant of the committed file
  with only "--no-lazy-fetch" removed from GIT_ISOLATION, run under 2.44.0.

Writes OUT/summary.json and per-run files. Exit 0 iff every gate passes.
"""
from __future__ import annotations

import difflib
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CLONE = Path("/tmp/kama-r23w2/ExecOldGitRun")
AUDIT = CLONE / "tools/report-landing-audit.py"
GRID = CLONE / "tests/report-audit/repo-state-grid.py"
OLD_BIN = {
    "2.44.0": CLONE / "old/2.44.0/usr/bin",
    "2.45.0": CLONE / "old/2.45.0/usr/bin",
}
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/out/ExecOldGitRun")
HEAD = "245a37f69628c2c6bb29bbf17897d8fb5946c857"
FLAG_ON = '"--no-replace-objects", "--no-lazy-fetch",'
FLAG_OFF = '"--no-replace-objects",'
SYSTEM_GIT = "/usr/bin/git"
LINE = re.compile(r"^(\d+)\s+(.*)$")
START = re.compile(r'^execve\("((?:[^"\\]|\\.)*)"')
RESUMED = re.compile(r"^<\.\.\. execve resumed>")
RC = re.compile(r"\)\s*=\s*(-?\d+)")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_digest(root: Path) -> dict:
    rows = []
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            rows.append(f"L {rel} {os.readlink(p)}")
        elif p.is_dir():
            rows.append(f"D {rel}")
        else:
            rows.append(f"F {rel} {sha256(p.read_bytes())}")
    return {"sha256": sha256("\n".join(rows).encode()), "entries": len(rows)}


def load_grid():
    spec = importlib.util.spec_from_file_location("repo_state_grid", GRID)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_execs(trace: Path):
    """(succeeded, failed) program paths from `strace -f -e trace=execve`."""
    pending, ok, failed = {}, [], []
    for raw in trace.read_text(errors="replace").splitlines():
        m = LINE.match(raw)
        if not m:
            continue
        pid, body = m.groups()
        if body.startswith("execve("):
            prog = START.match(body).group(1)
            if body.rstrip().endswith("<unfinished ...>"):
                pending[pid] = prog
                continue
        elif RESUMED.match(body):
            prog = pending.pop(pid)
        else:
            continue
        rc = RC.findall(body)[-1]
        (ok if rc == "0" else failed).append(prog)
    return ok, failed


def identity(grid, path_value: str) -> dict:
    which = shutil.which("git", path=path_value)
    if which is None:
        raise SystemExit(f"no git on PATH={path_value}")
    env = grid.env(PATH=path_value)
    ver = subprocess.run([which, "--version"], capture_output=True, env=env)
    ep = subprocess.run([which, "--exec-path"], capture_output=True, env=env)
    return {"PATH": path_value, "git": which,
            "version": ver.stdout.decode().strip(), "version_rc": ver.returncode,
            "exec_path": ep.stdout.decode().strip(), "exec_path_rc": ep.returncode}


def build_fixture(grid) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="execoldgit-c01-", dir="/tmp"))
    lane, fleet, extra, marker = grid.c_clean(tmp)
    if extra or marker is not None:
        raise SystemExit("unexpected C01 builder output")
    return {"tmp": tmp, "lane": lane, "fleet": fleet}


def audit_argv(auditor: Path, fx: dict) -> list:
    return [sys.executable, str(auditor), "--lane-repo", str(fx["lane"]),
            "--fleet-repo", str(fx["fleet"]), "--json", "--rounds", "1",
            "--no-errata"]


def run_auditor(grid, name, path_value, auditor, fx, expect_git):
    d = OUT / "runs" / name
    d.mkdir(parents=True, exist_ok=True)
    env = grid.env(PATH=path_value)
    argv = audit_argv(auditor, fx)
    cwd = str(fx["tmp"])
    before = tree_digest(fx["tmp"])
    plain = subprocess.run(argv, capture_output=True, env=env, cwd=cwd, timeout=120)
    mid = tree_digest(fx["tmp"])
    trace = d / "execve-trace.txt"
    traced = subprocess.run(["/usr/bin/strace", "-f", "-qq", "-e", "trace=execve",
                             "-s", "200", "-o", str(trace), *argv],
                            capture_output=True, env=env, cwd=cwd, timeout=120)
    after = tree_digest(fx["tmp"])
    ok, _failed = parse_execs(trace)
    git_ok = sorted({p for p in ok if Path(p).name == "git"})
    (d / "argv.txt").write_text(shlex.join(argv) + "\n")
    (d / "PATH.txt").write_text(path_value + "\n")
    (d / "stdout.txt").write_bytes(plain.stdout)
    (d / "stderr.txt").write_bytes(plain.stderr)
    (d / "exit.txt").write_text(f"{plain.returncode}\n")
    (d / "traced-exit.txt").write_text(f"{traced.returncode}\n")
    return {
        "name": name,
        "exit": plain.returncode,
        "stdout": plain.stdout.decode(errors="replace"),
        "stderr": plain.stderr.decode(errors="replace"),
        "traced_exit": traced.returncode,
        "traced_matches_plain": (traced.stdout == plain.stdout
                                 and traced.stderr == plain.stderr),
        "git_exec_paths": git_ok,
        "git_exec_expected": expect_git,
        "git_exec_only_expected": bool(git_ok) and all(p == expect_git for p in git_ok),
        "tree_stable": before == mid == after,
        "tree": before,
    }


def run_grid(name, path_value):
    d = OUT / "grid-harness" / name
    d.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PATH=path_value)
    p = subprocess.run([sys.executable, str(GRID), "--arm", "current",
                        "--case", "C01-clean", "--json"],
                       capture_output=True, env=env, timeout=600)
    (d / "stdout.json").write_bytes(p.stdout)
    (d / "stderr.txt").write_bytes(p.stderr)
    (d / "exit.txt").write_text(f"{p.returncode}\n")
    row = None
    try:
        row = json.loads(p.stdout)["arms"]["current"]["rows"][0]
    except (ValueError, KeyError, IndexError, TypeError):
        pass
    return {"name": name, "exit": p.returncode, "row": row,
            "stderr": p.stderr.decode(errors="replace")}


def make_mutant() -> Path:
    src = AUDIT.read_text(encoding="utf-8")
    if src.count(FLAG_ON) != 1:
        raise SystemExit(f"expected one flag pair, found {src.count(FLAG_ON)}")
    text = src.replace(FLAG_ON, FLAG_OFF, 1)
    mdir = OUT / "mutant"
    mdir.mkdir(parents=True, exist_ok=True)
    dst = mdir / "report-landing-audit.no-lazy-fetch-flag-removed.py"
    dst.write_text(text, encoding="utf-8")
    diff = difflib.unified_diff(
        src.splitlines(keepends=True), text.splitlines(keepends=True),
        fromfile="tools/report-landing-audit.py@245a37f6",
        tofile="mutant/report-landing-audit.no-lazy-fetch-flag-removed.py")
    (mdir / "diff.txt").write_text("".join(diff), encoding="utf-8")
    return dst


def doc_of(stdout: str):
    try:
        return json.loads(stdout)
    except ValueError:
        return None


def defects(doc):
    return sum(len(r["defects"]) for r in doc["results"]) if doc else None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    grid = load_grid()
    clean_env = grid.env()
    head = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "HEAD"],
                          capture_output=True, text=True, env=clean_env).stdout.strip()
    blob = subprocess.run(["git", "-C", str(CLONE), "rev-parse",
                           "HEAD:tools/report-landing-audit.py"],
                          capture_output=True, text=True, env=clean_env).stdout.strip()
    provenance = {
        "clone_head": head, "expected_head": HEAD, "auditor_blob": blob,
        "auditor_file_sha256": sha256(AUDIT.read_bytes()),
        "grid_file_sha256": sha256(GRID.read_bytes()),
    }
    fx = build_fixture(grid)
    provenance["fixture_dir"] = str(fx["tmp"])
    provenance["fixture_lane_head"] = grid.g(fx["lane"], "rev-parse", "HEAD")
    provenance["fixture_fleet_head"] = grid.g(fx["fleet"], "rev-parse", "HEAD")
    mutant = make_mutant()
    system_path = os.environ.get("PATH", "")
    old44, old45 = str(OLD_BIN["2.44.0"]), str(OLD_BIN["2.45.0"])
    plan = [
        ("system-git-control", system_path, AUDIT, SYSTEM_GIT),
        ("git-2.44.0-1", old44, AUDIT, f"{old44}/git"),
        ("git-2.45.0-1", old45, AUDIT, f"{old45}/git"),
        ("mutant-git-2.44.0-1-flag-removed", old44, mutant, f"{old44}/git"),
    ]
    runs = {}
    for name, path_value, auditor, expect in plan:
        r = run_auditor(grid, name, path_value, auditor, fx, expect)
        r["identity"] = identity(grid, path_value)
        runs[name] = r
    grids = {
        "system-git-control": run_grid("system-git-control", system_path),
        "git-2.44.0-1": run_grid("git-2.44.0-1", old44),
        "git-2.45.0-1": run_grid("git-2.45.0-1", old45),
    }

    g44, g45 = runs["git-2.44.0-1"], runs["git-2.45.0-1"]
    gs, mu = runs["system-git-control"], runs["mutant-git-2.44.0-1-flag-removed"]
    d45, ds = doc_of(g45["stdout"]), doc_of(gs["stdout"])
    row = {k: (grids[k]["row"] or {}) for k in grids}
    gates = {
        "git-2.44.0-1: exit 2": g44["exit"] == 2,
        "git-2.44.0-1: stderr is could-not-evaluate naming --no-lazy-fetch":
            g44["stderr"].startswith("could-not-evaluate:")
            and "--no-lazy-fetch" in g44["stderr"],
        "git-2.44.0-1: no traceback, empty stdout":
            "Traceback" not in g44["stderr"] and g44["stdout"] == "",
        "git-2.45.0-1: exit 0": g45["exit"] == 0,
        "git-2.45.0-1: json, zero defects, empty stderr":
            defects(d45) == 0 and g45["stderr"] == "",
        "system-git-control: exit 0, zero defects": gs["exit"] == 0 and defects(ds) == 0,
        "traced runs match plain runs": all(
            r["traced_exit"] == r["exit"] and r["traced_matches_plain"]
            for r in runs.values()),
        "every git exec is the PATH-selected binary": all(
            r["git_exec_only_expected"] for r in runs.values()),
        "fixture tree unchanged by every run": all(
            r["tree_stable"] for r in runs.values()),
        "grid C01 row: 2.44 exit 2 and not met": row["git-2.44.0-1"].get("exit") == 2
            and row["git-2.44.0-1"].get("met") is False,
        "grid C01 row: 2.45 met": row["git-2.45.0-1"].get("met") is True,
        "grid C01 row: system met": row["system-git-control"].get("met") is True,
    }
    info = {"mutant_exit": mu["exit"], "mutant_defects": defects(doc_of(mu["stdout"])),
            "mutant_stderr_head": mu["stderr"][:300]}
    summary = {
        "provenance": provenance,
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "mutant_informational": info,
        "runs": runs,
        "grid_harness": grids,
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for name, ok in gates.items():
        print(("PASS " if ok else "FAIL ") + name)
    print("--- git-2.44.0-1 stderr ---")
    print(g44["stderr"].rstrip())
    print("--- mutant (informational) ---")
    print(json.dumps(info, indent=1))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
