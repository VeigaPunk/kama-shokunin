#!/usr/bin/env python3
"""Supporting probe for CaseMarkerFleet: a marker-backed repository in which a
citation resolves nowhere locally must stay *unknown* (exit 2), never a
proved-absence verdict. Not part of the case oracle (the sibling
CaseUnknownCitation owns that row); it exists to show that evaluating a
marker-backed but complete repository does not force the repair to score an
unresolvable citation as absent.

Offline: the marker remote url names a path that does not exist and
protocol.allow=never forbids any transport.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, "/fast/scratch/hyaku/kama-r24/CaseMarkerFleet/build")
from case_marker_fleet import (ABSENT_ORIGIN, REL, ROOT, commit, g,  # noqa: E402
                               init, publish, report, run_auditor)

FAKE = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"


def main():
    auditors = {
        "base": ROOT / "repo/tools/report-landing-audit.py",
        "probe": ROOT / "build/auditor-probe.py",
    }
    work = ROOT / "run" / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) \
        / "U1-marker-unknown-citation"
    work.mkdir(parents=True, exist_ok=True)
    lane = init(work / "lane")
    fleet = init(work / "fleet-plain")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc, FAKE]))
    marker = work / "fleet-marker"
    shutil.copytree(fleet, marker, symlinks=True)
    g(marker, "config", "core.repositoryformatversion", "1")
    g(marker, "config", "extensions.partialclone", "origin")
    g(marker, "config", "remote.origin.url", str(ABSENT_ORIGIN))
    g(marker, "config", "remote.origin.promisor", "true")
    g(marker, "config", "remote.origin.partialclonefilter", "blob:none")
    g(marker, "config", "protocol.allow", "never")
    doc = {"case": "U1-marker-unknown-citation", "fake": FAKE, "runs": {}}
    for name, auditor in auditors.items():
        run = run_auditor(auditor, lane, marker, work)
        doc["runs"][name] = {"exit": run["exit"], "stderr": run["stderr"],
                             "summary": run["summary"],
                             "results": run["results"],
                             "store_before": run["store_before"],
                             "store_after": run["store_after"]}
    doc["expectation"] = ("base: exit 2 (partial clone refusal); probe: exit 2 "
                           "with an unknown-citation refusal, never exit 0/1 "
                           "with an unresolved-full-hash verdict")
    out = ROOT / "obs/unknown-citation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(json.dumps(doc, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
