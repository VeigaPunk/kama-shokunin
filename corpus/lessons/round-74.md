# kama round 74 — lesson

author: kama L1 (KamaR74a2) with w1 seats. Frozen plan: `plans/round-74-claims.md`
(freeze `df18ad1e`, base `868dd701`); wave spec/dispatch `b0b903a0`. Closure pointer:
latest outside closure is round 73 (`corpus/lessons/round-73-verifier-spotcheck.md`),
which routed defects 1/2/5 → this round's C1/C2/C3.

## Gate

Candidates considered this round, with the round-73 spot-check discipline (≥1 admit,
≥1 reject; a rejection is evidence of taste):

| Candidate | Decision | Grounds |
|---|---|---|
| S546 — os-release(5) man page (man7.org) | **admit (tier A, mined)** | Opened live 2026-11-04 by seat SCR01Sources; 45,239 bytes fetched, sha256 `c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e`, retained at .ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html; located quote (16 words, §OPTIONS `ID=` entry, lines 187–194 of the retained HTML): "A lower-case string … identifying the operating system, excluding any version information and suitable for processing by scripts". Grounds the distribution component of C3's host triple. used-by: `corpus/knowledge/host-block-base-revision.md`. |
| Own-work control receipts as SOURCES rows | **reject (no row)** | Same ruling as rounds 70/73: the control outputs are lane-authored evidence cited from SCORECARD/LOG/plan; CORPUS rule 4 forbids row padding. Flip: none sought. |
| shokuknow `merge/kama/` package (142 staged rows, 65 entries) | **reject (Assimilation: none)** | No entry re-grounded this round; the id-collision check finds 9 collisions (S330 S333 S334 S335 S346 S347 S352 S353 S363) — mass drift the read-only check cannot fix; per §10, adopt nothing and record here. Receipt: `.ufo/waves/round-74/assimilation/summary.out` (`reg_ids=285 staged_ids=142 collisions=9 quarantine_rows=7`). Quarantine slice: 7 rows, all `payload-absent` (S200 S202 S206 S210 S211 S224 S230) — the register's unchecked family stays quarantined; verdicts land here, the register is never edited. |
| `considerthese/2026-10-26.md` proposals 1–4 | **reject (nothing adopted)** | Correction to the frozen plan's wording (seat SCO01 disagreed, freeze unedited): proposals 1, 2 and 3 already **landed as lane-round work** — proposal 1 = `tools/append-only-audit.py` (r46), proposal 2 = KQ97 (`corpus/QUALITY.md:477`, r53), proposal 3 = `tools/shortcut-tally.py` (r48, KQ118). Proposal 4 = KQ122 + the live pin-watch run (r73; this round's own live run at `.ufo/waves/round-74/measured/pinwatch/pin-watch-live.out`: `pins=3 current=0 behind=3 missing=0 error=0`, exit 1 — engine=sglang pin=v0.5.22 newest=v0.5.23 newer=1; engine=vllm pin=v0.32.0 newest=v0.33.0 newer=1; engine=llama.cpp pin=b11755 newest=b12098 newer=273). Nothing **new** adopted. |

Status/recheck/used-by transitions logged old→new: S546 appended `queued`→`mined` at
append time (the knowledge entry cites it; the draft row's queued status was the
pre-append state, SCR01's report records the flip). No other registry cells changed.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| 1 | number-drift | `.ufo/waves/round-73/w1-spec.json` — milestone/goal prose says "14 seats", the items array carries 15 (derivation: .ufo/waves/round-74/w1/SCR02Lesson/r73-drift-derivation.out) | none | `tools/round74-seat-count-check.py` — red demo on the r73 spec bytes (exit 1, `SEAT_COUNT_CHECK_FINDING number-drift`), green on the r74 spec (13 items, prose names 13); selftest 10/10 with the green arms proven non-vacuous (`census-flip-guard-red`). |
| 2 | landing | `corpus/lessons/round-73-verifier-spotcheck.md` §6 item 6 — r73's registry append preceded the first exit-0 mirror census | none | Round-74 runbook orders mirror-census-exit-0 before append; receipts `.ufo/waves/round-74/measured/after/mirror-census-gate.out` (`mode=mirror-gate exit=0`) precede the sources-append receipt, and `round74-seat-count-check.py --census-order .ufo/waves/round-74` exits 0 while replaying the r73 ordering red (.ufo/waves/round-74/w1/SCR02Lesson/census-order-r73.out). |
| 3 | landing | .ufo/waves/round-74/w1/EX02ClaimV2/report.md §7 — the L1's emergency C2 build overwrote the seat's completed deliverable twice before WAVE-DONE (the seat preserved the L1's first version as receipts/overwritten-peer-version.py) | `none` — §6's concurrent-writer rule binds seats, and the L1 failed to apply it to itself: an L1 emergency build must use a distinct scratch path until WAVE-DONE confirms the seat dead, and the L1 must re-read w1-results.json before integrating | Fix shown able to fail: this lesson row + the corrected record (SCORECARD preamble names the incident; the EX02 report is committed; the critic-fixture matrix re-ran against the committed bytes); the rule is now stated in the round-75 plan. |

## L1 integration addendum

- **Concurrent-write incident (the round's real defect — see Mistakes 3):** seat
  EX02ClaimV2 did NOT die. It completed a 15-arm build of the C2 module; but the L1,
  concluding from a mid-wave directory check that the seat was dead, ran an emergency
  build on the SAME checkout path and overwrote the seat's deliverable twice (the
  seat's report §7 preserves the L1's first version as `receipts/overwritten-peer-version.py`
  and documents the restorations). EX02's own tested bytes were lost with its scratch
  deletion; its committed report and receipts (15-arm selftest record, critic-fixture
  matrix, frozen-digest receipts) stand as evidence of what the fleet's dispatch
  produced. The committed instrument is the L1's replacement, re-certified end-to-end
  (scorer, selftest 9/9 incl. the `blob-reader-seam` arm MT01Mutants named for the
  surviving `c2_p2l_case_hex` mutant, gate arm 7, and a fresh run of CRT01's four
  critic fixtures against the committed bytes — `measured/after/critic-fixtures-committed-module.out`,
  with the one documented divergence: `nc2_recorded_at_hex` grades exit 0 under the
  committed module's context-reading of revision mentions vs EX02's literal reading,
  the F2c ambiguity routed to next round).
- **Freeze disagreements resolved at integration (freeze never edited):**
  - CRT01 F2b (kind boundaries): wrapped-claim = nearest token/citation lines
    separated by continuation lines (distance ≥ 2); offset-claim = adjacent (distance
    1); same-line stale keeps the inherited round-73 `stale-claim` name (the frozen
    predicate enumerates the three new arm kinds). Boundaries fixed on the frozen
    fixture bytes, documented in the module docstring.
  - CRT01 F2a blind spot closed: the selftest `stale-revision` and
    `same-line-stale-claim` arms grade the cases the frozen fixture set never
    constructs.
  - RVW01/EX03 C3 exceptions (token-strip + forward resolution to the recording
    commit): adopted as the only reading under which both frozen fixture arms pass;
    recorded in the module docstring, the knowledge entry and the SCORECARD row.
  - EX01 `total` union semantics (union of bold-canon names and newer-demonstrated
    names): the only reading satisfying both pinned numbers (fixture total=7, live
    total=22); CRT01 F1b (older-demonstrated ambiguity) routed to next round with a
    proposed pin.
  - SCO01 considerthese correction: recorded in the Gate table above.
- **Routed to the next non-author closure / next round:** F1b, F2c (context-free hex
  binding), CRT01's `nc2_two_receipts` kind fixture, MT01's requirement that any
  future C2 regression run re-probe the seam arm, RVW01's C1 non-git exit-map note
  (plain-directory fixtures vs "not a git repository" exit-2 wording).
- **Attack dispositions:** RVW01 found no shortcut meeting any frozen target (nine
  native-base attempts, receipts in its dir); CRT01 refuted no claim and its
  pre-registered gaming acceptance holds (path-independent grading verified on
  randomized-path fixture copies); MT01: 24/25 mutants killed — the survivor is the
  uncommittable case-tip fixture class (hash fixed point), covered by the seam arm;
  LAB01 reproduced the before receipt byte-for-byte and demonstrated one named
  junk-row cheat per claim, each forbidden by the frozen wording.
