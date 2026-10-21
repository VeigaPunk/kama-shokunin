#!/usr/bin/env python3
"""OracleLocalBlobType probe: what does the r23 auditor do when ONLY the
blanket promisor refusal is removed?

This is an ORACLE-CONSTRUCTION PROBE, not a candidate: it is the r23 base
auditor (blob cf706c52233139920da60f8b55d06f031286c4f9, sha256
da5041a8...) copied into scratch with the two promisor-specific refusals
deleted in tools/report-landing-audit.py::check_history_repo.  Nothing else
is touched, no production file is written, nothing is fetched.

It answers one question: given promisor metadata and a locally complete
object store, does the rest of the r23 pipeline already produce the full
clone's verdict?  If yes, the round-24 repair for this case is exactly
"replace the blanket refusal by an availability check that passes", and the
expected outcome for the case is the full clone's outcome.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/OracleLocalBlobType")
BASE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/"
            "tools/report-landing-audit.py")
PROBE = ROOT / "probe-audit-no-promisor-refusal.py"

OLD_PACK = """        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            raise EvalError(f"{repo}: partial clone (promisor pack)")
"""
NEW_PACK = """        # ORACLE PROBE: promisor pack marker refusal removed
"""
OLD_CFG = """        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
"""
NEW_CFG = """        # ORACLE PROBE: promisor config refusal removed
"""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_ALLOW_PROTOCOL="file")
    e.update(extra)
    return e


def audit(tool, lane, fleet):
    argv = [sys.executable, str(tool), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    try:
        p = subprocess.run(argv, capture_output=True, env=env(), timeout=30)
    except subprocess.TimeoutExpired:
        return {"exit": None, "timed_out": True}
    out = {"exit": p.returncode,
           "stderr_tail": p.stderr.decode(errors="replace").strip()[-200:]}
    if p.returncode in (0, 1):
        doc = json.loads(p.stdout)
        out["kinds"] = sorted({d["kind"] for r in doc["results"]
                               for d in r["defects"]})
        out["defects"] = [d for r in doc["results"] for d in r["defects"]]
        out["summary"] = doc["summary"]
    return out


def main():
    src = BASE.read_text()
    assert OLD_PACK in src and OLD_CFG in src, "base auditor shape changed"
    PROBE.write_text(src.replace(OLD_PACK, NEW_PACK).replace(OLD_CFG, NEW_CFG))
    doc = {"probe": str(PROBE),
           "probe_sha256": hashlib.sha256(PROBE.read_bytes()).hexdigest(),
           "base_sha256": hashlib.sha256(src.encode()).hexdigest()}
    cases = ROOT / "cases"
    twins = {"B": "A", "C": "A", "F": "A", "G": "A", "I": "A", "E": "D"}
    doc["rows"] = {}
    for name, twin in twins.items():
        lane, fleet = cases / name / "lane", cases / name / "fleet"
        t_lane, t_fleet = cases / twin / "lane", cases / twin / "fleet"
        mine = audit(PROBE, lane, fleet)
        base_full = audit(BASE, t_lane, t_fleet)
        doc["rows"][name] = {
            "probe": mine,
            "full_clone_twin_base": base_full,
            "same_exit_as_twin": mine.get("exit") == base_full.get("exit"),
            "same_kinds_as_twin": mine.get("kinds") == base_full.get("kinds"),
            "same_defects_as_twin": mine.get("defects") == base_full.get("defects"),
            "same_summary_as_twin": mine.get("summary") == base_full.get("summary")}
    out = ROOT / "probe-results.json"
    out.write_text(json.dumps(doc, indent=1, sort_keys=True))
    for name, row in doc["rows"].items():
        print(f"{name}: probe_exit={row['probe'].get('exit')} "
              f"kinds={row['probe'].get('kinds')} "
              f"twin_exit={row['full_clone_twin_base'].get('exit')} "
              f"same_summary={row['same_summary_as_twin']} "
              f"same_defects={row['same_defects_as_twin']}")
    print(f"written {out}")


if __name__ == "__main__":
    main()
