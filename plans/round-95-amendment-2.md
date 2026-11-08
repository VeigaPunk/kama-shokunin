# Round 95 — amendment 2 (post-wave narrowing, Amendment 59 ledger)

Date: 2026-11-08. Author: L1 `KamaR95`. Frozen plan `plans/round-95-claims.md` (`c798e831`), amendment 1
(`719214fa`, `bba10f75`). This file records what the round's own wave falsified in the freeze's wording and the
enforceable property each claim is filed on. It rewrites no frozen byte.

Falsifying artifacts (all under `.ufo/waves/round-95/w1/`): `EX01FreezeAuditControl.md` (F1–F9),
`CR02SetterCounter.md` (BLOCKER + 2 DEFECTs + NOTE), and, for C1, the wave's attack seats
`CR01BudgetCounter`, `RV01ProbeDiff`, `MT01ProbeMutants`, `SN01VerdictBoundary` (recorded in the
claim-falsification ledger with their verdicts).

## C1 operability — **verified as narrowed** (wording unchanged; limits restated)

Frozen sentence: the router file-state verdict is a function of the file's bytes, and the pass limit is derived from
the candidate count. Predicate reproduces at M1 `f6325660` (`measured/c1.out`), and the red control reproduces the
defect (`controls/c1-base.out`, `mismatches=1`).

Wave-falsified sub-clauses and their disposition:

- **The K2 phrase "the base harm receipt the M1 commit carries"** (`EX01FreezeAuditControl.md` F4) named a receipt
  no round-95 commit carries; `git rev-list --all --objects | grep -E 'round-95/.*harm'` was empty when the wave
  ran. **Disposition:** the wave's `EX02HarmSuites` seat produces the base/tip pair; the receipt is committed with
  the wave evidence and named in LOG.md. If it is absent, C1 files with K2 **unfired-not-unfalsified**: the harm
  claim is then not evidence for this round and is recorded as carried debt.
- **Disclosed, unchanged:** a candidate declaring more than `MAX_TENSORS` tensors or needing more than `MAX_STEPS`
  steps stays `-` and therefore loadable (cell W09 grades that as the disclosed expectation, not as a fix); the
  derived wrapper is still a wall clock at the pass level; a slow `/props` answer still decides the verdict
  (round-94 SC02 F4) — routed, not claimed.

## C2 depth — **verified as narrowed (instrument coverage only)**

Frozen sentence claimed the printed line `… entries=7 decisions=9 decisions_bound=9 met=True` **and** exit 0 as the
predicate. `CR02SetterCounter.md` BLOCKER shows the exit condition never reads `entries=` (a section printing
`entries=6` still exits 0), so as worded the sentence claims more than the instrument enforces.

`RV02SetterRows.md` (non-author read) adds four falsifications of the section's own **prose** — B1 (the
router-child slot count is still undecided and has no `R21` row), B3 (the pattern does not contain a
`preset.name == "*"` token), D1 (the `cli-server.h:43` copy carries the slot count but not the listen port, which
`:35`/`:44` replace), D2 (`R21 other` describes perplexity's clamps as sequential) — plus B2 (`R21 other` should
acknowledge P16's reach). Disposition: `SKILL.md` §Round 95 correction c1–c4 lands the corrected readings in the
same round (`37820b5b`); the frozen rows are not rewritten, and the claim below is filed on the counter-enforced
property only.

Filed property (exactly what the frozen counter enforces at M2 `beef8922`): the round-95 section's population of
106 archive lines is fully bound (text byte-exact, source resolvable to a `/b12177/<file>` row, derived cells
agreeing), and for every (parameter, entry) pair that owns a `default`/`overrides` row there is exactly one decision
row whose id set equals that row set and whose decision text carries the entry's precedence tokens. That is what
`met=True` is computed from.

Disclosed limits (from `CR02SetterCounter.md`, all reproduced with receipts in its out dir):

- `entries=` is printed but not part of `met`; a relabelled `copies` row moves it without changing the exit.
- The 14 carrier rows (P93–P106) are enum-graded only: none enters a decision id set, so a wrong Entry cell on the
  whole-struct carrier (`cli` → `server`) still scores `met=True`.
- Row ids are not unique and the decision model compares id **strings**, so a renamed row can satisfy two
  decision rows.
- Still binding from round 94: non-integer-literal value cells, `default`↔`overrides` swaps, condition and scope
  garbage on non-`arg.cpp` rows, decision-text negation that keeps the tokens, and a fabricated SOURCES row.
- A decision row's Sources cell is never read; a P-row's source is graded only as "some cell contains
  `/b12177/<file>`", with no S-row status or digest check.

The prose truth of the nine decision rows remains a non-author read (`RV02SetterRows.md`), never the counter.

## C3 calibration — **verified as narrowed (presence + token names only)**

`EX01FreezeAuditControl.md` F1 is decisive against the frozen tool's own docstring: `sources_status` stores
`cells[8]` (the `opened` date) instead of `cells[7]` (the `status`), so the `rejected` arm is dead on all 28
rejected rows of the lane registry, and a forged plan citing two rejected rows scores `unresolved=0 met=True`.
F2 adds that the token arm checks only that a metric **name** occurs somewhere in the counter's bytes, never that a
value is the one printed; F5/F6 add that only backticked `controls|measured|w\d/…` paths count and a directory
counts as a receipt.

Filed property (what the frozen counter enforces at `bba10f75` over `plans/round-95-amendment-1.md`): every
backticked receipt path the statement names exists at the audited revision (`receipts=9 present=9 missing=0`),
every metric **name** on a predicate line occurs in that counter's committed bytes (`tokens=24 matching=24`), and
every cited `S###` resolves to a Registry row at that revision (`cited=14 unresolved=0`), exit 0 — while the same
instrument on the round-94 plan at its own freeze reports `receipts=12 present=0 missing=12` with the named counter
absent, exit 1.

Explicitly **not** claimed: row **status** (the arm is dead — the fix is routed to round 96), metric-value equality,
receipt **content**, and path forms other than a backticked `controls/`-style relative path. The presence arm over
history is real (`EX01` F9: r94 at its freeze 12/0/12, r93 with S600–S603 unresolved, r92 with one missing receipt).

## Net verdicts

| claim | verdict | basis |
|---|---|---|
| C1 | verified (narrowed limits disclosed) | `measured/c1.out` exit 0; `controls/c1-base.out` exit 1 |
| C2 | verified as instrument coverage | `measured/c2.out` exit 0; limits above disclosed |
| C3 | verified as presence + token names | `measured/c3-amended.out` exit 0; `controls/c3-base.out` exit 1 |

No axis harmed: `controls/harm-pair.out` — `tests/probe-verdicts/check.py` 77/77 passes at both the base
(`2011161d`) and the round-95 probe (`f6325660`) and `tools/test-snapshot.sh` `RESULT pass=30 fail=0` at both; the
wave's `EX02HarmSuites.md` reports all seven K2 suites plus a read-only live GET identical at base and tip (verdict
`holds`). The round changed no registered consumer row and no probe verdict class for a healthy endpoint.
