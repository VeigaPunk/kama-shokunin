# R39-32 — C1 phrase-count overcount risk

## Observations

- Frozen C1 in `.ufo/waves/round-39/assimilation/preregistration.json` requires a named admitted-theme entry, a non-fitting rejected-theme entry with reason/flip, and new sourced quote evidence; base is pinned to `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`.
- The SCORECARD C1 command counts `grep -c 'Admit the amendment'` anywhere in the lesson, `grep -c '^Reject staged'`, and the exact S472 table-row prefix. Current direct counts are `1`, `1`, `1`; lesson lines 19 and 21 contain the respective decision prose and `corpus/SOURCES.md:216` contains S472. The base lesson path does not exist (`git show BASE:corpus/lessons/round-39.md` returned 128); the saved no-op control reports admit=0, reject=0, source_rows=203, met=False. The after receipt reports admit=1, rejects=1, sourced_rows=1.
- The admit phrase is not scoped to the Gate or to a decision row. A repeated/quoted `Admit the amendment` elsewhere in the lesson would increment this phrase count without creating a second admitted decision. The reject pattern is anchored to line start but similarly does not constrain section or decision semantics. No evidence inspected shows such a duplicate in the current lesson.
- More importantly, `sourced_rows=1` can prove only that one S472 row exists; C1's preregistration text calls for source evidence, and the lesson supplies that via S472's line-17 quote. The three counts alone do not establish that the counted admission is grounded in that source or is within the selected theme. The frozen predicate additionally spells out those semantic requirements, but its count command is merely textual evidence.

## Assessment

**Phrase-count overcount risk is real as a counter-design limitation, not an observed current false positive.** Current phrase counts agree with the visible single Gate decisions; the committed/working evidence does not show an actual overcount. C1's declared calibration result is consequently not falsified by this specific risk alone. Confidence: high for the command's unscoped substring behavior and observed counts; moderate for the limit's effect on the overall predicate because the frozen predicate includes semantic source conditions beyond the counts.

## Remaining unknowns

No adversarial lesson mutation was executed; this is a source/read-only inspection. The current report evidence does not establish how an independent reviewer adjudicates the prose's semantic fit.
