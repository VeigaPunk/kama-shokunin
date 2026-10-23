# kama — round 29 report skeleton (attempt 2 / w2)

**Draft for L1 integration. Verdict lines remain TODO.** This draft records only committed round-29 facts through `513eba3ba51a142c9936553e3a85918345eb5c4c`; it does not treat the current final receipt, lesson, or SOURCES edits as committed evidence.

## Behavior

- **C1 (measured; calibration): [TODO — L1 verdict].** Frozen contract: check base `SCORECARD.md`/`SHONEN.md` self-assessments in six classes (P/H/N/C/T/Q) against the writing revision `W`; append one correction row with the counter-observed value for each false statement. Evidence: `.ufo/waves/round-29/preregistration.json` and `.ufo/waves/round-29/count-c1.py`, frozen at `827d136546b85059a984b34970f5b493d9a71290`; base is `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`.
- Frozen instrument identity: SHA-256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (`preregistration.json`, `counter_sha256`). The committed base receipt says `statements 69 mismatched_at_base 11 ... unresolved 11 met False` (`.ufo/waves/round-29/before/c1-base.out`, commit `827d1365…`). **Final measured result: [TODO — L1 verdict and committed receipt citation].**

## Gates

- **Pre-data controls: [TODO — L1 verdict].** Commit `35b90184f638ab6a4149092b93143c7a2b873787` freezes the 14-seat control receipts before correction rows. Its committed `.ufo/waves/round-29/controls/SUMMARY.md` states: `Target: mismatched_at_base >= 1 and unresolved == 0. No control meets it; the counter was not changed.`
- The same summary records all 14 controls as `False`; reference policy `RefPaste` is `valid 11, false 0, unresolved 0` / `True` by design. Evidence: `.ufo/waves/round-29/controls/RefPaste/REPORT.md`, `counter.out`, and `receipt.json` (commit `35b90184…`). This is a control-wave result, not the final fresh-clone measurement.
- **Final fresh-clone receipt: [TODO — L1 verdict].** Do not quote a final result from this skeleton unless L1 binds it to its committed artifact and hash.

## Touched surfaces

- Commit `513eba3ba51a142c9936553e3a85918345eb5c4c` records 11 appended self-assessment correction rows in `SCORECARD.md` under `## Round 29 — self-assessment corrections`; the table names each `SA29:` statement, its writing commit `W`, cause, and observed value. Evidence: that commit's `SCORECARD.md`.
- The same commit adds round-29 mined receipts under `.ufo/waves/round-29/mined/`, and the routed repair receipt under `.ufo/waves/round-29/repairs/echo-exit2/receipt.txt`; its subject also records the `tools/prereg-time-check.py` space/tilde time-form fix. These are committed side surfaces; **C1 verdict: [TODO — L1].**
- Freeze and control artifacts: `.ufo/waves/round-29/before/c1-base.json`, `.ufo/waves/round-29/before/c1-base.out`, `.ufo/waves/round-29/controls/SUMMARY.md`, and per-control evidence under `.ufo/waves/round-29/controls/` (commits `827d1365…` and `35b90184…`).

## Out of scope

- This claim measures the accuracy/correction of historical lane self-assessments; it does not itself establish live model-serving or endpoint-health behavior. Evidence boundary: C1 `surface` and `claimed_work` in `.ufo/waves/round-29/preregistration.json` at freeze `827d1365…`.
- This draft makes no independent admission, axis-trend, or final-receipt verdict. **[TODO — L1 decision.]**

## Findings

- **Round-29 lesson: [TODO — L1 cite committed lesson/hash].** `git ls-tree -r --name-only 513eba3 -- corpus/lessons` contains no `corpus/lessons/round-29.md`; do not cite the local working-tree lesson as committed evidence. The committed preregistration points to the prior routed source at `corpus/lessons/round-28-verifier-spotcheck.md` (`repairs_not_claims`, line 51).
- **SOURCES rows: [TODO — L1 cite committed rows/hash].** The frozen preregistration says the C1 sources rely on Git manuals and that corresponding SOURCES rows are to be opened and cited (line 48). The current working-tree diff from `513eba3` adds `S174`–`S177` to `corpus/SOURCES.md`, but those additions are not in that commit; do not present them as committed until L1 lands them.
- **Final receipt: [TODO — L1 cite committed fresh-clone artifact/hash].** Commit `513eba3`'s tree has no `.ufo/waves/round-29/final/` receipt, so the final result stated outside the committed artifacts is not reproduced here.
- L1 integration target: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-29/kama.md`. This seat's draft is stored at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/ScribeReportDraft/report.md`.
