#!/usr/bin/env python3
"""Measure one auditor over the promisor fixture arms (bounded, offline).

Usage: measure.py --auditor PATH --root DIR [--json OUT.json]

Runs the auditor once per arm with a 30 s deadline, records exit code,
defect kinds, summary, stderr tail, timeout flag and whether the hostile
transport marker was created. No network, no transport, no payload.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

TIMEOUT = 30
ARMS = ("full-clean", "promisor-clean", "full-omission", "promisor-omission",
        "full-fabricated", "promisor-fabricated", "tok-bool-maybe",
        "tok-filter", "tok-extensions", "promisor-hostile-ssh",
        "full-missing-unrelated-blob", "promisor-missing-unrelated-blob",
        "promisor-missing-report-blob")


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def repo_state(repo):
    """Program-free fetch evidence: a fetch adds packs / FETCH_HEAD / objects."""
    gitdir = Path(repo, ".git")
    packs = sorted(p.name for p in (gitdir / "objects/pack").glob("*")) \
        if (gitdir / "objects/pack").is_dir() else []
    fetch_head = (gitdir / "FETCH_HEAD").exists()
    loose = sum(1 for _ in (gitdir / "objects").glob("??/*")) \
        if (gitdir / "objects").is_dir() else 0
    return {"packs": packs, "fetch_head": fetch_head, "loose": loose}


def run_arm(auditor, root, arm):
    lane, fleet = root / arm / "lane", root / arm / "fleet"
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    before = {"lane": repo_state(lane), "fleet": repo_state(fleet)}
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env(), cwd=str(root),
                            start_new_session=True)
    timed_out = False
    try:
        out, err = proc.communicate(timeout=TIMEOUT)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        code, timed_out = None, True
    kinds, summary = None, None
    if code in (0, 1):
        try:
            doc = json.loads(out)
            kinds = sorted({d["kind"] for r in doc.get("results", [])
                            for d in r.get("defects", [])})
            summary = doc.get("summary")
        except Exception:
            kinds, summary = "unparseable", None
    marker = root / arm / "transport-ran"
    after = {"lane": repo_state(lane), "fleet": repo_state(fleet)}
    fetch_observed = any(
        after[k]["fetch_head"] and not before[k]["fetch_head"]
        or set(after[k]["packs"]) - set(before[k]["packs"])
        or after[k]["loose"] != before[k]["loose"]
        for k in ("lane", "fleet"))
    return {
        "arm": arm, "exit": code, "kinds": kinds, "summary": summary,
        "timed_out": timed_out,
        "traceback": b"Traceback (most recent call last)" in err,
        "transport_marker_created": marker.exists(),
        "fetch_observed": fetch_observed,
        "repo_state_before": before, "repo_state_after": after,
        "stderr_tail": err.decode(errors="replace").strip()[-240:],
        "argv": argv,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--auditor", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--json")
    ap.add_argument("--arms", default=",".join(ARMS))
    args = ap.parse_args(argv)
    root = Path(args.root)
    rows = [run_arm(args.auditor, root, a) for a in args.arms.split(",")]
    doc = {"auditor": str(args.auditor),
           "auditor_sha256": __import__("hashlib").sha256(
               Path(args.auditor).read_bytes()).hexdigest(),
           "timeout_seconds": TIMEOUT, "rows": rows}
    text = json.dumps(doc, indent=1, sort_keys=True)
    if args.json:
        Path(args.json).write_text(text + "\n", encoding="utf-8")
    for r in rows:
        print(f"{r['arm']:32s} exit={r['exit']} kinds={r['kinds']} "
              f"timeout={int(r['timed_out'])} tb={int(r['traceback'])} "
              f"transport={int(r['transport_marker_created'])} "
              f"fetch={int(r['fetch_observed'])} "
              f"status={(r['summary'] or {}).get('status')} "
              f"err={r['stderr_tail'][:120]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
