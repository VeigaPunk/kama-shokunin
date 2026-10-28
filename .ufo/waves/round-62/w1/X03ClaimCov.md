# X03ClaimCov — round 62 cross-pattern scan

## Evidence and axis mapping

- **C1 → operability / request plane.** The frozen claim says the completion lifecycle yields a held live `POST /v1/completions` answer bound to alias, build fingerprint and fresh nonce; it independently measures a request-plane behavior, not calibration. `tools/round62-c1-counter.py` docstring predicate matches the C1 frozen predicate after whitespace folding (551 characters each). Evidence: `controls/freeze.txt` lines 11–27; counter docstring lines 6–14.
- **C2 → calibration / capability self-assessment.** It measures whether 12 pre-round-62 capability assertions are uniquely present, row-bound to allowed executable checks, actually re-executed and sensitive to decisive-output mutation, plus control rejection. It is calibration, not request-plane operability. Evidence: `controls/freeze.txt` lines 29–54; `tools/round62-c2-counter.py` docstring lines 6–18.
- **Frontier → SOURCES / lessons.** The frontier item belongs to sourcing/learning evidence (`corpus/SOURCES.md` and `corpus/QUALITY.md`/lessons), rather than either frozen C1 or C2 claim. This does not establish a third claim's exact frozen wording or status; the consulted round freeze contains only C1 and C2. `PROVINCE.md` describes endpoint-health scope and lane instruments; it does not collapse sources/lessons into either measurement.

**Axis collision check:** no two of the three named work items claim the same axis: C1 is operability, C2 calibration, frontier is the SOURCES/lessons surface (not a claim assigned either of those two axes in the supplied freeze). No scalar reconciliation is warranted.

## Predicate/docstring check

- C1: exact sentence agreement after normalizing whitespace: **MATCH**.
- C2: **DRIFT**. The counter docstring inserts the word **“below”** after “listed in MANIFEST”; freeze says “listed in MANIFEST (including …)”. Whitespace-folded predicate lengths are 864 (counter) versus 858 (freeze). This contradicts the counter's label “identical” and freeze's statement that the predicate is identical to the docstring. No other predicate difference was found by token comparison.

## One bounded proposed move

Align the C2 counter docstring phrase with the frozen sentence by removing “below” (or, if intentional, amend the frozen sentence through the canonical owner before treating them as identical). This is a tiny calibration-integrity correction: it makes the published instrument declaration match its immutable criterion, without changing what the counter computes or touching the C1 request-plane claim. Preserve the frozen freeze artifact; practical choice is counter docstring correction only.

## Affected axes, risks, verification

- **Improves:** calibration, by removing ambiguity in the declared criterion-to-instrument correspondence.
- **No harm identified:** operability remains governed by the independently frozen C1 request-plane predicate; SOURCES/lessons frontier remains untouched.
- **Risk:** the wording difference may have been intentional clarification, but “below” is not part of the frozen sentence and the docstring explicitly claims identity; any semantic intent should be resolved by the canonical planner, not silently normalized here.
- **Verification:** exact predicate comparison after whitespace folding should report C1 MATCH and C2 MATCH; independently inspect the fixed token sequence against `freeze.txt`. No tests or counters were run for this scoped scan.

Report generated with read-only inspection; no tool installs/updates.