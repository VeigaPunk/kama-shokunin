# R13Lesson — round-56 Gate and Mistakes review

**Axes:** operability; calibration. Reviewed `CORPUS.md`, `corpus/lessons/round-56.md`, `corpus/SOURCES.md`, the two round-56 snapshots, and the round-55 verifier spot-check. Access date in the lesson: **2026-10-27**.

## Findings

1. **Gate / S513 quote count is inaccurate (low).** The located quote is “A list of user-specified, ELF shared objects to be loaded before all others in a separate linker namespace” at §LD_AUDIT in the `.ufo/waves/round-56/sources/ld.so.8.html` snapshot. It contains **18 whitespace-separated words**, not 16 as claimed in `corpus/lessons/round-56.md` Gate, line 15. This still meets CORPUS.md’s ≤25-word rule, so this is a count accuracy issue, not a length violation. Fix: change `16 words` to `18 words` (or provide an explicit counting method).

2. **Mistakes evidence misdescribes the cited round-55 row (medium).** Round-56 Mistakes line 19 says “Round-55 Mistakes row 1 says those receipts are held.” In the cited `corpus/lessons/round-55.md` row 1, the receipts named as “further receipts” are `m-ldaudit-writable` and `m-extra-in-tree`; row 1 does **not** say they were held, and its explicit receipt inventory is not the two paths cited in the round-56 exact check. The round-55 verifier spot-check, defect 2, specifically says both were deleted in `c2c05e30`, and calls out that the lesson statement falsely claimed their presence. The actual stale claim is that those receipts existed/printed `met=True`, not that they remain held. Fix the round-56 sentence to quote/name the exact stale claim in round-55 row 1 and distinguish that historical claim from the round-56 start-time `test -e` check.

   The appended correction itself follows CORPUS.md’s append-only rule and supplies a concrete check and failure text; its `class: stale-premise` and `captured-by: none` fields are explicit. The fix is shown able to fail: its stated `test -e` sweep reports each missing path. Note scope: the sweep concerns absent artifacts, not the older claim’s measurement result.

## Gate and change audit

- **S512 — ADMIT/mined, tier A:** URL `https://man7.org/linux/man-pages/man7/rtld-audit.7.html`; opened live **2026-10-27**; located §DESCRIPTION quote “the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared libraries” (**15 words**). Snapshot exists at `.ufo/waves/round-56/sources/rtld-audit.7.html`; its stated scope supports the variable-name gate. Registry row records man-pages 6.19 / 2025-05-17 and lesson `used-by`.
- **S513 — REJECT/rejected, tier A:** URL `https://man7.org/linux/man-pages/man8/ld.so.8.html`; opened live **2026-10-27**; located §LD_AUDIT quote (18 words; see finding 1). Snapshot exists at `.ufo/waves/round-56/sources/ld.so.8.html`. Rejection reason and flip condition are explicit in both Gate and row. Both decisions are represented in `corpus/SOURCES.md`.
- `git diff --unified=0 e10b6d39af450e8d652be9ac2986768b531fe13f efc6b3ec6fb6ea308c15855e9b8b62856f4255b7 -- corpus/SOURCES.md corpus/lessons/round-56.md` showed only S512/S513 additions to SOURCES.md (no prior row mutation). Thus no old→new `status`, `recheck`, or `used-by` change was found that requires a Gate log.
- **Residual / verification gap:** CORPUS.md says the Gate records spot-check results, but round-56’s Gate has no independent non-author spot-check result. The assigned evidence was checked here; this review is not evidence of an independently reopened live source. The task does not ask me to alter lane-owned files; corrections are recommendations only.
