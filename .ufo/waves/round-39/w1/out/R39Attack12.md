# R39-12 — README map pointer count

Item: inspect committed/working evidence only for the README map pointer. Axes: calibration (C1) and coverage (C2). Lane content was not modified; no tools installed.

## Observable findings

- At frozen base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`, `corpus/README.md` has no pointer to `served-identity-crosswalk-amendment-2026-10-24-r16.md`; the frozen `readme-base.md` ends after the round-36 addition and likewise has no pointer.
- The working `corpus/README.md:551` adds exactly one coverage-map row for that amendment, labeled round 39 and citing S472. Independent literal count: **0** such filename matches at base, **1** coverage-map row at tip. `claim-after.out` independently reports `round39_pointer=1`; `c2-noop.out` records the base no-op as `coverage_block=0`.
- The filename also occurs once in the round-39 frontier prose at `README.md:565`, so there are **two total literal filename occurrences** at tip, but only one map pointer. The distinction is important: the C2 predicate concerns the round-39 coverage block, not every textual mention.
- Tip diff adds the map row and frontier disposition; it does not alter or remove existing map entries. The amendment file and S472 source row are present in the working tree; the C2 preregistration requires these alongside the pointer.

## Verdict

No falsification found for this item: C2's README pointer component is supported as one new map row, absent at base and present at tip. The total-occurrence count is two only when frontier prose is included; reporting that as two map pointers would be incorrect. This scoped count alone does not establish all C2 conditions or assess the frozen scores beyond the evidence cited above.