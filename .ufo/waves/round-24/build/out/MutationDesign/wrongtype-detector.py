#!/usr/bin/env python3
"""One offline wrong-type citation measurement; no suite or network fixtures.

Detector exits: 0 exact expected audit result; 1 substantive mismatch;
2 inconclusive (premise, process, timeout, JSON, or output failure).
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys


def main():
    auditor, fixture = map(Path, sys.argv[1:])
    manifest = json.loads((fixture / "manifest.json").read_text())
    lane, fleet = fixture / "lane", fixture / "fleet"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    probes = []
    for repo, token, kind in ((lane, manifest["lane_commit"], "commit"),
                              (lane, manifest["wrongtype_token"], "blob"),
                              (fleet, manifest["fleet_commit"], "commit")):
        argv = ["git", "--no-lazy-fetch", "--no-replace-objects", "-C",
                str(repo), "cat-file", "-t", token]
        p = subprocess.run(argv, capture_output=True, env=env, timeout=5)
        probes.append({"argv": argv, "exit": p.returncode,
                       "stdout": p.stdout.decode(), "stderr": p.stderr.decode()})
        if p.returncode or p.stdout.decode().strip() != kind:
            raise ValueError("fixture does not establish local object type")
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
            "--rounds", "1", "--no-errata", "--json"]
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env, cwd=fixture, start_new_session=True)
    try:
        out, err = p.communicate(timeout=25)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        out, err = p.communicate()
        print(json.dumps({"classification": "inconclusive", "argv": argv,
                          "audit_exit": p.returncode, "reason": "timeout",
                          "stdout": out.decode(errors="replace"),
                          "stderr": err.decode(errors="replace")}))
        return 2
    if p.returncode not in (0, 1) or err:
        print(json.dumps({"classification": "inconclusive", "argv": argv,
                          "audit_exit": p.returncode,
                          "stdout": out.decode(errors="replace"),
                          "stderr": err.decode(errors="replace")}))
        return 2
    doc = json.loads(out)
    defects = [{"kind": d["kind"], "token": d["token"]}
               for r in doc["results"] for d in r["defects"]]
    expected = [{"kind": "landed-unresolved", "token": manifest["wrongtype_token"]}]
    matched = (p.returncode == 1 and doc["summary"]["status"] == "failed"
               and doc["summary"]["required_commits"] == 1
               and len(doc["results"]) == 1 and defects == expected)
    print(json.dumps({"classification": "pass" if matched else "mismatch",
                      "expected_audit_exit": 1, "expected_defects": expected,
                      "auditor_sha256": hashlib.sha256(auditor.read_bytes()).hexdigest(),
                      "fixture_manifest_sha256": hashlib.sha256(
                          (fixture / "manifest.json").read_bytes()).hexdigest(),
                      "argv": argv, "premise_probes": probes,
                      "audit_exit": p.returncode, "actual_defects": defects,
                      "stdout": out.decode(), "stderr": err.decode()},
                     indent=2, sort_keys=True))
    return 0 if matched else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"classification": "inconclusive",
                          "reason": f"{type(exc).__name__}: {exc}"}))
        sys.exit(2)
