# R57Item07LessonDraft — round-56 outside-defect lesson material

Axes: calibration; operability. Read-only review; no source-tree/lesson changes. Tool installs: none.

## Round-56 outside defects and exact lesson corrections

R13Lesson identifies two actionable round-56 lesson defects. The round-56 Gate reports the S513 quote as 18 words, which is supported by an independent whitespace count (18); preserve the count and make the counting convention explicit if the lesson's ≤25-word policy expects reproducibility. The Gate already marks S512 admit and S513 reject, records URLs/dates/locations/reasons/flip condition, and notes no non-author closure. For S515, retain the source row's explicit exact quote, source URL, access date and section/location; do not present an author advisor as a non-author source re-open or admit/reject spot-check. R13's finding is the prior Gate's lack of a separate non-author spot-check, not a reason to treat reviewer-seat advice as one.

The round-56 Mistakes sentence must state the precise stale historical assertion, not attribute “held” to round-55 row 1. R13 says the stale assertion was that `m-ldaudit-writable` and `m-extra-in-tree` existed / printed `met=True`; closure says they were deleted in `c2c05e30`. Separately, the round-56-start `test -e` sweep found those paths missing. Preserve that temporal distinction and do not infer a counter's old output from current file existence.

The Round-56 report also records two separate defects relevant to future lesson discipline: the battery-field substring comparator survived despite green C1/C2; and C2's roster checker accepted a no-op harness. Avoid claiming roster fidelity establishes execution or meaningful calibration. Frozen round-57 control receipts specifically say `canonical_table_reads=0`, `self_description_reads=0`, `mismatches=0 maxN=46 met=True`, exit 0; this is a demonstrated vacuous target, not evidence the repair works. The frozen round-57 context sets expected canonical count 46 and baseline mismatch 1, with C1 calibration and C2 operability; do not conflate the axes or overstate either predicate.

## Paste-ready Gate material (draft)

- **S515 — ADMIT, tier B, mined.** `git-config(1)`, https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT; opened live 2026-10-27. Locate §`GIT_CONFIG_COUNT`; quote the reopened source verbatim, at most 25 words, and record the exact location and access date. The round-56 lesson's quoted statement is: “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process's runtime configuration” (18 whitespace-separated words). Use it only to support the declared runtime-configuration-pair claim. A fresh independent source reopen is required before claiming that this quote remains current; the citation here is the round-56 record, not this seat's source reopen.
- Record each admit/reject decision with its opened source, concise rationale, and reject flip condition. Require at least one sampled admit and one sampled reject in the non-author closure; lane-dispatched author advisors may advise but cannot satisfy that independent spot-check.
- Distinguish author Gate curation from the independent closure: report the closure result as pending until a non-author has actually reopened the source and sampled the decisions. Do not count frozen screenshots/snapshots or author seat reports as a live independent reopen.

## Paste-ready Mistakes material (draft)

| Class | Evidence | Captured-by | Fix and failure criterion |
|---|---|---|---|
| stale-premise | Round-56 outside review R13Lesson, finding 2; round-55 Mistakes row 1; round-55 verifier defect 2 records deletion at `c2c05e30`; round-56 start-time existence sweep | none identified | State that the old lesson asserted the two receipts existed/printed `met=True`; state separately that the round-56-start `test -e` check found both absent. Do not say row 1 claimed they were held. Preserve the historic assertion as historical evidence, not a current inventory. |
| quote-count | R13Lesson finding 1; S513 Gate quote | CORPUS quote-length requirement catches only >25, not inaccurate stated counts | Retain 18 words (whitespace-delimited), not 16; quote remains within ≤25. A mismatch between stated and independently counted words is a failing review even when under the maximum. |
| vacuous-target | Round-56 Mistakes C2 no-op finding; round-57 frozen `.ufo/waves/round-57/controls/noop-c2.out` | Frozen counter fails to test executed calls/canonical content | Do not treat roster equality or `met=True` as proof of execution. A future predicate must fail this exact no-op (zero canonical reads, zero self-description reads) and establish actual canonical-row content binding; preserve the frozen counter/claim rather than retroactively changing its result. |
| survivor | Round-56 Mistakes comparator control; `.ufo/waves/round-56/w1/out/M08ReceiptField.md` | No comparator-ablation selftest in the frozen battery | Preserve the recorded substring counterexample and require evidence to describe the comparator actually exercised. Do not infer comparator correctness from a green unrelated roster check. |

## Distinct case 28 — independent evidence

Assigned case: test the lesson-draft/outside-defect case independently. Read-only checks, run from the lane root:

```sh
printf '%s\\n' 'A list of user-specified, ELF shared objects to be loaded before all others in a separate linker namespace' | wc -w
# 18
for p in .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out .ufo/waves/round-55/c1/battery/m-extra-in-tree.out; do test -e "$p" && printf 'present %s\\n' "$p" || printf 'missing %s\\n' "$p"; done
# missing .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
# missing .ufo/waves/round-55/c1/battery/m-extra-in-tree.out
```

Actual output: `quote_words=18`; both paths printed `missing`; the shell command exited 0 (the successful `printf` in the final branch determines the loop's status). This independently confirms the quote count and current absence only; it does not establish the historical output of those receipts. No bounded behavioral detector exists for lesson prose or this assigned drafting case, so no mutation verdict is claimed. Frozen C2 no-op evidence is independently read, not rerun: `control=no-op instrument`, `canonical_table_reads=0`, `self_description_reads=0`, `summary=mismatches=0 maxN=46 met=True`, `exit=0`.

Scratch `/fast/scratch/hyaku/kama-r57/R57Item07LessonDraft` was created and removed with an EXIT trap. No shared/source files were modified.

Report: .ufo/waves/round-57/w1/out/R57Item07LessonDraft.md