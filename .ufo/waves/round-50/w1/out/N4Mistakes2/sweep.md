# Round 50 frontier step-3 sweep — routed items of closures 45–49 vs lesson Mistakes rows and QUALITY criteria

Seat N4Mistakes2. Lane kama, round 50, leaf. Read-only analysis. Sources read: `corpus/lessons/round-4[5-9]-verifier-spotcheck.md` (routed defect sections + conformance notes + discernment tables), `corpus/lessons/round-4[5-9].md` `## Mistakes` tables, `corpus/QUALITY.md` (KQ1–KQ79), the round-46..50 preregistrations, and the r46/r48/r49 sweeps that already live under `w1/out/`. Verified by hand against committed bytes; where a command is cited it was run and its output is quoted or committed beside this file.

Supersedes in scope: `.ufo/waves/round-46/w1/out/S9Lesson/sweep.out` (routed 40–45), `.ufo/waves/round-48/w1/out/N5Mistakes/sweep.md` (routed 45–48; never cited by a committed file), `.ufo/waves/round-49/w1/out/N5Mistakes/sweep.md` (routed 45–48, written during round 49; also uncited — T5Mistakes check C). This sweep re-derives the ledger at round 50, carries forward every still-open finding with its new status, and adds the round-49 closure.

## Verdict

**7 routed items (or sub-items) still have no lesson Mistakes row and no QUALITY criterion** at the round-50 base. Two are new since the r49 sweep and one is a mechanism regression that makes the rest recur:

1. **Routed-ledger mechanism regression** — the `routed`/`carried` block the round-48 fix installed exists only in the round-46/47/48 preregistrations and is **absent from round-49 and round-50**; the carried items it existed to track (`prerelease`, `b11906 population`) are therefore absent from the frozen record this round.
2. **Sub-20-line deletion blind spot** — routed three closures running (r48-R5, r49-R5; first routed at r48 from seat L1Lowthr), still unwatched; the `ed135b3c` LOG.md loss (7 deleted lines, 2 restored) is still partial and still invisible to the default audit.
3. **r45-D1 deferred-then-dropped** — the deferral itself is a defect class no row names: a `deferred` disposition with no re-arm condition silently expires.
4. **r46-D3 named sub-gaps** ("reworded witnesses could be auto-picked"; V1Code F1–F4) — the family row was written (round-47 row 1) but the two named items the closure demanded be rowed-or-dropped were neither.
5. **r47-D2 multi-receipt replay** — closed by implementation at r48 (`replayed=3/3`) but the *rule* (a replay claim covers every committed receipt) exists in no Mistakes row and no KQ.
6. **r48-R5 record-time fetch (K2Record)** — an accepted disclosed limit that lives only in wave output; no limit row, so it will be re-litigated.
7. **Mutation survivors** (r47-D5 13/44; r48-R5 21/52+15/55+6/27; r49-R4 11/20+10/23+16/49+8/29) — routed each round as defect counts; per-mutant disposition is tracked nowhere durable. Low priority: the sufficiency family row (round-47 row 1) covers the class abstractly, and QUALITY.md's round-20 preamble excludes a universal kill-score policy — but nothing requires each survivor to carry a disposition (killed-fix / equivalent / carried-with-reason).

**Staleness correction to the r49 sweep (N5Mistakes):** its F9 ("sources-append-only parser still unfixed, unbounded deferral") is **resolved** — the pre-repair tool at `c4b2175d^` exits 2 on the r45 failing pair while the tip tool exits 0 (`added S496/S497/S498 (allowed)`, selftest 45/45); committed receipts `T5Mistakes/sources-guard{,-pre-repair}.out`. Its F10/F11a/F11d are **captured this round or last**: unbounded member read → round-49 Mistakes row 4; execution witness → KQ76; content-blind binding → KQ77/KQ78. Its F1/F2/F3/F5/F6/F7/F8/F11b/F11e/F12 are carried below with current status.

**Disagreements:** none uncaptured. Every closure step-3 discernment table (r45:124-130, r46:117-121, r47:75-81, r48:88-93, r49:81-86) ends in `agree` for all sampled admits/rejects. The one closure-to-closure disagreement — r48-R4 (`round-48-verifier-spotcheck.md:113`) correcting r47's "quoted map matches" conformance row — is operator-side (the prompt addendum), carried open as r49-R6 (`round-49-verifier-spotcheck.md:108`); the lane-side shadow (role share computed from a stale map) is round-49 Mistakes row 3. The r45 closure's in-table disagreements (o1/u2/other/absent) were adjudicated inside that closure; the systemic underclaim pattern is captured by KQ61/KQ44.

## Routing ledger, closures 45–49 → lessons/QUALITY (file:line both sides)

| Closure item | Source | Disposition | Captured? |
|---|---|---|---|
| r45-D1 reader re-freeze | r45-spotcheck:146 | deferred r46 (`round-46.md:12`); absent r47–r50 routing; named as dropped example `round-48.md:31` | **no** (substance: KQ65 `QUALITY.md:380` insufficient) — Row C |
| r45-D2 freeze timestamp | r45-spotcheck:147 | applied r46+ | yes — `round-45.md:27`, KQ64 `QUALITY.md:379` |
| r45-D3 model locator durability | r45-spotcheck:148 | r46 row 1, KQ66 | yes — `round-46.md:35`, `QUALITY.md:386` |
| r45-#4 carried frontier (S013, S022, floating-series, S002–S004, post-b11889) | r45-spotcheck:149 | post-b11889 absorbed into r46 C1; S013/S022/floating/S002-4 nowhere since (r49 sweep F5: `hexrun-ledger.tsv:16,83` record S013 broken pin + proposed re-pin, no recheck row) | **no** — covered by Row A's rule (work items, not defects; three-closures rule applies) |
| r45-#5 operator/driver | r45-spotcheck:150 | N-D → r46 row 2 (`round-46.md:36`); N-A + L0 operator | n/a operator-owned |
| r46-D1 `---` blind spot | r46-spotcheck:137 | r46 row 6 + KQ70 | yes — `round-46.md:40`, `QUALITY.md:397` |
| r46-D2 measure drift | r46-spotcheck:138 | r47 row 2 + KQ70 | yes — `round-47.md:46` |
| r46-D3 sufficiency family + 2 named sub-gaps | r46-spotcheck:139 | family → r47 row 1 (`round-47.md:45`); **sub-gaps itemized nowhere** | family yes; **sub-gaps no** — Row D |
| r46-D4 hexrun unknown=21 | r46-spotcheck:140 | closed r47 (22 ledger rows + evidence; r47-spotcheck:53 `unknown=0`); class cited in `round-48.md:31` | closed; class captured |
| r46-D5 dead log pointer | r46-spotcheck:141 | r47 row 3 + KQ69 | yes — `round-47.md:47`, `QUALITY.md:396` |
| r46-D6 sibling truncation census | r46-spotcheck:142 | operator/aggregator (`round-47.md:14`) | n/a operator-owned |
| r47-D1 counter trusts evidence | r47-spotcheck:97 | r48 row 3 + KQ74 | yes — `round-48.md:30`, `QUALITY.md:410` |
| r47-D2 replay only receipt-1 | r47-spotcheck:98 | implemented r48 (`replayed=3/3`); rule nowhere | **no** — Row E |
| r47-D3 record-time provenance | r47-spotcheck:99 | KQ74 | yes — `QUALITY.md:410` |
| r47-D4 comparison depth | r47-spotcheck:100 | KQ75 | yes — `QUALITY.md:411` |
| r47-D5 counter gaps (mutants 13/44, `append` substring binding, playback cheat) | r47-spotcheck:101 | KQ72/KQ70 + r48 C1 fixtures; mutant counts disclosed | mostly; per-mutant disposition **no** — Row G |
| r47-D6 moving `main` URL | r47-spotcheck:102 | KQ74 pinned clause; S492 | yes |
| r47-D7 prerelease cliff | r47-spotcheck:103 | r48 routed-block "disclosed limit"; carried r48-R5:120, r49-R5:107; **absent from r50 preregistration** (limits :39-44, no routed key) | **no** — Row A carries it |
| r47-D8 sources guard blind | r47-spotcheck:104 | r47 row 5 (`round-47.md:49`); parser repaired r48 (r48-spotcheck:65 exit 0; r49-spotcheck:60 exit 0; `T5Mistakes/sources-guard.out`) | yes (row + fixed) |
| r47-D9 receipt-tip precision | r47-spotcheck:105 | r48 row 2 | yes — `round-48.md:29` |
| r48-R1 unbounded member read | r48-spotcheck:110 | r49 row 4 + C1 `cap` leg | yes — `round-49.md:37` |
| r48-R2 report placeholders/rewrite | r48-spotcheck:111 | r49 row 1 + KQ79 | yes — `round-49.md:34`, `QUALITY.md:424` |
| r48-R3 census W01 paraphrase | r48-spotcheck:112 | r49 row 2 + KQ79 | yes — `round-49.md:35` |
| r48-R4 stale route map | r48-spotcheck:113 | lane share → r49 row 3 (`round-49.md:36`); prompt itself operator-side, carried r49-R6:108 | lane yes; **operator open** |
| r48-R5 carried gaps | r48-spotcheck:114-120 | witness → r49 C1 + KQ76; binding → r49 C2 + KQ77/78; mutants → carried; **sub-20 → carried, Row B**; **record-fetch → open disclosed, Row F**; **prerelease → carried, Row A** | mixed |
| r49-R1 pid/env/model bind | r49-spotcheck:103 | **r50 C1** (bind leg; dry run `bind=1 … met=True` at build) | in-flight claim capture |
| r49-R2 killed-counter teardown | r49-spotcheck:104 | **r50 C1** (teardown leg, `python -I` + allowlist env + pdeathsig) | in-flight claim capture |
| r49-R3 v4 definition gaps (rev-list origin, fence-blind, CRLF, arithmetic bound, shared binder) | r49-spotcheck:105 | **r50 C2** (birth-DAG origin, CommonMark fences, CR-strip, graded+ungraded==deleted); **shared binder disclosed open** — `preregistration.json:44` | mostly claim capture; binder limit disclosed |
| r49-R4 mutation survivors | r49-spotcheck:106 | to r50's four mutation seats per T1Log draft (`w1/out/T1Log/log.md:7`); no ledger, no criterion | in-flight; **no persistent capture** — Row G |
| r49-R5 carried (sub-20, prerelease, b11906 population) | r49-spotcheck:107 | sub-20 → r50 limits :44; **prerelease + b11906 → absent** from r50 preregistration | **partially dropped** — Row A/B |
| r49-R6 prompt route map | r49-spotcheck:108 | operator-side, carried | n/a operator-owned |
| Operator/L0 (planner seat, MISSION axes pair, parked worktree) | r45:150, r46:143, r47:106, r48:121, r49:109 | open by statement every closure | n/a — not lane-capturable |
| Promotion (SHONEN boxes) | r46:144-149, r47:107, r48:122-127, r49:110-115 | operator-owned | n/a |

## Proposed rows (class, evidence, captured-by, fix able to fail)

### Row A — `carrier-loss`: the routed-item ledger itself disappeared, and two carried items fell out of the frozen record with it

- **Evidence:** `round-48.md:31` fixed "routed items dropped without capture" with a `routed` block naming each closure id. Present: `.ufo/waves/round-48/preregistration.json` (`r47-D1..D9`, 9 ids); `round-47/preregistration.json` (`r46-D1..D6`+`r45-D3`); `round-46/preregistration.json` (`r45-D1..D3`). **Absent:** `round-49/preregistration.json` and `round-50/preregistration.json` — keys are `lane, round, attempt, author, frozen_at_utc, base, authority, separability, claims, controls, limits` only (routed items survive only as prose inside `authority` and two `limits` sentences). Consequence: `round-49-verifier-spotcheck.md:107` carries three items; `round-50/preregistration.json:44` names `sub-20` only; `prerelease` and `b11906` appear nowhere in the frozen file (grep → 0). The check the row described cannot have been run.
- **Captured-by:** none. Same defect second instance (r45-D1's carrier died r47; the fix's own carrier died r49 — the pattern is self-referential).
- **Fix able to fail:** land seat T5Mistakes' `checks.py` as a committed tool (`tools/routed-block-check.py`): check B requires any preregistration whose base closure routed ≥1 lane item to carry a `routed`/`carried` block; check D requires each carried item's content word in `limits` or a named disposition. Already shown able to fail — committed receipt `w1/out/T5Mistakes/checks.out`, rerun `w1/out/N4Mistakes2/t5-checks-rerun.out`: `check B FAIL: round-49, round-50`; `check D FAIL: 'prerelease', 'b11906' missing`; exit 1. On `round-48/preregistration.json` the same checks pass. Absorb the r46 sweep's rule (`round-46.md:87`: a carried item surviving three closures without a row must be rowed or dropped with a reason) — the block diff makes it mechanical.

### Row B — `graded-below-threshold`: a substantive lane loss smaller than 20 lines is invisible by construction, routed at three closures

- **Evidence:** routed `round-48-verifier-spotcheck.md:119` ("sub-20-line deletions unwatched (L1Lowthr; the `LOG.md` loss at `ed135b3c` predates this round)"), carried `round-49-verifier-spotcheck.md:107`, disclosed-not-fixed `round-50/preregistration.json:44` ("the sub-20 threshold is unchanged"). The blind spot is the event gate `tools/append-only-audit.py:91` ("event (commit, file) with |D| >= threshold (default 20)") → `:520` `if ns[f] < threshold: continue`. The live loss: `git show --numstat ed135b3c` → `1 7 LOG.md` (7 deleted; `restored_max 2`). Seat census at `--threshold 1` (`w1/out/L1Lowthr/audit-threshold1.json`, rerun of `w1/out/L1Lowthr.md`): 98 events, 93 with deleted<20, 66 graded partial/unrestored — the one substantive loss being the 2026-10-13 HOURS ledger opening.
- **Captured-by:** none — no `## Mistakes` row, no KQ (grep `sub-20|threshold` over `round-4[5-9].md` + `QUALITY.md` → no relevant hit).
- **Fix able to fail:** commit one `append-only-audit --threshold 1` census receipt per round beside `measured/` and require every event it grades partial/unrestored to be dispositioned in the lesson (explain or restore — same KQ67 rule the default run uses). It fails today: the receipt shows `ed135b3c` LOG partial unrestored with no restoration, and its deleted lines are real lost history (not re-anchors).

### Row C — `dropped-deferred`: a `deferred` disposition without a re-arm condition silently expired (r45-D1)

- **Evidence:** routed `round-45-verifier-spotcheck.md:146`; deferred `round-46/preregistration.json` `routed` + `round-46.md:12` ("No reader was written or run"); absent from every later routing (`grep r45-D1` over r47–r50 lane files → 0); named only as a dropped example in `round-48.md:31`. KQ65 (`QUALITY.md:380`) covers the sample-read requirement but not the known-data constraint the closure named (sample scored before the reader sees *this* ledger, plus citing the closure's 58/61 recomputation).
- **Captured-by:** none for the deferral-defect class; KQ65 for the substance.
- **Fix able to fail:** any future claim-outcome reader freeze must cite its score on the committed sample sets (`.ufo/waves/round-46/w1/out/S8Sample{1,2,3}/sample.tsv`, `R8Sample/sample.tsv`) and the r45 recomputation before the freeze commit. Check: grep the claim's preregistration/control receipts for the sample paths — fails on the r45 v1/v2 freezes themselves (`c2-v1.out` `valid=91 bad=35 met=False` shows the un-gated failure mode). Row A's block rule is the carrier that makes this enforceable round-over-round.

### Row D — `sub-item drop`: two named attack findings the closure demanded be rowed-or-dropped were neither (r46-D3 sub-gaps)

- **Evidence:** `round-46-verifier-spotcheck.md:139` demands "write it as a lesson row with a check that can fail, or drop it with a reason" for three named items; the sufficiency *family* got `round-47.md:45`, but "reworded witnesses could be auto-picked" and "V1Code's F1–F4" appear in no later lesson or QUALITY (grep `V1Code|auto-pick|reworded witness` over `round-4[5-9].md` → only `round-46.md:91` naming the seat in the wave roster).
- **Captured-by:** none.
- **Fix able to fail:** the next freshness claim's `limits` must name both sub-gaps or the preregistration must drop them with a reason. Check: a grep over the preregistration for `V1Code|reworded witness` when the claim re-runs release-recheck — exits 1 on every preregistration 46–50 today (the dormant counter carries the same gaps).

### Row E — `closed-without-capture`: multi-receipt coverage exists in code, not in any rule (r47-D2)

- **Evidence:** `round-47-verifier-spotcheck.md:98` routed "loop replay over all three receipts"; implemented `replayed=3/3` (r48-spotcheck:49). The rule exists nowhere: KQ69 (`QUALITY.md:396`) and KQ75 (`QUALITY.md:411`) speak of "the original"/receipt, never of set coverage; no Mistakes row.
- **Captured-by:** none.
- **Fix able to fail:** amend KQ69 or append a KQ: a replay claim over N committed receipts replays all N; a replay of one receipt is a disclosed partial. Check: counter receipt field `replayed=k/N` must equal the receipt count — fails on the r47 counter's receipt (receipts=1 replayed=1/3 coverage).

### Row F — `accepted-limit unrowed`: record-time never fetches URLs is a settled limit that exists only as wave output (r48-R5 K2Record)

- **Evidence:** `round-48-verifier-spotcheck.md:116` carried "record time never fetches the URLs (K2Record)". The decision (fetch is the replay's job, not record time's — offline capability) sits in `w1/out/K2Record*` wave files; no Mistakes row, no KQ scope clause records it, so a future seat can re-litigate it as a hidden gap.
- **Captured-by:** none.
- **Fix able to fail:** a disclosed-limit row (Mistakes class `disclosed-limit`) naming the limit and its flip condition; or one scope sentence inside KQ74 (`QUALITY.md:410`) stating record-time provenance binds operator-declared digests to fetched bytes, never performs the fetch. Check: grep `QUALITY.md`/`round-50.md` for `record.time.*fetch` → exits 1 today.

### Row G — `per-mutant undispositioned`: surviving-mutant counts are routed every round; the per-mutant ledger is tracked nowhere durable

- **Evidence:** `round-47-verifier-spotcheck.md:101` (13/44), `round-48-verifier-spotcheck.md:117` (21/52, 15/55, 6/27), `round-49-verifier-spotcheck.md:106` (11/20, 10/23, 16/49+5 equiv, 8/29). SCORECARD discloses the counts; each survivor's disposition (kill-fix / equivalent / accepted) exists only in the producing seat's wave output, which is scratch-classed evidence. Caveat honored: `QUALITY.md` round-20 preamble excludes a universal kill-score policy — the row asks for a *ledger*, not a threshold.
- **Captured-by:** partially — the sufficiency family `round-47.md:45` covers the class abstractly; nothing covers per-mutant disposition.
- **Fix able to fail:** `registry/mutant-dispositions.tsv` naming each surviving mutant's id and disposition, regenerated each round a mutation seat runs; a checker fails when the survivor count and ledger rows disagree. Fails today: no such ledger exists for any of the 3 rounds' survivors.

## Operator-owned items (listed for the integrator's operator route; not lane defects)

- r45-#5 / r46 L0 / r47 L0 / r48 L0 / r49 L0: planner seat impossible under policy-v2 validator (`kama | round-39`), MISSION axes pair (`kama | round-35`), parked worktree (`kama | round-41..43`) — still open by statement at `round-49-verifier-spotcheck.md:109`.
- r46-D6 sibling-lane truncation census (14/21 lanes) → aggregator arbitration; lane must not act on sibling repos (`round-47.md:14`).
- r48-R4 → r49-R6: prompt §6 still quotes `critic @m_flash` vs live `@m_kfc`; the r48 closure also corrects the r47 closure's "quoted map matches" row — a correction to a committed closure document, operator-side.
- Promotion/SHONEN boxes — operator-owned per every closure's promotion note.

## Contradiction disclosure

- T5Mistakes' `checks.py` check C currently requires sweep files to be cited by a committed `corpus/`/`registry/` file; that makes every sweep self-referential (a sweep cannot cite itself into existence in the same commit it lands). The fix for Row A should require the *routed block* and *carried limits* in the frozen preregistration, not citation of the sweep artifact.
- `check A` (label-resolution) also fails on T4Lesson's spec-text citations of r49 R2/R3 and R4 — a different surface (spec label accuracy), noted here so the integrator does not conflate the two FAILs.
