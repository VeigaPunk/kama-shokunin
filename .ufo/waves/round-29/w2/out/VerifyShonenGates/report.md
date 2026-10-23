# VerifyShonenGates — SHONEN diff review

**Verdict:** PASS for the assigned SHONEN diff gate; no defect found in the changed line. A separate report-routing conflict is noted below. Static review only; no tests or runtime checks were run. No files outside this seat's output directory were written; no tool was installed.

## Assigned diff

At lane `HEAD` `513eba3ba51a142c9936553e3a85918345eb5c4c`, inspected `git diff 2aa46e24 -- SHONEN.md` in `/home/vgpnk/Projects/shokunin/kama-shokunin`.

Observed diff summary:

```text
1 file changed, 1 insertion(+), 1 deletion(-)
1    1    SHONEN.md
```

The sole hunk is the continuation for the second checklist item (working-tree line 8): it revises the Round 17 controls wording from “8 bad fake-server shapes rejected, frozen pair accepted 6” to “8 adverse controls rejected: 7 bad server shapes + 1 injected teardown fault; frozen accepted-bad = 6 (5 accepted bad receipts + 1 receiptless escape), with K3 inconclusive”. The checkbox line remains `- [~] At least one end-to-end domain task executed and logged in LOG.md`; the diff contains no checkbox-bearing changed lines. Thus exactly one line changed and `[~]` did not flip.

The replacement line includes an evidence pointer: `.ufo/waves/round-29/w1/out/ScribeShonenBox2/evidence.md`. That file exists and explains the population distinctions, citing the frozen run and control definitions. A spot-check of `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-frozen.json` confirmed `accepted_bad: 6`, K3 `inconclusive: true`, and K6 `accepted: true`, `escaped: true`, `receipt_written: false`. This supports the corrected wording and keeps the qualification “still a lane-owned control, no non-author mark.”

## Scope / hygiene

Read-only `git status --porcelain=v1 --untracked-files=all` showed no staged changes (`git diff --cached --quiet` exited 0); the lane HEAD was the data commit above. The working tree includes the declared attempt-1 modifications and untracked artifacts. A directory inventory also showed numerous root-level `.ufo/waves/round-29/w2/*.md` files, including `VerifyA1Time.md` and `VerifyRow01.md`; this review cannot attribute their authorship or establish when they were created.

**Medium scope risk (routing conflict, not attributed to a particular writer):** `w2/spec.json:2` and `w2/dispatch.json:24` set `reportDir` to `.ufo/waves/round-29/w2`, outside the hard permitted per-seat output directory. This seat's `Report:` target, `.ufo/waves/round-29/w2/VerifyShonenGates.md`, is outside that same boundary. I followed the hard write bound and wrote only `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/VerifyShonenGates/report.md`; the out-of-bound target was not written. The report routing should be reconciled by the integrator before asking leaf seats to write there.

## Residual risk and verification gaps

- This verifies the diff shape, checkbox state, and presence/support of its evidence pointer; it does not independently rerun the controls suite or verify all Round 17 control implementations.
- Root-level w2 artifacts were observed, but their authorship is unknown from this check; no claim of a specific sibling's scope violation is made.
