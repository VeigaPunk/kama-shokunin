#!/usr/bin/env python3
"""Round-23 ExecLocaleArms probe (scratch; not part of the repo).

Runs every fixture of tests/report-audit/repo-state-grid.py (its CASES table)
through the auditor in JSON mode, exactly as the grid does, and in text mode,
which the grid never runs, under each locale variant.

Fixtures are built once by the grid's own builders under this process's env
(the baseline). Only the auditor's environment varies per cell. Each fixture
is processed by one thread so its exec marker is not shared across variants.

Usage: probe-grid-text-mode.py GRID_PY OUT_JSON
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GRID_PY, OUT = Path(sys.argv[1]), Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("grid", GRID_PY)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)
AUDIT = grid.LANE_DIR / grid.AUDIT

# name -> (variables set, variables removed), applied to the probe's own env
VARIANTS = {
    "baseline": ({}, ("LC_ALL", "PYTHONIOENCODING")),
    "LC_ALL=C": ({"LC_ALL": "C"}, ("PYTHONIOENCODING",)),
    "LANG=C.UTF-8": ({"LANG": "C.UTF-8"}, ("LC_ALL", "PYTHONIOENCODING")),
    "PYTHONIOENCODING=ascii": ({"PYTHONIOENCODING": "ascii"}, ("LC_ALL",)),
    "LC_ALL=C+PYTHONIOENCODING=ascii": ({"LC_ALL": "C", "PYTHONIOENCODING": "ascii"}, ()),
    "LANG=C.UTF-8+PYTHONIOENCODING=ascii": ({"LANG": "C.UTF-8", "PYTHONIOENCODING": "ascii"}, ("LC_ALL",)),
    "strict-C LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0": (
        {"LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"},
        ("LANG", "PYTHONIOENCODING")),
}


def auditor_env(sets, drops):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for k in drops:
        env.pop(k, None)
    env.update(sets)
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return env


def argv_for(extra, lane, fleet, text_mode):
    # mirrors grid.run_case argv construction; --json only in JSON mode
    rounds = [e[7:] for e in extra if e.startswith("rounds=")]
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet)]
    if not text_mode:
        argv.append("--json")
    argv += ["--rounds", rounds[0] if rounds else
             ("1-" if "open-range" in extra else "1")]
    if "errata" not in extra:
        argv.append("--no-errata")
    return argv


def kinds_of(stdout):
    try:
        doc = json.loads(stdout)
        return sorted({d["kind"] for r in doc["results"] for d in r["defects"]})
    except (ValueError, KeyError, TypeError):
        return "unparseable"


def run_fixture(fx):
    cells = []
    marker = fx["marker"]
    for vname, (sets, drops) in VARIANTS.items():
        for text_mode in (True, False):
            if marker is not None and marker.exists():
                marker.unlink()
            try:
                p = subprocess.run(argv_for(fx["extra"], fx["lane"], fx["fleet"], text_mode),
                                   capture_output=True, timeout=30,
                                   env=auditor_env(sets, drops), cwd=str(fx["tmp"]))
                rc, out, err, timed_out = p.returncode, p.stdout, p.stderr, False
            except subprocess.TimeoutExpired as exc:
                rc, out, err, timed_out = None, exc.stdout or b"", exc.stderr or b"", True
            executed = bool(marker is not None and marker.exists())
            if marker is not None and marker.exists():
                marker.unlink()
            cells.append({
                "case": fx["name"], "kind": fx["kind"], "variant": vname,
                "mode": "text" if text_mode else "json", "expected_exit": fx["want_exit"],
                "rc": rc, "traceback": b"Traceback (most recent call last)" in err,
                "executed": executed, "timed_out": timed_out,
                "kinds": None if text_mode else kinds_of(out),
                "stdout": out.decode("utf-8", errors="replace").strip()[:600],
                "stderr": err.decode("utf-8", errors="replace").strip()[:400],
            })
    return cells


def main():
    root = Path(tempfile.mkdtemp(prefix="kama-r23-grid-text-", dir="/tmp"))
    fixtures, build_errors = [], []
    for i, (name, kind, build, want_exit, _want_kinds) in enumerate(grid.CASES):
        tmp = Path(root, f"{i:02d}")
        tmp.mkdir()
        try:
            lane, fleet, extra, marker = build(tmp)
        except Exception as exc:  # recorded, never silently skipped
            build_errors.append({"case": name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        fixtures.append({"name": name, "kind": kind, "lane": lane, "fleet": fleet,
                         "extra": extra, "marker": marker, "tmp": tmp,
                         "want_exit": want_exit})
    with ThreadPoolExecutor(max_workers=4) as ex:
        cells = [c for group in ex.map(run_fixture, fixtures) for c in group]
    doc = {"fixture_root": str(root), "grid": str(GRID_PY), "auditor": str(AUDIT),
           "fixtures_built": len(fixtures), "build_errors": build_errors, "cells": cells}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print("fixtures_built", len(fixtures), "build_errors", len(build_errors),
          "cells", len(cells), "root", root.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
