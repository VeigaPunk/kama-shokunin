#!/usr/bin/env python3
"""Apply the EXACT registered PM03 operator to a private copy of the pinned
auditor, using the pinned mutator's own apply_mutation/compiles APIs.
No re-anchoring, no retargeting, no edit to any production file."""
import difflib
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM03/clone")
RUNNER = CLONE / "tests/report-audit/promisor-mutants.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM03/mutant")
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("pinned_promisor_mutants", RUNNER)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

MID = "PM03-skip-required-object-availability"
mutant = None
for m in pm.MUTANTS:
    if m["id"] == MID:
        mutant = m
        break
if mutant is None:
    print("could-not-evaluate: the pinned inventory has no " + MID)
    sys.exit(2)

source = AUDIT.read_text(encoding="utf-8")

# unique applicability: the same counting the runner's --anchors path does
counts = []
for alt in mutant["alternatives"]:
    if alt["kind"] == "replace":
        counts.append({"kind": "replace", "matches": source.count(alt["old"])})
    elif alt["kind"] == "regex":
        counts.append({"kind": "regex",
                       "matches": len(re.findall(alt["pattern"], source,
                                                 re.DOTALL))})
    else:
        counts.append({"kind": "insert", "matches": source.count(alt["anchor"])})

mutated, info = pm.apply_mutation(source, mutant)
if mutated is None:
    print(json.dumps({"status": "could-not-evaluate", "reason": info,
                      "counts": counts}, indent=1))
    sys.exit(2)
compiled = pm.compiles(mutated, MID)

target = OUT / (MID + ".py")
target.write_text(mutated, encoding="utf-8")

diff = list(difflib.unified_diff(source.splitlines(), mutated.splitlines(),
                                 "pinned/tools/report-landing-audit.py",
                                 "mutant/" + target.name, lineterm="", n=2))

summary = {
    "mutant": MID,
    "execution": mutant["execution"],
    "expect_rows": mutant["expect_rows"],
    "alternative_match_counts": counts,
    "applied_alternative": info,
    "mutant_compiles": compiled,
    "pristine_auditor": str(AUDIT),
    "pristine_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
    "mutant_path": str(target),
    "mutant_sha256": hashlib.sha256(mutated.encode("utf-8")).hexdigest(),
    "mutant_bytes": len(mutated.encode("utf-8")),
    "pristine_bytes": len(source.encode("utf-8")),
    "diff": diff,
}
print(json.dumps(summary, indent=1))
