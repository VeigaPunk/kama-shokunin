Verdict: defect found. C1 does not fit the calibration axis. The measured value `registered 28 stale 0 []` holds. Wave 1 missed three things. First, this is drift, which AXES files under freshness. Second, the filed text describes the before value wrongly. Third, failing the axis fit makes round 25 miss the lowest-axis rule. It is not a cosmetic label dispute.

# CriticC1AxisFit: wave-2 falsify, C1 axis fit

Seat KamaR25a2.CriticC1AxisFit. Lane tip read: 46be41c, the child of fa3b62ae, which adds only the report draft and the wave spec. The lane was read-only. Git-writing runs happened only in my own clones under `/fast/scratch/hyaku/kama-r25a2w2/CriticC1AxisFit/`. I started no llama-server child, installed no tool and upgraded nothing.

## Axes

- Calibration fit: does C1's count equal a count of SCORECARD/SHONEN self-assessment mismatches against observed repo state?
- Axis taxonomy: which AXES row the observed defect belongs to.
- Round admission: whether the lowest-axis obligation still holds.
- Wording accuracy of the filed text.

## 1. The measured value holds and is not in dispute

I ran the registered C1.command in clone2 at each commit. Every run exited 0. The output is in `out/CriticC1AxisFit/c1-command-history.txt`:

```
e876b95 | registered 31 stale 0 []
ed1cc3a | registered 27 stale 0 []
2e254a1 | registered 27 stale 0 []
92063cf | registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']
147f5bd | registered 27 stale 2 [...same...]
efe58e9 | registered 27 stale 2 [...same...]
1fc41e3 | registered 28 stale 0 []
fa3b62a | registered 28 stale 0 []
46be41c | registered 28 stale 0 []
```

New fact: the anchors went stale at round-24 commit 92063cf ("correct local object scope and measurement provenance"). They were not stale when the round-24 registry text was written at ed1cc3a.

## 2. Against the author: no SCORECARD/SHONEN mismatch existed to count, before or after

The prompt rule (`.ufo/prompts/kama-round-25.md:347-348`) and AXES.md:15 both require the count to be self-assessment versus observed state.

- **SCORECARD at the before revision had zero mismatches on this subject.** SCORECARD:1166 (30/31 killed, survivor M20) is bound to auditor e876b953 at SCORECARD:1155-1156. At e876b95 the command prints `stale 0` (above), so that row was true at its revision. The round-24 final record at SCORECARD:1237-1238 says: "No fresh final-epoch full both-arm grid, legacy population, selftest/parity or default sensitivity confirmation was performed". The lane disclosed that it had not rerun the sensitivity probe. That statement matched the repo.
- **SHONEN.md has four `[~]` boxes (lines 5-11). None mentions mutants or the auditor.** Last touched at round 17 (`git log -- SHONEN.md`). Zero mismatches.
- **A dilemma that wave 1 missed.** Suppose SCORECARD:1166 is read as a live claim (the author's direction). Then the repair does not fix the mismatch. The tip full run gives 28 mutants, 26 killed, survivors M17 and M20 (`final/c1/c1-tip-mutants.json`: `killed 26, mutants 28, pristine passed, surviving list2`). Line 1166 still says 30/31 with only M20 surviving. If line 1166 is historical (the critic's reading), it was never a mismatch. Under neither reading does `stale 2 → stale 0` equal a change in SCORECARD mismatches.

## 3. Against the author's SKILL-row argument: the row was not falsified

The author says the SKILL registry row "promised an evaluated inventory the command could not deliver" (SCORECARD:1272-1276). I checked that row at the before revision.

- 147f5bd SKILL.md:871, now SKILL.md:888, has this verdict map: "0 pristine passed and selected inventory evaluated, survivors reported; 2 fail-fast could-not-evaluate". The exit-2 path is part of the registered contract. The row does not claim the inventory runs green.
- The probe evaluates any selection that does not include a stale id. The instrument checks each anchor only inside the per-mutant loop (147f5bd `isolation-mutants.py:167-175`). I ran it in my own clone at 147f5bdd (`out/CriticC1AxisFit/only-probes-147f5bd.txt`):
  - `--only M12-shallow-check --json`: exit 0, 66 s, pristine passed, mutants 1, killed 1.
  - `--only M11-listing-surrogates --json`: exit 2, 33 s, stderr `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times`. That is the outcome the row registers.
- The row's state column ("27 retained literals, 4 retired IDs without reuse") was true. 27 entries were registered.
- The superseded 31-mutant gate row (SKILL.md:820) is retired explicitly at SKILL.md:1003-1009, so it is not a live mismatch.
- Two texts come closest to a real mismatch, and both are drift:
  - LOG.md:1498 at 147f5bd says "retained27 applicable elements". Blame: ed1cc3a, where the command prints `stale 0`, so it was true when written.
  - 92063cf added SKILL.md:989 "holds 27 retained literals" as "the current count" in the same commit that made 2 of them non-applicable. "Retained" is literally true, but the reading of 27 as applicable went stale in that commit.

## 4. The defect fits freshness by the lane's own taxonomy and precedent

- AXES.md:14 defines freshness as "skill claims re-verified against live surfaces; stale items flagged or fixed". AXES.md:15 defines calibration as "gaps named honestly, confidence graded, overreach caught". A claim that was true when written and went stale after a later code change is drift, not overreach.
- The lane names it as drift itself. `corpus/lessons/round-25.md:48` reads "stale-anchor: a registered counting instrument drifted from the source it measures". KQ36 (`corpus/QUALITY.md:203`) says the instrument "is reported as stale, and the value it supports is unverified at that tip". Unverified is not the same as mismatched.
- Lane precedent: round-10 C1 "re-anchor stale source anchors" was filed and admitted as **freshness** (SCORECARD:196; `corpus/lessons/round-10-verifier-spotcheck.md:17` "freshness improved (50 stale anchors → 0 uncorrected").
- The verifier that routed this defect did not file it under calibration. `corpus/lessons/round-24-verifier-spotcheck.md:80-82` names the stale instrument. Its axis table at line 140 puts it under operability ("unprovable ... registered instrument stale"), and the quality row says harmed ("registered measurement-contract deficits"). Its calibration row (line 139) is about the original clause, not the instrument.

## 5. For the author: precedent that wave 1 missed, and why it no longer decides the case

The lane's outside closures admitted calibration before for making an instrument's self-description true:

- Round 17 C1: SCORECARD:654-662 says "an instrument's self-description made true is a bounded calibration repair". It was admitted in `corpus/lessons/round-17-verifier-spotcheck.md:7,11`.
- Round 15: `round-15-verifier-spotcheck.md:7` says "Repairing a falsified executable assessment promise is a bounded improvement".

Two reasons this precedent does not carry C1:

1. **The rule is new.** `grep -c 'A calibration claim must count mismatches'` gives 0 in `.ufo/prompts/kama-round-{15,17,18,19,22,23,24}.md`. Rounds 15 and 17 were judged before the SCORECARD/SHONEN counting rule existed. Round 25 is the first kama round bound by it.
2. **Overreach versus drift.** In round 17, SKILL.md:533 claimed grading that no detector could fail at the time it was written, which is overreach. Here the self-description was true when written (ed1cc3a, `stale 0`) and drifted at 92063cf.

## 6. A consequence wave 1 missed: the lowest-axis rule

- Scores: calibration 7, depth 7, adjacency 7, operability 8, freshness 8, coverage 9 (SCORECARD §Round 25, "Other scores held"). The saturation line is 8 (SCORECARD:132). Calibration is below it, so the stagnation waiver does not apply (AXES.md stagnation nudge).
- AXES.md:33 and prompt lines 15-17 require at least one claim on the lowest-scoring non-retired axis.
- If C1 lacks calibration fit, C2 (coverage 9) is the only remaining claim. Filing C1 under freshness (8) would not reach the lowest axis either.
- Round 25's SCORECARD section (from line 1252) never states which claim meets the lowest-axis rule. Every earlier kama round did: SCORECARD:1037, 1154, 1197.
- So the axis dispute decides admission. The canonical judge cannot fix it by relabeling. Prompt line 350 says "Never narrow a target after landing", and the author already declines to relabel (SCORECARD:1276).

## 7. Wording defect in the filed critic text

SCORECARD:1270 (and the same wording in `corpus/lessons/round-25.md:94`) says "The before command aborts on reaching M11 ... and emits no completed JSON report". The registered C1 before command is the anchor counter. At efe58e96 it exits 0 and prints `registered 27 stale 2 [...]` (section 1). What aborts is the instrument run `python3 tests/report-audit/isolation-mutants.py --json` (exit 2). `errata-attempt-2.json` already says this correctly: "The instrument stops on reaching M11". The filed sentence confuses the claim's counting command with the supporting instrument.

## Impacted axes

- calibration: claim fit not established. No credit, no harm.
- freshness: the true home of the defect, but it cannot be relabeled after landing.
- Round admission: the lowest-axis obligation is unmet if C1 fails fit.
- quality: one inaccurate sentence in the filed text, which can be fixed.

## Fixable versus judge-rejected

- **Fixable:** the "before command" sentence in SCORECARD:1270 and lesson:94, and the missing lowest-axis statement. The correction must be appended, not overwritten.
- **Tradeoff the judge must reject for credit:** C1 as calibration. The measurement is valid repair evidence. It is not a calibration count, so the round's lowest-axis claim is unproven.

## Exact wording the report should use

Put this in the report's C1 result section, replacing "Axis fit is contested ... closure decides", and append the same text to SCORECARD §Round 25 as a correction:

> C1's measured value holds: the registered anchor counter prints `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` at efe58e96 (exit 0) and `registered 28 stale 0 []` at 1fc41e34 and at the lane tip (exit 0). It counts registered mutant literals against the auditor source, not SCORECARD or SHONEN self-assessments against repo state. On this subject the lane's self-assessment matched the repo before the repair: SCORECARD line 1166 is bound to auditor e876b953, where the counter prints `stale 0`, and the round-24 record says no default sensitivity confirmation was run. The anchors went stale at round-24 commit 92063cf, after the registry text was written at ed1cc3a. That is drift (freshness), not overreach, and the round-24 verifier filed it under operability and quality. Calibration-axis fit is not established and no calibration credit is claimed. Because calibration 7 is the lowest non-retired axis tied with depth and adjacency, and the stagnation waiver does not apply, round 25 has no claim proven on a lowest axis; the author does not relabel C1 after landing. What stopped on reaching M11 at the before revision was the supporting instrument run `isolation-mutants.py --json` (exit 2, no JSON), not the registered counting command.

In the Work-performed list, write "C1 — declared calibration (repair-first; axis fit not established)" instead of "C1 — calibration (repair-first)". The discernment trend must not count C1 as a calibration success.

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/CriticC1AxisFit.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/CriticC1AxisFit/c1-command-history.txt`
- `.ufo/waves/round-25/a2-falsify/out/CriticC1AxisFit/only-probes-147f5bd.txt`
- Scratch, outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/CriticC1AxisFit/{clone,clone2,only-*.json,only-*.err,only-*.exit,only-*.time,c1-command-history.txt}`. The first `--only` attempt failed with exit 127 because `/usr/bin/time` is not installed. I reran without it, and the results above come from the rerun.
