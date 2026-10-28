# KR08CalibrationHonesty — round 63 calibration audit of lane self-description

Seat: KR08CalibrationHonesty (advisory leaf; no verdict on the frozen claims; no commit; no lane edit).
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (`master`). Audited from git blobs at tip. The lane
worktree is dirty (uncommitted `PROVINCE.md`, `corpus/SOURCES.md`, `corpus/knowledge/completion-request-plane.md`,
L1 in flight); those edits are NOT audited, except where noted.
Evidence: `.ufo/waves/round-63/w1/out/KR08CalibrationHonesty/` (reconciler, counter, selftest, ledger and mutant
receipts; `resolve-pointers.py` is the pointer resolver). Scratch removed. No installs. No lane or fleet git mutation;
mutant commits were made only in my scratch clone.

## 1. Reconciler at tip (`python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip master`)

Output (`out/.../reconcile-tip.out`):
`r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=63 met=False`

| # | Detail (verbatim) | Cause (checked at tip) |
|---|---|---|
| 1 | r41 coverage run `… glob … corpus/knowledge/*.md …` no stdout line == '36' | Typed run output is stale. The glob now returns **38** (tip `corpus/knowledge/` has 40 `.md`; the filter excludes `context-capacity-engine-sides.md` and `runtime-health-surface-processes.md`). Two entries added after the round-60 count of 36: `ollama-live-amendment-r61.md` (added `7848fbea`, r61) and `completion-request-plane.md` (added `dc5e1010`, r62). Row not re-derived since r60 (`SCORECARD.md:17`). |
| 2 | banner: head lacks `Latest measured round: 63` | Expected pre-measurement (freeze: L1 re-derives after measurement). Already stale for round 62: `SCORECARD.md:6` says `Latest measured round: 61`, while `### Round-62 measured results` exists at `SCORECARD.md:3294`. |
| 3 | planned: section does not name `### Planned (round 64)` | Expected pre-measurement. `SCORECARD.md:53` says "The live plan is `### Planned (round 61)` below"; that block is at `:3187` and is a round-60 plan. |
| 4 | planned: no `### Planned (round 64)` followed by a numbered item | Same as 3. |
| 5 | retired: does not state `12 capabilities` | `SCORECARD.md:57` says "6 axes and 11 capabilities"; the round-63 canonical list has 12 rows (`SCORECARD.md:3303` onward). Typed count is stale. |
| 6 | saturation: does not state first-working rounds `…, 46, 47, 61` | `SCORECARD.md:137` lists 10…47 only; the 12-row canonical list adds `live-ollama-lifecycle` at 61. |
| 7 | caps: head names 11 vs canonical 12 (missing `live-ollama-lifecycle`) | `SCORECARD.md:117` mirror is the round-49 list, by its own label. Expected to be re-derived by L1 after measurement. |
| 8 | province: `PROVINCE.md` lacks `registry/ollama-live-claims-r61.tsv` | True at tip (`PROVINCE.md:188` is the round-60 note only). The uncommitted worktree `PROVINCE.md:190` already adds a Round-63 note naming that file, so this is resolved in the worktree, not at tip. |

Items 2, 3, 4, 6, 7 are expected to close only through L1 re-derivation after measurement (per freeze). The 8 is
therefore not itself a defect. The defects below are the ones the reconciler cannot see.

## 2. Assigned axes: scores not claimed to move

- Operability 8 (`SCORECARD.md:14`) and calibration 7 (`SCORECARD.md:18`): no section at tip claims a move. The
  claim rows for rounds 58–62 read `operability 8→8` or `calibration 7→7` (C2 rows at `SCORECARD.md:3199, 3218,
  3227, 3238, 3254, 3270`; C1 rows nearby). Round 63 is pre-measurement. **No score-move overclaim found at tip.**
- The only "improved" verdicts in rounds 59–63 come from the non-author closures, not from the lane's own claims:
  `corpus/lessons/round-61-verifier-spotcheck.md:67` rates calibration and operability "improved" on the r61 reading.
  The lane kept 8/7, which is the conservative behaviour; see A4 for the missing record.
- Gate weakness (see §6, M3): the score is a typed constant (`tools/round41-scorecard-reconcile.py:57–58`,
  `EXPECTED = {"operability": 8, …, "calibration": 7, …}`). Moving a score needs only the head cell plus that constant
  in one commit; no claim and no non-author verifier is consulted.

## 3. Run facts behind operability 8 and calibration 7 (re-executed on a `git archive` export of tip)

All reproduce (`out/.../assigned-axis-run-facts.out`):
- `tools/kama-probe.sh` sha256 `4393ab81…964f4`, 1138 lines: matches.
- `bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0` (exit 0): matches.
- `python3 tools/pin-watch.py selftest` → `selftest pass=9 fail=0`: matches.
- `python3 tools/report-landing-audit.py --selftest` → `selftest cases=79 failed=0`: matches.
- `python3 tools/sources-append-only.py --selftest` → `45/45 selftest cases passed`: matches.
- `python3 tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0`: matches.
- `python3 tools/instrument-agreement.py --selftest` → `IA_SELFTEST pass=4 fail=0`: matches.
- Ledgers cited by the calibration row: `registry/verdict-ledger.tsv` 204 data rows (matches);
  `registry/claim-outcome-ledger.tsv` 126 data rows (matches). Recomputed from ledger rows, verdict pairs with a
  non-absent verdict on both sides: 87, equal 69, overclaim 2 (`improved`→`unchanged` 1, `improved`→`unprovable-but-better`
  1), underclaim 16 (`unchanged`→`improved`); matches "69/87 overclaim=2 underclaim=16". Claim ledger: 63 pairs,
  equal 58, overclaim 1 (`met`→`not-met`), underclaim 2 (`not-met`→`unprovable`), other 1 (`mixed`→`unprovable`),
  absent 1; matches "58/61 overclaim=1 underclaim=2 other=1 absent=1".
- `corpus/knowledge/cross-lane-scope.md` pipe-lines 16 (matches). `SKILL.md` sha `ea303f…`, 1641 lines, 44 `## `
  headings (matches). `PROVINCE.md` sha `a60591…`, 188 lines (matches tip; the worktree copy is modified, so this hash
  breaks when the uncommitted PROVINCE edit lands).
- **Broken:** the coverage row's `36` (§1 item 1) is the only run fact of the six axes that fails.
- The calibration row's pointer claim (A1) is not a `run X → Y` fact, so the r41 engine does not execute it.

## 4. Overclaims and stale self-description, by path:line (tip)

Ranked. "A" bears on the calibration axis; "B" is a stale or misstated fact.

**A1 — calibration row names a stale closure pointer and says it is derived at tip. (`SCORECARD.md:18`)**
The row states: "latest outside closure `corpus/lessons/round-57-verifier-spotcheck.md` (rejected-honest-stop),
including round 57"; "derived at the measured tip by `python3 tools/round59-c2-counter.py --repo <repo> --tip <rev>
--fleet-ref HEAD`"; and "evidence re-anchored round 58". At tip the closures run through round 62
(`corpus/lessons/round-58…round-62-verifier-spotcheck.md`; the round-63 paragraph itself cites the round-62 closure at
`SCORECARD.md:3301`). Counter at tip (`out/.../round59-c2-counter-tip.out`, fleet `c7fb588a`):
`rows=49 mismatches=2 met=False`, `pointer_round=1 including_round=1`, exit 1. Round-58 counter at tip
(`round58-c2-counter-tip.out`, pinned `--manifest-rev 941acf70`): `r42=8 missing=0 stale=1 verdict=0 including=1
mismatches=10 met=False`. The row's "derived at the measured tip" therefore describes a counter that currently fails.
The reconciler does not report it (its 8 details contain no pointer item), so the 8 → 0 target would not catch it.
The round-58 counter also cannot be satisfied by any later closure while pinned to `941acf70`, whose kama closure
rows stop at round 57 (checked: the fleet MANIFEST at `HEAD` has kama closure rows 57–62). The round-58 section said
"the next closure appends a round-58 row and the pointer then legitimately names round 58" (`SCORECARD.md:3201`);
that was not carried out for rounds 59–62.

**A2 — the head says the Axes table, Planned, Retired, Saturation and Capabilities are "re-derived" by the reconciler,
which currently fails on each of those sections. (`SCORECARD.md:6`)** The same banner says "Latest measured round: 61
(wave verdicts pending at this commit)" although round 62 has measured results (`SCORECARD.md:3294`) and non-author
closures exist for rounds 60, 61 and 62 (`corpus/lessons/round-6{0,1,2}-verifier-spotcheck.md`). This is the most
visible self-description overclaim at the head.

**A3 — the round-63 title asserts an outcome not yet true. (`SCORECARD.md:3299`)** "…with the self-description
reconciled (calibration)". At tip the reconciler reports 8 mismatches. Acceptable only as pre-measurement wording; it
must be reworded if the reconciliation does not land in this round.

**A4 — rounds 61 and 62 still show pending verdicts that non-author closures have already filed. (`SCORECARD.md:3253–3254`
"PENDING wave verdicts"; `SCORECARD.md:3269` "Awaiting falsification wave; provisional")** The round-62 closure at
`corpus/lessons/round-62-verifier-spotcheck.md:20` rates both r62 claims "unprovable"; the round-63 paragraph
(`SCORECARD.md:3301`) repeats that, so the round-62 table is internally stale. The round-61 closure
(`corpus/lessons/round-61-verifier-spotcheck.md:64–67`) records "improved" for both axes and C2 `met=True`; the lane
has recorded neither verdict in SCORECARD. Scores are correctly held (8/7), but the self-description carries no
verdict for two closed rounds.

**B1 — stale coverage run fact. (`SCORECARD.md:17`)** "`→ 36`" against a live 38 (§1 item 1). The row's "evidence
re-anchored round 60" is false after rounds 61–62 added two knowledge entries.

**B2 — stale retired count and a present-tense DEAD claim. (`SCORECARD.md:57`)** "6 axes and 11 capabilities" against
12. "the registered consumers still sample DEAD (`registry/history/latest.tsv`)" is present tense; the only tracked
snapshot is `20261014T124232Z` (header of `registry/history/latest.tsv`), dated 2026-10-14, 14 days before the tip date
2026-10-28. No later snapshot is tracked. The claim is true of that snapshot and has not been re-observed since.

**B3 — stale saturation statement. (`SCORECARD.md:137`)** "The last capability entered in round 47 is older than the
N=4 stagnation window" is false at tip: `live-ollama-lifecycle` entered at round 61 (first-working 61 in the canonical
list, `SCORECARD.md:3303` onward). The nudge conclusion itself still holds (calibration 7 < 8).

**B4 — capabilities mirror is 11 rows and lacks `live-ollama-lifecycle`. (`SCORECARD.md:117–131`)** Labelled a mirror of
the round-49 list; expected to be re-derived by L1 after measurement (freeze).

**B5 — the "live plan" pointer names a round-61 plan. (`SCORECARD.md:53`)** "The live plan is `### Planned (round 61)`
below": that block (`:3187`) is the round-60 plan. No round-63 or round-64 plan exists at tip.

**B6 — README's wave range is stale. (`README.md:28`)** "`waves/` (`round-11/`–`round-43/`)". Tip `.ufo/waves/` holds
rounds 11 through 63 (`git ls-tree`). `.ufo/scopes/` is also unlisted (low).

**B7 — host claim about `opencode.json` is wrong on this host. (`PROVINCE.md:11`)** "the file is now 5 lines holding
`$schema`/`theme`/`autoupdate` only", "verified by read-only host inspection". Read-only check on 2026-10-28: 4 lines;
top-level keys `$schema` and `autoupdate` only; no `theme`. Undated host fact: drift since the observation, or a wrong
original count.

**B8 — SHONEN pointer names a heading that does not exist exactly. (`SHONEN.md:6`)** "`SKILL.md` §§Decision table, Error
signatures, Checklist". Headings at tip: `## Decision table — rules with dated September host examples` (`SKILL.md:125`),
`## Historical error signatures — September runtime sample` (`SKILL.md:167`), `## Checklist — current registered-endpoint
workflow` (`SKILL.md:193`). Resolvable by substring only (low).

**B9 — untracked paths contradict the round-63 hygiene statement. (`SCORECARD.md:3301`)** "the lane worktree now has no
lane-authored untracked paths". The worktree now has about 1005 untracked paths (round-63 wave outputs under
`.ufo/waves/round-63/`) and a stray doubled-path file `kama-shokunin/.ufo/waves/round-62/w1/A04C1SchemaFuzz.md` at the
lane root (created 09:26, 2026-10-28). The statement was true at round-62 close-out only. L1 must not commit the stray
path.

**Checked, not overclaims:** no `[x]` anywhere in the lane's self-description (grep over SCORECARD, SHONEN, PROVINCE,
README, AGENTS, SKILL, LOG, `corpus/SOURCES.md`, `corpus/QUALITY.md`; `SCORECARD.md:90` and `LOG.md:400` say "never
`[x]`"). Every SHONEN box is `[~]` with an "Author assertion" and "no named non-author verifier", which is honest.

## 5. SHONEN [~] pointers

Four `[~]` lines, each with an arrow-pointer (`SHONEN.md:6, 8, 10, 12`):
- `LOG.md` §§round 1–3 (headings `LOG.md:7, 100, 203`) and `LOG.md` §round 16 (`LOG.md:925`): resolve.
- `.ufo/waves/round-16/live/receipt.json`: resolves; schema `kama-llamacpp-live/v1`; `checks` 10 of 10 `passed` (matches
  "10/10").
- `.ufo/waves/round-17/live/receipt-{1,2,3}.json`: resolve; schema v2; 11 of 11 `passed` each (matches).
- `tests/llamacpp-live/controls.py` and `.ufo/waves/round-29/w1/out/ScribeShonenBox2/evidence.md`: resolve.
- `SKILL.md` §Checklist (`SKILL.md:193`) and `corpus/knowledge/snapshot-history.md` §Run it (`:7`): resolve.
- `PROVINCE.md` §Write boundary: resolves as the bold paragraph at `PROVINCE.md:47` ("**Write boundary (hard):**"), not a
  heading. `corpus/knowledge/cross-lane-scope.md`: resolves.
- SKILL §Decision table / Error signatures: see B8 (fuzzy).
No `[x]`, no non-author verifier claimed, all four correctly `[~]`.

## 6. Control attacks (mutants in my scratch clone; counter outputs verbatim)

Clone `$S/clone` from `03a6a1d8`; each mutant committed in the clone; the counter run from the clone path with the
tree at the mutant commit. Full outputs in `out/.../mutant-*.out`.

- **M1 — fix A1 only (pointer `round-57`→`round-62`, `including round 62`), commit `9fc946a2`.**
  Round-59 counter: `tip=9fc946a2… fleet=5144b531… maxN=62 manifest=rejected-honest-stop` /
  `rows=49 mismatches=0 met=True` / `row_missing=0 typed_count=0 pinned_fleet_revision=0 pointer_missing=0
  pointer_round=0 pointer_verdict=0 including_round=0 count_command=0` (exit 0). This confirms A1 is a single typed
  pointer. Same tree under the round-42 reconciler: `mismatches=8 met=False` (unchanged). Round-58 counter:
  `r42=8 missing=0 stale=0 verdict=1 including=0 mismatches=9 met=False`, with `manifest=None` for N=62, because the
  pinned `941acf70` MANIFEST has no round-62 row. Outcome: the r59 pointer check is **KILLED-as-designed** (it accepts
  the one-token fix); the r58 counter is **stale by construction** at its pinned revision (a defect of the control set).
- **M2 — score cell only, operability 8→9 (`SCORECARD.md:14`), commit `ec1703a6`.**
  `axes=6 facts=37 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=1 hollow=0 mismatches=2 met=False`; detail
  `operability score 9 != expected 8`. **KILLED** (correct).
- **M3 — score cell 8→9 plus the typed `EXPECTED` constant 8→9 (`tools/round41-scorecard-reconcile.py:57`), commit
  `f08ddcd1`, counter run from the mutated clone.**
  `axes=6 facts=37 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False`; the one
  remaining detail is the pre-existing coverage run. **SURVIVED**: an operability score move passes the score gate with
  no claim, no measured evidence and no non-author check. Defect of the control set.
  (An earlier M3 run was made with the wrong tree checked out and printed `score_bad=1`; it was superseded. The
  counter reads its own code from disk, not from the `--tip` commit, so the tree must be at the mutant commit.)
- **M4 — banner text only, `Latest measured round: 61` → `63` (`SCORECARD.md:6`), commit `dcef3c8b`.**
  `r41=1 banner=0 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=7
  maxN=63 met=False`. **SURVIVED**: the banner rule checks text against the highest `## Round N` heading and never
  against a measured result, so the banner can say "measured round 63" before round 63 is measured. Defect of the
  control set; it bears on the freeze's "reconciler reports 0" target, which text alone can reach.

Summary: 2 of 4 mutants SURVIVED (M3 score move without claim; M4 banner without measurement). One real pointer defect
(A1) is invisible to the reconciler. The r58 counter is stale by construction at its pinned revision.

## 7. What the reconciler and counters cannot see (limits)

- The round-42 reconciler checks text presence, not truth. Run facts are executed only for the r41 `run X → Y` form
  (`tools/round41-scorecard-reconcile.py:63`); typed closure pointers and verdict text are not executed at all.
- The score gate is a typed constant the same commit can change (M3).
- The banner gate is text presence against a heading (M4).
- Dated host facts (`PROVINCE.md:11`, `latest.tsv` DEAD) are not re-observed by any counter (B2, B7). I did not run the
  probe against registered consumer ports; DEAD was not re-observed here.
- `tools/round59-c2-counter.py --fleet-ref HEAD` moves with the fleet repo (fleet HEAD observed as `c7fb588a`, then
  `b2eada22`, then `5144b531` during this session). Its result is HEAD-dependent; the tip receipt above is from `c7fb588a`.

## 8. Handoff for L1 (advisory; the L1 decides)

1. Re-derive the SCORECARD head after measurement (§1 items 2–7). Do not reach 0 by banner text alone (M4); A2 and A3
   wording must also be true.
2. Fix A1 before claiming "derived at measured tip": update the calibration row's pointer to round 62 and record the
   round-62 closure verdict. M1 shows the one-token fix satisfies the round-59 counter. Either advance the round-58
   counter's `--manifest-rev` or state that its predicate is retired for rounds after 57.
3. Record the round-61 and round-62 closure verdicts in the round-61/62 tables (A4).
4. Update the coverage row (`SCORECARD.md:17`: 36 → 38, and the r61/r62 entries). Its `PROVINCE.md` sha256 changes when
   the worktree PROVINCE edit is committed.
5. Correct B2, B3, B4, B5, B6, B7 (or re-observe the host fact and date it), and B9 (the stray doubled-path file must not
   be committed).
6. Do not keep the round-63 title (`SCORECARD.md:3299`) if the reconciliation is not measured.

## 9. Tally

`reconcile tip=03a6a1d8 mismatches=8 met=False` (r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 province=1)
· `round59-c2 @tip mismatches=2 met=False` (pointer_round=1 including_round=1)
· `round58-c2 @tip mismatches=10 met=False`
· `assigned-axis run facts 5/5 + 2 selftests reproduce; coverage run 36≠38`
· `SHONEN [~] pointers resolved 4/4; receipts 10/10 and 11/11×3`
· `[x] found 0` · `overclaims A1–A4, B1–B9`
· `mutants KILLED 2 (M1 as designed, M2), SURVIVED 2 (M3 score move, M4 banner)`.
