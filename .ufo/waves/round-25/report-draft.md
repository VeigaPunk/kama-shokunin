# kama — round 25 report (attempt 2)

Lane: kama (local model serving and endpoint health). Round 25, attempt 2,
dispatched 2026-10-22T09:19:49Z. Attempt 1 was stood down by the orchestrator
for capacity (job limit), not for a fault; no attempt-1 identity was resumed.
Lane HEAD at report time: `LANE_TIP` (pushed).

## Work performed

Declared claims (`.ufo/waves/round-25/preregistration.json`, amendments 1-4,
errata `errata-attempt-2.json`):

- **C1 — calibration (repair-first), registered isolation mutant anchors.**
  Repairs the round-24 spot-check's routed defect 2 (stale M-series
  instrument). Target `stale 0`.
- **C2 — coverage, learning claim on frontier K05 (declared versus served
  context capacity).** Target `registered 14 observed 14 bound True`.
  Sourced on S106-S113, opened this round.

Work items:

- Re-verified the inherited state: commit efe58e96 (preregistration,
  amendment 1, pilot, census before exit 0 with 105 rows); C1 before
  `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`.
  Committed the attempt-1 build wave as a record only, with a disposition
  note (5388b7cf; corrections in `errata-attempt-2.json`).
- Amendment 2 (5388b7cf): fresh-author rules, not-blind disclosure, new cells
  X1-X3 and L1-L3, strict counter `count-c2.py`.
- C1 repair (1fc41e34): `tests/report-audit/isolation-mutants.py` M11
  re-anchored, M17 kept on its round-23 line, new M33 for the second call
  site. Full run at 1fc41e34 (`.ufo/waves/round-25/final/c1/`): exit 0,
  pristine passed, 28 mutants, 26 killed, survivors M17 and M20.
- C2 tool and receipt: `tools/kama-context-capacity.py` (5ea4fc44, request
  timing at 46fb04bd), counter tightened by amendments 3 (c808ba07) and 4
  (46fb04bd) after two attack seats found false counts; final receipt re-run
  after amendment 4 (5c95c8f1).
- Knowledge and skill (fa3b62ae): `corpus/knowledge/context-capacity.md`,
  SKILL.md round-25 decision rows, S106-S113 and the S060 used-by change,
  KQ36, lesson `corpus/lessons/round-25.md`, SCORECARD and LOG entries.
- Routed repairs (fa3b62ae): PM08 wording in SKILL.md; registry counts
  27 → 28; `SKILL.md:188-190` premise; round-24 locator erratum in the
  lesson.
- Planner seat: the L1 author held the canonical planner seat; the planning
  data walk rode the pilot (`pilot.md`, attempt 1) and an L1 verbosity walk
  (amendment 2 honesty note 3). No planner seat was put in a wave.

## Landed changes

Lane commits of round 25, in order (all pushed through `jj-lane.sh`):

| commit | subject | LOG entry |
|---|---|---|
| efe58e96e6cfbef88a0fba9d64505e18b7ad7356 | round-25: preregistration, amendment 1, L1 pilot and census before (attempt 1) | LOG §Round 25 first bullet |
| 5388b7cf1d5bad9c228da6f95c40f323414be2f1 | attempt-2 amendment 2, strict C2 counter, attempt-1 build wave record | LOG §Round 25 |
| 1fc41e346853afd98cbd7010af5db4e54dc877f7 | C1 re-anchor M11 and M17; M33 | LOG §Round 25 C1 bullet |
| 5ea4fc44e1d0b5236e14e8b4881f446626a56682 | C2 tool and first 14-cell receipt | LOG §Round 25 C2 bullet |
| c808ba07f09c4be55413d3d6516c542ab69b64f8 | amendment 3, stricter counter | LOG §Round 25 C2 bullet |
| 46fb04bd54978a2a3c47b3da098a2526804014e0 | amendment 4, critic counter, request timing | LOG §Round 25 C2 bullet |
| 5c95c8f111a981e316cd4933e38fc363e51f8604 | final receipt re-run after amendment 4 | LOG §Round 25 C2 bullet |
| fa3b62ae6475d111eb466d79af616aeebb08bbb9 | entry, sources, SKILL rows, KQ36, lesson, SCORECARD, LOG, errata, C1 evidence, wave-1 record | LOG §Round 25 |
| WAVE2_COMMITS | falsify-wave record and integration | LOG §Round 25 |

## Before → after measurements

- **C1:** registered command (preregistration.json C1.command, enumerates
  the whole MUTANTS list): `registered 27 stale 2 ['M11-listing-surrogates',
  'M17-ref-shadow']` at efe58e96 → `registered 28 stale 0 []` at 1fc41e34
  (and at LANE_TIP).
- **C2:** `python3 .ufo/waves/round-25/count-c2.py` (amendment-4 bytes):
  no receipt (counter exit 2, no count printed) → `registered 14 observed
  14 bound True missing []`, receipt 5c95c8f1.

## Sources & frontier

- Census command: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`.
  Start: exit 0, 105 rows (`.ufo/waves/round-25/before/census-validate.out`).
  End: exit 0 (END_CENSUS).
- Rows 105 → 113; added by tier: A +8 (S106-S113), B 0, C 0; mined 86 → 94.
- Touched: S060 used-by gains `corpus/knowledge/context-capacity.md`.
- Frontier advanced: K05 on the lane fixture only (corpus/README.md
  §Frontier advanced — round 25).
- Mined mistake: stale registered instrument (lesson §Mistakes row 1),
  captured-by none, fix KQ36 shown able to fail.

## Trend verdicts

- expansion: TBD
- quality: TBD
- discernment: TBD

## SHONEN

- [~] SKILL.md contains real decision tables… → `SKILL.md` §Round-25 decision rows; no non-author verifier named.
- [~] At least one end-to-end domain task… → `.ufo/waves/round-25/final/context-capacity-receipt.json`.
- [~] Instructions executable by an agent without oral context → `SCORECARD.md` §Round 25 capability row command.
- [~] No cross-domain bleed → `corpus/knowledge/context-capacity.md` §Related lane evidence (kengaku cited, not absorbed).

Stale-lane: respawn-per-round driver; no other mission of this lane is open.
