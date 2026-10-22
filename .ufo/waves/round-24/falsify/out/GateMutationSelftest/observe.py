#!/usr/bin/env python3
"""Bounded offline harness: exercise promisor-mutants.py's CLI status rules
using the module's own stub grid plus one extra stub mode. No repository, no
network, no real grid. Scratch only.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/GateMutationSelftest")
TOOL = ROOT / "tests/report-audit/promisor-mutants.py"
OUT = Path("/fast/scratch/hyaku/kama-r24/falsify/GateMutationSelftest/tmp/harness")
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("pm", TOOL)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

grid = OUT / "stub-grid.py"
grid.write_text(pm.STUB_GRID, encoding="utf-8")
cand = OUT / "candidate.py"
cand.write_text(pm.CANDIDATE + "# PRISTINE\n", encoding="utf-8")

# extra stub mode: exit 1 with a row that is NOT graded -> the runner's
# "exit 1 without an identifiable violated row" branch.
EXTRA = '''
if mode == "rc1_ungraded_row" and not pristine:
    doc = {"arms": {arm: {"rows": [row("PG01", kind="open")]}}}
    print(json.dumps(doc))
    sys.exit(1)
'''
src = pm.STUB_GRID
grid2 = OUT / "stub-grid2.py"
grid2.write_text(src.replace('if mode == "rc1_no_rows"', EXTRA + 'if mode == "rc1_no_rows"'), encoding="utf-8")


def run(mode, g=grid, c=cand):
    env = dict(os.environ, GRID_STUB_MODE=mode)
    p = subprocess.run([sys.executable, str(TOOL), "--grid", str(g),
                        "--current", str(c), "--json"],
                       capture_output=True, env=env, timeout=300)
    try:
        doc = json.loads(p.stdout.decode("utf-8", "replace"))
    except (ValueError, UnicodeDecodeError):
        doc = {"__unparsed__": p.stdout.decode("utf-8", "replace")[:200]}
    return p.returncode, doc, p.stderr.decode("utf-8", "replace")


def summarize(tag, rc, doc, err):
    print(f"--- {tag}: runner_exit={rc}")
    if "mutants" in doc:
        print(f"    mutants={doc['mutants']} evaluated={doc['evaluated']} "
              f"killed={doc['killed']} surviving={len(doc.get('surviving', []))} "
              f"cne={doc.get('could_not_evaluate')}")
        for r in doc["rows"]:
            extra = ""
            if r.get("failed_rows"):
                extra = f" failed_rows={r['failed_rows']}"
            if r.get("unexpected_rows"):
                extra += f" unexpected_rows={r['unexpected_rows']}"
            if r.get("status") == "could-not-evaluate":
                extra += f" reason={r.get('reason')!r}"
            print(f"    {r['mutant']}: {r['status']} killed={r.get('killed')}"
                  f"{extra}")
    else:
        print(f"    doc_keys={sorted(doc.keys())}")
    if err.strip():
        print(f"    stderr={err.strip()[:300]}")


for mode in ("ok", "unmet", "twin", "exit2", "rc1_no_rows", "leak",
             "timeout_row", "pristine_fails"):
    rc, doc, err = run(mode)
    summarize(f"mode={mode}", rc, doc, err)

rc, doc, err = run("rc1_ungraded_row", g=grid2)
summarize("mode=rc1_ungraded_row(EXTRA, ungraded row)", rc, doc, err)

# broken candidate -> compilation failure -> CNE
broken = OUT / "broken.py"
broken.write_text(pm.BROKEN_CANDIDATE, encoding="utf-8")
rc, doc, err = run("ok", c=broken)
summarize("mode=ok cand=broken (compilation failure)", rc, doc, err)

# --anchors status rules
for label, path in (("broken", broken), ("sound", cand)):
    p = subprocess.run([sys.executable, str(TOOL), "--anchors", str(path)],
                       capture_output=True, timeout=120)
    print(f"--- --anchors {label}: exit={p.returncode}")
    print("    " + p.stdout.decode("utf-8", "replace").strip().replace("\n", "\n    "))
