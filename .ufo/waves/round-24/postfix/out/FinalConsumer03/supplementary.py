#!/usr/bin/env python3
"""Supplementary discrimination checks for the fleet-only-tag consumer.

Bounded, single-fixture, on the already-constructed fixture under
/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer03/fix.
Nothing here edits expectations; it only observes the tool's own output.
"""
import json
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer03")
F = S / "fix"
AFTER = S / "clone/tools/report-landing-audit.py"
BEFORE = S / "out/before-2e254a1.py"
LANE, FLEET = F / "lane", F / "fleet"
VALID_COMMIT = "94e0024da42ebb1c45af0f16eb0f54fc17628efa"
TAG = "a41c20ec9d249f5de4f163d6a0914d0bd49fe59c"
TARGET_BLOB = "a6714745b7826cf987108278ecac7d8c380a71ba"
results = []


def run(tool, draft, errata=None, label=""):
    cmd = [sys.executable, str(tool), "--lane-repo", str(LANE),
           "--fleet-repo", str(FLEET), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"]
    cmd += ["--errata", str(errata)] if errata else ["--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=60,
                       env={"PATH": "/usr/bin:/bin", "TMPDIR": str(S / "tmp"),
                            "GIT_CONFIG_GLOBAL": "/dev/null",
                            "GIT_CONFIG_NOSYSTEM": "1"})
    kinds, errata_invalid, defects = [], None, []
    if p.returncode in (0, 1):
        try:
            d = json.loads(p.stdout.decode("utf-8", "replace"))
            kinds = sorted({x["kind"] for r in d["results"] for x in r["defects"]})
            errata_invalid = d["summary"].get("errata_invalid")
            defects = [x for r in d["results"] for x in r["defects"]]
        except Exception as exc:
            kinds = [f"UNPARSEABLE:{exc}"]
    rec = {"label": label, "tool": tool.name, "exit": p.returncode,
           "kinds": kinds, "errata_invalid": errata_invalid,
           "defects": defects,
           "stderr_last": p.stderr.decode("utf-8", "replace").strip().splitlines()[-1:] }
    results.append(rec)
    return rec


# A. the primary fixture, after and before, with the no-ledger arm
d1 = F / "draft.md"
run(AFTER, d1, None, "A after / fixture draft / no ledger")
run(BEFORE, d1, None, "A before / fixture draft / no ledger")

# B. counterfactual: the SAME fixture WITHOUT the valid work commit cited.
#    If an unrelated landed-omitted finding can mask the wrong-type
#    citation, this is where it would show.
d2 = F / "draft-no-valid-commit.md"
d2.write_text(f"## Landed changes\n- `{TAG}` under test\n", encoding="utf-8")
run(AFTER, d2, None, "B after / valid commit NOT cited (mask probe)")

# C. ledger arm: a row that tries to launder the fleet-only tag with a
#    fleet-only BLOB as its correction -> the correction is not a commit.
d3 = F / "errata-wrong-type.tsv"
d3.write_text(f"1\tlanded-unresolved\t{TAG}\t{TARGET_BLOB}\tev\n", encoding="utf-8")
run(AFTER, d1, d3, "C after / ledger row correcting the tag with a blob")

# D. ledger arm: the same row with a VALID lane commit as the correction.
d4 = F / "errata-valid.tsv"
d4.write_text(f"1\tlanded-unresolved\t{TAG}\t{VALID_COMMIT}\tev\n", encoding="utf-8")
run(AFTER, d1, d4, "D after / ledger row correcting the tag with the lane commit")

# E. ledger arm: a row for an UNSELECTED round (round 2) naming the tag.
d5 = F / "errata-unselected.tsv"
d5.write_text(f"2\tlanded-unresolved\t{TAG}\t{TARGET_BLOB}\tev\n", encoding="utf-8")
run(AFTER, d1, d5, "E after / ledger row for an UNSELECTED round")

print(json.dumps(results, indent=1, sort_keys=True))
(S / "out/supplementary.json").write_text(json.dumps(results, indent=1, sort_keys=True))
