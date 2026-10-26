# Round 49 frontier step-3 sweep — routed defects (closures 45–48) vs lesson Mistakes rows and QUALITY criteria

Seat N5Mistakes. Lane kama, round 49, leaf. Read-only analysis against the lane at the round-49 build `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (base `438127bc…` = round-48 closure). No counter was run; no scratch needed; every citation below is from committed lane files (paths under `corpus/lessons/`, `corpus/QUALITY.md`, `registry/`, `.ufo/waves/round-{45..49}/`).

Verdict: **from closures 45–48, 6 routed items have still never become a lesson Mistakes row or a QUALITY criterion** (F1 r45-D1 dropped; F2 r46-D3 sub-gaps; F3 r46-D4 closed without capture; F5 carried frontier rows; F6 r44-D3 closed without capture; F8 r47-D7 carried, then absent from round-49 planning), **3 items closed by implementation without capture** (F7 r47-D2; R1 in round-49 C1 claim, capture pending; the R5 witness/binding halves in round-49 C1/C2 claims, capture pending), **1 is an unfixed unbounded deferral whose class is captured but whose fix is not** (F9 r47-D8 sources guard), **1 R5 sub-item is open and disclosed without a row** (F11b record-time fetch; F11e sub-20 threshold), and **operator/L0 items stay open by design** (F12). The round-48 closure's R2/R3/R4 **are now captured** in the round-49 lesson draft rows 1–3. No spot-check disagreement went uncaptured: closures 45–48 agree with the Gate on every sampled admit/reject (2/2+2/2, 2/2+2/2, 3/3+3/3, 2/2+3/3), and each reject is recorded in its round's lesson Gate.

## Method

Compare every routed item in `corpus/lessons/round-{45,46,47,48}-verifier-spotcheck.md` §Routed defects (and the closure-level conformance notes) against (a) `## Mistakes` rows in `corpus/lessons/round-{45,46,47,48}.md` plus the round-49 lesson draft `corpus/lessons/round-49.md`, and (b) `corpus/QUALITY.md` KQ rows (added rounds 45–48: KQ62–KQ75). Evidence commands (all read-only, run against the lane path):

- `grep -nE '^\*\*D[0-9]|^\*\*R[0-9]|^\*\*Operator|^\*\*Carried' corpus/lessons/round-4[5-8]-verifier-spotcheck.md` → item line anchors (listed per finding).
- `grep -nE '^\| [0-9]+ \| ' corpus/lessons/round-4[5-8].md` → Mistakes row anchors.
- `grep -n 'floating-series|base-unresolved|rerank' -R corpus/lessons registry/` → only round-45 closure:149, round-43/44 closures, and the round-46 sweep transcript quote the list; no later file.
- `grep -n 'V1Code|reworded witness|auto-picked' -R corpus/lessons/` → only round-44.md, round-46.md, round-46 spotcheck.
- `grep -n 'r45-D1' -R corpus/lessons/ .ufo/waves/round-49/` → 0 matches (drop confirmed).
- `grep -n 'prerelease' .ufo/waves/round-49/preregistration.json corpus/lessons/round-49.md` → 0 matches (r47-D7 dropped from round-49 planning).
- `grep -n 'sparse|GiB|member size' corpus/QUALITY.md` → 0 matches (no R1 criterion).

## Routing ledger (closures 45–48 → lessons 45–49 + QUALITY)

| Closure item | Routed for | Disposition in later lessons | Captured as Mistakes row / KQ? |
|---|---|---|---|
| r45-D1 claim-outcome reader re-freeze | r46 | Deferred at r46 (`round-46.md:12`: "No reader was written or run"); **absent from every later routing**; r48 lesson row 4 names it only as a dropped example | **no** — F1 |
| r45-D2 freeze timestamp (KQ64 + receipt) | r46 | Applied at r46 (`round-46/freeze/prereg-time-check.out`, exit 0; committed `4a2a4d55`, see R0Prereg note) | yes (r45#1, KQ64) |
| r45-D3 evidence durability: model locator | r46 | r46 row 1; KQ66 | yes (r46#1, KQ66) |
| r45-#4 carried frontier: S013, S022, floating-series, S002–S004, llama.cpp after b11889 | r46 | None re-checked, none tracked; llama.cpp-after-b11889 partially covered by r46 C1 (91 on-release rows at b11906); the S013/S022/floating-series/S002–S004/rerank list appears nowhere after the r45 closure | **no** — F5 |
| r45-#5 operator/driver (N-D stall, N-A salvage, L0) | r46 | N-D → r46 row 2; N-A driver-side, never a row; L0 operator | N-D yes (r46#2); N-A/L0 no (F12) |
| r46-D1 `---`-line blind spot | r47 | r46 row 6; KQ70 | yes (r46#6, KQ70) |
| r46-D2 restoration measure drift | r47 | r47 row 2; KQ70 | yes (r47#2, KQ70) |
| r46-D3 C1 sufficiency: row-or-drop | r47 | r47 row 1 captures the family + tally; **the two named sub-gaps (reworded witnesses auto-picked; V1Code F1–F4) never itemized** | family yes (r47#1); sub-gaps **no** — F2 |
| r46-D4 hexrun red gate (unknown=21) | r47 | Fixed at r47: 22 ledger rows + evidence (`round-47.md:14`; closure re-verifies `unknown=0`). No Mistakes row, no criterion (KQ55 predates; does not require ledger-row evidence) | **no** — F3 |
| r46-D5 dead log pointer | r47 | r47 row 3; KQ69 | yes (r47#3, KQ69) |
| r46-D6 N3Fleet adjacency | operator | Not acted on (`round-47.md:14`) | n/a operator-owned (F12) |
| r47-D1 C2 counter sufficiency | r48 | r48 row 3; KQ74 | yes (r48#3, KQ74) |
| r47-D2 replay loop over all three receipts | r48 | Implemented in r48 C2 (`replayed=3/3`, r48 closure :49; r48 routed block). No Mistakes row; neither KQ69 nor KQ75 encodes multi-receipt coverage | **no** — closed without capture, F7 |
| r47-D3 record-time provenance | r48 | KQ74 (record-time binding); r48 row 3's sibling | yes (KQ74) |
| r47-D4 comparison depth | r48 | KQ75 | yes (KQ75) |
| r47-D5 C1 counter gaps | r48 | KQ72 (regions/binding), KQ70 (line model); fixture coverage in r48 C1; mutant survivors disclosed in SCORECARD | mostly yes (KQ70/72) |
| r47-D6 URL drift (main→pinned) | r48 | KQ74 pinned-model clause; S492 row | yes (KQ74) |
| r47-D7 prerelease cliff | r48 | r48 routed block: "frontier: disclosed limit; no cache hardening this round"; carried again in r48 R5 (r48 closure :120); **absent from r49 preregistration/lesson** | **no** — F8 |
| r47-D8 sources-append-only parser | r48 | Class captured as r47 row 5; fix NOT landed (K0Harm F1 at r48 build: exit 2 on every revision since r45; proposed patch in wave evidence never integrated); no round bound; absent from r49 planning | class yes (r47#5); fix **no** — F9 |
| r47-D9 receipt-tip precision | r48 | r48 row 2 | yes (r48#2) |
| R1 verify_archive_member unbounded size | r49 | In round-49 C1 claim (cap=1; statement cites Sen2Live F1/R1). No Mistakes row, no KQ (QUALITY.md ends at KQ75) | **no** (in-flight) — F10 |
| R2 report filed with placeholders, rewritten in place | r49 | r49 lesson draft row 1 | yes (r49#1) |
| R3 census W01 paraphrased | r49 | r49 lesson draft row 2 (KQ60 existed but did not prevent recurrence) | yes (r49#2) |
| R4 prompt route map (role share) | operator + r49 | r49 lesson draft row 3 (role share); the round-47 closure's "quoted map matches" row correction stays operator-side | share yes (r49#3); doc correction operator (F12) |
| R5 replay never witnesses server execution (K2Cheat/K2Urlswap) | r49 | In round-49 C1 witness leg (predictate `witness=1`). No row/criterion yet | **no** (in-flight) — F11a |
| R5 record time never fetches URLs (K2Record) | r49 | Open; K2Record (r48 wave) documents why no record-time fetch is added; r48 limits disclose | **no** — F11b |
| R5 surviving mutants (C1 21/52, tool 15/55, C2 6/27) | r49 | Disclosed in SCORECARD; no kill-threshold criterion exists by design | **no** (disclosed) — F11c |
| R5 content-blind exemption + substring declaration binding (K1Regions/K1Binding) | r49 | In round-49 C2 v4 claim (origin, whole-word, negation, wildcard). KQ72 covers the region cell only | **no** (in-flight) — F11d |
| R5 sub-20-line deletions unwatched (L1Lowthr; LOG loss ed135b3c) | r49 | Open; r48 C1 limits disclose ("sub-threshold deletions are not graded") | **no** — F11e |

## Findings

### F1 — r45-D1 (claim-outcome reader re-freeze) was deferred once, then dropped: never a row, never a criterion, absent from all later routing

- Source side: `corpus/lessons/round-45-verifier-spotcheck.md:146` — "the 126-row ledger is now known data. Any reader frozen after it is post-data. A re-claim on this ledger needs the KQ65 sample control … committed and scored *before* the new reader sees the ledger, and must cite this closure's recomputation (58/61, o1, u2, other 1, absent 1) as the outside reference. Alternatively, claim on a population the reader has not seen (rounds 45+)."
- Deferral: `corpus/lessons/round-46.md:12` — "No reader was written or run."
- Loss: `grep -n 'r45-D1' -R corpus/lessons/ .ufo/waves/round-49/` → 0 matches. The r46/r47/r48 closures route only D1–D6 / D1–D9 / R1–R5; the r48 routed block keys are exactly `r47-D1..D9`. r48 lesson row 4 (`round-48.md:31`) names r45-D1 as a *dropped example* but gives it no row, no fix, no criterion.
- Why it matters: KQ65 covers "a counter that reads outcomes from cited lines is frozen only after it reads a hand-picked sample", not the known-data constraint (sample scored before the reader sees *this already-published ledger*), not the mandatory citation of the r45 closure recomputation, not the unseen-population alternative. A fresh reader over rounds 10–45 can still recur the r45 failure mode unannounced.
- Proposed row (class `dropped-deferred`, updates r48 F1): "A re-claim of the claim-outcome ledger (rounds 10–45) freezes its reader only after that reader is scored on the committed KQ65 sample sets (`.ufo/waves/round-46/w1/out/S8Sample{1,2,3}/sample.tsv`, `R8Sample/sample.tsv`) and the claim cites the round-45 closure recomputation (58/61) as the outside reference; a claim on rounds the reader has not seen is exempt." Fix able to fail: a checker that greps the round's preregistration/claim for a reference to the sample sets when the claim's counter reads the ledger — today no such reference exists anywhere at tip (exit 1); against the r45 v1/v2 readers it fails (`c2-v1.out`/`c2-v2.out`, `valid=91 bad=35` / `valid=103 bad=23`).

### F2 — r46-D3's named sub-gaps ("reworded witnesses could be auto-picked"; "V1Code's F1–F4") never became a row or a later claim

- Source side: `corpus/lessons/round-46-verifier-spotcheck.md:139` — D3 lists three open items (K1Cheat relocation script; reworded witnesses auto-picked; V1Code F1–F4) and demands "write it as a lesson row with a check that can fail, or drop it with a reason."
- What happened: r47 row 1 (`round-47.md:45`) captures the sufficiency family and the shortcut tally but names neither "reworded witnesses" nor V1Code F1–F4; r48 C1's statement covers V1Ctr F1, regressed-exit, region binding and fixtures, not V1Code's drafter-checker defects. `grep -l 'V1Code' corpus/lessons/` → only round-44.md, round-46.md, round-46 spotcheck; `reworded witness|auto-picked` → only the r46 closure. The "row or drop" instruction was not executed for these two named items.
- Proposed row (class `stale-premise`, sub-item): "The release-recheck drafter's checker gaps (V1Code F1–F4) and the auto-pickable reworded witnesses either enter the next release-recheck counter's limit section or are dropped with a stated reason (r46-D3)." Fix able to fail: grep the round's C1 claim/receipt for `witness`-policy text; absent → exit 1.

### F3 — r46-D4 (hexrun red gate) closed without capture

- Source side: `corpus/lessons/round-46-verifier-spotcheck.md:140` — "Close or ledger the 21 unknowns."
- Fix landed: r47 filed 22 hexrun ledger rows with committed evidence (`round-47.md:14`; seats X4Hex*); r47 closure §2 re-derives `unknown=0` at tip. No Mistakes row in r46–r48 encodes the "unknowns must be ledgered, not just described" rule; KQ55 predates and does not require per-row committed evidence.
- Proposed row (class `closed-without-capture`): "A red hexrun gate closes only with ledger rows carrying committed evidence per unknown (`registry/hexrun-ledger.tsv`), cited in the round's lesson; closing by description alone is a defect (r46-D4)." Fix able to fail: a check that at a round claiming hexrun green requires the ledger row count ≥ the base unknown count — fails on r46's claim (unknown=21 described, no rows at that tip).

### F5 — carried frontier rows were never re-checked and never tracked (r44#5 rerank candidates; r45#4 S013, S022, floating-series, S002–S004, llama.cpp after b11889)

- Sources: `corpus/lessons/round-44-verifier-spotcheck.md:112` (rerank candidates) and `corpus/lessons/round-45-verifier-spotcheck.md:149` (S013, S022, floating-series, S002–S004, llama.cpp after b11889).
- Checks: r45 C1 = the 11 planned keys; r46 C1 = the 91 on-release llama.cpp rows at b11906 (covers the llama.cpp-after-b11889 half); r47/r48 had no freshness claim. `grep -n 'floating-series' -R corpus/lessons/ registry/` → only the r45 closure and the r46 sweep transcript. `registry/release-recheck-b11889.tsv`/`release-recheck-b11906.tsv` contain no S013/S022/S002–S004 rows; `registry/hexrun-ledger.tsv:16` records S013's pin as broken (`docs/import.md` 404 at it) and `:83` records a proposed re-pin commit (seat U9Floating) — no recheck row, no tracking. Rerank candidates appear only in `round-44.md:37` as history.
- These are not defects, but routed work that never became a tracked row; the r46 sweep's own rule (a carried item surviving three closures without a lesson row must become one or be dropped with a reason) is the standing obligation.
- Proposed row (class `carried-uncaptured`): "A routed recheck frontier (S013, S022, floating-series rows, S002–S004, rerank candidates) enters the next release-recheck population or is dropped with a stated reason; carrying it a fourth time without either is the defect." Fix able to fail: a checker comparing the round's recheck ledger population against the carried list — today the list appears in no ledger.

### F6 — r44-D3 (registry hygiene: process-qualification citations) closed without capture

- Source side: `corpus/lessons/round-44-verifier-spotcheck.md:110` (D3: entries cite "(S480, S481)" where S480 disclaims and S481 is tier C; cite S483).
- Fix: r45 Gate "Rows touched old→new" (`round-45.md:19`) updates S483 `used-by` and the entries; r45 closure verifies. No Mistakes row, no KQ encodes "cite the row whose `teaches` supports the claim" — KQ22/KQ31 govern cell immutability, not id choice. Class has not recurred (low priority; record for completeness).

### F7 — r47-D2 (replay loop over all three receipts) closed by implementation without capture

- Source side: `corpus/lessons/round-47-verifier-spotcheck.md:98` — "Loop replay over all three receipts next round."
- Implementation: r48 C2 replays all three receipts (`replayed=3/3`, r48 closure :49; r48 routed block "r47-D2: C2 (replay leg over all three receipts)"). No Mistakes row in r48; neither KQ69 (single-receipt "compares the new receipt with the original") nor KQ75 (projection surfaces) encodes multi-receipt coverage.
- Proposed row (class `closed-without-capture`): "A replay claim over N receipts replays every receipt in the set; a replay of receipt-1 alone is a disclosed partial (r47-D2)." Fix able to fail: a check asserting the replay receipt count equals the receipt set size — fails on r47's `replayed=1/1` (`round-47` counter receipt).

### F8 — r47-D7 (prerelease cliff) carried twice, then absent from round-49 planning

- Source: `corpus/lessons/round-47-verifier-spotcheck.md:103` (b11909 is a GitHub prerelease; if the tag is pruned the replays permanently refuse) → r48 routed block "frontier: disclosed limit; no cache hardening this round" → carried again in r48 R5 (`round-48-verifier-spotcheck.md:120`).
- Round 49: `grep -n 'prerelease' .ufo/waves/round-49/preregistration.json corpus/lessons/round-49.md` → 0 matches. The disclosed limit is not carried into the round that rewrites the replay tool's witness path, which is precisely the round where a tag-prune would surface.
- Proposed row (class `carried-uncaptured`): "A disclosed limit that blocks replay permanence (r47-D7) is carried in the next round's preregistration `limits` or closed with a digest-verified cache; absence from a round that changes the replay path is the defect." Fix able to fail: a checker that greps the round's preregistration for the limit when the round's claim touches `kama-live-replay.py` — fails today (no occurrence in round-49 preregistration).

### F9 — r47-D8 (sources-append-only parser) unfixed, deferred unbounded

- Source: `corpus/lessons/round-47-verifier-spotcheck.md:104` ("Parser fix pending"). Class captured as r47 row 5 (`round-47.md:49`).
- Status: K0Harm F1 at the r48 build (`round-48/w1/out/K0Harm.md:54`): `tools/sources-append-only.py` exits 2 on every revision since round 45 (`row-like line outside the parsed registry table`), so no SOURCES transition has been graded since; a patch was proposed in wave evidence but never integrated (r48 lesson rows 1–5 do not mention it; r48 closure R1–R5 do not mention it; round-49 preregistration/lesson do not mention it). The deferral has no round bound and no owner.
- Proposed fix-bound row (extends r47 row 5): "The sources-append-only parser repair lands by a named round or the guard is retired with a stated replacement; an unbounded deferral past the round that records it is the defect (r47-D8)." Fix able to fail: `python3 tools/sources-append-only.py --from <r45 base> --to <tip>` still exits 2 today (K0Harm `evidence/commands.out`).

### F10 — R1 (verify_archive_member unbounded) is fixed inside the round-49 C1 claim but has no row and no criterion yet

- Source: `corpus/lessons/round-48-verifier-spotcheck.md:110` — a 104-byte archive whose digest the operator declared makes record time read ~10^15 bytes before the server starts; "Cap the member size against the declared asset size before hashing."
- In-flight: round-49 C1 predicate carries `cap=1` and the statement cites "verify_archive_member() refuses a sparse or size-mismatched member before hashing it (seat Sen2Live F1; closure R1)" (`.ufo/waves/round-49/preregistration.json` C1). No Mistakes row yet; `grep -n 'sparse|GiB|member size' corpus/QUALITY.md` → 0 matches (QUALITY.md ends at KQ75). Commit the capture at integration: a KQ row in the KQ74/KQ75 pattern ("an archive member is hashed only after its declared size is bounded by the asset size, members ≤ 4096 index entries, and sparse members refused") with the `cap=1` counter leg as the shown-able-to-fail check.

### F11 — R5 sub-items status

- **F11a witness (K2Cheat/K2Urlswap)** (`round-48-verifier-spotcheck.md:115`): in round-49 C1 witness leg (predicate `witness=1 witnessed=3/3`). No row/criterion yet — same capture-pending note as F10.
- **F11b record-time fetch (K2Record)** (`round-48-verifier-spotcheck.md:116`): open. `K2Record.md` (r48 wave) documents that record-time verification binds local bytes to operator-supplied digests only and argues against adding a network fetch at record time (offline capability). This is an *accepted disclosed limit*, but it has no Mistakes row and no criterion note; it should be written as a limit row (class `disclosed-limit`) so it is not later re-litigated as a hidden gap.
- **F11c surviving mutants** (C1 counter 21/52, tool 15/55, C2 counter 6/27; `round-48-verifier-spotcheck.md:117`): disclosed in SCORECARD; no kill-threshold criterion exists by design (round-20 criteria explicitly exclude a universal mutation-testing score policy). Record-only.
- **F11d content-blind exemption + substring declaration binding (K1Regions/K1Binding)** (`round-48-verifier-spotcheck.md:118`): in round-49 C2 v4 claim (origin, whole-word token, negation window, wildcard self-declaration refusal; predicate `scenarios=8/8`). KQ72 covers the region-cell mechanics; the v4 origin/negation rules are claim-level, not yet a criterion — capture at integration.
- **F11e sub-20-line deletions unwatched (L1Lowthr)** (`round-48-verifier-spotcheck.md:119`): open; r48 C1 limits disclose ("The threshold stays 20: sub-threshold deletions are not graded"); the LOG.md loss at `ed135b3c` predates. Suggest a row or an explicit drop-with-reason; at minimum the limit sentence should name the `ed135b3c` LOG loss as the known consequence.

### F12 — operator/L0 items (still open by design, never lesson rows)

- Sources: r45 closure :150 (L0 questions; N-A salvage commit under lane identity), r46 closure :142-143 (N3Fleet adjacency; planner seat), r47 closure :106 (parked worktree), r48 closure :121 (untracked fleet-root files). The round-47 closure's "quoted map matches" row is corrected by r48 R4 — operator-side, not a lane file.
- These are operator-owned/routed, not lane defects. Flagged so the integrator can pass them to the operator route, including the round-47 closure document correction.

## Disagreement side

None. Every discernment table in closures 45–48 ends in agree for all sampled admits/rejects, and each reject decision is mirrored in the corresponding lesson Gate:

- round-45: rejects "3 ms teardown re-assertion" and "rounds 25/31 C1 as met" → `round-45.md:20` ✓
- round-46: rejects teardown-as-property, S121 builder's single-line `holds`, carryforward `holds`, S039-as-refetch-record → `round-46.md:26-29` ✓
- round-47: rejects record-time provenance, host-path locator, term_wait_ms property → `round-47.md:32-35` ✓
- round-48: rejects x-linked-etag, CDN redirect target, relabelled v2/dropped row → `round-48.md:34-39` ✓

## Notes for the integrator

1. The round-48 lesson row 4's fix — the r48 preregistration `routed` block — is **not repeated** in the round-49 preregistration (keys: `lane, round, attempt, author, frozen_at_utc, base, authority, separability, claims, controls, limits`; no `routed`). The mechanism that flagged r47-D1..D9 has no round-49 counterpart, so R1/R5 have no committed disposition beyond the claim statements; the sweep comparison the r48 row describes cannot run next round.
2. The round-46 sweep's own proposed rule ("a carried item surviving three closures without a lesson row must become one or be dropped with a stated reason") never became a QUALITY criterion; F1/F5/F8 are the continuing casualties. Recommend a KQ row for it.
3. Round-49 lesson draft rows 1–3 already capture R2/R3/R4 (report-before-tip + in-place rewrite; census W01 paraphrase; stale role-share quote). Keep them when the lesson lands.

## File:line anchor index (both sides)

- Closures: `round-45-verifier-spotcheck.md:146-150`; `round-46-verifier-spotcheck.md:137-143`; `round-47-verifier-spotcheck.md:97-107`; `round-48-verifier-spotcheck.md:110-127`.
- Lessons: `round-45.md:27-31`; `round-46.md:35-42,87-88`; `round-47.md:45-50`; `round-48.md:28-32`; `round-49.md:31-35` (draft).
- QUALITY: KQ62–KQ75 (`corpus/QUALITY.md:377-413`); no KQ covers F1, F2, F3, F5, F6, F7, F8, F9 (as a fix bound), F10, F11a/b/d/e.
