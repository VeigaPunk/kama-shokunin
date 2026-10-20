# Round 13 — AttackQuality (critic): trend attribution

Seat: KamaR13.AttackQuality, critic and author-side advisor. Scope: the
expansion, quality and discernment attributions for C1 (KQ16 criterion
precision). I used static reads and read-only `git status`/`git diff` only. I
built nothing, tested nothing, and did not run `fidelity.py`, `reproduce.py`,
selftest, census or any gate. Tools installed or updated: none.

Axes: calibration (C1 owner axis; not attacked here), plus the three LEARNING
trends: expansion, quality and discernment. No-harm check: operability,
freshness, depth, coverage and adjacency.

## Verdict proposal

| Trend | Proposed | Current draft wording | Status |
|---|---|---|---|
| expansion | **unchanged** | lesson `round-13.md:55`, README `:158-159`, LOG `:720` | Holds; no defect |
| quality | **unchanged** | lesson `:56-61` (unchanged; round-12 D4 credit not reclaimed) | Holds; tighten LOG `:720` qualifier |
| discernment | **unchanged, pending outside round-13 sample** | lesson `:62-64` "improves in the bounded learning sense that an outside disagreement becomes a grounded criterion"; LOG `:713` "KQ16 learns that disagreement" | **Counterexample below; fixable** |

## CE1 — discernment "improved" rests on a disagreement that was not recorded (fixable)

The rule: `LEARNING.md:35` says discernment is improved when "the spot-check
agrees with the gate on admits *and* rejects, or a disagreement becomes a
lesson that adds a grounded `QUALITY.md` criterion."

The round-13 draft uses the second branch. Local evidence does not show a
disagreement:

- The closure's sample table, `round-12-verifier-spotcheck.md:101-104`, records
  **agree** on all four sampled gate decisions: one admit and three rejects.
- The closure files D1 at `:147` as "status-neutral criterion precision debt:
  fail-closed behavior, required protocol exit classes and measured C1 delta
  remain verified". That is a defect found from outside in criterion prose. It
  is not a disagreement with a gate decision.
- KQ15 was never a round-12 gate candidate. The Gate rows at
  `round-12.md:27-31` are snapshot/checker, old snapshot, archive authority,
  remote locality and source-row-as-knowledge. KQ15 appears only as grounding
  for the admit at `:27`, and the closure agreed with that admit.
- KQ16 flips no admit or reject. The round-12 fidelity admit stands under KQ15
  and under KQ16. The only change is that criterion text now matches the code
  (`fidelity.py:319` shows exits 1/2/2).
- **Double credit.** The closure already raised round-12 discernment to
  improved and wrote "KQ15 learns the prior outside D1 defect, subject to the
  wording correction below" (`:123`). KQ16 meets that existing condition. It is
  not new learning to count a second time.
- **Inconsistency with kama's own precedent.** The round-12 author report
  (`.ufo/reports/round-12/kama.md:108`) handled the same pattern, outside
  finding learned into KQ15, as "discernment — unchanged … await independent
  admit/reject sampling". Lanes that used the disagreement branch cited a
  recorded disagreement, e.g. `.ufo/reports/round-12/tameshi.md:89` ("previous
  independent box-3 disagreement became grounded criterion 13"). Kama has no
  such record.
- **Triple-credit risk.** One two-proposition textual erratum would back the
  C1 calibration claim, a discernment improvement, and (if the qualifier is
  read loosely) a quality improvement.

**Impacted axes:** discernment (overclaim) and calibration (self-grading
honesty).

**Smallest safe correction:** say discernment is **unchanged, pending outside
round-13 sampling**. Describe KQ16 as discharging round-12 closure D1, the
condition attached to round-12's credit, not as new discernment credit. For
L1's prose, which is the only planned writer:

- lesson `round-13.md:62-64`: replace "improves … disagreement" with
  "unchanged: outside D1 was criterion-precision debt, not a gate
  disagreement; KQ16 discharges it".
- LOG `:713`: "disagreement" → "outside precision finding".

Tradeoff: if L1 keeps "improved", it must quote an actual recorded
disagreement. The cited closure contains none, so the canonical judge should
reject that unless one is supplied.

## CE2 — a quality claim cannot rest on criterion bookkeeping (lesson holds; one qualifier to tighten)

- The quality observable in `LEARNING.md:34` is *entries* that are
  re-verified, deepened or superseded. Criteria belong to the discernment
  observable (`:35`). KQ16, the literal probe `measure.py` and S033 are a
  criterion, a probe and a registry row. None of them is a knowledge entry. So
  "quality improved: KQ16 more precise" is a category error.
- Round 13 edits no `corpus/knowledge/` entry. `git status --porcelain` at
  review time showed modified `LOG.md`, `SCORECARD.md`, `corpus/README.md` and
  `corpus/SOURCES.md`, and untracked `corpus/lessons/round-13.md` and
  `.ufo/waves/round-13/`. KQ16 was not yet appended.
- The D4 crosswalk interpretation (`served-identity-crosswalk.md:87-134`) is
  round-12 work. The non-author closure already credited it (`:122`). If round
  13 cites D4 as a round-13 improvement, that is double counting. The lesson
  correctly says "That credit belongs to round 12 and is not reclaimed here"
  (`round-13.md:61`). README `:156-158` restates the basis correctly.
- Harm probe: a grep for `distinct (nonzero|non-zero)` and `git show` over
  `corpus/`, `SKILL.md`, `LOG.md`, `SCORECARD.md` and the round-12 fleet report
  found the bad exit wording only at `QUALITY.md:49`. No knowledge entry
  carries it. The `git show` mentions at `SKILL.md:396` and
  `round-12.md:14-15` describe capture correctly. So no false entry is left
  unmarked, and quality is not harmed.
- Residual: LOG `:720` says "No new serving-knowledge quality … delta". The
  qualifier "serving-knowledge" leaves room to claim "criterion quality
  improved" in the fleet report. **Correction:** the report should state
  `quality — unchanged`, and cite D4 only as the round-12 basis restated per
  closure item 3 (`:149`).

## CE3 — expansion (no defect)

- S033 is mined docs/A Git documentation (`SOURCES.md:45`). It is the same
  kind of source as S032 (git-scm.com, docs/A, opened round 12), so it is not a
  new source kind.
- S033's used-by is `corpus/lessons/round-13.md`. No knowledge entry `source:`
  cites it.
- No coverage-map or frontier row advances: README `:158-161` says "adds no
  knowledge entry, covered serving surface, capability or runtime sample".
- `KQ12` already rejects "row or field growth is called new knowledge".
- `measure.py` is a textual probe. It must not enter `SCORECARD.md`
  §Capabilities, and `SCORECARD.md:128` admits rows only for demonstrated
  domain capability.

Expansion is **unchanged**. Count rows 32 → 33 as census growth only.

## CE4 — "outside D1" is ambiguous across two closures (fixable, sent to Criterion)

KQ15's motivating cell cites `lessons/round-11-verifier-spotcheck.md` D1, the
truncated snapshot (`QUALITY.md:49`). KQ16 learns `round-12-verifier-spotcheck.md`
D1, the KQ15 wording (`:147`). A KQ16 motivating cell that says only "outside
D1" or "round12 outside D1" invites conflation. A conflated cite would make
KQ16 look like a restatement of KQ15's lesson, which is the "criterion with no
lesson" harm in `LEARNING.md:35`.

**Correction:** in the KQ16 motivating cell, cite
`lessons/round-13.md` Mistakes plus `lessons/round-12-verifier-spotcheck.md`
§Routed defects item 1 explicitly. The lesson Mistakes rows already exist
(`round-13.md:50-51`).

Minor: the Mistakes class `number-drift` (`round-13.md:50`) for
"distinct nonzero exits" fits the vocabulary (`CORPUS.md:174-175`), but the
error is an exit-class mapping, not a changed count. `reference-drift`
or `stale-premise` would also fit. This is not blocking.

## No-harm

The diffs are 76 insertions and 0 deletions (`git diff --stat`, review time).
They touch no tool, probe, endpoint, config or knowledge entry. Operability,
freshness, depth, coverage and adjacency are unchanged. KQ16 has not landed
yet; re-check its motivating cell against CE4 once it lands.

## Limits

- All findings come from static reads at review time. The tree was changing
  mid-flight, with KQ16 and `measure.py` absent.
- [INFERENCE] The closure's "status-neutral precision debt" label is read as
  "not a gate disagreement". A non-author reviewer could rule otherwise.
- I did not reopen the Ollama or Git pages. D4's upstream support rests on
  closure-reported quotes (`round-12-verifier-spotcheck.md:108`).
- This seat is an author-side advisor, not outside closure.
