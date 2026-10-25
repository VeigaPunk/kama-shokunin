# R39 Attack30 — overlap with consumer-registry

**Axes:** calibration; coverage. Read-only inspection of the frozen base and lane working evidence. No files modified, no mutation run.

## Counterexample / finding

The proposed round-39 coverage addition is not genuinely new knowledge relative to the existing corpus, although it is a new README map pointer and new source row. The specific distinction—OpenAI model-list `created` is catalog metadata, not local endpoint identity/readiness—was already documented in the base `corpus/knowledge/served-identity-crosswalk.md`, which cites S016 and states that OpenAI's reference describes available models but says nothing about local server health, loaded weights, or execution (lines 9, 26, 39, 50). Round-39 S472/amendment repeats that same bounded distinction and says `id` remains the endpoint identifier. The target item mentions `consumer-registry`; that file is **not** the closest actual overlap: base `consumer-registry.md` has zero occurrences of `created` or `catalog metadata` and concerns loopback consumer pins. The direct overlap is with `served-identity-crosswalk.md`.

## Evidence

- Base identity: lane scratch HEAD is exactly frozen base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`.
- Base crosswalk (`corpus/knowledge/served-identity-crosswalk.md`): lines 9 and 26 already say OpenAI model-list documents catalog/account availability, not local runtime proof; line 39 warns against using `shutdown_date`/`owned_by` as readiness; line 50 says the reference has no residency field. This is semantically overlapping coverage, while the precise `created` field is newly sourced.
- Base `corpus/knowledge/consumer-registry.md`: no matches for `created` or `catalog metadata`; it is about endpoint consumers and pins. So an assertion of direct overlap with that registry would misidentify the prior authority.
- The working C2 addition creates a new coverage-map entry and S472: README pointer and amendment file were absent at base, and SOURCES count changes from 203 to 204 (working row S472 at line 216). `claim-after.out` records C2 `9 -> 9`; no-op C2 fails at base. These prove a newly registered map pointer/source row, not novelty of the underlying distinction.
- The amendment (`corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md`) grounds the field-specific wording with a newly opened quote, but it does not displace or contradict the existing crosswalk's broader catalog-vs-readiness boundary.

## Impact and smallest safe correction

**Coverage:** materially weakens any interpretation of C2 as adding a novel concept; C2's frozen predicate is presence-based and can remain true, but should be described as a field-specific extension/re-grounding of existing crosswalk coverage, not as uncovered knowledge. **Calibration:** no direct counterexample to the frozen C1 predicate: S472's quote supports the narrow `created` claim, while prior S016 coverage shows the boundary was already broadly known. Do not change either predicate or numeric score on this evidence.

Smallest safe correction: annotate the round-39 coverage claim/report to credit `served-identity-crosswalk.md:9,26,39,50` as prior overlapping coverage and call S472's `created` quote a field-specific sourced extension. Do not point to `consumer-registry.md` as the prior authority; it is the wrong file for this distinction.