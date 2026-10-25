# R39-17 — source tier and row schema

## Scope / evidence
Read-only inspection of the lane scratch working copy `/fast/scratch/hyaku/kama-r39`, HEAD `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea` (the frozen base), plus its working-tree round-39 evidence. No commands were run that modify source files, Git/JJ state, or the index; no tools were installed. Report path is `.ufo/waves/round-39/w1/out/R39Attack17.md` in the report repository.

## Observable findings

- The current `corpus/SOURCES.md` registry declares an 11-column schema at lines 11–12: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`. The contract above it says tiers are scoped to `scope` (lines 3–7); tier is not a universal source-ranking assertion.
- S472 is present in the working tree at `corpus/SOURCES.md:216`. Its tier is `A`, scope is explicitly limited to OpenAI model-card field semantics (`created` versus endpoint identifier), and its `used-by` names the admitted amendment. Its source is OpenAI's List models markdown reference; status `mined`, opened `2026-10-25`, recheck `90d`.
- The S472 source note `.ufo/waves/round-39/assimilation/S472.md:1-10` records the reference subsection, `id` and `created` descriptions, open date, and scope boundary. The round lesson `corpus/lessons/round-39.md:19,27` records the same citation and describes S472 as a transformed row conforming to the 11-column contract; it further asserts full-repository scratch mirror validation exit 0 with W04-only warnings.
- The row schema is observable and S472's displayed cells are consistent with that schema. However, evidence that the *validator actually enforces exactly 11 fields and the tier vocabulary/meaning* is not established by these read-only observations alone. The lesson reports a prior validation run; this assignment did not rerun it, and the captured `census-end.out` is census output with W04 warnings, not a standalone schema-validation receipt. Consequently this attack neither falsifies nor independently confirms the validator's enforcement behavior.
- The source tier A is a declared scoped classification, not proof that the source was independently fetched during this inspection. The lesson records a prior opening/re-grounding and quote, but I did not make a network request.

## Axes / verdict
- **Calibration:** No counterexample observed to the stated scoped tier and row-shape claims. No basis here to change the frozen score.
- **Coverage:** S472 and its `used-by` amendment linkage are visible; validator enforcement and independent source retrieval are outside the exercised evidence. No basis here to change the frozen score.

## Gates and limits
Only repository/evidence reads were performed. No tests, validators, census, external fetch, or runtime checks were executed. The working tree contains uncommitted round-39 changes; findings about S472 explicitly describe working-tree evidence, not the frozen HEAD. No product code or source evidence was changed.
