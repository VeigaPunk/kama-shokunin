VERDICT: partial - M8 counter numbers, exit records and the S055 live/ vs live-recovery split reproduce from committed bytes; the gate-live-1 pin points at the wrong revision, M9's good_rejected guard has no unit case, bucket-stripped rows evade the accepted_bad check, E5 stays open, and erratum defects 1 (LOG.md) and 4 (uncommitted dispatch record) are not closed.

## Scope and method

- Work copy: `/tmp/kama-r19-MistakesEvidence` (cp -a of the lane at HEAD `8bf99ca`). The lane was not modified; this report is the only lane write.
- "Committed bytes" = git objects at HEAD and at the cited revisions (`1b85a24`, `1c325b2`, `eb78788`, `101f399`, `c6dc46f`). The M8/M9 rows are committed. The erratum (`corpus/lessons/round-18.md` 387–421), `registry/required-citations.json`, `tools/citation-provenance.py`, `residual/assignments.json` and the SCORECARD/SOURCES additions are **uncommitted** (C12–C13; `git diff --stat`). Their claims were checked against the committed artifacts they cite.
- Official counts were not re-run (L1-owned). Seat-permitted `--selftest` only: C1 45/45 exit 0 (C17); C2 60/60 exit 0 (C18).
- Receipts: `/tmp/kama-r19-MistakesEvidence/out/receipt.log` (`out/receipt.sh`; checks C01–C41, each `[exit=N]`). Mutant transcripts `out/mut/MA–ME.{out,err}`. End-to-end fixtures `out/m9/results.json` (driver `out/m9/cases.py`, exit 0, C19).
- Installs/updates: none.

## Verified

1. **M8 official exits and counts.** `c1-measure` and `c2-survivors` exit 0 at HEAD. C1: accepted_bad 5→0, good_rejected 1→0, misclassified 1→0, uncontrolled 0→0. C2: 15 named; after killed 11 / correct 1 / handled 3; inconclusive 0 (C23–C24, C36–C37). All 32 recorded stdout/stderr digests and exit files in `runs/commands.json` match committed files (C29).
2. **M8 failing records.** Both counters exit 2 at `101f399` (C21–C22). Published head bytes differ from the retained run: C1 retained `55b26b3b` (= c6dc46f) vs head `a9577ed8`; C2 retained `2af03fed` vs head `87cad1ca` (C32–C35).
3. **M9 behaviour at HEAD** (fixtures, out/m9): accepted_bad under-report with bucket present → exit 2 (01); bucket-less sibling beside a bucketed forgery → exit 2 (02); good_rejected under-report → exit 2 (04); undeclared exclusion → exit 1 (05) and declared → exit 0 (06); arms below rows → exit 2 (08); good_ok=false → exit 2 (09, 10).
4. **Erratum defect 1 verdicts.** 4 confirm (ResidPrivacy, ResidHealth, ResidImplPin, ResidCounterC2) and 3 partial (ResidCounterC1, ResidCorpus, ResidClaims) match the committed advice VERDICT lines (C14).
5. **S055 pointers.** `commands.json` is absent at c6dc46f (C03, exit 128) and first added at 1c325b2. Identical bytes at 1c325b2, 101f399, eb78788 (C04a/b). Tip `live-gate-1..3` cite `live-recovery/` (C07, C39). `live/` unchanged 1c325b2→HEAD (C25). Checkpoint `live/receipt-1` at 1c325b2: pass, 11/11 (C28). Tool digests `dc036d7d` (live/) and `83eac5c0` (live-recovery/) (C26–C27).
6. **Erratum defect 3 command.** Official argv is `survivors.py --json` (commands.json). The stdout JSON matches its cite (C05, exit 0). Defect numbering traces to the committed spot-check `8bf99ca:corpus/lessons/round-18-verifier-spotcheck.md` §Routed defects 1–5.

## Refuted or not shown

A. **gate-live-1 pins the wrong revision (refuted as pinned).** The row and the erratum sentence say the gate output "describes `live-recovery/`", but `cite(eb78788, live-gate-1.stdout, b2043ba8…)` pins bytes reading `live/receipt-1.json` with zero `live-recovery` matches (C06b–c). The checker still reports it ok (C08–C09, verified=3). Correct pin: `1b85a24`, sha `1cb5a41b…` (C07). A re-pinned token verifies (C11, exit 0).
B. **"Routed revision defects are now machine-checked" overclaims.** Three rows cover defects 2 and 3 only. Defect 2's row is the wrong revision (A). Defects 1 and 4 have no row. The checker tests token presence and blob digest, not the sentence it supports (C08–C10).
C. **Defect 4 (6 reviewer / 1 critic) has no committed record.** `residual/assignments.json` is untracked (C12 exit 1; C13 exit 128). Its totals are internally consistent, but no committed advice file records a role.
D. **Defect 1 is half-done.** The lesson gets an appended correction. `LOG.md:1122` still says "five confirm, two partial" and is unchanged (C15–C16). The spot-check named LOG.md explicitly.
E. **"The two agree" holds for outcomes only.** Per-item before/after verdicts (15/15) and counts match (C30, exit 0). The tool bytes differ (`87cad1ca` vs `ac934794`). The 04:08Z run used the 101f399 counter, which lacks the selftest_arm target-literal rule and the `combine_arms([])` guard (`git diff 101f399 HEAD -- c2/survivors.py`). The erratum should say so.
F. **M9 good_rejected guard is not shown able to fail.** Removing the under-report check leaves the committed selftest at 45/45, exit 0 (MB; `out/mut/MB.out`). Mutants MA (accepted_bad check, exit 1), MC (declared-exclusion, exit 1), MD (arms-below-rows, exit 1) and ME (document-wide bucket gate restored, exit 1) are each caught. Mutants were applied in the copy with `edit` and restored (C20, exit 0).
G. **M9 cross-check is silently skipped for bucket-stripped rows.** Fixture 03 is the E1 forgery with the forging row's `bucket` removed. It has accepted_bad=0 and exits 0 CLEAN with no fault or note. The skip is `if bucket_rows:` (measure.py:620). Misclassified still falls back to classification, so the docstring's "cross-checked the same way" (lines 46–48) is false for accepted_bad/good_rejected. Delivered `controls.py` always emits `bucket` (line 1140), so this needs a non-conforming child. M9 does not name it. The good_rejected path shares the mechanism [INFERENCE from the same filter at line 632–633]. E1 is therefore closed only for bucketed rows.
H. **E5 is not closed.** `gate_flip_arms=99` with one flip row exits 0 CLEAN with a note (fixture 07). The fix covers below-rows only, so E5 should not be listed as closed evidence.
I. **M8 pre-repair claim holds for C2 only.** `runs/pre-repair/` holds `c2-survivors.json` alone (C38). C1's exit-2 record exists only in git history at 101f399.
J. **Process claims are not checkable from bytes** [INFERENCE]: M8 "the coordinator treated counter repair as done without re-running"; M9 "fresh falsifier attacked the counting command" (consistent with committed `falsify/advice/CounterC1.md`).

## Requested changes (not applied)

1. Re-pin gate-live-1 to `1b85a24` (sha `1cb5a41b…`) before commit, or reword the sentence to what the pinned bytes show.
2. Add committed selftest cases: good_rejected under-report must fault; bucket-stripped accepted rows must fault or emit a note. Reword measure.py lines 46–48 to match the code.
3. State E5 as an open note in M9 and remove it from closed evidence. Narrow E1 to bucketed rows.
4. Append a correction to `LOG.md:1122` (defect 1).
5. Commit and pin `residual/assignments.json`, or drop the 6/1 claim (defect 4).
6. Qualify "the two agree" to outcomes and name the counter-byte difference.
7. Commit the erratum, registry, tool and SCORECARD/SOURCES additions. None is in committed bytes yet.

## Not executed / observed

- Official `survivors.py --json` and the official `measure.py` run were not executed by this seat (L1-owned).
- During C31, other seats' transient C2-counter processes were visible (pids 376526, 376527, 515797, 523793, 528120). This seat started none, touched none, and they had exited by the next check. No copy-local process remains.
