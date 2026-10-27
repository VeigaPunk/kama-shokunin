Verdict: SCORECARD restoration is structurally complete for its 23 disclosed lines; four restored line instances in `## Planned` are exempt under C2's simplified section-only rule but graded by append-only-audit v6.

Evidence (build tip `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`):

- Ran `python3 tools/round52-append-restore-check.py --repo <shared-clone> --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch <seat-scratch>`; exit 0, output `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`. Tool leg reports `append-only-audit.py` v6 exit 0, 109 events, no unheld A-corr lines.
- `git show <build>:SCORECARD.md` places `### Restored lines (round 52)` at line 2929. The body explicitly states one fenced block per deleting commit in history order (line 2931); eight commit blocks appear, each delimited by five backticks. The eight groups contain 6+4+4+1+3+2+2+1 = 23 line instances (commits fd48f9a3b7ca, 4d2e74f421bc, 6de225c289b7, 026eede9f46a, ce41bae692c8, ef76777e5fbd, 42ea1204aef3, db6bfa8d9354). The round-30 heading and all other restored payload text are retained within the fences.
- Base ledger has 23 SCORECARD.md disclosure rows; tip ledger has 0 SCORECARD.md rows. The C2 lane check confirms 10 remaining ledger lines exactly match A/A-row unheld keys and 0 A-corr losses.

Four instances missed by C2's simplified exemption, but graded by the tool:
1–2. The two lines under deletion event `ef76777e5fbd` at SCORECARD block lines 2979–2980: `Superseded in round 42. The live plan is ...` and `### Planned (round 44)...`.
3–4. The same two lines under deletion event `42ea1204aef3` at block lines 2986–2987: `Superseded in round 42. The live plan is ...` and `### Planned (round 47)...`.

Why: in each parent blob these deletions sit in the exempt-titled `## Planned` section, so C2's `graded_of()` rule (counter lines 195–206) classifies them ungraded solely from that title. The tool's v6 rule (append-only-audit.py docstring lines 19–22) additionally requires the deleted line's origin to contain an exempt title and that the parent section be eligible/not gutted. These old head-plan lines originated in the historical/dated round plan sections, not an exempt-title origin; thus origin does not authorize exemption and v6 grades them. They are nevertheless present verbatim in the four five-backtick blocks above, so tool restoration is satisfied. This demonstrates a real calibration difference: the C2 counter's corr_lost check alone would not detect omission of these lines; the tool's independent lane leg does.

Verification gaps: I did not independently reimplement the full origin genealogy; the classification is grounded in the frozen tool definition and the restored block's event labels, with the C2 counter's eight fixtures and lane/tool exit evidence recorded above. No lane files were modified.
