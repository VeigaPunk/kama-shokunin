#!/usr/bin/env python3
"""Containment proof for case C-WT1.

Runs the fixture builder and then shows that nothing escaped the scratch
root: no fixture directory in the lane repository, no new file in the lane
repository working tree, no new file under /tmp, and every path the builder
reported lives under the scratch root.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

REPO = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseWrongTypeCitation")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "build/out/CaseWrongTypeCitation")
BUILDER = OUT / "build_case.py"


def run(*args, cwd=None):
    return subprocess.run(list(args), capture_output=True, cwd=cwd)


def status():
    p = run("git", "-C", str(REPO), "status", "--porcelain=v1",
            "--untracked-files=normal")
    return p.stdout.decode()


def tmp_snapshot():
    out = {}
    for base in ("/tmp", "/var/tmp"):
        b = Path(base)
        if not b.is_dir():
            continue
        for entry in sorted(b.iterdir()):
            try:
                out[str(entry)] = entry.stat().st_mtime
            except OSError:
                pass
    return out


def main():
    before_status = status()
    before_tmp = tmp_snapshot()
    before_head = run("git", "-C", str(REPO), "rev-parse", "HEAD").stdout.decode().strip()
    t0 = time.time()
    proc = run(sys.executable, str(BUILDER), "--out", str(OUT / "results"))
    t1 = time.time()
    after_status = status()
    after_tmp = tmp_snapshot()
    after_head = run("git", "-C", str(REPO), "rev-parse", "HEAD").stdout.decode().strip()

    new_tmp = sorted(k for k, v in after_tmp.items()
                      if k not in before_tmp or v > before_tmp[k])
    # files created under /tmp during the run window
    in_window = []
    for path in new_tmp:
        try:
            if Path(path).stat().st_mtime >= t0 - 1:
                in_window.append(path)
        except OSError:
            pass

    results = json.loads((OUT / "results" / "results.json").read_text())
    root = Path(results["root"]).resolve()
    inside = root.is_relative_to(SCRATCH.resolve())

    stray = [p.name for p in REPO.iterdir()
             if p.name.startswith(("lane-", "fleet-", "origin-", "case-"))
             or p.name in ("lane", "fleet")]
    stray_nested = []
    for dirpath, dirnames, _ in os.walk(REPO / ".ufo" / "waves" / "round-24"):
        for d in list(dirnames):
            if d.startswith(("lane-", "fleet-", "origin-")):
                stray_nested.append(os.path.join(dirpath, d))

    doc = {
        "builder_rc": proc.returncode,
        "builder_stdout": proc.stdout.decode()[-2000:],
        "builder_stderr": proc.stderr.decode()[-2000:],
        "run_seconds": round(t1 - t0, 2),
        "scratch_root": str(root),
        "scratch_root_inside_assigned_scratch": inside,
        "repo_head_before": before_head,
        "repo_head_after": after_head,
        "repo_head_unchanged": before_head == after_head,
        "repo_status_before": before_status.splitlines(),
        "repo_status_after": after_status.splitlines(),
        "repo_status_delta": sorted(
            set(after_status.splitlines()) - set(before_status.splitlines())),
        "stray_fixture_dirs_in_repo": stray,
        "stray_fixture_dirs_in_wave_dir": stray_nested,
        "new_or_touched_tmp_paths": in_window,
        "fixture_paths_in_results": sorted({
            str(Path(v).resolve()) for v in
            [results["root"], results["auditor_path"]] +
            [r["argv"][3] for r in
             (a for a in results["arms"].values())] +
            [a["argv"][5] for a in results["arms"].values()]}),
    }
    (OUT / "containment.json").write_text(json.dumps(doc, indent=1, sort_keys=True),
                                          encoding="utf-8")
    print(json.dumps(doc, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
