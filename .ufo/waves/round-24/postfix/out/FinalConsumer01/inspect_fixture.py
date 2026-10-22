#!/usr/bin/env python3
"""FinalConsumer01: build the fleet-only-blob fixture with the COMMITTED
replay-v3 driver's own scenario() code (imported, not retyped), keep it on
disk, and inspect the actual Git object types/presence plus the raw auditor
JSON on both sides.

Nothing here is a new expectation: the expectation is the driver's
EXPECTED["fleet-only-blob"], read from the committed driver.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer01")
DRIVER = BASE / "clone/.ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py"
BEFORE = BASE / "out/before-report-landing-audit.py"
AFTER = BASE / "clone/tools/report-landing-audit.py"
FIXTURE = BASE / "fixture"

spec = importlib.util.spec_from_file_location("replay3", DRIVER)
drv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drv)

GITENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
          "GIT_AUTHOR_NAME": "kama-shokunin", "GIT_COMMITTER_NAME": "kama-shokunin",
          "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
          "PATH": "/usr/bin:/bin"}


def g(repo, *args):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
                        str(repo), *args], capture_output=True, env=GITENV,
                       timeout=30)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip(), \
        p.stderr.decode("utf-8", "replace").strip()


def main():
    if FIXTURE.exists():
        import shutil
        shutil.rmtree(FIXTURE)
    FIXTURE.mkdir(parents=True)
    lane, fleet, draft, errata = drv.scenario(str(FIXTURE), "fleet-only-blob")
    report = {"fixture_root": str(FIXTURE), "lane": str(lane),
              "fleet": str(fleet), "draft": str(draft),
              "errata": str(errata) if errata else None}
    report["draft_text"] = Path(draft).read_text(encoding="utf-8")
    report["errata_text"] = (Path(errata).read_text(encoding="utf-8")
                             if errata else None)
    # the tokens cited by the draft
    tokens = []
    for line in report["draft_text"].splitlines():
        if line.startswith("- `") and "`" in line[3:]:
            tokens.append(line[3:].split("`")[0])
    report["cited_tokens"] = tokens
    obj = {}
    for tok in tokens:
        rec = {"token": tok, "length": len(tok)}
        for label, repo in (("lane", lane), ("fleet", fleet)):
            rc, out, err = g(repo, "cat-file", "-t", tok)
            rec[label + "_cat_file_t"] = {"rc": rc, "stdout": out,
                                          "stderr": err}
            rc2, out2, err2 = g(repo, "cat-file", "--batch-check", tok)
            rec[label + "_batch_check"] = {"rc": rc2, "stdout": out2,
                                          "stderr": err2}
            rc3, out3, err3 = g(repo, "rev-parse", "--verify", "--quiet",
                                tok + "^{commit}")
            rec[label + "_peel_commit"] = {"rc": rc3, "stdout": out3,
                                           "stderr": err3}
        obj[tok] = rec
    report["objects"] = obj
    # repo-level facts
    for label, repo in (("lane", lane), ("fleet", fleet)):
        rc, out, err = g(repo, "config", "--local", "--list")
        report[label + "_local_config"] = {"rc": rc, "stdout": out, "stderr": err}
        rc, out, err = g(repo, "rev-parse", "HEAD")
        report[label + "_head"] = out
        rc, out, err = g(repo, "cat-file", "--batch-check", "--batch-all-objects")
        report[label + "_all_objects"] = out.splitlines()
    # raw auditor runs on the same fixture
    runs = {}
    for side, tool in (("before", BEFORE), ("after", AFTER)):
        cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
               "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
               "--report", f"1={draft}", "--json", "--no-errata"]
        p = subprocess.run(cmd, capture_output=True, timeout=120,
                           env={**os.environ, "TMPDIR": str(BASE / "tmp")})
        runs[side] = {
            "cmd": cmd, "exit": p.returncode,
            "stdout": p.stdout.decode("utf-8", "replace"),
            "stderr": p.stderr.decode("utf-8", "replace"),
            "tool_sha256": hashlib.sha256(Path(tool).read_bytes()).hexdigest(),
        }
        try:
            runs[side]["json"] = json.loads(runs[side]["stdout"])
        except Exception as exc:
            runs[side]["json_parse_error"] = str(exc)
    report["runs"] = runs
    report["expectation_from_driver"] = drv.EXPECTED["fleet-only-blob"]
    report["control_expectation_from_driver"] = drv.CONTROL["fleet-only-blob"]
    outp = BASE / "out/fixture-inspection.json"
    outp.write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
