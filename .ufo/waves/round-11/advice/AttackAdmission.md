# AttackAdmission — round-11 critic: round requirements vs planned wave and prior mistakes

Seat: `AttackAdmission` (critic, parent-dispatched → **author-side advisor, not a non-author verifier**).
Read-only except this file. No network, endpoint, host-config or credential access. No builds/tests.
Review time: `date -u` → `2026-10-20T02:14:54Z` (local America/Sao_Paulo is still 2026-10-19 evening;
steered round label 2026-10-19). Installs/updates: **none**.

Axes named: admission legality (claim rules), independence of review, score derivability (padding),
attribution of inherited state, taxonomy/routing honesty.

## Verdict summary

| # | Finding | Severity | Status |
|---|---|---|---|
| A1 | Lowest-axis rule: C1 targets freshness (8) while depth/calibration/adjacency sit at 7; planned calibration claim dropped | **blocking unless ruled** | open |
| A2 | Round-11 cannot self-admit: no non-author spot-check exists for round 11; round-10's cannot be reused | blocking for "admitted" wording | structural |
| A3 | C1 repeats round-10 defect D-6 / critic C1 (definitional before, marker-presence counter) and inflates units 9→27 | score padding | fixable |
| A4 | Freshness/coverage scalar moves not derivable from these counts; coverage already 9 (highest) | score padding | fixable |
| A5 | Planner taxonomy: ruled by orchestrator (L0), mapping must be reported; no routing downgrade under overlay | resolved, report duty | fixable |
| A6 | Inherited `.ufo/round-10/{plan.json,SEAT-PROTOCOL.md}`: lane-authored 2026-10-18, never executed; round-10 commit cited an untracked file | attribution risk | fixable |
| A7 | Round-10 routed defects D-4, D-7, D-8 have no owning seat in this wave; D-8 is an unlearned lane-vs-outside disagreement | report/lesson duty | open |
| A8 | Single build wave runs attackers concurrently with builders; no post-landing falsification wave | process gap | fixable |
| A9 | 18 planned entries → 9; CORPUS "opens with" trio vs KQ7 append-at-end | scope disclosure | fixable |
| A10 | Date: host UTC 2026-10-20 vs steered 2026-10-19 | provenance honesty | fixable |

No pass is asserted by this seat. Nothing here was measured after landing; all findings are against the plan and the pre-landing tree.

## A1 — Lowest-scoring non-retired axis (strongest counterexample)

- Rule: `templates/round-prompt.md:15-17` "At least one claim works the **lowest-scoring non-retired axis** — unless the stagnation nudge waives it"; same in `AXES.md:33-34`, `MISSION.md:43`.
- Current scores (`SCORECARD.md:211-213`, round-10 erratum): freshness 8, coverage 9, operability/depth/calibration/adjacency "unchanged (8, 7, 7, 7)". `SCORECARD.md:59` §Retired: "None."
- Lane itself treats all six as owned: `SCORECARD.md:132` "Round 10: not saturated (depth/calibration/adjacency self-assessed 7)".
- Nudge not available: `AXES.md:68-70` requires every owned axis ≥ saturation line (8) **and** no capability in window; depth/calibration/adjacency = 7 and `sources-registry` entered in round 10 (`SCORECARD.md:126`).
- Spec justifies C1 as "lowest LIVE tie" (spec.json context). "LIVE" is lane vocabulary (`SCORECARD.md:6`), not in the template or AXES. Under the template's wording the lowest axes are depth/calibration/adjacency (7), not freshness (8).
- Internal inconsistency: the wave uses LIVE to pick freshness but spends its second claim on **coverage**, a non-LIVE axis already at 9 (the highest).
- Dropped plan: `SCORECARD.md:203` Planned round 11 item (3) "calibration — non-author admit/reject spot-check plus the SKILL.md stale-anchor sweep (scout: 13 of 14 anchor-bearing lines)". No wave item covers it.
- Impacted axes: admission (every claim may verify and the round still fails the lowest-axis condition).
- Smallest safe correction: either (a) add a third claim on depth, calibration or adjacency with its own counting command (the planned SKILL.md 13-of-14 anchor sweep is a candidate, but it is freshness-shaped; a calibration claim must measure calibration, e.g. SHONEN/SCORECARD-vs-repo mismatches), or (b) append an L0 question asking whether "lowest non-retired" means "lowest LIVE", record the dropped item (3) as a deferral with its reason, and do not write "admitted" before that ruling. Do not silently drop item (3).

## A2 — Independent non-author review

- `LEARNING.md:42-46`: "Each round a non-author — a fresh reviewer or the operator — spot-checks … at least one admit and one reject … A subagent the lane dispatched is still the lane."
- `../.ufo/l0-questions.md:52` L0 answer (orchestrator, 2026-10-19, "operator may override"): "the hyaku closure session (fresh non-author, @m_opus) re-runs claim measurements and spot-checks ≥1 admit and ≥1 reject after each landed round."
- All 32 seats (incl. this one, ReviewContract, AttackFreshness, AttackCoverage) are dispatched by the lane: spec context already says so ("Parent-dispatched seats are author advisors").
- `corpus/lessons/round-10-verifier-spotcheck.md` is round-10's outside check (commit `03b5f0e`, author `protocol-shokunin`). It grades round-10 decisions only; it must not be cited as discernment evidence for round 11, and its "discernment improved" trend (line 17) is round-10 credit.
- Smallest safe correction: round-11 lesson `## Gate` spot-check field = "pending hyaku closure (non-author)"; SHONEN marks `[~]` only; SCORECARD rows "self-assessed, pending non-author verification" (same wording as `SCORECARD.md:192`). Give the closure verifier a pasteable check that **does not depend on author-written `measure.py`** (see A3), because round-10's critic found the author counter measured marker presence only (`../.ufo/waves/kaika-w3/kama-critic.md:7`).

## A3 — C1 measurement repeats round-10's flagged pattern; unit inflation

- Round-10 non-author defect D-6 (`../.ufo/waves/kaika-w3/kama-review.md:175`): "C1 before-state is definitional." Critic: the counter "passes for a pointer explicitly left unresolved" (`kama-critic.md:7`).
- Round-11 C1 is the same shape: before = 27 by construction (`legacy-baseline.json`: 9 files × `source/verified-at/recheck` all missing; re-measured now: all nine `0 0 0` for `grep -cE '^<field>:'`). After = 0 is met by any three column-zero lines, including `source: none — historical record`, which Legacy prompts explicitly allow.
- Counterexample: nine files each appending `source: none — historical record` / `verified-at: not re-verified` / `recheck: unavailable` move the counter 27 → 0 with zero claims re-verified and zero new sources.
- Units: 27 is fields; the work unit is 9 files (one appended block each). Reporting "27 → 0" triples the visible delta.
- Smallest safe correction: report `files_with_trio 0 → 9`, plus a split analogous to round-10's `resolved/terminal/unresolved` fix — count `source:` values citing retained evidence vs `none — historical record`, and `recheck:` values naming a command/path vs `unavailable`. Independent re-check one-liners for the closure verifier, per baseline file `f` with baseline bytes `n`: `head -c n f | sha256sum` equals baseline sha256; `grep -cE '^(source|verified-at|recheck):' f` = 3.

## A4 — Score padding

- Freshness definition `AXES.md:14`: "skill claims re-verified against live surfaces; stale items flagged or fixed." C1 forbids re-verification (spec; Legacy prompts "must not claim live revalidation"). At most this is "flagged"; it is not re-verification.
- Round-10 critic `kama-critic.md:22`: scalar increases were "self-assessed; … not a re-derivable point-to-count mapping". A freshness 8 → 9 from metadata presence repeats that.
- Coverage is 9 (`SCORECARD.md:212`). One crosswalk entry (knowledge 12 → 13) would be the second count-based coverage bump; `CORPUS.md` rule 4: "Expansion is knowledge, not rows" and must sit on "uncovered coverage-map ground" — overlap with `runtime-health-surface-matrix.md` / `served-model-identity.md` is AttackCoverage's lane; if partially covered, call it an extension (as round 10's erratum did, `SCORECARD.md:216`).
- SOURCES status flips S011/S012/S016 queued → mined (mined 17 → 20; census before: `mined 17`, `.ufo/waves/round-11/sources-census-before.json`) are bookkeeping, not a capability or a second coverage count.
- Redundant source opening: the same five URLs are opened by 5 scouts + Crosswalk + SourceCurator (7 seats). Corroboration is fine; counting them as independent re-opens or as round output is padding (`scripts/hyaku/lane-addendum.md` §2 "never padding").
- Smallest safe correction: per claim state verdict + counting command + whether the scalar moves; recommend **no freshness scalar move** for presence-only metadata unless an explicit point mapping is written and re-derivable; coverage verdict only on uncovered-ground rationale.

## A5 — Planner taxonomy

- Canonical template still asks for a planner seat: `templates/round-prompt.md:86` "1× planner, 1× connector". `MISSION.md:63` routes planner to "heavy-reasoning route"; `:65` revenger to "economy route".
- Wave: `Planner` registered with role `revenger` (`dispatch.json` members; `spawn-result.json` lists roles "executor, scout, connector, revenger, …" — no planner).
- Lane raised it: fleet commit `07c2296` (author kama-shokunin) "round-11: kama planner taxonomy question"; answered 58 s later by `3eb7c58` (author `ci`): "planner is a frozen-topology seat the swarm validator rejects by design; the L1 holds the canonical §3 planner seat" (`../.ufo/l0-questions.md:52`), bound at `scripts/hyaku/lane-addendum.md:33-36` "Record that mapping in the report; never bypass validation to add a planner."
- Counterexample tested against my own hypothesis (routing downgrade): the addendum overlay binds "planner/revenger/mutation-tester → m_luna" (`lane-addendum.md:40`), so under this session's overlay the revenger seat gets the same alias a planner would. No downgrade under the overlay; the MISSION table is "advisory" (`MISSION.md:59`). I did not open the overlay YAML itself (limit).
- Residual duties: the report must (1) state L1 holds the §3 planner seat, (2) record Planner→revenger item mapping, (3) cite the ruling as orchestrator-issued "operator may override", not an operator ruling, (4) not count the Planner seat as a planner role toward template line 86.

## A6 — Inherited leftover attribution

- Untracked: `.ufo/round-10/plan.json` (sha256 `3fa5df3ce23ef6c336a01e4b3f7d1ed0dda7e76cb0939fb12787d725d809197c`), `.ufo/round-10/SEAT-PROTOCOL.md` (sha256 `e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a`); both mtime `2026-10-18 15:43:45 -0300`.
- Lane-authored evidence: same pair pattern as rounds 6–9, committed by `kama-shokunin` (e.g. `.ufo/round-6/plan.json` in `f396b98`, 2026-10-18 15:35 -0300); SEAT-PROTOCOL line 1 "L1-issued".
- Content is a **never-executed** plan: `"dispatch_utc": null`, `"seats_total": 64`, model `opencode-go/deepseek-v4.1-flash-free`. Round 10 actually ran 12 seats on the kaika campaign (`LOG.md:519`). SEAT-PROTOCOL did not govern round-10 execution.
- Dangling citation: round-10 commit `1e41928` cites `.ufo/round-10/plan.json` (`SCORECARD.md:192`, `corpus/lessons/round-10.md:123`) while the file was untracked (`git ls-files .ufo/round-10` tracks only audit/fragments/gates). Committing it in round 11 repairs a round-10 evidence gap.
- Policy allows it: `lane-addendum.md` §5 "Uncommitted lane-authored leftovers → resolve per PROTOCOL (commit under this round's entry or revert) and name them in the report." `inherited-state.json` disposition matches.
- Smallest safe correction: commit bytes unchanged (verify the two sha256 above at commit), commit/LOG text says "round-10 L1 pre-dispatch plan authored 2026-10-18, never dispatched; superseded by the steered 12-seat round 10; repairs round-10 citation `SCORECARD.md:192`". Claim no round-11 axis credit for it.

## A7 — Round-10 routed defects with no owner this round

- Outside review lists "Non-blocking for round 11: D-4 (re-anchor host rows), D-5 to D-9" (`kama-review.md:198`). Addendum §5 requires each routed defect → criterion, fix, or stated reason.
- D-8 (`kama-review.md:177`): S009 quote uses ASCII `'`, live page U+2019. The lane's own L2 reviewer said the opposite (`corpus/lessons/round-10.md:135` "the page uses ASCII `'` (fragment correct)"). That is a lane-vs-outside **disagreement** left unlearned (`LEARNING.md:35` discernment "harmed" signal: "a disagreement is left unlearned"). Still present: `round-10.md:69` contains 0 U+2019. No wave seat owns `round-10.md` errata or S009.
- D-4 (20 host-state ledger rows): cannot be re-run this round (contract forbids host-config reads) — report must say so, not drop it.
- D-7 (mis-cited README §Known gaps): no owner.
- Smallest safe correction: parent (owner of the round-11 lesson) records D-4/D-7/D-8 dispositions; D-8 gets an appended erratum or an explicit lesson row with a captured-by criterion. Verify the U+2019 claim by re-opening S009 before writing (I did not re-open it).

## A8 — No falsification wave after landing

- `lane-addendum.md` §2: "wave 2 falsifies (re-run counting commands, re-open sources, attack each claim)". Budget allows it (≤100 members/round; 32 used).
- This wave's critics/mutation seats run concurrently with the executors writing the artifacts, so they attack a plan, not landed bytes.
- Smallest safe correction: a post-landing wave (still author-side) re-runs the counters/negative controls and attacks the actual nine supplements and crosswalk; label it author falsification, not outside verification.

## A9 — Scope and conformance disclosures

- Planned "18 pre-round-10 entries" (`SCORECARD.md:203`) = 9 knowledge + 9 lessons (all 0/0/0 trio by grep). Wave covers 9 knowledge only. Defensible (`CORPUS.md:18` requires the trio for `knowledge/` entries; lessons carry `## Gate`), but the narrowing must be stated, not silent.
- `CORPUS.md:163-164`: "A new knowledge entry opens with its provenance trio … come first." Appended legacy trios do not open the file; KQ7 (`corpus/QUALITY.md:29`) requires appends at end. Report as a recorded legacy exception; the crosswalk (new) must open with the trio.

## A10 — Dates

- Registry `createdAt` `2026-10-20T02:13:06Z`; my `date -u` `2026-10-20T02:14:54Z`. Legacy prompts fix the heading date 2026-10-19 (steered label). Any `verified-at:` and any round-11 source access date must state the actual UTC review date (or date + timezone), keep original observation dates separate, and leave historical SOURCES `opened` cells unchanged (parent instruction).

## Limits

- Did not read sibling advice files except a grep hit in `ReportScribe.md`; did not read the hyaku overlay YAML or `ufo-swarm-wave.mjs`; did not open any URL; did not run measure.py or any mutation. Findings about landed C1/C2 bytes are not possible yet.

## Addendum — after parent axis correction (appended; findings above unchanged)

Checked: `../shokunin.conf:52` → `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`; `.ufo/waves/round-11/claims.json` C1 axis `calibration`, "Keep historical self-assessment 7 unchanged".

- A1: resolved by the correction — calibration 7 is lowest (tied with depth/adjacency 7, so the rule is met). The original "lowest LIVE tie" rested on the historical `MISSION.md:29` example; that is a wave-spec mistake now preserved in immutable spec/dispatch.
- New prior-round mistake to mine: round 10 made the same error in the opposite direction — `SCORECARD.md:192` "the round prompt's 'operability + calibration' is overridden by the mission file (the G5 recurrence)". The prompt matched `shokunin.conf`; the override cited a historical example. Round-10 freshness was then worked as "lowest LIVE". Record it as a round-10 mistake (append-only); do not rewrite round-10 lines. The SCORECARD header "assigned LIVE axes remain operability and freshness" (`SCORECARD.md:6-7`) also needs appended supersession.
- A3 still applies under calibration: a presence counter reaches 0 with nine all-`none`/`unavailable` supplements. For a calibration claim, report the graded split (evidence-cited vs `none — historical record`; command recheck vs `unavailable`) so the move shows graded confidence, not field fill.
- A4: resolved for scalars (both claims keep scores unchanged per claims.json). Verdict wording should still not call presence-only metadata "freshness improved".
- A2, A5–A10: unchanged.
