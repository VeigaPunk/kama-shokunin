# ReviewerInstrumentDocstring: round 25, attempt 2, wave 2 (falsify)

Verdict: defect found. The M17 mechanism, the count change from 27 to 28, the C1 command result and the PM08 status all hold. Found: an overclaim in the SKILL 16384 premise line (F1), a false sentence in the round-25 lesson about the SKILL registry row (F2), an overbroad PM08 phrase (F3), and smaller gaps (F4 to F9).

Target: `git diff 1fc41e346853afd98cbd7010af5db4e54dc877f7 fa3b62ae6475d111eb466d79af616aeebb08bbb9 -- tests/report-audit/isolation-mutants.py SKILL.md`. The diff is 31 insertions and 7 deletions. The instrument change is the new seven-line M17 bullet at isolation-mutants.py:33-39. The MUTANTS and RETIRED lists are unchanged. Line numbers are at fa3b62ae unless marked otherwise. A "survivor" is a mutant the grid does not catch (grid exit 0).

Every new sentence in the diff was checked: the instrument bullet (33-39), the SKILL 16384 line (187-190), the entry pointer (669), the decision-row section (676 onward), the promisor row (887), the isolation row (888), the PM08 paragraph (992-995), and the superseded-count paragraph (1003-1006).

## Findings, by severity

### F1 Medium: SKILL.md:187-190 (16384 premise) states as fact what the lane has not observed

Text: "...`--ctx-size 16384` only because that launch also set `--kv-unified`: both slots share one 16384-cell pool; see `corpus/knowledge/context-capacity.md`)."

- The launch is a sibling lane's September capture, from another build and another model. kengaku-shokunin/corpus/evidence/round10-fleet/r10-scout-endpoint.md:33 gives the argv: `--ctx-size 16384 ... --cache-type-k q4_0 --cache-type-v q4_0 --flash-attn on --fit off --kv-unified ... --parallel 2`. The model is Qwen3-Coder-30B (:33). GPU offload is at :75 and the build commit d7bd3bf is at :36. The per-slot 16384 is observed on /slots (:59, :67).
- Nothing in the lane observes the pool for that launch. context-capacity.md:134-146 says no endpoint reports the KV pool or the cache layout at these flags. The entry calls the capture "historical, other-build evidence, not a kama observation" (context-capacity.md:178-185).
- The "only because" counterfactual is not observed. kama's only paired evidence is at `-c 2048`, fit on, stories260K, build 11755: K2 (`--no-kv-unified`) has per-slot 1024 and K3 (`--kv-unified`) has per-slot 2048, both with a pool of 2048 (committed receipt, cells K2 and K3). That supports the direction only under those settings. The historical launch also had `--fit off`, and no cell tests that setting with and without kv-unified.
- ConnectorSiblingOverlap.md:88 proposed "a split cache would report a smaller per-slot value" and marked "smaller" as [INFERENCE], "not run at 16384". ConnectorSiblingOverlap.md:99 requires every citation to carry "historical, other build". The committed line keeps neither label.
- Partial mitigation: the line sits under "## Historical error signatures — September runtime sample" (SKILL.md:167). The sentence itself carries no label.

Smallest correction: give the September launch's flags, including `--fit off`. Say that per-slot 16384 was observed on /slots in another build. Mark "one 16384-cell pool" and the split-cache counterfactual as [INFERENCE], and point to the "Related lane evidence" section of context-capacity.md.

### F2 Medium: corpus/lessons/round-25.md:49 says the SKILL registry row names M17's survival; it does not

- Lesson text: "the instrument docstring and SKILL registry row now say M17 survives and why".
- SKILL.md:888 (the registry row) says only "survivors reported" and "M11 and M17 re-anchored; M33 is the second call site of the M17 refusal". It has no M17 survival clause. The only SKILL lines that name M17 are :882 and :888.
- The survival statement is in the instrument docstring (isolation-mutants.py:33-39) and in SCORECARD.md:1278-1279 only.

Smallest correction: add one clause to SKILL.md:888, such as "full run at 1fc41e34: 28 mutants, 26 killed; survivors M17 and M20 (reasons in the instrument docstring)". Or change the lesson sentence to name the two places that do say it.

### F3 Low: SKILL.md:887 "with no assertion of any kind" is broader than the code

- promisor-mutants.py:1396-1428 asserts facts about the review-only note's bookkeeping: zero executions, uncredited, and no grid call for PM08. promisor-mutants.py:1755-1772 asserts that `--anchors` skips the note.
- The harness does assert things about the note. It asserts nothing about PM08's behaviour in a candidate. SKILL.md:994-995 already states the narrower claim ("no permanent AST, text or wiring assertion exists for it").

Smallest correction: "...with no assertion about the candidate's PM08 behaviour (the self-test checks only that the note is skipped, uncredited and never executed)".

### F4 Low: the M17 inline comment still reads as live coverage

- isolation-mutants.py:85-87 (the round-25 comment above the M17 tuple) is unchanged from 1fc41e34. It does not say that M17 survives.
- ReviewerC1Patch.md:20-30 asked for "so M17 survives the grid" in this comment. The diff changed only the docstring.

Smallest correction: add that clause to the comment.

### F5 Low: M20's survival has no stated reason

- The docstring names M20 as a survivor (isolation-mutants.py:36) with no reason. Nothing in the instrument or the SKILL gives one.
- A reason is visible in the auditor. `check_history_repo` (report-landing-audit.py:698-706) refuses any repository whose object format is not sha1. `run()` calls it for both repositories (:846-847) before `round_commits` runs `git log --format=%H` (:354) and checks the 40-hex shape (:367). For sha1 repositories, `%H` is always 40 hex, so the M20 check cannot fire. [INFERENCE from the call order. Grid row F15 (grid.fa3b.py:663 and :703) expects the object-format refusal, which fits.]
- M20 also survived at round 23 (ReviewerC1Patch.md:79).

Smallest correction: add one sentence after the M17 bullet with this reason.

### F6 Low, precision: "reached only by full 40-hex tokens" and "no caller reaches"

- The only production call without a peel is report-landing-audit.py:538. It passes FULL tokens only (FULL is at :90). This was verified.
- The self-test calls `lookup()` without a peel on a 4-character prefix (:1169-1170). That token is ambiguous, so it returns at the ambiguous branch (:267-269) and never reaches the check at :275.
- The docstring is right in effect (isolation-mutants.py:37-38), but it reads as a statement about every call. SCORECARD.md:1278 and corpus/lessons/round-25.md:49 say "no caller reaches" the refusal. Caller :538 does reach the check for full tokens, so "fires" is the accurate word.

Smallest correction: "the refusal can fire only for a non-peel token that git resolves through a ref. The one production non-peel caller passes full 40-hex tokens, which git never resolves through a ref." Use the same wording in the SCORECARD and the lesson.

### F7 Low: a stale round-23 row still shows "31 single-literal mutants"

- SKILL.md:820 (the round-23 "Isolation mutants" gate row) still says "31 single-literal mutants of the auditor". ReviewerC1Patch.md:37 flagged it. The diff does not touch it. The supersession paragraph at SKILL.md:1003-1006 covers the count.

Smallest correction: mark the row as superseded in place and point to :1003.

### F8 Info: the M08 numbering gap is not documented

- Neither MUTANTS (isolation-mutants.py:59-131) nor RETIRED (:140-161) has an M08. The gap predates round 25 (ReviewerC1Patch.md:40-44; RevengerM17Sites.md section 7). The counts are right: round 23 had 31 entries, which is 27 retained plus 4 retired. Only the gap is unexplained.

Smallest correction: one sentence next to RETIRED: "M08 was never assigned."

### F9 Low, out of target: context-capacity.md:2 timestamps come from an earlier run

- The entry says the 14 cells were observed "2026-10-22T09:36:51Z to 09:36:59Z". The committed receipt says the run started at 2026-10-22T09:42:42.438Z and ended at 2026-10-22T09:42:50.502Z (out/ReviewerInstrumentDocstring/receipt-timestamps.txt).

## What holds (checks run)

1. Count 27 to 28.
   - Python import of each committed blob. MUTANTS has 27 entries at 147f5bdd, efe58e9 and 92063cf (identical blob, sha256 eace4f56...), and 28 entries at fa3b62ae (sha256 67f57f1a...). RETIRED has 4 entries in all four. Exit 0.
   - The preregistration C1 command, run in a clone checked out at fa3b62ae, printed `registered 28 stale 0 []`, exit 0 (out/ReviewerInstrumentDocstring/c1-command-at-fa3b-clone.txt).
   - SKILL.md:888 and :1006 match these counts. The SCORECARD's "efe58e96" is the 8-character prefix of commit efe58e9 (`git rev-parse --verify -q efe58e96`, exit 0).
2. M17 mechanism (isolation-mutants.py:33-39).
   - Committed full run, final/c1/c1-tip-mutants.json: mutants 28, killed 26, pristine passed, survivors M17-ref-shadow and M20-log-sha-shape. M17 has no failed rows. M33 has failed row F13-ref-named-abbreviation. The .exit file reads "exit=0", .err is empty, and .time reads 16m25.987s.
   - My targeted run in a clone at fa3b62ae: `python3 tests/report-audit/isolation-mutants.py --only M17-ref-shadow --only M33-ref-shadow-bare-objects --only M20-log-sha-shape --json`. Exit 0, wall time 131.9 s, pristine passed. M17 grid_exit 0 with no failed rows (survives). M20 grid_exit 0 (survives). M33 grid_exit 1 with F13 (killed). Copy: out/ReviewerInstrumentDocstring/targeted-M17-M33-M20.json.
   - Round 23: a2-build/out/RevengerM17Sites/r23-M17-run.json (committed) shows M17 killed by F13.
   - Mechanism: F13 is the grid row at grid.fa3b.py:661 (expected text at :702). The peel path calls bare_objects at report-landing-audit.py:246. The M33 site is at :212-214 and the M17 site at :275-277. Both sites are registered.
   - The auditor and grid are byte-identical between 1fc41e34 and fa3b62ae (report-landing-audit.py sha256 b9be4f42...; repo-state-grid.py sha256 99418695...). The instrument differs only in its docstring. The full-run result therefore carries to the tip.
3. The git premise behind "[INFERENCE from source and a probe]". My own probe (git 2.56.0, scratch repo outside the lane) matches the lane's probe_git_shadow.out. A short name shadowed by a tag resolves to the tag's commit. A full 40-hex name resolves to its own object, even when a tag with that name points elsewhere (out/ReviewerInstrumentDocstring/git-probe-own.txt; each command exit 0). The [INFERENCE] label is fair.
4. PM08 status. promisor-mutants.py:418-438 is the entry (execution "review-only", no alternatives, no expect rows). :770-779 and :893-901 show it is never built, never gridded, with executions 0 and not credited. :1396-1428 is the self-test, and :1772 expects 10 checked mutants. The list has 11 entries: 10 executable plus PM08. "Manual, review-only, unexecuted, uncredited" holds. "No assertion of any kind" does not (F3).
5. Round-25 decision rows (SKILL.md:676 onward). The values match the committed receipt: K1 to X3 props_n_ctx, total_slots, kv_pool_n_ctx and slots_n_ctx; L1 both 500 with "Context size has been exceeded."; L2 and L3 both 200; K1 and X2 identical endpoints with pools 2048 and 8192. Not checked: "fit never lowers a context on this fixture" (relies on S106, another seat) and the raw-log line numbers for L1.
6. The entry pointer (SKILL.md:669) holds. context-capacity.md has the rule and the observed cells (:7-67 and :99-130).

## Verification gaps

- I did not repeat the full 28-mutant run (about 16 minutes). The full-run JSON has no commit stamp. The claim "full run at 1fc41e34" comes from the lesson, the docstring and ExecC1TipReplicate.md. The byte-identity check above supports it.
- I did not re-open S106 or S109, or re-check the M11/F20 kill. Other seats cover those.
- The kengaku evidence was read from the sibling lane's working tree (r10-scout-endpoint.md:24-83), not from committed bytes.
- No llama-server was started and no port was opened.
- No tool was installed or upgraded. The host git 2.56.0 was used (`git --version`, exit 0).

## Files written

- .ufo/waves/round-25/a2-falsify/advice/ReviewerInstrumentDocstring.md (this report)
- .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/instrument.diff
- .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/targeted-M17-M33-M20.json
- .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/targeted-M17-M33-M20.err
- .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/c1-command-at-fa3b-clone.txt
- .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/context-capacity.committed-fa3b.md
- .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/lesson-round-25.committed-fa3b.md
- .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/receipt-timestamps.txt
- .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/git-probe-own.txt
- Scratch outside the lane: /fast/scratch/hyaku/kama-r25a2w2/ReviewerInstrumentDocstring/ (clone at fa3b62ae, extracted blobs, probe repository gp/, tmp/).
- Directories created in the lane: .ufo/waves/round-25/a2-falsify/out/ReviewerInstrumentDocstring/ and .ufo/waves/round-25/a2-falsify/advice/.

Report: .ufo/waves/round-25/a2-falsify/advice/ReviewerInstrumentDocstring.md
