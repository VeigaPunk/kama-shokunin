# K7Calib — verdict: `corr_lost 151 → 0` is a count of unheld historical lines under the frozen audit, but it is not by itself a count of mismatches between self-assessment and repository state.

## Axes
Calibration (C2). No operability claim assessed.

## Evidence

- Ran `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --to 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --json` (exit 0). At the requested build tip, its output says `definition=v6`, `threshold=1`, `events=109`, `partial=0`, `unrestored=0`, `disclosed_lines=10`, `bad_disclosures=0`, and `bad_declarations=0`. This is a history-derived result for the *declared contract*, not a direct comparison against all self-descriptive sentences.
- At `SKILL.md:1553` the lane says the round-52 disclosure ledger “holds only the 10 lines” in the two named categories. The counter output agrees: ten valid disclosures, five events disclosed, no bad rows. This statement is true for the counter's disclosed set.
- At `SKILL.md:1558`, the lane says each restored block holds lines lost in place, verbatim, inside five-backtick fences, one block per deleting commit. The audit's zero partial/unrestored result supports restoration of every *graded key* at the tip; the counter does not independently establish byte-for-byte provenance/meaning of each fenced block solely from that aggregate.
- The supplied frozen build result for the separate round-52 C2 counter is `fixture=1 lane=1 corr_lost=0 met=True`; that supports its preregistered behavior. It still does not turn 151→0 into a general census of self-assessment mismatches: it grades contract-bound files/regions and its own simplified exemption rules.
- Current lane sentences in the requested grep set that make historical or procedural append-only claims include `SKILL.md:578, 614, 630, 1341, 1363, 1434–1558`; `corpus/README.md:637, 759–761, 776–826, 910–997, 1073, 1082–1203, 1239, 1247, 1294–1383, 1432–1476`; and `SCORECARD.md:6, 14, 26` (search output includes many explanatory/historical references, not all compliance assertions). The 80-line grep limit stopped before the full requested set; these are not represented as exhaustive.

## True / false distinction

At the build tip, categorical assertions that **all** append-only declarations were continuously obeyed are false: the lane's own audit history records 109 events, including historical losses. In particular the round-51 `corpus/README.md:1432–1435` prose reports 166 disclosed lines in 51 events at that build, which was accurate for round 51 but is not current at round 52. Declarations remain self-assessment; historical commits are state evidence.

The narrower current claims that all *graded* line losses are now restored or disclosed, and that the remaining ten disclosures are exactly the permitted A/A-row exceptions, are supported by the audit output. The broader claim “corr_lost=0 means no mismatch between every append-only sentence and actual Git history” is false: the counter is bounded to declared contract paths/regions and does not parse every sentence surfaced by grep into an independent compliance proposition. An exemption/ungraded result is also not evidence that a line was never lost.

## Smallest safe correction

Describe C2 as “count of contract-graded lost lines no longer unheld at this tip, subject to the registered regions, exemptions and disclosure rules,” not as the total mismatch count for every self-description. Keep the separate sentence-level inventory and history audit if the intended calibration quantity is declaration-vs-history mismatch. This is a calibration framing limitation, not evidence that the frozen counter is defective under its preregistered contract.
