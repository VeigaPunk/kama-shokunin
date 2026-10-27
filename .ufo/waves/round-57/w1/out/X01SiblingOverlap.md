# X01SiblingOverlap — cross-claim and sibling-overlap scan (kama round 57)

Report: `.ufo/waves/round-57/w1/out/X01SiblingOverlap.md`
Evidence (separate file, commands and exact outputs): `.ufo/waves/round-57/w1/out/X01SiblingOverlap/evidence.md`
Receipts: `.ufo/waves/round-57/w1/out/X01SiblingOverlap/{receipts,fixtures}/`
Seat role: connector, read-only on the lane. Scratch only under `/fast/scratch/hyaku/kama-r57/X01SiblingOverlap/`. No installs, no lane edits, no commits.

Pins: freeze base `b89bdab2` (round-56 tip). Lane HEAD moved during the seat `8640e34c` → `16efcf5e` → `77e7f5ee` → `3d2d5d4d`; counters were re-run at `3d2d5d4d`. Dispatch context says the axes are operability + calibration; `shokunin.conf:52` agrees.

## Summary

1. **The claim labels disagree across the round's own artifacts.** The dispatch and `controls/freeze.txt` say C1 = calibration, stale canonical-table count (maxN 46); C2 = operability, canonical-row execution binding. `controls/freeze-amendment.txt` (commit `7c873d7b`, "claim ordering only") and the committed SCORECARD §Round 57 say C1 = operability, round-56 prereg-checker no-op; C2 = calibration, round-42 spot-check count. The amendment's "ordering only" is not accurate: the targets changed, and no round-57 claim measures canonical-row binding at HEAD. Not resolved here.
2. **"maxN=56 instead of 46" is not a defect in the counter.** `maxN` is `max` over `^## Round N` headings (`tools/round42-selfdesc-reconcile.py:167-168`): 56 at base, 57 at HEAD. It feeds the banner and planned legs. Forcing maxN to 46 makes the planned leg fail (`planned: section does not name '### Planned (round 47)'`, exit 1). No formula in the tree yields 46; it is the hard-coded literal in `controls/c1-noop.py` and `noop-c*.out`.
3. **The base mismatch is one stale count.** At `b89bdab2` the only failing leg is the calibration run fact: expects `42`, the glob returns `43` (the round-56 outside closure file itself was added in that commit). The same class recurs (SCORECARD line 2723: "red at the base: the spot-check count 32 → 33"). Repaired at `7b74e2f2`/`8640e34c`; `3d2d5d4d` gives `mismatches=0 maxN=57 met=True`.
4. **Real canonical-row defect: stale-table selection.** Both `round42 canon()` and `capability-repertoire-audit.py` take the highest-numbered "canonical list as of round N" marker present and never compare it with the latest round. Removing the round-49 table (frozen `controls/no-canonical/SCORECARD.md`) silently selects the round-48 table (11 identical names). Round-42 reports only the count leg; capability census reports `met True`. The frozen "no-canonical" control is therefore not red for canonical rows.
5. **Canonical-row binding is absent in both counters.** Round-42 never executes or content-checks capability rows; its only canonical checks are name equality and "tools/registry tokens appear in PROVINCE.md". The eleven round-49 rows contain zero run facts. Round-41's run-fact check accepts any stdout line equal to the expected text, whatever the command does. A fixture whose calibration command is `echo verifier-spotcheck; echo 43` passes with `met=True`, exit 0.
6. **An existing instrument already does part of C2.** `tools/capability-repertoire-audit.py` (round 34 capability census; `--selftest` is already a calibration run fact) checks canonical-row path existence (`unsubstantiated`) and head-vs-canonical name difference (`missing`). Round-42 does not call it. A new canonical-row tool (E02CanonicalBinding's prototype) would be a third instrument on the same surface.
7. **The round-57 operability repair is bypassable by dead code.** The amended C1 check (`tools/round56-prereg-check.py:61-71`) tests whether each roster label appears as a `run(...)` call anywhere in the AST. An appended `def _never_called(): run(<label>)` for every label yields `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0. The round-56 outside defect routed "bind actual executed battery entries; a roster literal/no-op harness must fail". The literal-roster no-op now fails; call-site presence still passes. The lesson's `no-op-counter` row overstates the fix.

## Findings with evidence

### F1 — claim labels (cross-claim conflict)

| Source | C1 | C2 |
|---|---|---|
| `controls/freeze.txt` (`89dc4f52`) | calibration, stale canonical-table count | operability, canonical-row execution binding |
| dispatch `w1-spec.json` / `w1-dispatch.json` | same as freeze.txt | same as freeze.txt |
| `controls/freeze-amendment.txt` (`7c873d7b`) | operability, round-56 prereg-check no-op | calibration, round-42 stale spot-check count |
| SCORECARD §Round 57 (`8640e34c`, `3d2d5d4d`) | operability 8→8, prereg-check no-op | calibration 7→7, spot-check count |
| `corpus/lessons/round-57.md` (`3d2d5d4d`) | no-op-counter class | calibration-staleness class |

`grep -ci canonical` over SCORECARD §Round 57 at `8640e34c`: 0. The round's measured set contains no canonical-row binding claim. Evidence E7.

### F2 — maxN and the 46 target

- Source lines: `round42-selfdesc-reconcile.py:167-168` (derivation), `:190` (banner requires `Latest measured round: <maxn>`), `:195` (planned requires `### Planned (round <maxn+1>)`).
- Base max heading 56; head `3d2d5d4d` max heading 57 (fixture fx8: `maxN=57 met=True`).
- fx7 (headings 47–56 demoted, banner set to 46, count repaired): `r41=0 … planned=1 … maxN=46 met=False`, exit 1, detail `planned: section does not name '### Planned (round 47)'`.
- "46" appears only as: the `c1-noop.py` literal, `noop-c1.out`/`noop-c2.out` literals, the first-working round of `append-only-audit`, and prose. Evidence E2.

### F3 — stale canonical table selection

- Canonical markers at base: rounds 16, 17, 34, 41, 42, 43, 46, 47, 48, 49 (SCORECARD lines 676…2844). Selection = highest present.
- `fixtures/ctl-no-canonical-on-base`: round-49 table absent → round-42 `r41=1 … mismatches=1 maxN=56 met=False` (count leg only); cap `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0.
- `fixtures/ctl-canonical-noop` (frozen partial tree, no `tools/`, no `.ufo/`): `r41=29 receipts=9 mismatches=38` and cap `unsubstantiated 10 met False`. This control is red because files are absent, not because canonical rows are unbound.
- Evidence E3.

### F4 — canonical-row and run-fact binding (fixtures, all on the count-repaired base)

| fixture | edit | round-42 | capability census |
|---|---|---|---|
| fx3 | round-49 pin-watch evidence → `none` | `met=True` exit 0 | `unsubstantiated 1` exit 1 |
| fx2b | evidence → `tools/pin-watch-gone.py` + PROVINCE token + coverage re-anchor | `met=True` exit 0 | `unsubstantiated 1` exit 1 |
| fx5b | head-mirror `## Capabilities` evidence → dangling + PROVINCE token + re-anchor | `met=True` exit 0 | `met=True` exit 0 |
| fx11 | round-49 evidence → `corpus/SOURCES.md` (real, wrong file) | `met=True` exit 0 | `met=True` exit 0 |
| fx4 | round-49 pin-watch row deleted | `caps=1 retired=1 saturation=1` exit 1 | `missing 1` exit 1 |
| fx6 | calibration run command → `echo verifier-spotcheck; echo 43` | `met=True` exit 0 | — |

Reading: round-42 is blind to canonical evidence cells and head-mirror cells; the capability census catches whole-cell dangling paths in the canonical table only. Neither checks that a pointer supports its row, that the head mirror agrees with the canonical table on evidence, or that a run fact executes. Evidence E4.

### F5 — overlap with the existing capability census

`tools/capability-repertoire-audit.py` is already the lane's canonical-row instrument: `listed/observed/missing/unsubstantiated`, `--selftest` `CAP_SELFTEST pass=2 fail=0` (exit 0), and a run fact in the calibration row. Round-42 neither imports nor calls it. Its own gaps: any-token-resolves substantiation (code read, not fixture-tested), no head-mirror check, no content check (fx11), the same highest-marker selection (F3). Proposed domain boundary: canonical-row binding belongs to this tool, extended in place, not to a new file in the same lane. Owner is the same lane (kama), so no cross-lane conflict is found; the overlap is duplicated instruments on one surface.

### F6 — shared dependencies and axis coupling

- **Calibration count leg (round-41 `calibration` run fact).** Every outside closure file changes the count. The closure commit `b89bdab2` made the lane's own base red. Recurring (round 47 line 2723). Outside closures are written by the fleet integrator into the lane's `corpus/lessons/`; the counter binds that into the lane's self-description. This is a boundary between outside admission and lane self-assessment, not a bug in either.
- **PROVINCE.md ↔ coverage row.** Round-42's province leg requires canonical `tools/`/`registry/` tokens to appear in PROVINCE.md; round-41's coverage row pins PROVINCE.md by sha256 and line count. Any canonical-row repair that adds a PROVINCE token moves the coverage axis's evidence (coverage 9, not assigned). Without re-anchoring it fails the r41 leg (fx2: `r41=2`). Planner decision: either canonical repair avoids PROVINCE tokens or it re-anchors the coverage row in the same commit.
- **maxN ↔ banner/planned.** Each new `## Round N` heading requires the head banner and a `### Planned (round N+1)` in the same commit. The 8640e34c integration did this correctly (fx8).
- **Axis authority (not resolved).** `shokunin.conf:52`: operability + calibration. SCORECARD line 6: `MISSION.md:29` still says operability + freshness. The round-56 outside closure routed this to the operator/L0 channel. The dispatch and config agree on operability + calibration; this seat uses that set.

### F7 — prereg checker bypass (C1 amendment)

- `tools/round56-prereg-check.py` at `8640e34c` lines 61–71: `invoked` collects every `run(...)`/`assert_mutant_breaks_detection(...)` Call label via `ast.walk`, regardless of reachability; `executed = expected <= invoked`.
- fx9 (unchanged): `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0.
- fx10 (appended dead function calling every roster label): `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0.
- Consequence: the operability claim measures call-site presence, the same class as the canonical-row defect in F4. The round-57 lesson and SCORECARD describe the change as "binds actual call sites"; that phrase should be read as presence only.

### F8 — shortcut tally and the considerthese proposal

`tools/shortcut-tally.py` exists at base (v2, round 48). Its docstring says it promotes the round-47 draft from `considerthese/2026-10-26.md` proposal 3 to a lane tool. The round-57 lesson's assimilation line says proposal 3 "was opened" and does not cite the tool. Route: the R06 / ProposalAudit seat should decide the disposition against the landed tool; this seat does not re-implement it.

### F9 — sibling overlap in the wave

- Prompt-target scan over the 64 items: only `tools/round42-selfdesc-reconcile.py` (E01CounterRepair, scratch-only) and `corpus/lessons/round-57.md` (S02LessonDraft) are named. Most prompts repeat the same assignment (four PlannerDataWalk, four SiblingOverlap, four CounterRepair, … copies with `Distinct case N` suffixes).
- Integrator commits touched shared files while seats were reading them: `7b74e2f2` (`tools/round56-prereg-check.py`, `SCORECARD.md`, `LOG.md`, lesson), `8640e34c`, `16efcf5e`, `77e7f5ee`, `3d2d5d4d` (SCORECARD, `corpus/SOURCES.md`, lesson). Untracked sibling seat outputs sit in `.ufo/waves/round-57/`.
- E02CanonicalBinding ("prototype an operability-side tool with canonical rows as input") and R57Item04CanonicalBinding overlap F5 and should be coordinated with the capability-repertoire owner in the same lane, not built as a parallel instrument.

## Round-56 outside defects (lesson addressing)

- "Bind actual executed battery entries; a roster literal/no-op harness must fail" — **partly addressed.** Literal-roster no-op now fails (`noop-c1.out` per SCORECARD); dead-code harness passes (F7). Not closed.
- "Resolve MISSION.md vs prompt/config axis conflict" — **open**, routed to operator/L0 (F6).

## Affected axes

- Calibration: the C1 target (stale count) is a real defect and is repaired at HEAD; the canonical-row binding (C2 per freeze) is unmeasured at HEAD; the stale-table selection (F3) is unrepaired in both counters.
- Operability: the amended prereg check (F7) is bypassable; the capability census is an existing instrument whose gaps (F4) are unrepaired.
- Coverage/adjacency: touched only if a canonical repair edits PROVINCE.md (F6).

## Risks

1. Claim-label conflict (F1): a closure that checks the dispatch's C1/C2 wording will find a different measured set. Needs one planner decision and an explicit amendment to the frozen claims, not a silent relabel.
2. Re-building a canonical-row instrument (F5, E02) duplicates `capability-repertoire-audit.py`.
3. Chasing maxN=46 (F2) would break planned and banner legs; it should not be a target.
4. Presence-based gates (F4, F7) will be read as execution-bound unless the lesson says otherwise.

## Verification the main agent should run once (not run by this seat)

- `python3 tools/round42-selfdesc-reconcile.py --repo . --tip HEAD` → expect `mismatches=0 met=True` at `3d2d5d4d` or later.
- `python3 tools/capability-repertoire-audit.py --repo . --tip HEAD` and `--selftest`.
- Fixture re-run: fx3/fx2b/fx5b/fx6/fx10 from `fixtures/` receipts (regenerate from `evidence.md` pins if the planner wants them red).
- Decide F1 with the planner before any C1/C2 closure text is written.

## Limits

- Fixtures test presence and disposition, not correctness of any repaired counter.
- Tips moved during the seat; the 16efcf5e and 77e7f5ee contents were read only through the `3d2d5d4d` diff stat.
- This seat did not verify S515, the round-56 spot-check disposition of S513, or the lesson's census numbers; those belong to other seats.
