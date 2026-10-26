# Round 48 frontier step-3 sweep — routed defects (closures 44–47) vs lesson Mistakes rows and QUALITY criteria

Verdict: **4 routed items are lost or were closed without capture** (F1 dropped after deferral; F2 closed-without-capture, class recurred; F4 never addressed; F5 never tracked), **2 named sub-items of r46-D3 never became a row** (F3), and **2 items closed-without-capture without recurrence** (F6, F7). Operator/L0 items (F8) stay open by design and are not lane defects. No spot-check disagreement went uncaptured: closures 44–47 agree with the Gate on every sampled admit/reject (8/8, 6/6, 5/5, 6/6), so there is no disagreement side to this sweep.

## Method

Compare each routed item in `corpus/lessons/round-{44,45,46,47}-verifier-spotcheck.md` §Routed defects (the "outside closures") against (a) `## Mistakes` rows in `corpus/lessons/round-{44,45,46,47}.md` (and the round-48 lesson draft), and (b) `corpus/QUALITY.md` KQ rows (added rounds 44–47: KQ58–KQ71). Lane tip read: `380bcdff9c8af06997c482f6eb03db926a794a2b` (build) / `b85783e889c261ff870da65d091ff1014ffe7c10` (wave-spec tip). Commands below run against a scratch clone; reads are `git grep <tip>` / `git log`.

## Routing ledger (closures 44–47 → lessons 44–47 + QUALITY)

| Closure item | Routed for | Disposition in later lessons | Captured as Mistakes row / KQ? |
|---|---|---|---|
| r44-D1 report seat count 64/65 | r45 | Fixed: r45 row 3; KQ62 | **yes** (r45#3, KQ62) |
| r44-D2 commit tip-side receipts | r45 | Fixed at r45 (tip receipts @ `82b5e9d3`, verified r45 closure §2) | **no** — no row, no KQ; class recurred as r47-D9 (→ r48 draft row 2) — F2 |
| r44-D3 registry hygiene: cite S483, not S480/S481 | r45 | Fixed: r45 Gate "Rows touched old→new" (round-45.md:19) | **no** — closed without capture — F6 |
| r44-D4 manifest-crosscheck probe vs gate | r45 | Fixed: r45 row 4; KQ63 | **yes** (r45#4, KQ63) |
| r44-#5 carried: counters prove facts not sufficiency + owed rows (S038, S477, S041/S046/S055, S014/S058, S010/S019/S048) + rerank candidates + base-unresolved producer | r45 | Sufficiency family → r47 row 1 (tally check). Owed recheck rows were covered by r45 C1 (11 keys). Rerank candidates: never re-checked. base-unresolved producer: never addressed | sufficiency **yes** (r47#1); rerank candidates **no** — F5; base-unresolved **no** — F4 |
| r44-#6 operator L0 (r35/r39/r41-43) | r45 | Still open in r45#5, r46/47 operator bullets | n/a operator-owned (F8) |
| r45-D1 claim-outcome reader re-freeze | r46 | Deferred by r46 preregistration (round-46.md:12; KQ65 samples committed, "no reader was written or run"); then **absent from every later routing** | **no** — dropped — F1 |
| r45-D2 freeze timestamp (KQ64) | r46 | Fixed at r46 freeze (receipt committed, `exit=0`) | yes (r45#1, KQ64) |
| r45-D3 evidence durability: model locator | r46 | Fixed: r46 row 1; KQ66 | yes (r46#1, KQ66) |
| r45-#4 carried: still frontier S013, S022, floating-series, S002–S004, llama.cpp after b11889 + sufficiency | r46 | Frontier rows never re-checked, never tracked; sufficiency half → r47 row 1 | frontier **no** — F5; sufficiency yes (r47#1) |
| r45-#5 operator/driver: dispatcher stall (N-D), salvage (N-A) | r46 | N-D → r46 row 2; N-A driver-side | N-D yes (r46#2); N-A n/a |
| r46-D1 `---`-line blind spot | r47 | Fixed by r47 C1 (v2 numstat) | yes (r46#6) |
| r46-D2 restoration measure drift | r47 | Fixed by r47 C1 (window max) | yes (r47#2) |
| r46-D3 C1 sufficiency: K1Cheat relocation, auto-picked reworded witnesses, V1Code F1–F4 → row-or-drop | r47 | r47 row 1 captures the family + shortcut tally; **the two named sub-gaps are not itemized in the row or in any later claim** | family yes (r47#1); sub-items **no** — F3 |
| r46-D4 hexrun red gate (unknown=21) | r47 | Fixed: r47 screwed 22 hexrun ledger rows + evidence; closure re-verifies `unknown=0` | **no** — closed without capture — F7 |
| r46-D5 dead log pointer | r47 | Fixed by r47 C2 (v4 null log_path) | yes (r47#3) |
| r46-D6 N3Fleet adjacency | operator | Not acted on (round-47.md:14, "operator/aggregator") | n/a operator-owned (F8) |
| r47-D1..D9 | r48 | All dispositioned in r48 preregistration `routed` (r47-D1..D4,D6→C2; D5→C1; D7→disclosed limit; D8→frontier; D9→Mistakes row 2); r48 lesson draft rows 2/3 already carry D9 and D1 | yes (routed block; draft rows) — pending r48 lesson finalization |

## Findings

### F1 — r45-D1 (claim-outcome reader re-freeze) was deferred once, then dropped: never a Mistakes row, never a criterion, absent from all later routing

- Source side: `corpus/lessons/round-45-verifier-spotcheck.md:146` — "the 126-row ledger is now known data. Any reader frozen after it is post-data. A re-claim on this ledger needs the KQ65 sample control … committed and scored *before* the new reader sees the ledger, and must cite this closure's recomputation (58/61, o1, u2, other 1, absent 1) as the outside reference. Alternatively, claim on a population the reader has not seen (rounds 45+)."
- Deferral: `corpus/lessons/round-46.md:12` — "r45-D1 (claim-outcome reader re-freeze) is deferred by the preregistration. The hand-read KQ65 sample … is committed this round as wave evidence … No reader was written or run."
- Loss: the item never reappears: r46 closure routed list (`round-46-verifier-spotcheck.md:137-142`) has no r45-D1; r47 lesson routed block (`round-47.md:14`) lists only r46-D1..D6; r47 closure (`round-47-verifier-spotcheck.md:97-106`) lists D1..D9; r48 preregistration `routed` keys are exactly `r47-D1..D9`. `git grep -n 'r45-D1' 380bcdff -- corpus/lessons/` → 0 matches; `claim-outcome` appears after r46 only in wave-seat evidence, never in a lesson row or KQ.
- Why it matters: KQ65 covers "a counter that reads outcomes from cited lines is frozen only after it reads a hand-picked sample" — but it does **not** encode the known-data constraint (sample must be scored before the reader sees *this already-published ledger*, plus the mandatory citation of the r45 closure recomputation, plus the unseen-population alternative). If the lane ever re-claims the round-10..45 claim-outcome ledger with a fresh reader, nothing forces pre-scoring on the committed S8Sample/R8Sample sets, and the r45 failure mode (an honest ledger failing its own counter) can recur unannounced.
- Proposed row (class `dropped-deferred`): "A re-claim of the claim-outcome ledger (rounds 10–45) freezes its reader only after that reader is scored on the committed KQ65 sample sets (`.ufo/waves/round-46/w1/out/S8Sample{1,2,3}/sample.tsv`, `R8Sample/sample.tsv`) and the claim cites the round-45 closure recomputation (58/61) as the outside reference; a claim on rounds the reader has not seen is exempt." Fix able to fail: a checker that greps the round's preregistration/claim for a reference to the sample sets when the claim's counter reads the ledger — fails against the r45 v1/v2 readers (`c2-v1.out`/`c2-v2.out`, `valid=91 bad=35` / `valid=103 bad=23`) and against any hypothetical re-claim today (no such reference exists anywhere at tip).

### F2 — r44-D2 (commit tip-side receipts) closed without capture; the class recurred as r47-D9

- Source: `round-44-verifier-spotcheck.md:109` (report states r42 counter, capability census and 12 `run … →` facts at tip with no tip receipts; only `ef76777e` receipts exist).
- Fix landed: r45 committed tip receipts at `82b5e9d3`; r45 closure §2 (lines 96–102) verifies them and closes D2. No Mistakes row in r45 (rows 1–5) or r46/r47 encodes the obligation.
- Recurrence: `round-47-verifier-spotcheck.md:105` (r47-D9): the r47 report again says checks were "re-run at the final tip `6b7e6cf8`" while the committed `*-fix.out` receipts show `tip=3442d707`. The class is now captured only via r48 lesson draft row 2 (`round-48.md:29`, "from round 48 every regression receipt cited in the report is re-run at the final lane tip and committed with its `tip=` line"). If r47 had not re-hit it, the lesson would still be empty.
- Proposed addition to r48 row 2: cite r44-D2 as the first instance (`round-44-verifier-spotcheck.md:109`) so the row records both occurrences; the shown-able-to-fail check is the report-vs-receipt `tip=` comparison, which fails on the r47 report vs `*-fix.out` (3442d707).

### F3 — r46-D3's named sub-gaps ("reworded witnesses could be auto-picked"; "V1Code's F1–F4") never became a row or a later claim

- Source: `round-46-verifier-spotcheck.md:139` — D3 lists three open items (K1Cheat relocation script; reworded witnesses auto-picked; V1Code F1–F4) and demands: "write it as a lesson row with a check that can fail, or drop it with a reason."
- What happened: r47 row 1 (`round-47.md:45`) captures the sufficiency family and the shortcut tally but names neither "reworded witnesses" nor V1Code F1–F4; r48 C1's statement (preregistration) covers V1Ctr F1, regressed-exit, region binding and fixtures, not V1Code's drafter-checker defects. `git grep -l 'V1Code' 380bcdff -- corpus/lessons/` → only round-44.md, round-46.md, round-46 spotcheck; `reworded witness|auto-picked` → only the r46 closure. The r46-D3 "row or drop with reason" instruction was not executed for these two named items.
- Proposed row (class `stale-premise`, sub-item): "The release-recheck drafter's checker gaps (V1Code F1–F4) and the auto-pickable reworded witnesses either enter the next release-recheck counter's limit section or are dropped with a stated reason (r46-D3)." Fix able to fail: grep the round's C1 claim/receipt for `witness`-policy text; absent → exit 1.

### F4 — `base-unresolved.tsv` has no producer: routed twice, explicitly left unaddressed, then vanished

- Source: `round-43-verifier-spotcheck.md:110` (#6, "`base-unresolved.tsv` has no in-repo producer"), carried again `round-44-verifier-spotcheck.md:112` (#5), and recorded as unaddressed in `round-44.md:56` (D6: "`base-unresolved.tsv` producer not addressed").
- Status at tip: the file survives only as round-43 wave artifacts (`.ufo/waves/round-43/c2/base-unresolved.tsv`, `.ufo/waves/round-43/w1/out/W1F02/base-unresolved.tsv`); `git grep -l base-unresolved 380bcdff -- tools/ scripts/` → nothing. No committed command emits it; no later round mentions it; no lesson row or KQ covers "a committed assertion at freeze with no rerunnable producer."
- Proposed row (class `unresolved-data-integrity`): "Every `.tsv` committed as counter output has a committed producer command in `tools/` or `scripts/` that emits it, or the file is removed from evidence (r43#6/r44#5)." Fix able to fail: `git grep -l base-unresolved <tip> -- tools/ scripts/` is empty today → exit 1; the check passes only when a producer exists or the file is gone.

### F5 — carried frontier rows were never re-checked and never tracked (r44#5 rerank candidates; r45#4 S013, S022, floating-series, S002–S004, llama.cpp after b11889)

- Sources: `round-44-verifier-spotcheck.md:112` (rerank candidates: "the next release recheck should carry it", echoed in `round-44.md:37`); `round-45-verifier-spotcheck.md:149` (S013, S022, floating-series rows, S002–S004, llama.cpp after b11889).
- Checks: r45 C1 = the 11 planned keys; r46 C1 = the same 91 on-release llama.cpp rows (no ollama/vLLM docs rows); r47 had no freshness claim. `git grep -n 'floating-series' 380bcdff -- corpus/lessons/` → only the r45 closure. These rows are not defects, but they are routed work that never became a tracked row (the r46 sweep's own rule: a carried item surviving three closures without a lesson row must become one or be dropped with a reason).
- Proposed row (class `carried-uncaptured`): "A routed recheck frontier (S013, S022, floating-series rows, S002–S004, rerank candidates) enters the next release-recheck population or is dropped with a stated reason; carrying it a fourth time without either is the defect." Fix able to fail: a checker comparing the round's recheck ledger population against the carried list — today the list appears in no ledger.

### F6 — r44-D3 (registry hygiene: process-qualification citations) closed without capture

- Source: `round-44-verifier-spotcheck.md:110` (D3: entries cite "(S480, S481)" where S480 disclaims and S481 is tier C; cite S483).
- Fix: r45 Gate "Rows touched old→new" (`round-45.md:19`) updates S483 `used-by` and the entries; r45 closure verifies (line 105). No Mistakes row, no KQ encodes "cite the row whose `teaches` supports the claim" — KQ31/KQ22 govern cell immutability, not id choice. The class has not recurred (low priority; record for completeness).

### F7 — r46-D4 (hexrun unknown=21) closed without capture

- Source: `round-46-verifier-spotcheck.md:140` ("Close or ledger the 21 unknowns").
- Fix: r47 filed 22 hexrun ledger rows with committed evidence (`round-47.md:14`; seats X4Hex*); r47 closure re-derives `unknown=0` at tip. No Mistakes row. This is a substantive fix, but no row/criterion records the "unknowns must be ledgered, not just described" rule (KQ55 predates it and does not find the ledger-row requirement).

### F8 — operator/L0 items (planner seat, MISSION axes pair, parked worktree, N3Fleet adjacency) — open since rounds 35–43, never lesson rows

- Sources: r44 closure:113, r45 closure:150, r46 closure:143, r47 closure:106; N3Fleet adjacency routed to operator (`round-47.md:14`). These are operator-owned/routed, not lane defects; they are still open by statement and were never (and need not be) lesson rows. Flagged so the integrator can pass them to the operator route.

## R47-D items: captured by the r48 routed block (not lost)

The r47 closure's D1–D9 are all dispositioned in the r48 preregistration `routed` block (keys `r47-D1..D9`), and the r48 lesson draft already carries rows 2 (D9) and 3 (D1); D7 (prerelease cliff) is a disclosed limit and D8 (sources guard parser) is frontier-deferred to seat X9SourcesGuard. Caveat: D7/D8 are deferrals with no round bound — the same pattern that lost F1; per the r46 sweep rule, the r48 lesson should either name the round or record a reason.

## File:line anchor index (both sides)

- Closures: `round-44-verifier-spotcheck.md:108-113`; `round-45-verifier-spotcheck.md:146-150`; `round-46-verifier-spotcheck.md:137-143`; `round-47-verifier-spotcheck.md:97-107`.
- Lessons: `round-44.md:37,56`; `round-45.md:19,27-31`; `round-46.md:12,35-42`; `round-47.md:14,45-50`; `round-48.md:14,28-30` (draft, untracked in workspace).
- SearchITY: KQ58–KQ71 (`corpus/QUALITY.md:373-398`); no KQ covers F1, F2, F4, F5, F6, F7.
