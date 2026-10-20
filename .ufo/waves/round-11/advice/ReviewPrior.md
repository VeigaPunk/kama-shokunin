# ReviewPrior — round-10 verifier spot-check and SCORECARD erratum: disagreement and defect ledger

Seat: ReviewPrior (leaf, advisory). Author-side advisor output; not a non-author verification (QUALITY.md §Review boundary).

**Verified-at (actual review):** 2026-10-20 UTC (`date -u` → 2026-10-20T02:16Z). The steered round label 2026-10-19 is retained only as a label. Historical observations are cited as recorded: reviewer fetches in `.ufo/waves/kaika-w3/kama-review.md` are dated 2026-10-19 by their author. Nothing in this file was fetched or re-run this session.

**Method and scope.** Read `corpus/lessons/round-10-verifier-spotcheck.md`, `SCORECARD.md` §Round 10 and §Erratum, and the fleet verifier files `../.ufo/waves/kaika-w3/kama-review.md`, `kama-critic.md`, `VERIFICATION-PROVENANCE.md`. Checked current text by grep/read in the lane. No builds, tests, lint, formatters, or network fetches. No installs. No files edited; parent-owned files (LOG.md, SCORECARD.md, QUALITY.md, corpus/README.md, lesson files) are untouched.

## 1. Ledger: every disagreement or routed defect, and whether it is fixed

Status key: FIXED = text change verified present; PARTIAL = fix present but does not reach the stated defect; OPEN = not addressed in current text; DISPUTED = the orchestrator ruled against a verifier without new evidence.

| ID | Source of defect | Defect or disagreement | Status now (evidence) | Sev |
|---|---|---|---|---|
| R1 | spotcheck:17 vs kama-review §5/§10, kama-critic | Spot-check agreement is orchestrator-dispatched. Spotcheck header calls W3ReviewKama "fresh agents dispatched by the orchestrator"; review self-labels "orchestrator-dispatched" and says its verdict is superseded only "if the orchestrator accepts this reviewer as the non-author check." The orchestrator accepted it. | OPEN. QUALITY.md:17 already says "parent-dispatched advisor agreement [is] not an outside spot-check." SCORECARD.md:199 still says "discernment awaits a non-author spot-check." Spotcheck Trends still says "discernment improved." | HIGH |
| R2 | spotcheck:17 vs SCORECARD erratum table | Internal contradiction on discernment and calibration. Spotcheck Trends: "discernment improved." Spotcheck per-axis line and erratum: calibration "unchanged (8, 7, 7, 7)". No erratum row records discernment. | OPEN. | MED |
| R3 | erratum:220; lesson round-10.md:152; kama-review D-1 and Q1 | Documentation-only ruling. The reviewer's binding quote: "no live-target probing, scanning, logins or submissions — documentation only" (kama-review.md:166, citing `kama-round-10.md` §6.5 bullet 4). Reviewer Q1: "yes — the binding names kama." Reviewer condition 1 required the lane to record L1 gate outputs as out-of-rule with no claim citing them. The orchestrator instead ruled them "inside kama's province" and said the rule "targeted external live targets." The ruling does not quote the binding text. The critic calls the same runs "a prohibited live-target probe" (kama-critic.md:14). Ruling is self-issued by the integrator. | DISPUTED. Reviewer condition 1 is not met as written; the ruling reverses it. KQ10 requires census/probe scope to be "the task's declared scope"; the ruling widens scope after the fact. | HIGH |
| R4 | erratum:219-220; spotcheck:13 S030 "agree" | S030 rejection rests on the rule R3 overturned. Reviewer row 7: "agree on rejection … correct under the documentation-only binding." Erratum: "its flip condition is now met," yet S030 "stays rejected" and re-admission is deferred to a later round. No in-round re-decision. | OPEN. SOURCES.md:42 still records S030 with `check.json` as evidence. | MED |
| R5 | erratum C1 row and freshness pointer vs kama-review §13 condition, D-4 | Admitted scope mismatch. Reviewer admits C1 "narrow (7→8) for the 30 repo-local rows." 20 of 50 ledger rows (A06, A16–A29, A31, A33, A35, A36, A38) read host state (`~/.config`, `/tmp`, fleet-root paths). The erratum's freshness pointer and SCORECARD round-10 C1 row cite all 50. | OPEN. Host-state rows not re-anchored, not labelled lane-observed-unverified, and not excluded from the 50→0 evidence. | MED |
| R6 | kama-critic C1 counterexample; validator header; lesson:151 | Pointer "resolved" is bounds-only. `validate-new-pointers.sh` header: "Bounds only: whether the range carries the claimed content was sampled by reviewers." Lesson:151: "Content correspondence (not just bounds) remains the sampled reviewer check." Erratum prints `rows=50 resolved=48 terminal=2 unresolved=0` with no "bounds-only" qualifier. Critic's point that the old counter ignored `new` is handled by the classification split. | PARTIAL. Split present (lesson:143-151, LOG:527). Qualifier missing from erratum. Content check not done for 48 rows. | MED |
| R7 | kama-review D-3; lesson:142; erratum | Mistake-14 count retired. Lesson errata retire the substring count (15 base / 29 head) and withdraw "target 15 to 0." | FIXED (lesson:142; LOG:527). Residual: QUALITY.md:29 (KQ7) still cites "Mistake 14" as its motivating lesson, although that mistake's count is retired. | LOW |
| R8 | kama-review D-2 | SCORECARD axes table stale. Top table still reads "freshness 6 → 7 / coverage 1 → 8." | FIXED as an appended superseding erratum (SCORECARD.md:205-220). PARTIAL on the contract: SCORECARD.md:3-4 requires "the round that last changed it" for each row, but the erratum's "unchanged" row shows "—" for operability, depth, calibration, and adjacency. The top table records last-change rounds 3/1/1/1 for those rows. | LOW-MED |
| R9 | kama-review D-5 | A18 config-body read (4 lines of `config/l1-max-context.yml`) under Mistake 9 scope. | OPEN, disclosed, no erratum. Reviewer: non-blocking. | LOW |
| R10 | kama-review D-6; kama-critic C1 | C1 "before" is definitional (base 50 = absence of tag). | PARTIAL. Lesson:143 labels it. SCORECARD round-10 C1 row (line 196) and erratum still read "uncorrected 50 → 0" with no label. | LOW |
| R11 | kama-review D-7 | Mis-cited anchor: metrics/GGUF "no rows" claim attributed to README §Known gaps. | Appears FIXED. No current text carries the metrics/GGUF phrasing with Known gaps. Lesson:98 cites §Known gaps only for "llama.cpp-only runtime evidence," which matches README:49. No erratum records the rewording. | LOW |
| R12 | kama-review D-8 | S009 gate quote uses ASCII apostrophe; live page uses U+2019. | OPEN. lesson:69 still carries "Ollama's API isn't strictly versioned…" in the form the reviewer recorded. Byte-level check not re-fetched this session. | LOW |
| R13 | kama-review D-9 | Five append-only exceptions (newline-only rewrites, SCORECARD row replacements). | CLOSED as recorded (LOG:523 discloses them). | INFO |
| R14 | kama-review D-10 | S026 tier A scoped to "proposal history only." | CLOSED, note only. | INFO |
| R15 | kama-critic C3 | Coverage padding by administrative rows (`SOURCES.md`, lesson). | FIXED. Erratum restates C3 on knowledge entries (9→12; 0→3). Verified by grep: 12 files in `corpus/knowledge/*.md`; 3 with `^source: S###`; 9 without any `source:` line. | — |
| R16 | kama-critic C3 | Critic asks that the independent source re-open be recorded by appended correction, replacing "pending-outside-check" wording. | OPEN. SCORECARD.md:192 still reads "pending non-author verification." | MED (ties to R1) |
| R17 | kama-critic C1 A16 | A16 portability: correction names host-absolute paths (`/home/vgpnk/Projects/shokunin/MISSION.md`), so it does not resolve from the repo. | OPEN. Correction still host-absolute (alias-endpoint-normalization.md:60). | LOW |
| R18 | VERIFICATION-PROVENANCE.md:3 vs spotcheck:3 | Chronology boilerplate ("after the round landed at `40660352d`") is withdrawn in the fleet provenance note as "not necessarily the workers' dispatch or execution cutoff." The withdrawal is not appended in the kama spotcheck file. | PARTIAL (fleet note only). Needs an appended correction in the kama file. | LOW |
| R19 | spotcheck:12 vs kama-review §4 | Row count mismatch. Spotcheck: reviewer "re-opened 10 rows." Reviewer §4 table lists 11 (S001, S004, S005, S020, S026, S013, S015, S007, S003, S009, S010). | OPEN. Correct to 11 by appended note. | LOW |
| R20 | lesson:151 | Negative control for validator ("SKILL.md:9999 and nope.md:1 prints unresolved=2"). | Stated in lesson; not re-run (no-tests rule). The script file itself embeds no control. | UNVERIFIED |
| R21 | erratum:219-220 | "No claim rests on them either way" for the contested gate runs. The critic and reviewer both say the outputs are cited in LOG, SCORECARD, and the lesson. | OPEN. Citations remain. Not re-verified against all citing lines. | MED (ties to R3) |

## 2. Missing criteria: recommended exact text

QUALITY.md's Review boundary (line 17) is prose only. Nothing in the admit table requires a spot-check's dispatch record, and nothing bars a binding reinterpretation by the adjudicator. Recommended rows, appended as new lines (no existing line moves; parent-owned file). Each is grounded in the cited ledger item.

**KQ11 — spot-check independence (ties R1, R2, R16).**
- Admit only when: a discernment or calibration trend, or any `[x]`, cites a spot-check whose verifier provenance (dispatcher, workspace, and author) shows no author and no parent dispatch, and the verdict text names that provenance.
- Reject or limit when: a verifier dispatched by the orchestrator, or one whose dispatch is unrecorded, is counted as the non-author check. Such a verdict is recorded as "author-side advisory."
- Motivating lesson: `lessons/round-10-verifier-spotcheck.md`; QUALITY.md §Review boundary.

**KQ12 — binding scope and after-the-fact rulings (ties R3, R4, R21).**
- Admit only when: a gate or census output enters an admission only if the round's binding text, quoted verbatim, names its target class. Any ruling that reinterprets that text is appended with the quoted text, the reviewer's recommended ruling, and the reason it differs. Outputs produced outside the binding are excluded and any citing line is marked out-of-rule.
- Reject or limit when: a ruling narrows or widens a binding without quoting it, or reverses a reviewer's condition without new evidence. An output cited in an admission while excluded is a defect.
- Motivating lesson: `lessons/round-10.md` §Contested L1 gate runs; KQ10; `kama-review.md` D-1.

**KQ13 — pointer "resolved" means content, not bounds (ties R6, R10, R17).**
- Admit only when: a `resolved` pointer is one whose cited range contains the quoted claim (`grep -F` of the claim inside the range). Bounds-only counts are reported under a different label (e.g. `in-bounds`) and never as `resolved`.
- Reject or limit when: a host-absolute or host-state pointer is counted in the repo-evidence total. Such rows are labelled lane-observed-unverified.
- Motivating lesson: `lessons/round-10.md:143-151`; `kama-critic.md` C1; `kama-review.md` D-4, D-6.

**Amend KQ7 (ties R7).** Keep the row; add a supersession note that Mistake 14's count is retired and that the ledger count is the operative measure. QUALITY.md's supersession rule requires naming the old criterion, not erasing it.

## 3. Corrections needed (append-only, owner noted)

1. Erratum (SCORECARD, parent): add discernment row "unverified — author-side advisory (KQ11)"; state calibration remains 7 pending a non-author check. Annotate R2 in the spotcheck Trends line.
2. Erratum (SCORECARD, parent): restate freshness evidence as "30 repo-local rows; 20 host-state rows lane-observed-unverified" to match the reviewer's admitted scope (R5). Add "bounds-only" to the `resolved=48` line (R6). Add last-change rounds to the unchanged rows (R8).
3. Erratum (SCORECARD, parent): S030 re-decision row, or an explicit "rejected by superseded rule; re-decision due round N" with the rule reference (R4).
4. Lesson (round-10 owner, appended): correct the reviewer count to 11 (R19); quote the binding verbatim beside the ruling and record the reviewer's recommended ruling (R3); keep the critic's "prohibited live-target probe" finding visible rather than recording only the ruling (R21).
5. Spotcheck file (appended): withdraw the chronology in the header per `VERIFICATION-PROVENANCE.md` (R18).
6. A51 (KQ8): the ledger row records no verbatim error for any blocked command. Append the exact blocked command and its verbatim error, or keep `UNDECIDABLE` with an explicit "no blocked command run" note.
7. A16 (R17): replace host-absolute paths with a repo-resolvable pointer or label the row lane-observed.

## 4. Verification gaps and limits

- Not verified this session: reviewer fetch results (historical, 2026-10-19), the validator negative control (R20), S009 apostrophe bytes (R12), and the 20 host-state rows (R5). No network or host reads were done, per the round-11 contract.
- Dispatch record for W3CriticKama is not shown in `kama-critic.md`. It self-labels "external." KQ11 applies to it too until its dispatch record is produced.
- L2 floor and sentinel/critic transcripts were not checked (kama-review D-11).
- Adjudication of R3 belongs to the canonical adjudicator and parent; I recommend, I do not rule.

## 5. Installs

None. No tool installed, updated, or upgraded for this slice.
