# R39-09 — quarantine rows and disposition

Axes: **calibration** and **coverage** (read-only observations).

## Counterexample / evidence

The round-39 lesson's quarantine paragraph is an explicit disposition, not evidence that the slice was newly evaluated in round 39. It says seven rows (S200, S202, S206, S210, S211, S224, S230) were already hand-checked in round 36 and none was appended. The frozen slice at `.ufo/waves/round-39/assimilation/quarantine-slice` lists exactly those seven IDs, all labeled `payload-absent`. Comparing the seven per-row verdicts in `corpus/lessons/round-36.md:51-57` confirms materially distinct outcomes: S200/S210/S211 absent; S202 present but not appended; S206 present but hosted/out of province; S224 quote not located; S230 present and covered by S329. Thus the slice's common `payload-absent` label does not mean all seven sources were absent, nor does it encode their round-36 dispositions. The lesson does preserve those individual dispositions and says no row from that register was appended.

The most concrete disposition dependency is S206: `corpus/SOURCES.md` contains S206 as `mined`, and `corpus/knowledge/serving-alias-contract.md` is its `used-by`; round-36 says that source is outside kama's local-serving province. This is not a new round-39 admission or a new quarantine clearance. Treating the round-39 slice's shared class as a new verdict, or treating the S206 registry row as evidence of in-province fit, would erase the recorded scope boundary.

The evidence also shows the slice was copied into the round-39 assimilation package and the lesson repeats its seven IDs/dispositions, but no new hand-check receipt for those seven appears in the round-39 assimilation artifacts reviewed. The round-39 disposition is therefore a carry-forward of round-36 decisions, not a fresh source check. This does not contradict the preregistered C1/C2 predicates, which concern the new OpenAI source and coverage pointer, not quarantine disposition.

## Axis impact

- **Calibration:** no counterexample to the frozen C1 decision predicate found in this quarantine slice. However, any claim that round 39 revalidated the seven quarantine rows would be unsupported; the lesson itself attributes their hand-check to round 36.
- **Coverage:** no counterexample to frozen C2 found. The seven-row quarantine set is not evidence for the new S472 coverage pointer. S206's `used-by` is a source-to-entry reference, while its recorded out-of-province status remains a separate scope limitation.

## Smallest safe correction

Keep the existing no-append dispositions and the round-36 verdicts. If describing these rows in round-39 reporting, state that their status is carried forward from round 36 and retain the per-ID outcomes; do not call them newly checked, relabel all as absent, or infer that S206 is admitted as an in-province source. No quarantine row should be released or disposition changed on this evidence.
