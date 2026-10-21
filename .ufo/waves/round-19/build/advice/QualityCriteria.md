VERDICT: partial - every headline count reproduces (checker required=3 verified=3, pre-token missing=3; pinned grid rejected 0/3 without the pin and 3/3 with it, baseline VALID both times), but the gate-live-1 pin fails KQ14 (its verified blob says live/, the sentence says live-recovery/), the grid fails KQ20/KQ21/KQ24, the checker fails KQ20/KQ18, and the S057 admission fails KQ6/KQ7/KQ13 at named points.

Scope: private copy /tmp/kama-r19-QualityCriteria (lane HEAD 8bf99ca; round-19 edits uncommitted). Lane unmodified except this file. Every cited command has a receipt and exit in /tmp/kama-r19-QualityCriteria/out/receipts/INDEX.tsv; full map (39 evidence rows, fault-injection table, superseded receipts): /tmp/kama-r19-QualityCriteria/out/criteria-map.md. Not run: official run.py, live llama-server, live install tree, controls.py, counters.

## Claim to KQ map

| Claim / evidence | Receipts (exit) | KQ | Status |
|---|---|---|---|
| C1 `required=3 found=3 verified=3 missing=0 mismatch=0`; before tokens `missing=3` | cite-default 0; cite-before-head 1; cite-selftest 0 | 9, 14, 20 | reproduces |
| Pin `gate-live-1` (eb78788) backs "recovery output describes live-recovery/" | live-gate-1-at-eb78788 0 says `live/receipt-1`; gate1-at-1b85a24 0 says `live-recovery/` (sha 1cb5a41b…) | 14, 7 | FAIL: verified blob contradicts its sentence |
| "Four routed pointer defects become machine-checkable" | registry covers defects 2–3 only; defect 1 is prose (residual-check 0: 4 confirm / 3 partial, correct); defect 4 is untracked | 3, 14 | overclaim |
| S055 pin (1c325b2) and C2 official stdout (1b85a24) | commands-paths 0 (live/); counter-sha 0 (= official tool sha) | 14 | PASS |
| "The two agree" (c2-survivors.json vs stdout) | c2-diff 0, c2-leaves 0: counts and verdict leaves equal; tool.sha256 differs; both record an escaped child (grid-rows-escaped 0) | 14, 21 | PARTIAL: undisclosed |
| C2 counts 0/3 without pin, 3/3 with pin | grid-nopin 1; grid-pin 0; gate-pinned-negative 1 shows the pin reason | 4, 20 | reproduces |
| Lesson wording "accepted 0/3 before the pin" (round-19.md:15–18) | grid-nopin 1: rejected 0/3, i.e. 3 accepted | 20 | FAIL (inverted) |
| Pin deletion detectable (new) | gate-nopin-selftest 1 (`tree-consistent-member-swap` only); grid-pin-vs-nopin-gate 1 (0/3) | 20 | PASS |
| Grid default members (fixed denominator 3) | fixture-renamed-pinned-grid 0: `members=2 rejected=2/2`, exit 0 | 20, 12 | FAIL: silent shrink |
| S057 quotes verbatim; RUNPATH is step (3) | s057-quotes 0; s057-steps 0; ld-so-fetch 0 (sha d9b7737e…) | 13 | PASS |
| S057 word counts "11" and "14" | s057-quotes 0: 10 and 11 | 13 | FAIL (minor) |
| S057 documented revision | page says man-pages 6.19 (2026-08-03); row has only the access date | 6 | FAIL (partial) |
| S057 "identity is not authentication" and launcher-bytes claim cited to the page | s057-quotes 0: no digest, hash or auth term on the page | 13 | FAIL: needs [INFERENCE] label |
| S057 used-by lists registry/required-citations.json | s057-registry-grep 1 (no S057 in registry) | 13, 22 | FAIL |
| S057 mid-table insertion (SOURCES.md:69) | source-anchors 0; round-18.md:285 cites SOURCES.md:209-213, now 210–215 (read 207–216) | 7 | FAIL: stale anchor; no ledger (ledger-check 0) |
| SOURCES append-only (S055 qualification, S057) | git-diff-head-srcs +7/−0; sa-append-only-pair 0 on scratch commit (added [S057], violations []) | 22, 11 | PASS on pair; round-end check absent from the plan (round-19.md:43–48) |
| Census 56 → 57 rows (A 54, C 3; mined 46, queued 5, rejected 6) | census-sources 0 | 9 | PASS (count first; "exit 0" command unnamed) |
| SOURCES header "every row opened in round 10" | census-opened-dates 0: 27 rows are not 2026-10-19 (pre-existing) | 3 | FAIL (stale) |
| Axis authority (operability + calibration) | axis-authority 0: shokunin.conf:52 kama row; MISSION "Fleet shape" | 12 | PASS (no prior-coverage statement) |

## Criteria the grid or checker fails

- **Checker `tools/citation-provenance.py`:** KQ20: mismatch grading has no detector. The edited mutant (branch deleted) gives a false green, cite-mismatch-nomismatch-mutant-edited 0 (status ok, wrong digest), and survives its own selftest, cite-mutant-selftest-edited 0. Documented exit 2 for unusable git or docs is not produced: cite-nogit-explicit 1, cite-nodoc 1. KQ18: "token per material citation" is bounded by the registry; material-citations 0 finds 13 unregistered round-18 paths. KQ3: any document satisfies the check, cite-any-doc 0. KQ14: "verified" is digest correspondence only. KQ15 (by analogy): unavailable source and mismatch share exit 1.
- **Grid `tests/llamacpp-live/install-tree-grid.py`:** KQ20: silent denominator shrink (E15); kill = any nonzero exit, so a traceback counts (grid-crash-wrapper-pin 0, rejected 3/3, empty stdout); no selftest (grid-selftest-flag 2); reason never asserted. KQ21: bad input exits 1 with traceback, grid-missing-receipt 1, where the gate exits 2 (gate-missing-receipt 2); mutants go to a TemporaryDirectory. KQ24: missing input and surviving mutant share exit 1.
- **Harness `.ufo/waves/round-18/runs/run.py`:** KQ20/KQ21: `run()` compares exit codes only (line 27); `tree-grid-no-pin want=1` would accept the grid traceback; members and reason are never asserted.
- **Gate pin (`check-receipt.py` 384–390):** no failing criterion found (gate-pinned-valid 0, gate-pinned-negative 1, gate-missing-receipt 2).

## Proposed append-only corrections (not applied)

1. Re-pin gate-live-1 to 1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, sha256 1cb5a41bbfeb8f0f9306d9bf86df83d33cf9bc3aa46887c574e1dd07875574c7. candidate-checker 0 verifies digest only; the content is read in gate1-at-1b85a24. Or keep eb78788 and reword to "describes live/". (KQ14)
2. Grid: exit 2 on unreadable receipts; absent default member forces exit 1; count rejected only when stdout names the install-tree mismatch; add --selftest with renamed-member, missing-receipt, crash and pin-deletion fixtures. (KQ20, KQ21, KQ24)
3. Checker: CLI-level red/green for mismatch and exit 2; assert status labels; separate unavailable from mismatch; drop LOG.md from default docs. (KQ20, KQ18, KQ3)
4. run.py: pin run asserts `members=3 rejected=3/3` and the reason; no-pin asserts `rejected=0/3`. (KQ20, KQ21)
5. round-19.md:15–18: "accepted 0/3" → "rejected 0/3 (3 accepted)". (KQ20)
6. S057 (no commit yet, so cells may still change): fix word counts, add man-pages 6.19 (2026-08-03), label inferences, correct used-by. S051 anchor and SOURCES header: append errata. (KQ6, KQ7, KQ13, KQ3)
7. Commit the round-19 tree; run sources-append-only over each committed SOURCES pair; commit residual/assignments.json. (KQ22)
8. SCORECARD: "the two agree" → verdict-level agreement, disclose tool sha and escaped child; "four pointer defects" → "two pointer defects registry-checked". Publish a correction ledger (none exists). (KQ14, KQ7)

## Not executed or [INFERENCE]

- Official run.py, live server, live install tree (run.py:57 pins from it; not read), controls.py, counters.
- "Grid digest equals gate recomputation": inferred from the no-pin run (3 accepted). [INFERENCE]
- KQ15/KQ16 apply to the C1 rows only by analogy. [INFERENCE on scope]
- The gate's `tree-sha-mismatch-expect` case is killed without the pin, so only one case isolates the pin. (observed; not a failure)
- Escaped-child events in the counter runs: observed, not claimed by round 19.
