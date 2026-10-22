#!/usr/bin/env python3
"""Run the pinned auditor over the independently built omission fixtures and
grade the observed verdicts against the fixed expectation rows.

Bounded: only the four OmissionTwins cases plus two local mutation probes
(cite the omitted commit / remove the omission).  Offline, no network.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_omission import build_family, facts, g, inventory  # noqa: E402

AUDITOR = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()
REL = ".ufo/reports/round-1/kama.md"


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def audit(lane, fleet, cwd):
    argv = [sys.executable, str(AUDITOR), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(cwd))
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def defects_of(out):
    try:
        doc = json.loads(out)
    except ValueError:
        return None, None
    uncorrected, raw = [], []
    for res in doc.get("results", []):
        for d in res.get("defects", []):
            raw.append((d.get("kind"), d.get("token")))
            if not d.get("corrected_by"):
                uncorrected.append((d.get("kind"), d.get("token")))
    return sorted(uncorrected), sorted(raw)


def normalise(out, lane, fleet):
    try:
        doc = json.loads(out)
    except ValueError:
        return None
    text = json.dumps(doc, sort_keys=True)
    text = text.replace(str(fleet), "<fleet>").replace(str(lane), "<lane>")
    return json.loads(text)


def run_variant(mark, root):
    fx = build_family(root / mark, mark)
    lane, fleet = fx["lane"], fx["fleet"]
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    code, out, err = audit(lane, fleet, root)
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    unc, raw = defects_of(out)
    return {"mark": mark, "exit": code, "stderr": err.strip(),
            "defects": unc, "raw_defects": raw,
            "document": normalise(out, lane, fleet),
            "objects_acquired": acquired,
            "l1": fx["l1"], "l2": fx["l2"],
            "facts": facts(fx)}


def probe_cite_omitted(root):
    """Mutation: the report cites the omitted commit too -> clean."""
    fx = build_family(root / "probe_cite", "plain")
    lane, fleet = fx["lane"], fx["fleet"]
    report = ("# kama round 1\n\n## Landed changes\n\n"
              f"- {fx['l1']}\n- {fx['l2']}\n")
    (fleet / REL).write_text(report, encoding="utf-8")
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: report v2",
      GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
      GIT_AUTHOR_DATE="@2100 +0000", GIT_COMMITTER_DATE="@2100 +0000")
    code, out, err = audit(lane, fleet, root)
    unc, raw = defects_of(out)
    return {"probe": "cite-omitted", "exit": code, "stderr": err.strip(),
            "defects": unc, "raw_defects": raw}


def probe_no_omission(root):
    """Mutation: the lane holds no second round-1 commit -> clean."""
    fx = build_family(root / "probe_clean", "plain")
    lane, fleet = fx["lane"], fx["fleet"]
    g(lane, "reset", "-q", "--hard", fx["l1"])
    code, out, err = audit(lane, fleet, root)
    unc, raw = defects_of(out)
    return {"probe": "no-omission", "exit": code, "stderr": err.strip(),
            "defects": unc, "raw_defects": raw}


def main():
    res = {}
    for mark, case in (("plain", "PG10-omission-lane-plain"),
                       ("lane_config", "PG09-omission-lane-promisor"),
                       ("fleet_config", "PG11-omission-fleet-promisor"),
                       ("lane_marker", "PG12-omission-marker-lane")):
        r = run_variant(mark, ROOT / "cases" / case)
        r["case"] = case
        res[case] = r
    res["probes"] = [probe_cite_omitted(ROOT / "probes"),
                     probe_no_omission(ROOT / "probes")]
    # twin comparison: every marked variant's document against the plain one
    plain = res["PG10-omission-lane-plain"]["document"]
    res["twin_equal_vs_PG10"] = {
        c: (res[c]["document"] == plain) for c in
        ("PG09-omission-lane-promisor", "PG11-omission-fleet-promisor",
         "PG12-omission-marker-lane")}
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
