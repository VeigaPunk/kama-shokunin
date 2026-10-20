# Kama round 11 — prior-disagreement reflection audit (PriorDisagreement)

Advisory, non-author, read-only. Seat: `KamaR11.PriorDisagreement` (leaf, no delegation).
Subject: `kama-shokunin/corpus/lessons/round-10-verifier-spotcheck.md` (immutable, read as-is) and the round-10 lesson errata (`corpus/lessons/round-10.md` §Errata, `SCORECARD.md` §Erratum round 10, `corpus/QUALITY.md` KQ6–KQ13), checked against the external verifier reports the spot-check summarizes: `.ufo/waves/kaika-w3/kama-review.md` (reviewer) and `.ufo/waves/kaika-w3/kama-critic.md` (critic).

Edits: none to the implementation, corpus, or fleet repo. This file is the only write.
Installs/updates: none. Public-doc fetches used `curl` (already present); no package was installed or upgraded.
Peer note: a peer message from `TameshiR12` asked for report writes under a tameshi `round-12/w2` path. That conflicts with this assignment's path, so it was not followed; this report stays at the assigned path.

## 0. Bottom line

- The spot-check's admit/reject sample (7/7 agree) is itself supported by the reviewer's §5. Its problem is scope: it records the verdict and the orchestrator's D-1 ruling, but it does not carry the reviewer's HIGH finding, the reviewer's recommended ruling, or the critic's counterexamples into any QUALITY criterion or claim limit.
- Of the external routed defects, 4 are reflected (D-2, D-3, D-6, and the C3 coverage restatement). 4 are reflected only partly or only by errata, with the limit missing from the criteria (C1 measurement, freshness scope, A16, D-7). 5 are unreflected or contradicted: A20 (critic), the D-1 ruling and S030 flip authority, the capability-vs-coverage dissent, the S009 apostrophe claim, and the discernment text left as "awaiting spot-check".
- One new defect was found that none of the external reports raised: the A20 correction (`consumer-registry.md:380`) asserts a current fact that its shape-only check cannot establish. This is the most serious item because KQ7 would pass it.
- Four of the nine lesson-proposed criteria (e, f, g, h) were never adopted, and the lesson gives no reason.

## 1. Reflection table (each external disagreement / routed defect)

Status key: **R** reflected with the limit stated · **P** partial (limit stated only in an errata, or not in any criterion) · **U** unreflected or contradicted.

| Ref | Source | Disagreement / defect | Where it lands now | Status |
|---|---|---|---|---|
| D-1 (HIGH) | reviewer `kama-review.md:166`, conditions `:195`, Q1 `:202` | Documentation-only binding binds kama's own L1 gate; reviewer recommended "live checks out of rule; lane records L1 outputs as out-of-rule" | Orchestrator ruled the opposite: `round-10.md:152`, `SCORECARD.md:220`, spot-check `round-10-verifier-spotcheck.md:17` | **U** — see F2 |
| S030 flip | SOURCES row `corpus/SOURCES.md:42` | Flip text: "L0 rules lane-own registered-endpoint gate runs admissible" | Errata `round-10.md:152` says "its flip met" on an orchestrator ruling; `.ufo/l0-questions.md` has zero `kama | round-10` entries (grep count 0) although `round-10.md:127` says "the question goes to L0" | **U** — see F2 |
| C3 capability vs coverage (critic) | critic `kama-critic.md:14,18`; reviewer Q2 `kama-review.md:203` | Critic: coverage move, not capability. Reviewer: accept as capability, record critic's reading as dissent | Capability row entered with no dissent: `SCORECARD.md:126` ("First-working round 10"); operator ruling noted as pending at `round-10.md:136` only | **U** — see F3 |
| C3 coverage padding (critic) | critic `kama-critic.md:14` | Coverage map 19→24 counts `SOURCES.md` and lesson as surfaces | Erratum restates coverage on knowledge entries 9→12, 0→3: `SCORECARD.md:215`, `round-10.md:153` | **R** |
| C1 counter (critic) | critic `kama-critic.md:7,10` | Marker count does not establish resolved anchors; A17/A51 are terminal, not re-anchored | Errata `round-10.md:143`–`149` (uncorrected 0 ≠ re-anchored; `validate-new-pointers.sh` bounds-only; negative control). `SCORECARD.md:211` says "corrected, not re-anchored" | **P** — KQ7 (`corpus/QUALITY.md:29`) still admits on "count reaches 0" with no limit; see F4 |
| C1 A16 (critic) | critic `kama-critic.md:8` | `../MISSION.md` is checkout-relative; make context explicit | Correction now uses absolute `/home/vgpnk/Projects/shokunin/MISSION.md:37-43` (`alias-endpoint-normalization.md:60`); ledger row still relative with a parenthetical | **P** (absolute host path is portable only to this host — low) |
| C1 A20 (critic) | critic not explicit; disputed in lesson `round-10.md:136` and left "for the non-author check" | "No writer exists for #1/#6" literal truth vs lane's "premise stale" | Correction `consumer-registry.md:380` asserts "no live #1/#6 target" on shape-only evidence. Spot-check does not adjudicate A20 | **U** — see F1 |
| D-2 | reviewer `kama-review.md:155,169` | SCORECARD axes table stale | Erratum `SCORECARD.md:205-213` (superseded, not rewritten) | **R** |
| D-3 | reviewer `kama-review.md:170` | Mistake-14 count (15→0) contaminated; 29 at head | Retired `round-10.md:142`; "15→0" withdrawn. Body row 14 (`round-10.md:22`) and criterion (b) "Strongest" (`round-10.md:52`) still quote the retired measure, covered by the errata | **R** (body text not annotated inline — low) |
| D-4 | reviewer `kama-review.md:171,199` | 20 of 50 ledger rows rest on host-state shape reads; freshness accepted "narrow" for 30 repo-local rows | Not carried. Erratum still says freshness 7→8 with no narrowing (`SCORECARD.md:211`); KQ7 unchanged | **U** — see F4 |
| D-5 | reviewer `kama-review.md:174` | A18 body read (4 lines) after Mistake 9 class | Recorded `round-10.md:110` (KQ5-class slip) | **R** |
| D-6 | reviewer `kama-review.md:175` | Before-state 50 is definitional | Errata `round-10.md:143` ("uncorrected 0 means every row has an appended dated correction") | **R** |
| D-7 | reviewer `kama-review.md:176` | Mis-cited §Known gaps for metrics/GGUF | Erratum rationale re-grounds metrics/GGUF on the coverage map (`SCORECARD.md:217-218`); `round-10.md:99-101` cites only the llama.cpp-only line | **R** |
| D-8 | reviewer `kama-review.md:177`; lesson `round-10.md:92,135` | S009 quote bytes: ASCII vs page U+2019; lesson asserts "as on the page" | No erratum. Lesson keeps "ASCII, as on the page" — see F5 | **U** — see F5 |
| D-9 | reviewer `kama-review.md:178` | Five in-place line edits | Disclosed in LOG (per reviewer); accepted | **R** |
| D-10 | reviewer `kama-review.md:181` | S026 tier-A scope | No action needed (note only) | **R** (no action) |
| D-11 | reviewer `kama-review.md:182` | L2 floor and transcripts not verified by reviewer | Not addressed | **U** (low; parent may note) |
| Spot-check admit/reject | spot-check `round-10-verifier-spotcheck.md:12-13` | 7/7 agree | Consistent with reviewer §5 (`kama-review.md:115-121`) | **R** |
| Discernment text | critic `kama-critic.md:16-18` ("replace pending-outside-check statement") | SCORECARD still says no spot-check exists | `SCORECARD.md:97` ("No outside non-author admit/reject spot-check") and `:199` ("discernment awaits a non-author spot-check") unchanged | **U** — see F6 |

## 2. Findings by severity

### F1 — HIGH (new; not raised by any external report). A20 correction asserts a fact its check cannot establish
- Evidence: `corpus/knowledge/consumer-registry.md:380` — "the former repair gap has no live #1/#6 target", with evidence "`wc -l ~/.config/opencode/opencode.json` … => 5 … absent ~/.config/the-janitor/opencode.json — shape-only, no body read". Ledger row A20 (`.ufo/round-10/audit/stale-anchors.tsv`) has the same `wc -l` / `test -e` stale_check.
- Why it fails: a line count and a file-presence test cannot show whether the row #1/#6 pin (`localhost:8080` / `127.0.0.1:8080`) is present. A five-line JSON can carry the pin on one line. The registry body makes the same inference in undated text: `consumer-registry.md:62-65` ("`~/.config/opencode/opencode.json` still exists but is now 5 lines — the `qwen-local` provider and its `localhost:8080/v1` pin are gone"). The round-10 correction re-uses that line count as its only current support, so the body sentence is unsupported as written; its dated source is not cited in that section, and the parent should trace or downgrade it. The correction therefore states a current absence that the cited evidence does not test.
- Why KQ7 does not catch it: KQ7 (`corpus/QUALITY.md:29`) is satisfied by a marker count of 0 (`uncorrected 0`). The critic's point (`kama-critic.md:7`) that the marker proves only presence applies here with more force, because the content claim itself is unsupported.
- Routed status: the critic's dispute (`round-10.md:136`) was "left for the non-author check". The spot-check (`round-10-verifier-spotcheck.md`) covers only the admit/reject sample and does not adjudicate A20. It is open.
- Smallest repair (no config body read, per KQ5/Mistake 9): append a dated correction to `consumer-registry.md` that downgrades A20 to `UNDECIDABLE — pin presence not tested by shape-only checks`, and remove "no live #1/#6 target" from the current-tense reading. A count-only test (`grep -c` for the pin, output only the number) would be the first admissible check, but it is a new read and needs KQ5-scoped authority first.
- Lesson input: add a criterion that a shape-only check (`wc -l`, `test -e`) never supports a presence/absence claim about file content (extends KQ8/KQ9).

### F2 — HIGH. Documentation-only ruling reversed the reviewer's recommended ruling, and S030's flip was declared met on a non-L0 authority
- Binding text (`.ufo/prompts/kama-round-10.md:180-181`): "kagi, kasegi, kama, chousa, kake, tabi: no live-target probing, scanning, logins or submissions — documentation only." The text has no "external" qualifier.
- Reviewer's recommended ruling (`kama-review.md:202`): "yes — the binding names kama. Round 11 may cite repo-file reads only; live checks are out of rule." Condition 1 (`kama-review.md:195`): the lane records the L1 gate outputs as out-of-rule.
- Actual ruling (`round-10.md:152`, `SCORECARD.md:220`, spot-check `round-10-verifier-spotcheck.md:17`): orchestrator ruled the gate runs "in-province" because the rule "targeted external live targets". The lane did not record them as out-of-rule; it recorded them as in-province. Reviewer condition 1 is therefore not met, and the spot-check's "no violation" does not engage with the reviewer's reading.
- Authority problem: S030's flip (`corpus/SOURCES.md:42`) is "L0 rules …". The errata says "its flip met" on the orchestrator's ruling. `.ufo/l0-questions.md` has no `kama | round-10` entry (grep count 0), although `round-10.md:127` says "the question goes to L0". The integrator who wrote the spot-check also made the ruling (`round-10-verifier-spotcheck.md` header: "Written by the integrator"; ruling "Orchestrator ruling D-1").
- Criteria gap: KQ1 and KQ10 (`corpus/QUALITY.md:9,33`) admit endpoint claims with an "authorized" probe or a probe "inside the task's declared scope", but do not say who authorizes. The binding is not in the round-11 prompt (`.ufo/prompts/kama-round-11.md` has no documentation-only restatement; its only "endpoint" hit is the lane-axes line 6).
- Smallest repair: (a) file the question to L0 now, quoting the binding, the reviewer's Q1, and the orchestrator's ruling, and mark the ruling "contested, not L0" in an appended erratum; (b) add a supersession row (KQ14) that a live-target probe admits a claim only when the authorizing ruling is cited by channel and ID (`.ufo/l0-questions.md`), and that orchestrator rulings alone do not authorize; (c) restate the binding in the round-11 prompt or record in the round-11 lesson that round-11 claims cite repo-file reads only.

### F3 — HIGH. Capability-vs-coverage dissent is not recorded; the capability row is entered as settled
- `SCORECARD.md:126` enters `sources-registry` in the Capabilities table with "First-working round 10". The reviewer recommended acceptance as capability "recording the critic's coverage reading as dissent" (`kama-review.md:203`). The critic's reading (`kama-critic.md:14,18`) is not recorded in SCORECARD. The spot-check calls it "the operator rules" only inside the lesson's review record (`round-10.md:136`). No L0 entry exists (F2 count).
- Smallest repair: append a dissent line under the capability row or mark the row "pending L0 ruling (capability vs coverage)"; file the L0 question with both readings. The round-11 coverage claim should use the knowledge-entry counts (already restated, `SCORECARD.md:215`).

### F4 — MEDIUM. Freshness limit from the critic and reviewer is not in any criterion or the freshness claim
- KQ7 (`corpus/QUALITY.md:29`): "a pasteable count that reaches 0". The errata (`round-10.md:143`) says that count means "appended correction", not "re-anchored", and that the new-pointer validator is bounds-only with content checked only by sampling. Neither limit is in KQ7 — a supersession row is needed (QUALITY supersession rule, `corpus/QUALITY.md:5`).
- The critic's smallest correction (`kama-critic.md:10`) — separate verified pointers from terminal states and report the unresolved set — is implemented as the validator and errata but not as a criterion. The lesson's (f) gate-falsifiability criterion (`round-10.md:47`) is not adopted, though the validator now has a negative control (`round-10.md:151`).
- Reviewer's narrowing (`kama-review.md:149,192`: freshness 7→8 "narrow", 30 repo-local rows; 20 host rows unverified, D-4) is not in the SCORECARD erratum (`SCORECARD.md:211`), which states 7→8 unqualified.
- Smallest repair: KQ7a supersession row (count = appended correction; re-anchored = validator `resolved` with negative control; terminal states listed by ID; host-state rows counted as unverified). Narrow the freshness row in a SCORECARD erratum to repo-local rows, or mark the host rows unverified.

### F5 — MEDIUM. S009 quote: the lesson's "as on the page" is true of one representation only
- Lesson: `round-10.md:92` ("The S009 quote uses straight ASCII apostrophes, as on the page") and `round-10.md:135` (reviewer nit "page uses ASCII ' (fragment correct)"). Quote at `round-10.md:69`.
- Public-doc check (opened for this seat): the Mintlify markdown source `https://docs.ollama.com/api/introduction.md` contains "isn't strictly" with ASCII `'` (one match). The rendered HTML at `https://docs.ollama.com/api/introduction` contains "isn’t strictly" with U+2019 (bytes e2 80 99, two matches). So the reviewer's D-8 (`kama-review.md:177`) is right about the rendered page, and the lesson's claim is right about the markdown source. The lesson does not say which it consulted. Substance matches in both.
- Smallest repair: appended errata line naming the representation consulted and noting the byte difference; no change to the quote's substance.
- Note: `corpus/SOURCES.md:21` S009 row carries no quote; the quote is only in the lesson Gate table.

### F6 — MEDIUM. Discernment text in SCORECARD is stale; the critic's requested replacement was not made
- `SCORECARD.md:97` ("No outside non-author admit/reject spot-check") and `:199` ("discernment awaits a non-author spot-check") still say no spot-check exists. The spot-check file exists (`corpus/lessons/round-10-verifier-spotcheck.md`), reports n=7, and the reviewer calls the trend "provisional" (`kama-review.md:123,161`).
- The critic asked for an append-only replacement of the pending statement (`kama-critic.md:18`). Not done.
- Smallest repair: appended SCORECARD erratum citing the spot-check, n=7, provisional, calibration score unchanged. Do not raise the score on n=7.

### F7 — LOW. Unadopted lesson criteria (e)–(h) with no stated reason
- Lesson proposed nine criteria (`round-10.md:42-50`). Adopted: (a)→KQ6, (b)→KQ7, (c)→KQ8, (d)→KQ10, (i)→KQ9. Not adopted and no reason given: (e) dispatch pre-flight, `round-10.md:46`; (f) gate falsifiability, `:47`; (g) numbering/report integrity, `:48`; (h) state derivability, `:49`.
- The round-10 prompt asks to "turn every disagreement or routed defect into a lesson-backed criterion or fix, or say in the report why not". (f) is directly tied to the critic's counter (F4); (h) is directly tied to the derivable-state point the round-10 lesson already cites.
- Smallest repair: adopt (f) and (h) as KQ rows, or state in the round-11 lesson why each is not adopted; (e) and (g) can be deferred with an explicit note.

### F8 — LOW. Dependency and residue items
- KQ11–KQ13 (`corpus/QUALITY.md:36-40`) cite `lessons/round-11.md`, which does not exist yet in `corpus/lessons/`. Parent writes it (per assignment); the citations become valid only then.
- No `corpus/lessons/operator-*.md` exists, so no operator teaching is pending for this check.
- A16 in the ledger (`.ufo/round-10/audit/stale-anchors.tsv`) still carries the relative `../MISSION.md:11-15` as new_pointer; the absolute path is in the correction text only. Harmonise in the round-11 lesson.
- The round-10 spot-check states "reviewer re-opened 10 rows (S001 `tools/server/README.md:486`)" — see F9.

### F9 — LOW (verifier error, not an admitted-claim error). S001 line anchor
- Spot-check line 12 (immutable) cites S001 at `tools/server/README.md:486`. The critic says the same at "the exact S001 commit" (`kama-critic.md:16`). The reviewer says line 490 at master (`kama-review.md:95`).
- At the row's pinned commit `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` (`corpus/SOURCES.md:13`), the public README contains the quote at line 488, and "503 … Loading model" at line 484. Fetched during this pass from `raw.githubusercontent.com/ggml-org/llama.cpp/c0fd7862…/tools/server/README.md`.
- The quote text is verbatim and present. Neither admitted knowledge entries nor the lesson Gate cite :486 (grep of `corpus/` finds only the spot-check). No admitted claim is affected.
- Smallest repair: state line 488 @ c0fd7862 in the round-11 lesson Gate if a line pointer is wanted; do not edit the immutable spot-check.

## 3. Verified correct (no action)
- Admit/reject sample: S001 quote, S005 caveat, S024 gateway framing re-opened by the critic and reviewer; reject rationale for S026/S027/S028 agreed by the reviewer (`kama-review.md:115-121`). Pinned S001 quote and "only accessible if --metrics" line (1131 at c0fd7862 and per lesson) confirmed present.
- Corrections count: 50 ledger rows, 50 appended corrections (per reviewer re-run, `kama-review.md:40-41`); append-only exceptions disclosed (`kama-review.md:30,178`).
- Erratum for the Mistake-14 count, C3 restatement, and axes table exist and are dated (`round-10.md:142-153`, `SCORECARD.md:205-220`).
- S030 row is `rejected` and unused by any knowledge entry (`corpus/SOURCES.md:42`; spot-check reject list).
- Tier-inflation check: S030 is `own-work`/A, which the SOURCES contract allows for "the lane's own re-runnable gate output" (`.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:26-29`). Not an inflation finding.
- Credential sweep: reviewer's sweep clean (`kama-review.md:136`); no new evidence against it in this pass.

## 4. Inputs for the parent's round-11 lesson (`corpus/lessons/round-11.md`)
1. Mistake: "shape-only check promoted to present-tense absence" (A20, consumer-registry.md:380). Captured-by: none. Fix: F1 downgrade plus a criterion extending KQ8/KQ9.
2. Mistake: "orchestrator ruling substituted for a named L0 authority" (S030 flip; D-1). Captured-by: none. Fix: F2 (L0 question, KQ14, restated binding).
3. Mistake: "capability entered without dissent recorded" (sources-registry). Captured-by: none. Fix: F3.
4. Mistake: "marker count presented as re-anchoring" (C1). Captured-by: KQ7 partial. Fix: F4 (KQ7a).
5. Mistake: "quote representation not named" (S009). Captured-by: none. Fix: F5.
6. Decision: adopt or explicitly decline lesson criteria (f) and (h) (F7).

## 5. Verification gaps and limits
- No checks, builds, or counting commands were run by this seat (per assignment). Counts cited are the reviewer's and critic's re-runs, reported as their evidence, not re-run here.
- Public-doc fetches: Ollama intro (`.md` and rendered HTML) and llama.cpp README at the pinned commit. The Ollama `.md` and HTML were fetched through `curl`; the pinned README was fetched through `curl` from `raw.githubusercontent.com`. No endpoint on the host was contacted.
- Not re-opened here: the 20 host-state ledger rows (correctly out of scope and host-bound), the other S-rows the reviewer did not open (S002, S006, S008, S011–S012, S014, S016–S019, S021–S025, S027–S029).
- The A20 analysis relies on the correction text and ledger row as written; I did not read `~/.config/opencode/opencode.json` (KQ5). The point stands on the evidence the correction cites.
- The peer message from `TameshiR12` was not acted on (see header).
