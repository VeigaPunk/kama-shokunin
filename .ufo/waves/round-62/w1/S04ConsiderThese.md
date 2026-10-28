# S04 ConsiderThese — proposal audit

## Scope and method

Read the frozen round-62 claims (`.ufo/waves/round-62/controls/freeze.txt`) and the proposal lists in `considerthese/2026-10-26.md` and `considerthese/2026-10-25.md`. The proposal files are operator-authored inputs; neither was edited. Their text establishes what was proposed and, in one instance, reports prior uptake. It does not establish present implementation status for every proposal. I therefore report every proposal recorded in those two files and mark status only where the files themselves provide evidence.

## Proposals and status evidence

### 2026-10-26 (four proposals; `considerthese/2026-10-26.md:29-35`)

1. Flag deletions in append-only files the morning after they happen. **Current implementation status: not established in these proposal files.**
2. Track what happens to the author's own proposals, including rounds that took them up or deferred them and closure verdicts. **Current implementation status: not established.**
3. Keep a running count of counters that a shortcut can satisfy: tally shortcut controls met, surviving mutants, and whether the falsify wave ran. **Current implementation status: not established.** This is the most relevant item to round 62's counter-work and frozen predicates.
4. Report the pin gap each morning, with newest tags and releases above each pinned engine. **Current implementation status: not established.**

### 2026-10-25 (four proposals; `considerthese/2026-10-25.md:27-33`)

1. Recompute each digest and S-id cited by new lessons or rows, checking full digests and S-id attribution. **Current implementation status: not established.**
2. Watch upstream releases for pinned engine versions. **Current implementation status: not established.**
3. Keep a ledger of repeatedly rejected staged items, including reasons and repeat counts. **Current implementation status: not established.**
4. Report seat yield per wave, with launched seats, landed reports, and failure reasons. **Current implementation status: not established.**

The 2026-10-26 reflection does say that three of the four 2026-10-25 proposals became rounds 41–43, while one was first deferred; this is a historical uptake statement, not evidence of their current implementation (`considerthese/2026-10-26.md:31`).

## Selected proposal and located quote

Selected: 2026-10-26 proposal 3. The frozen C1 and C2 predicates explicitly require rejection of control families and sensitivity to decisive evidence; trending shortcut controls, surviving mutants, and falsify-wave execution is directly pertinent to assessing whether counter claims resist shortcuts over time. This relevance is a comparison to the frozen predicates, not a claim that the proposal is implemented.

> “Keep a running count of counters that a shortcut can satisfy: each SCORECARD section now has a \"What `met=True` does not show\" paragraph, but nothing trends it. I could tally, per round, the shortcut controls that met the frozen counter, the mutants that survived, and whether the falsify wave ran, so João can see whether counter design is actually getting harder to fool or just better disclosed.”
>
> — `considerthese/2026-10-26.md:33`

## Evidence boundary

The two reviewed files do not provide enough evidence to label all eight proposals “still unimplemented” at the round-62 tip. Establishing that status would require inspecting implementation/history beyond the requested proposal-file audit; no such status is asserted here. No tools were installed or updated.
