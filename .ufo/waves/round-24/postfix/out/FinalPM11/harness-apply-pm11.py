#!/usr/bin/env python3
"""Apply the EXACT registered PM11 operator from the pinned mutator.

Uses the pinned promisor-mutants.py module's own MUTANTS registry and its
own apply_mutation()/compiles() functions.  No re-anchoring, no hand-written
patch text, no retargeting.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

MUTATORS = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM11/clone/"
                "tests/report-audit/promisor-mutants.py")
PRISTINE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM11/work/"
                "auditor-pristine.py")
MUTATED = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM11/work/"
               "auditor-pm11.py")
MUTANT_ID = "PM11-any-hole-refusal"

spec = importlib.util.spec_from_file_location("pinned_promisor_mutants",
                                              MUTATORS)
mod = importlib.util.module_from_spec(spec)
sys.modules["pinned_promisor_mutants"] = mod
spec.loader.exec_module(mod)

matches = [m for m in mod.MUTANTS if m["id"] == MUTANT_ID]
if len(matches) != 1:
    print(f"could-not-evaluate: {len(matches)} registry entries for "
          f"{MUTANT_ID}", file=sys.stderr)
    sys.exit(2)
mutant = matches[0]

source = PRISTINE.read_text(encoding="utf-8")
alt = mutant["alternatives"][0]
anchor_count = source.count(alt["anchor"])

mutated, info = mod.apply_mutation(source, mutant)
if mutated is None:
    print(f"could-not-evaluate: apply_mutation refused: {info}",
          file=sys.stderr)
    sys.exit(2)
compiled = mod.compiles(mutated, mutant["id"])

# the exact registered operator text is recorded verbatim for provenance
doc = {
    "mutator_path": str(MUTATORS),
    "mutator_sha256": hashlib.sha256(MUTATORS.read_bytes()).hexdigest(),
    "mutant_id": mutant["id"],
    "mutant_execution": mutant["execution"],
    "mutant_expect_rows": mutant["expect_rows"],
    "mutant_attribution_basis": mutant.get("attribution_basis"),
    "alternatives": mutant["alternatives"],
    "alternative_applied_index": info,
    "anchor": alt["anchor"],
    "anchor_occurrences_in_pristine": anchor_count,
    "unique_applicability": anchor_count == 1,
    "mutant_compiles": compiled,
    "pristine_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
    "mutated_sha256": hashlib.sha256(mutated.encode("utf-8")).hexdigest(),
    "mutated_bytes": len(mutated.encode("utf-8")),
    "pristine_bytes": len(source.encode("utf-8")),
}
if not doc["unique_applicability"] or not compiled:
    print("could-not-evaluate: operator not uniquely applicable or does not "
          "compile", file=sys.stderr)
    print(json.dumps(doc, indent=1), file=sys.stderr)
    sys.exit(2)

MUTATED.write_text(mutated, encoding="utf-8")
doc["mutated_written_to"] = str(MUTATED)
doc["mutated_file_sha256"] = hashlib.sha256(MUTATED.read_bytes()).hexdigest()
print(json.dumps(doc, indent=1, sort_keys=True))
