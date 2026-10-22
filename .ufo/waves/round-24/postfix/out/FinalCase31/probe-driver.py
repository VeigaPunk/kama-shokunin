#!/usr/bin/env python3
"""Bounded boundary probes for FinalCase31 (PG31 two-root diagnosis).

Three direct invocations of the pinned candidate against a COPY of the PG31
fixture.  Not grid cells: they probe the boundary of the two-root diagnosis
on the same fixture.

  P1 cite-the-hole      the citation names the unavailable unselected-branch
                        blob -> the hole IS required -> refusal exit 2.
  P2 absent-fabricated  the citation names an object nobody holds and the
                        store does not reference -> proved absence keeps the
                        registered result (exit 1, unresolved-full-hash),
                        NOT a refusal.
  P3 wrong-type         the citation names a present tree (not a commit) ->
                        proved mismatch keeps the registered result
                        (exit 1, landed-unresolved), NOT a refusal.
"""
import json
import subprocess
import sys
from pathlib import Path

B = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase31")
P = B / "probe"
TOOL = B / "clone" / "tools" / "report-landing-audit.py"
LANE = P / "lane"
FLEET = P / "fleet"

TIP = "58866b563cd900df310588effe79028efc104c33"
MISSING = "2299c37978265a95cbe835a4b0f0bbf15aad5549"
SIDETREE = "d1418e9fdf7f4ffe2f0fb09464981a8d58f49199"
FAKE = "1234567890abcdef1234567890abcdef12345678"


def run(name, draft_text):
    draft = B / f"probe-{name}.md"
    draft.write_text(draft_text, encoding="utf-8")
    argv = [sys.executable, str(TOOL), "--lane-repo", str(LANE),
            "--fleet-repo", str(FLEET), "--branch", "master", "--rounds", "1",
            "--report", f"1={draft}", "--no-errata", "--json"]
    proc = subprocess.run(argv, capture_output=True, timeout=60,
                          cwd=str(B))
    row = {"probe": name, "argv": argv, "exit": proc.returncode,
           "stderr_tail": proc.stderr.decode("utf-8", "replace").strip()[-300:]}
    if proc.returncode in (0, 1):
        doc = json.loads(proc.stdout.decode("utf-8", "replace"))
        row["kinds"] = sorted({d["kind"] for r in doc["results"]
                               for d in r["defects"]})
        row["defects"] = sorted((d["kind"], d["token"]) for r in doc["results"]
                                for d in r["defects"])
        row["status"] = doc["summary"]["status"]
        row["errata_invalid"] = doc["summary"]["errata_invalid"]
    else:
        row["kinds"] = None
        row["defects"] = None
        row["stdout_bytes"] = len(proc.stdout)
    print(json.dumps(row, indent=1, sort_keys=True))
    return row


rows = []
rows.append(run("P1-cite-the-hole",
                f"## Landed changes\n- `{TIP}` work\n\n"
                f"## Work performed\n{MISSING}\n"))
rows.append(run("P2-absent-fabricated",
                f"## Landed changes\n- `{TIP}` work\n\n"
                f"## Work performed\n{FAKE}\n"))
rows.append(run("P3-wrong-type",
                f"## Landed changes\n- `{TIP}` work\n- `{SIDETREE}` tree\n"))
(B / "probe-results.json").write_text(
    json.dumps(rows, indent=1, sort_keys=True) + "\n", encoding="utf-8")
