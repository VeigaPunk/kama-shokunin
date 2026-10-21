## Round 23 — repository-local git state isolation in report-landing-audit (2026-10-21)

**DRAFT — not appended to `SCORECARD.md`.** Bracketed `[PENDING …]` cells are
filled only from the committed-run receipt, which does not yet exist
(`.ufo/waves/round-23/` has no `runs/` directory at lane HEAD `245a37f`).

Declared C1 calibration **7 → 7** (narrow), the lowest assigned non-retired
axis (operability 8); no stagnation waiver. Round base commit:
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d`. Measured lane master:
`245a37f69628c2c6bb29bbf17897d8fb5946c857` `[PENDING: confirm at measurement]`.

Before: `tools/report-landing-audit.py` (frozen auditor blob
`fcc255ce5115a749dfbd09cf992ba9851a2dc90a` at commit `4fe9339f`) could exit 1
through a traceback, flip a verdict, hang, or run a program when the audited
lane or fleet repository carried repository-local git state (config, replace
refs, grafts, promisor settings, log display keys, encoding, object format).
After criterion: the current auditor refuses or neutralizes each such channel
and returns its declared exit with no traceback, execution or timeout, while
the ordinary controls keep their verdicts. The docstring claim "Errors are
never verdicts" and "audited repositories cannot be redirected" are the
promises the grid tests.

This works the existing D4 calibration gap, not a new capability. It is not
untrusted-repository safety: KQ32 stays in force. Shallow and partial clones
are refused even when every cited object is local (declared tradeoff T01).
Sources S089–S095 and motivating lesson `corpus/lessons/round-23.md`. No
capability row added `[INFERENCE: lesson names none; L1 to confirm]`.

### Round-23 measured results — committed tree `[PENDING]`

Counting commands (the recipe run pins argv and streams; these are the
harness invocations the grids document):

- `python3 tests/report-audit/repo-state-grid.py --arm frozen --json` — expected exit 1
- `python3 tests/report-audit/repo-state-grid.py --arm current --json` — expected exit 0
- `python3 tests/report-audit/repo-state-grid.py --arm both --json` — expected exit 1 (frozen arm red)
- `python3 tests/report-audit/isolation-mutants.py --json` — pristine must pass; every mutant ran
- `python3 tools/report-landing-audit.py --selftest` — expected exit 0, 50/50
- `python3 tools/report-landing-audit.py --rounds 10-22 --no-errata --json` — expected exit 1, 9 defects
- `python3 tools/report-landing-audit.py --rounds 10-22 --json` — expected exit 0, ledger identical to frozen

| Claim | Axis/score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 repository-local git state isolation (26 fault rows F01–F26, graded) | calibration 7 → 7; verified narrow improvement | faults met 0/26 → `[PENDING]` (L1 declared 26/26); controls 8/8 both arms `[PENDING]`; tracebacks/executions/timeouts 0 → `[PENDING]` | `repo-state-grid.py --arm frozen --json` / `--arm current --json` | `runs/<SHA>/c1-grid-{frozen,current}.stdout` `[PENDING]`; frozen blob `fcc255ce…`, current SHA `[PENDING]`, population SHA `[PENDING]` |
| Isolation elements necessary to the grid (24 single-element mutants) | calibration evidence, not scored | killed 22/24 → `[PENDING]` (L1 declared); survivors M02 (`--no-lazy-fetch`, superseded by promisor refusal) and M20 (40-hex `%H` check) reported defensive-only | `isolation-mutants.py --json` | `runs/<SHA>/c1-mutants.stdout` `[PENDING]` |

The frozen arm is expected to be red (exit 1) by design; its red status is the
control that the fault grid can fail. The `--arm both` exit is the combined
status and is not a regression signal. Error-detail strings are informational,
not graded `[INFERENCE: grid docstring]`.

No-harm: auditor selftest `[PENDING]` (L1 declared 50/50); rounds 10–22
ledger `[PENDING]` (L1 declared byte-identical to frozen; `--no-errata` exit 1
with 9 raw defects `[PENDING: confirm against the committed receipt]`). No live
server, model or registered consumer is touched; this is audit-tool calibration.

Sources: corpus rows **88 → 95** (verified by the scribe at `245a37f` by row
count and by `git diff --numstat 4fe9339 HEAD -- corpus/SOURCES.md` = 7
insertions, 0 deletions). Tier counts A83 / B2 / C3 → A90 / B2 / C3. S089–S095
are additive rows; no existing status, recheck or used-by cell changed. The
census/validate command `scripts/sources-census.sh census --root
/home/vgpnk/Projects/shokunin kama` `[PENDING: run by main agent]`.

Trends `[INFERENCE — L1 to ratify]`: expansion **unchanged** (no capability
row; seven source rows support an existing claim); quality **improved**
(a measured D4 isolation gap closed on a committed grid with a frozen control
arm); discernment **improved narrowly**, because the gate is shown able to
fail on the frozen arm (0/26) and the 24-mutant check separates necessary from
defensive elements.

Planned: keep open and ungraded `O01` (objects through
`objects/info/alternates`), `O02` (`.git` gitfile redirect), peel/cross-repo
ambiguity overwrite, the second `## Landed changes` section, CR inside an
errata line, and the unisolated sibling tools `citation-provenance.py` and
`sources-append-only.py`. Declared tradeoffs: partial/shallow clone refusal
(T01) and the git ≥ 2.45 floor (`--no-lazy-fetch`). Await outside
non-author spot-check. No next round is started.
