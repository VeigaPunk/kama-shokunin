#!/usr/bin/env python3
"""FinalPM07: apply the registered PM07 operator to a private copy of the
pinned auditor, using the pinned mutator's own apply_mutation API.

Reads only from the pinned clone; writes only under the seat scratch.
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM07/clone")
WORK = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM07/work")
MUTATOR = CLONE / "tests/report-audit/promisor-mutants.py"
AUDIT = CLONE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("promisor_mutants", MUTATOR)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

source = AUDIT.read_text(encoding="utf-8")
mutant = next(m for m in pm.MUTANTS if m["id"] == "PM07-full-all-missing-gate")

counts = []
for index, alt in enumerate(mutant["alternatives"]):
    if alt["kind"] == "regex":
        n = len(re.findall(alt["pattern"], source, re.DOTALL))
    elif alt["kind"] == "replace":
        n = source.count(alt["old"])
    else:
        n = source.count(alt["anchor"])
    counts.append({"index": index, "kind": alt["kind"], "matches": n,
                   "pattern": alt.get("pattern") or alt.get("old")
                   or alt.get("anchor")})

mutated, applied = pm.apply_mutation(source, mutant)
if mutated is None:
    print(json.dumps({"error": "no alternative applied", "counts": counts},
                     indent=1))
    sys.exit(2)

canonical = WORK / "auditor-PM07-canonical.py"
canonical.write_text(mutated, encoding="utf-8")
compiles = pm.compiles(mutated, str(canonical))

# The supplementary, separately named variant: broaden ONLY the opacity
# (name-hiding) walk to the actual Git --all argv.  NOT the canonical
# operator, no primary-population credit.
opaque_old = 'opaque = walk(("--filter=blob:none",), [root])'
opaque_new = 'opaque = walk(("--filter=blob:none",), ["--all"])'
supp_counts = {"opaque_old": source.count(opaque_old),
               "opaque_new": source.count(opaque_new)}
supp = None
if supp_counts["opaque_old"] == 1:
    supp = source.replace(opaque_old, opaque_new)
    supp_path = WORK / "auditor-SUPPLEMENT-OPAQUE-ALLREFS.py"
    supp_path.write_text(supp, encoding="utf-8")

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

out = {
    "pinned_commit": "92063cfc60e217fa7e2098c568578119b16a1b95",
    "mutator": str(MUTATOR),
    "mutator_sha256": digest(MUTATOR),
    "auditor": str(AUDIT),
    "auditor_sha256": digest(AUDIT),
    "operator_id": mutant["id"],
    "operator_expect_rows": mutant["expect_rows"],
    "operator_execution": mutant["execution"],
    "alternative_counts": counts,
    "applied_alternative": applied,
    "canonical_mutant_path": str(canonical),
    "canonical_mutant_sha256": digest(canonical),
    "canonical_compiles": compiles,
    "supplement_counts": supp_counts,
    "supplement_path": str(WORK / "auditor-SUPPLEMENT-OPAQUE-ALLREFS.py")
    if supp is not None else None,
    "supplement_sha256": digest(WORK / "auditor-SUPPLEMENT-OPAQUE-ALLREFS.py")
    if supp is not None else None,
    "supplement_compiles": pm.compiles(supp, "supp") if supp is not None else None,
}
print(json.dumps(out, indent=1))
(WORK / "apply_pm07.json").write_text(json.dumps(out, indent=1) + "\n")
