# R39-18 — coverage novelty

**Axes:** coverage (primary), calibration (secondary cross-check). **Frozen base:** `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`. **Evidence inspected:** read-only scratch lane `/fast/scratch/hyaku/kama-r39`; no source edits or runtime calls.

## Finding

C2's frozen *presence* predicate is met, but it does not establish its stated coverage-novelty rationale (“previously uncovered-to-the-map”). It checks only that a named README pointer, file, and S472 occur at the working tip and were absent at base. It never compares the amendment's subject matter against the base coverage map or prior knowledge. Thus the 9→9 claim is not falsified as a pointer-presence assertion; novelty is untested by that assertion.

## Observations

- `assimilation/preregistration-frozen.json` C2 predicate (lines 15–20) requires the named file, its tip existence, and S472 presence at tip/absence at base. `c2-noop.out` records `coverage_block=0 file_exists=0 cited_new=0 met=False exit=1`; `claim-after.out` records `round39_pointer=1 entry=1 S472=1`. These support the narrow existence transition only.
- Base README snapshot `assimilation/readme-base.md` includes the OpenAI model-list crosswalk entry at lines 25–32 (map index subsequently corrected/expanded in round 11), and the base crosswalk snapshot `assimilation/crosswalk-base.md` already lists OpenAI fields `data[].id`, `created`, `owned_by`, and optional `shutdown_date` (line 26); it characterizes the route as catalog/account availability and says it establishes nothing about local server health or loaded weights. Base crosswalk is dated 2026-10-20 and cites S016.
- The new amendment states that `created` is creation-time catalog metadata rather than local served-artifact identity, and line 27 records the newly opened S472 source. Its exact timestamp definition is fresh, concrete support for that interpretation, but the round's map-pointer predicate neither tests whether that semantic distinction was already covered nor requires evidence of a new covered domain. Existing base coverage already addresses the `created` field and the catalog-vs-local-readiness boundary; therefore novelty is at least narrower than an entirely new model-list subject.
- The current README round-39 row (line 551) describes the new entry as a distinction between catalog metadata and local served-artifact identity. It is present in the working tree; `git status --short` showed README and SOURCES modified and the amendment untracked, so these are working-copy observations, not committed-at-tip evidence.

## Limits

No counterfactual semantic comparison, independent coverage adjudication, or external review was performed. I do not conclude the timestamp's precise definition was already stated at base: the inspected base row names `created` and establishes the catalog/local boundary, but does not quote its definition. Accordingly, what is directly falsified is the inference that the frozen C2 counter demonstrates novelty; the C2 pointer-presence result itself remains true. No tool was installed.