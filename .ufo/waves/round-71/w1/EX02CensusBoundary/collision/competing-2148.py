#!/usr/bin/env python3
"""census-waiver-boundary.py - round-71 C2 (operability): the census waiver boundary, registered.

Frozen predicate (plans/round-71-claims.md section C2; the same sentence is this tool's
verdict line and the receipt label):

    `python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py` prints
    `BOUNDARY cases=7 killed=5 survivors=0` and exits 0; it exits 1 if any named shim survives,
    if a waiver covers an evaluated failing member (that fixture must exit nonzero), or if the
    landed census bytes are killed by mistake.

The round-70 closure routed defect 4: `controls/refused-member-control.py` was a committed but
unregistered verdict script that reads only the exit pair. The round-70 critic built five census
designs that keep that pair while breaking a fact the freeze names
(`.ufo/waves/round-70/w1/out/CRT01ClaimC2/counterexamples.py`). This tool grades those five
shims against seven boundary checks and keeps the landed census bytes green.

Checks (each runs the census module in-process through `main()`, so its own `sys.argv` waiver
parsing is exercised; MEMBERS is replaced with a two-member synthetic set):

  c1 refusal-accounting   refused fixture exits nonzero AND verdict carries `not_evaluated=1`
  c2 allpass              all-pass fixture exits 0, `not_evaluated=0`, `total=<len(MEMBERS)>`
  c3 waived-ne            `--waive` on the not-evaluated member exits 0 with `waived=1`
  c4 fail-not-waivable    `--waive` on an evaluated failing member exits nonzero, no `waived=1`
  c5 unknown-waiver       an unknown waiver name warns on stderr and does not change the exit
  c6 no-second-call-cache two calls in one process print the same verdict (no silent 0)
  c7 refusal-branch       the refused fixture is not counted as a pass (verdict `pass` < total)

The five named shims and the check that must kill each:
  s4-refusal-as-fail            c1 (refusal counted as fail loses the not_evaluated verdict line)
  s5t-hardcoded-total           c2 (verdict total disagrees with the fixture population)
  s6w-waiver-swallows-failure   c3/c5 (no CLI waiver parsing: the waived member stays unwaived)
  s8r-second-call-silent        c6 (second call returns 0 with no verdict line)
  s10d-refusal-branch-deleted   c1/c7 (refusal branch deleted: the refusal reads as a pass)

Output: one `BOUNDARY_CASE <id> <held|FAIL> <detail>` line per case (the five shim verdicts
carry the shim name), then `BOUNDARY cases=7 killed=<k> survivors=<s>`.
Exit: 0 iff survivors == 0 and the landed census bytes hold all seven cases; 1 otherwise;
2 could-not-evaluate (a missing census file, a shim that will not import, an unreadable dir).

Usage:
    census-waiver-boundary.py [--census PATH] [--shims DIR] [--scratch DIR] [--selftest]

  --census PATH   census module to grade (default: tools/round65-host-census.py under the
                  current directory, then this file's repository root)
  --shims DIR     directory holding the five shim files (default: this repository's
                  .ufo/waves/round-70/w1/out/CRT01ClaimC2/shim set generated into --scratch,
                  using the committed counterexamples.py generator)
  --scratch DIR   scratch root for generated shims and selftest fixtures (default: TMPDIR)
  --selftest      grade the harness itself: landed census green, five shims killed,
                  a missing census path exits 2. Prints `BOUNDARY_SELFTEST pass=<n> fail=0`.

Read-only on the lane; writes only under --scratch (removed unless --keep).
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SHIM_GENERATOR = REPO / ".ufo/waves/round-70/w1/out/CRT01ClaimC2/counterexamples.py"
SHIMS = [
    "s4-refusal-as-fail",
    "s5t-hardcoded-total",
    "s6w-waiver-swallows-failure",
    "s8r-second-call-silent",
    "s10d-refusal-branch-deleted",
]
PASS_MARKER = "RESULT pass=30 fail=0"
REFUSAL_MARKER = "invalid path"
REFUSAL_REASON = "fail-closed refusal: synthetic boundary fixture"
REFUSED_FIXTURE = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-refused",
     ["bash", "-c", f"echo {REFUSAL_MARKER!r}: the lane holds a tracked path NTFS cannot check out"],
     "NEVER-PRINTED", [(REFUSAL_MARKER, REFUSAL_REASON)]),
]
ALLPASS_FIXTURE = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-pass-2", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
]
FAILING_FIXTURE = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-fail", ["bash", "-c", "exit 1"], "NEVER-PRINTED", []),
]
VERDICT_RE = re.compile(
    r"^HOST_CENSUS pass=(\d+) fail=(\d+) not_evaluated=(\d+)(?: waived=(\d+))? total=(\d+)")


class BoundaryError(Exception):
    """Could not evaluate a census module or its fixture."""


def resolve_census(arg: str | None) -> Path:
    if arg:
        path = Path(os.path.expanduser(arg))
        if not path.is_file():
            raise BoundaryError(f"census file not found: {path}")
        return path
    for candidate in (Path("tools/round65-host-census.py"), REPO / "tools/round65-host-census.py"):
        if candidate.is_file():
            return candidate
    raise BoundaryError("no census file found (pass --census PATH)")


def run_twice(path: Path, tag: str, members):
    """Call main() twice on ONE imported module (the second-call-cache probe)."""
    module = load_module(path, tag)
    module.MEMBERS = members
    results = []
    saved = sys.argv
    sys.argv = [str(path)]
    try:
        for _ in range(2):
            buf_out, buf_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                code = module.main()
            lines = [l for l in buf_out.getvalue().splitlines() if l.strip()]
            matches = [VERDICT_RE.match(l) for l in lines]
            matches = [m for m in matches if m]
            verdict = matches[-1] if matches else None
            results.append({
                "exit": int(code),
                "raw_verdict": verdict.string if verdict else "<no verdict line>",
                "ne_n": int(verdict.group(3)) if verdict else -1,
            })
    finally:
        sys.argv = saved
    return results[0], results[1]


def load_module(path: Path, tag: str):
    spec = importlib.util.spec_from_file_location(f"boundary_{tag}", path)
    if spec is None or spec.loader is None:
        raise BoundaryError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - import failure is a typed could-not-evaluate
        raise BoundaryError(f"cannot import {path}: {exc}") from exc
    if not hasattr(module, "main") or not hasattr(module, "MEMBERS"):
        raise BoundaryError(f"{path} has no main()/MEMBERS contract")
    return module


def run_case(path: Path, tag: str, members, argv=()):
    module = load_module(path, tag)
    module.MEMBERS = members
    buf_out, buf_err = io.StringIO(), io.StringIO()
    saved = sys.argv
    sys.argv = [str(path), *argv]
    try:
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            code = module.main()
    finally:
        sys.argv = saved
    lines = [l for l in buf_out.getvalue().splitlines() if l.strip()]
    verdicts = [VERDICT_RE.match(l) for l in lines]
    verdicts = [m for m in verdicts if m]
    verdict = verdicts[-1] if verdicts else None
    return {
        "exit": int(code),
        "lines": lines,
        "stderr": buf_err.getvalue(),
        "verdict": verdict,
        "raw_verdict": verdicts[-1].string if verdicts else "<no verdict line>",
        "pass_n": int(verdict.group(1)) if verdict else -1,
        "fail_n": int(verdict.group(2)) if verdict else -1,
        "ne_n": int(verdict.group(3)) if verdict else -1,
        "waived_n": int(verdict.group(4)) if verdict and verdict.group(4) else 0,
        "total_n": int(verdict.group(5)) if verdict else -1,
        "has_waived_token": "waived=" in (verdicts[-1].string if verdicts else ""),
    }


def check(condition: bool, detail: str) -> tuple[bool, str]:
    return condition, detail


def boundary_checks(path: Path, tag: str):
    """Seven checks over one census module. Returns {id: (held, detail)}."""
    out = {}
    r = run_case(path, tag + "c1", REFUSED_FIXTURE)
    out["c1"] = check(r["exit"] != 0 and r["ne_n"] == 1,
                      f"refused exit={r['exit']} ne={r['ne_n']} verdict={r['raw_verdict']}")
    a = run_case(path, tag + "c2", ALLPASS_FIXTURE)
    out["c2"] = check(a["exit"] == 0 and a["ne_n"] == 0 and a["total_n"] == len(ALLPASS_FIXTURE),
                      f"allpass exit={a['exit']} ne={a['ne_n']} total={a['total_n']} verdict={a['raw_verdict']}")
    w = run_case(path, tag + "c3", REFUSED_FIXTURE, ("--waive", "synthetic-refused"))
    out["c3"] = check(w["exit"] == 0 and w["waived_n"] == 1,
                      f"waived-ne exit={w['exit']} waived={w['waived_n']} verdict={w['raw_verdict']}")
    f = run_case(path, tag + "c4", FAILING_FIXTURE, ("--waive", "synthetic-fail"))
    out["c4"] = check(f["exit"] != 0 and f["waived_n"] == 0,
                      f"fail-waive exit={f['exit']} waived={f['waived_n']} verdict={f['raw_verdict']}")
    u = run_case(path, tag + "c5", ALLPASS_FIXTURE, ("--waive", "no-such-member"))
    out["c5"] = check(u["exit"] == 0 and u["waived_n"] == 0 and "not a census member name" in u["stderr"],
                      f"unknown-waive exit={u['exit']} waived={u['waived_n']} stderr={u['stderr'].strip()[:90]!r}")
    first, second = run_twice(path, tag + "c6", REFUSED_FIXTURE)
    out["c6"] = check(first["raw_verdict"] != "<no verdict line>" and first["raw_verdict"] == second["raw_verdict"]
                      and first["exit"] == second["exit"],
                      f"call1={first['raw_verdict']} call2={second['raw_verdict']}")
    out["c7"] = check(r["pass_n"] < len(REFUSED_FIXTURE),
                      f"refused-fixture pass={r['pass_n']} total={len(REFUSED_FIXTURE)}")
    return out


def real_census_case(path: Path) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True,
                          errors="replace", cwd=str(REPO), env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    verdict = next((l for l in reversed(proc.stdout.splitlines()) if l.startswith("HOST_CENSUS ")), "<no verdict line>")
    m = VERDICT_RE.match(verdict)
    ok = proc.returncode == 0 and m is not None and int(m.group(3)) == 0 and int(m.group(5)) == 22
    return ok, f"real-census exit={proc.returncode} {verdict}"


def build_shims(scratch: Path) -> dict[str, Path]:
    target = scratch / "shims"
    target.mkdir(parents=True, exist_ok=True)
    if not SHIM_GENERATOR.is_file():
        raise BoundaryError(f"shim generator missing: {SHIM_GENERATOR}")
    proc = subprocess.run([sys.executable, str(SHIM_GENERATOR), "--dir", str(target)],
                          capture_output=True, text=True, errors="replace")
    if proc.returncode != 0:
        raise BoundaryError(f"shim generator failed: {proc.stderr.strip()[:300]}")
    paths = {name: target / f"{name}.py" for name in SHIMS}
    missing = [n for n, p in paths.items() if not p.is_file()]
    if missing:
        raise BoundaryError(f"shim generator did not produce: {missing}")
    return paths


def grade(census: Path, shims: dict[str, Path]) -> int:
    solved = boundary_checks(census, "landed")
    base_ok = all(held for held, _ in solved.values())
    for cid in ("c1", "c2", "c3", "c4", "c5", "c6", "c7"):
        held, detail = solved[cid]
        print(f"BOUNDARY_CASE {cid} {'held' if held else 'FAIL'} {detail}")
    if not base_ok:
        print("BOUNDARY_BASE_FAILED the landed census bytes do not hold the seven cases")
    killed = 0
    survivors = 0
    for name, path in shims.items():
        checks = boundary_checks(path, name.replace("-", "_"))
        dead = [cid for cid, (held, _) in checks.items() if not held]
        if dead:
            killed += 1
            reasons = "; ".join(f"{cid}: {checks[cid][1]}" for cid in dead)
            print(f"BOUNDARY_CASE shim-{name} killed {reasons[:400]}")
        else:
            survivors += 1
            print(f"BOUNDARY_CASE shim-{name} FAIL survives all seven cases")
    real_ok, real_detail = real_census_case(census)
    print(f"BOUNDARY_CASE c8 {'held' if real_ok else 'FAIL'} {real_detail}")
    print(f"BOUNDARY cases={len(solved)} killed={killed} survivors={survivors}")
    return 0 if (base_ok and survivors == 0 and real_ok) else 1


def selftest(scratch: Path, keep: bool) -> int:
    work = Path(tempfile.mkdtemp(prefix="boundary-selftest-", dir=str(scratch)))
    arms = []
    try:
        census = resolve_census(None)
        shims = build_shims(work)
        base = boundary_checks(census, "st_base")
        arms.append(("landed-green", all(held for held, _ in base.values())))
        for name in SHIMS:
            checks = boundary_checks(shims[name], "st_" + name.replace("-", "_"))
            arms.append((f"shim-{name}-killed", any(not held for held, _ in checks.values())))
        # a census copy with the exit map gutted must be killed by c1
        gutted = work / "gutted-census.py"
        text = census.read_text()
        if "return 0 if (failed == 0 and not unwaived_ne) else 1" not in text:
            raise BoundaryError("selftest: census exit-map line not found")
        gutted.write_text(text.replace("return 0 if (failed == 0 and not unwaived_ne) else 1", "return 0"))
        g = boundary_checks(gutted, "st_gutted")
        arms.append(("gutted-exit-killed", any(not held for held, _ in g.values())))
        try:
            resolve_census(str(work / "does-not-exist.py"))
            arms.append(("missing-census-errors", False))
        except BoundaryError:
            arms.append(("missing-census-errors", True))
        failed = [name for name, ok in arms if not ok]
        for name, ok in arms:
            print(f"{'PASS' if ok else 'FAIL'} {name}")
        print(f"BOUNDARY_SELFTEST pass={len(arms) - len(failed)} fail={len(failed)}")
        return 0 if not failed else 1
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--census", default=None, help="census module to grade")
    parser.add_argument("--shims", default=None, help="directory holding the five shims")
    parser.add_argument("--scratch", default=None, help="scratch root for fixtures")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--keep", action="store_true")
    opts = parser.parse_args(argv)
    if opts.selftest:
        scratch = Path(opts.scratch) if opts.scratch else Path(tempfile.mkdtemp(prefix="r71-boundary-"))
        scratch.mkdir(parents=True, exist_ok=True)
        try:
            return selftest(scratch, opts.keep)
        except BoundaryError as exc:
            print(f"BOUNDARY_SELFTEST could-not-evaluate: {exc}", file=sys.stderr)
            return 2
    scratch = Path(opts.scratch) if opts.scratch else Path(tempfile.mkdtemp(prefix="r71-boundary-"))
    scratch.mkdir(parents=True, exist_ok=True)
    created = opts.scratch is None
    try:
        census = resolve_census(opts.census)
        if opts.shims:
            shims = {name: Path(opts.shims) / f"{name}.py" for name in SHIMS}
            missing = [n for n, p in shims.items() if not p.is_file()]
            if missing:
                raise BoundaryError(f"shims missing under {opts.shims}: {missing}")
        else:
            shims = build_shims(scratch)
        return grade(census, shims)
    except BoundaryError as exc:
        print(f"BOUNDARY could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    finally:
        if created and not opts.keep:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
