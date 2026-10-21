#!/usr/bin/env python3
"""Run one auditor (base or candidate) against the CaseUnknownCitation arms.

For every arm: run the auditor, record exit code / defect kinds / stderr,
and verify the two non-negotiable properties of the fixture:

  * no fetch happened (the lane still lacks the unknown commit, gained no
    pack and no FETCH_HEAD, and the fleet's objects are unchanged);
  * nothing outside the fixture root was written by the fixture
    (the builder's guard() covers writes; the runner re-checks the repos'
    absolute paths, alternates and remote URLs).

Usage: run_case.py --root DIR --auditor PATH [--label NAME] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

TIMEOUT = 60


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_TERMINAL_PROMPT="0", GIT_ALLOW_PROTOCOL="file")
    return e


def git(repo, *args):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       capture_output=True, env=env())
    return p.returncode, p.stdout.decode(errors="replace").strip(), \
        p.stderr.decode(errors="replace").strip()


def object_present(repo, sha):
    rc, out, _ = git(repo, "cat-file", "-t", sha)
    return rc == 0, out


def repo_state(repo):
    repo = Path(repo)
    packs = sorted(p.name for p in (repo / ".git/objects/pack").glob("*")
                   if p.is_file())
    loose = sum(1 for p in (repo / ".git/objects").glob("??/*")
                if p.is_file() and p.parent.name != "info")
    fetch_head = (repo / ".git/FETCH_HEAD").exists()
    alternates = repo / ".git/objects/info/alternates"
    alt = alternates.read_text() if alternates.exists() else ""
    return {"packs": packs, "loose": loose, "fetch_head": fetch_head,
            "alternates": alt}


def run_arm(auditor, lane, fleet, manifest):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
            "--rounds", "1", "--no-errata", "--json"]
    before = {"lane": repo_state(lane), "fleet": repo_state(fleet)}
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env(),
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=TIMEOUT)
        code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        code, timed_out = None, True
    after = {"lane": repo_state(lane), "fleet": repo_state(fleet)}
    kinds = None
    if code in (0, 1):
        try:
            doc = json.loads(out)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
        except (ValueError, KeyError, TypeError):
            kinds = "unparseable"
    present, otype = object_present(lane, manifest["o2_unknown_citation"])
    fetched = present or after["lane"] != before["lane"]
    return {
        "exit": code,
        "timed_out": timed_out,
        "defect_kinds": kinds,
        "stderr_tail": err.decode(errors="replace").strip()[-400:],
        "stdout_bytes": len(out),
        "unknown_citation_in_lane_after": present,
        "unknown_citation_type": otype,
        "lane_state_before": before["lane"],
        "lane_state_after": after["lane"],
        "fleet_state_before": before["fleet"],
        "fleet_state_after": after["fleet"],
        "fetch_observed": fetched,
        "argv": argv,
    }


def containment(root, manifest):
    """Every audited repository and every referenced path stays in the root."""
    root = Path(root).resolve()
    problems = []
    for name, arm in manifest["arms"].items():
        for key in ("lane", "fleet"):
            p = Path(arm[key]).resolve()
            if root not in p.parents:
                problems.append(f"{name}.{key} outside root: {p}")
        rc, top, _ = git(arm["lane"], "rev-parse", "--show-toplevel")
        if rc or Path(top).resolve() != Path(arm["lane"]).resolve():
            problems.append(f"{name} lane toplevel mismatch: {top!r}")
        rc, url, _ = git(arm["lane"], "config", "--get", "remote.origin.url")
        if rc == 0 and url.startswith("file://"):
            target = Path(url[len("file://"):]).resolve()
            if root not in target.parents:
                problems.append(f"{name} remote.origin.url outside root: {url}")
        alt = Path(arm["lane"], ".git/objects/info/alternates")
        if alt.exists():
            problems.append(f"{name} lane has alternates: "
                            f"{alt.read_text().strip()}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--auditor", required=True)
    ap.add_argument("--label", default="auditor")
    ap.add_argument("--expected", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    expected = {}
    if args.expected:
        expected = json.loads(Path(args.expected).read_text())["arms"]

    problems = containment(root, manifest)
    results = {}
    for name, arm in manifest["arms"].items():
        r = run_arm(args.auditor, arm["lane"], arm["fleet"], manifest)
        req = expected.get(name, {}).get("required", {})
        if req:
            r["expected_exit"] = req.get("exit")
            r["expected_defect_kinds"] = req.get("defect_kinds")
            r["met"] = (r["exit"] == req.get("exit")
                        and r["defect_kinds"] == req.get("defect_kinds")
                        and not r["timed_out"]
                        and not r["fetch_observed"])
        results[name] = r
    doc = {"label": args.label, "auditor": str(Path(args.auditor).resolve()),
           "root": str(root), "containment_problems": problems,
           "results": results}
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for name, r in results.items():
            print(f"{name}: exit={r['exit']} kinds={r['defect_kinds']} "
                  f"fetch={r['fetch_observed']} "
                  f"met={r.get('met')} stderr={r['stderr_tail'][:120]!r}")
        print(f"containment_problems={problems}")
    return 0 if not problems and all(
        r.get("met", True) for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
