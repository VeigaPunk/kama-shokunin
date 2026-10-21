#!/usr/bin/env python3
"""Grade an auditor against the pinned missing-errata-blob oracle.

Usage:
  grade_oracle.py --auditor PATH [--fixtures DIR] [--expected PATH] [--json]

Reads the pinned expectations (expected.json), runs the auditor against each
fixture arm, and reports per-arm met/not-met. Exit: 0 every arm met its
expectation; 1 at least one arm did not; 2 the harness itself could not
evaluate (missing fixture, unreadable auditor).

The grader never writes to the fixture repositories and never contacts a
network: the only remote-shaped URLs in the fixtures are file:// paths on
this disk or file:///nonexistent/local-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

TIMEOUT = 60


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def has_local(repo, oid):
    """Object present locally? Never fetches."""
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                        "cat-file", "-e", oid], capture_output=True,
                       env=env())
    return p.returncode == 0


def run_arm(auditor, arm, fx):
    """Run one arm on a SNAPSHOT of the fixture.

    The snapshot matters: an auditor that lazy-fetches restores the missing
    object inside the fixture repository, which would silently destroy the
    premise for every later run. Each arm therefore runs on its own copy,
    and the tripwire is evaluated against that copy.
    """
    with tempfile.TemporaryDirectory(prefix=f"oracle-arm-{arm}-") as tmp:
        lane = Path(tmp, "lane")
        fleet = Path(tmp, "fleet")
        shutil.copytree(fx["lane"], lane, symlinks=True)
        shutil.copytree(fx["fleet"], fleet, symlinks=True)
        argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
                "--fleet-repo", str(fleet), "--branch", "master",
                "--rounds", "1", "--json"]
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env(),
                                start_new_session=True, cwd=str(lane))
        timed_out = False
        try:
            out, err = proc.communicate(timeout=TIMEOUT)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            out, err = proc.communicate()
            code, timed_out = None, True
        row = {"arm": arm, "exit": code, "timed_out": timed_out,
               "stderr": err.decode(errors="replace").strip()}
        row["traceback"] = "Traceback (most recent call last)" in row["stderr"]
        summary = None
        if code in (0, 1):
            try:
                doc = json.loads(out)
                summary = doc["summary"]
                row["kinds"] = sorted({d["kind"] for r in doc["results"]
                                       for d in r["defects"]})
            except (ValueError, KeyError, TypeError) as exc:
                row["parse_error"] = f"{type(exc).__name__}: {exc}"
        row["summary"] = summary
        fetched = []
        if fx.get("errata_blob") and not fx["errata_present"]:
            if has_local(lane, fx["errata_blob"]):
                fetched.append("errata_blob")
        if fx.get("correction") and has_local(lane, fx["correction"]):
            fetched.append("correction")
        row["fetched"] = fetched
        return row


def grade(spec, row):
    problems = []
    if row["timed_out"]:
        problems.append("timed out")
    if row["traceback"]:
        problems.append("traceback")
    if row["fetched"]:
        problems.append("fetched missing object(s): "
                        + ",".join(row["fetched"]))
    if row["exit"] != spec["expect_exit"]:
        problems.append(f"exit {row['exit']} != expected {spec['expect_exit']}")
    if spec.get("expect_status") is not None:
        got = (row["summary"] or {}).get("status")
        if got != spec["expect_status"]:
            problems.append(f"status {got!r} != expected "
                            f"{spec['expect_status']!r}")
    if spec.get("expect_defects") is not None:
        got = (row["summary"] or {}).get("defects")
        if got != spec["expect_defects"]:
            problems.append(f"defects {got} != expected {spec['expect_defects']}")
    for key in ("corrected", "uncorrected", "errata_rows",
                "errata_unmatched", "errata_invalid"):
        want = spec.get(f"expect_" + key)
        if want is None:
            continue
        got = (row["summary"] or {}).get(key)
        if got != want:
            problems.append(f"{key} {got} != expected {want}")
    if spec.get("expect_kinds") is not None:
        if row.get("kinds") != sorted(spec["expect_kinds"]):
            problems.append(f"kinds {row.get('kinds')} != expected "
                            f"{sorted(spec['expect_kinds'])}")
    for needle in spec.get("require_stderr", []):
        if needle not in row["stderr"]:
            problems.append(f"stderr lacks {needle!r}")
    for needle in spec.get("forbid_stderr", []):
        if needle in row["stderr"]:
            problems.append(f"stderr contains forbidden {needle!r}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--auditor", required=True)
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--expected", required=True)
    ap.add_argument("--json")
    ap.add_argument("--arm", action="append")
    args = ap.parse_args(argv)
    auditor = Path(args.auditor).resolve()
    if not auditor.is_file():
        print(f"could-not-evaluate: no auditor at {auditor}", file=sys.stderr)
        return 2
    expected = json.loads(Path(args.expected).read_text())
    index_path = Path(args.fixtures, "index.json")
    if not index_path.is_file():
        print(f"could-not-evaluate: no fixture index at {index_path}",
              file=sys.stderr)
        return 2
    fixtures = json.loads(index_path.read_text())
    specs = {s["arm"]: s for s in expected["arms"]}
    # A stale fixture recipe silently drops arms, and a stale auditor copy
    # silently measures the wrong thing. Both are reported rather than
    # silently reducing the population.
    missing_fixtures = [s["arm"] for s in expected["arms"]
                        if s["arm"] not in fixtures]
    if missing_fixtures and not args.arm:
        print("could-not-evaluate: the fixture set is stale: no fixture for "
              + ", ".join(missing_fixtures), file=sys.stderr)
        return 2
    arms = args.arm or [s["arm"] for s in expected["arms"]
                        if s["arm"] in fixtures]
    rows = []
    for arm in arms:
        spec = specs.get(arm)
        if spec is None:
            print(f"could-not-evaluate: no expectation for arm {arm}",
                  file=sys.stderr)
            return 2
        row = run_arm(auditor, arm, fixtures[arm])
        row["class"] = spec.get("class")
        problems = grade(spec, row)
        row["problems"] = problems
        row["met"] = not problems
        rows.append(row)
    doc = {"auditor": str(auditor),
           "auditor_sha256": hashlib.sha256(auditor.read_bytes()).hexdigest(),
           "oracle": expected["oracle"],
           "base_revision": expected["base_revision"],
           "timeout_seconds": TIMEOUT,
           "rows": rows,
           "met": sum(r["met"] for r in rows),
           "total": len(rows),
           "violations": [r["arm"] for r in rows if not r["met"]]}
    if args.json:
        Path(args.json).write_text(json.dumps(doc, indent=1, sort_keys=True)
                                   + "\n")
    for r in rows:
        print(f"{'ok  ' if r['met'] else 'FAIL'} {r['arm']} "
              f"exit={r['exit']} class={r['class']} "
              f"{'; '.join(r['problems'])}")
    print(f"arms met {doc['met']}/{doc['total']} "
          f"violations={len(doc['violations'])}")
    return 0 if not doc["violations"] else 1


if __name__ == "__main__":
    sys.exit(main())
