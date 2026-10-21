# ConnFrontierLedger — round-23 frontier disposition (draft)

Seat: `CloseKama22.ConnFrontierLedger-2` (connector, leaf). Base verified:
`git -C /tmp/kama-r23w2/ConnFrontierLedger rev-parse HEAD` →
`245a37f69628c2c6bb29bbf17897d8fb5946c857`. git 2.56.0, Python 3.14.
No installs, no commits, no jj, no lane/fleet writes.

## Verdict: partially

The L1's uncommitted README draft (`corpus/README.md:317-329` in the working
tree; committed file ends at `:315` at 245a37f6) has the right claim —
`D4` partially advanced, not untrusted-repository safety — and the right
lesson-list of open items. It is not publishable as written: it carries no
count, repeats three statements the falsify wave bounded, and states the
partial-clone refusal as a benign trade. Exact replacement text is in
`out/ConnFrontierLedger/`; the SCORECARD tail had no round-23 section at
base, so a tail block is drafted too.

## Axes

1. **Ledger fidelity** — every sentence traceable to a command or a named
   falsify artifact at 245a37f6.
2. **Boundary honesty** — no claim wider than the committed population; open
   classes and routed debt named rather than smoothed.
3. **Integration safety** — append-only, no existing line moves, no axis
   score change, no new capability row.
4. **Cross-document consistency** — README, SCORECARD, lesson and knowledge
   entry tell the same bounded story.

## The one move

Replace the draft with a disposition whose counts are population facts, not
generalities: 26/26 graded fault rows and 8/8 controls (frozen `4fe9339f`
commit, auditor blob `fcc255ce`: 0/26, 8/8), 24 committed mutants with 22
killed; then name what the count does **not** cover — three contract-change
rows, one defensive-only survivor, one survivor that is load-bearing but
uncovered, and supplementary mutants outside the set — and turn the
partial-clone "declared tradeoff" into an operability trade with its
`--shared` bypass and over-refusal class. This improves ledger fidelity and
boundary honesty without touching the narrow D4 advance, the 7 → 7 axis
score, or any capability claim.

**Affected axes.** Ledger fidelity — improved (every clause is a measured or
named wave artifact). Boundary honesty — improved (counts bounded to the
committed population; open classes named). Integration safety — unchanged
(append-only, no score or capability change). Cross-document consistency —
improved only if the lesson/SKILL appends in Risks 1 and 6 land; otherwise
the README text and the committed lesson disagree on M02 and the traceback
count.

## Evidence (commands and observed results at 245a37f6)

**E1 — grid, both arms.** `python3 tests/report-audit/repo-state-grid.py
--arm both --json` → exit 1 (frozen red by design). Current: faults 26/26,
controls 8/8, tracebacks 0, `commands_executed` 0, timeouts 0. Frozen:
faults 0/26, controls 8/8, tracebacks 9, executed 2, timeouts 1. 37 rows =
26 fault + 8 control + 2 open (O01, O02 NOT-MET) + 1 tradeoff (T01 NOT-MET).
Auditor sha256 current `f228f174…`, frozen `09ecd63b…`; population
`83a84702…`; `frozen_revision` = `4fe9339f…`.

**E2 — frozen determinism.** `… --arm frozen --json` twice more → exit 1
both; 9 tracebacks both, same rows: F01, F02, F16, F18, F19, F20, F22
(strict `UnicodeDecodeError`) + F24, F26 (integer-digit `ValueError`). The
lesson's `8 tracebacks` (`corpus/lessons/round-23.md:64`) is stale.

**E3 — the three contract-change rows, frozen.** `… --arm frozen --case
F17-errata-revision-correction --case F21-nested-subdirectory-lane --case
F23-promisor-pack-without-config --json` → F17 exit 0 (expected 1), kinds
`unresolved-full-hash`; F21 exit 1 (expected 2), kinds `landed-unresolved`,
`unresolved-full-hash`; F23 exit 1 (expected 2), `unresolved-full-hash`; no
traceback, execution or timeout in any. Frozen fails closed, it does not
crash on these rows.

**E4 — committed mutants.** `python3 tests/report-audit/isolation-mutants.py
--json` → exit 0; mutants 24, killed 22, surviving `M02-lazy-fetch`,
`M20-log-sha-shape`.

**E5 — M02 is load-bearing.** `python3
.ufo/waves/round-23/falsify/out/CritDefensiveOnly/probe.py <clone>` →
pristine P01/P02 met (exit 1, exec 0); M02 P01/P02 NOT-MET (exit 1, **exec
1**); M20 met. A `remote.*.partialclonefilter`-only repo lazy-fetches and
runs `core.sshCommand` once `--no-lazy-fetch` is removed.

**E6 — over-refusal class.** `/tmp/probe-overrefuse.py` (grid `base()`
fixtures, frozen + current) → plain 0/0; `stray-promisor` 0 / 2 `partial
clone (promisor pack)`; `promisor-false` 0 / 2 `partial clone
(remote.origin.promisor)`; `nonutf8-config` 0 / 2 `output is not UTF-8 …`.
All on complete, sound fixtures.

**E7 — `--shared` bypass.** `/tmp/conn-shared-of-partial.sh` (adaptation of
`CritTradeoffHarm/shared-of-partial.sh`) → `--shared` clone of a blob:none
partial: current exit 1 with false `unresolved-full-hash c2981a9931`, frozen
identical; direct partial: current exit 2 refusal, frozen exit 0 and fetches;
truth: `cat-file -t c2981a9931…` in the source → blob.

**E8 — frozen identity.** `git cat-file -t 4fe9339f…` → `commit`;
`git rev-parse 4fe9339f…:tools/report-landing-audit.py` →
`fcc255ce5115a749dfbd09cf992ba9851a2dc90a`. Read via `cat-file blob` at
`tests/report-audit/repo-state-grid.py:639-640` with `FROZEN` at `:31`.

**E9 — real population, both arms.** `--lane-repo kama-shokunin
--fleet-repo …/shokunin --rounds 10-22 --json` and `--no-errata` → after
marker removal frozen and current both clean exit 0 / `--no-errata` exit 1;
stdout byte-identical across arms (`cmp` rc 0; sha256 `1ae84922…` /
`13b17b1c…`).

**E10 — fleet markers.** `ls -la …/shokunin/.git/objects/pack/*.promisor`
→ present at 12:50 and 12:58 -0300 (four zero-byte files, incl.
`pack-deadbeef.promisor`); absent at 13:05. Fleet
`config --get-regexp 'remote\..*\.promisor|extensions\.partialclone'` exits 1.

Anchor lines: `tests/report-audit/repo-state-grid.py:31,639-640`;
`tests/report-audit/isolation-mutants.py:30` (M02), `:58` (M20);
`tools/report-landing-audit.py:93` (`GIT_ISOLATION`), `:194` (40-hex record
shape), `:443-444` (any `*.promisor` file), `:447` (`remote..*.promisor`
name); `corpus/lessons/round-23.md:64,68-92`;
`corpus/knowledge/error-is-not-a-verdict.md:55-72`.

## Deltas from the current working-tree draft (`corpus/README.md:317-329`)

| Draft says | Problem | Replacement |
|---|---|---|
| No count | The assigned axis is countable; without it "graded and mutant-checked" is unanchored | 26/26, 8/8, 0/0/0; frozen 0/26; 24 mutants, 22 killed |
| "prefix-ambiguity overwrite" | Lesson and `RevLookup` F1 name **peel and cross-repo** results overwriting ambiguity | "peel/cross-repo ambiguity overwrite suppresses `landed-ambiguous` (F1)" |
| "duplicate Landed sections" | The defect is that only the **first** `## Landed changes` section is read; `ExecSecondLanded` shows a second section is ignored in both arms | "only the first `## Landed changes` section is read" |
| Open list omits `log.follow` | Lesson lists the path-vs-lineage contract as open | add "`log.follow` kept as a path contract" |
| "Declared tradeoffs: … partial clones refused" (benign) | E6 shows three sound clean verdicts become exit 2; E7 shows a `--shared` clone bypasses the refusal and yields a false defect | add both classes; call the refusal an operability trade |
| Omits M02 / fairness / mutant coverage | The wave bounded all three; repeating "mutant-checked" without them overstates | one sentence: F17/F21/F23 contract changes; M20 defensive-only; M02 uncovered; supplementary mutants survive |

## Placement

- `corpus/README.md`: append the bytes of
  `out/ConnFrontierLedger/README-frontier-round-23.md` after committed line
  315 (the round-22 paragraph), replacing working-tree lines 317-329; one
  blank line before the heading, as in every prior disposition.
- `SCORECARD.md`: append the bytes of
  `out/ConnFrontierLedger/SCORECARD-tail-round-23.md` after line 1150 with
  one blank line. No existing line moves; round-22's "trusted-repo audit
  hardening … not acquired here" (`:1108`) stays true at round 22 and needs
  no erratum.

## Verification (for L1 after integration)

1. `python3 tests/report-audit/repo-state-grid.py --arm current --json`
   (expect 0; 26/26, 8/8, 0/0/0).
2. `… --arm frozen --json` (expect 1; 0/26, 9 tracebacks).
3. `python3 tests/report-audit/isolation-mutants.py --json` (expect 0;
   24 mutants, 22 killed).
4. `python3 tools/report-landing-audit.py --rounds 10-22 --json` (expect 0)
   and `--no-errata` (expect 1), on a fleet with no stray markers.
5. `python3 tools/report-landing-audit.py --selftest` (expect 0, 50/50;
   not run by this seat).

## Risks and contradictions (stated, not smoothed)

1. **The draft corrects the lesson on two points** (M02 not defensive-only;
   8 → 9 frozen tracebacks). The lesson is committed and immutable; the L1
   must either append a lesson correction or drop those claims from the
   disposition. The SCORECARD block carries the 9 explicitly.
2. **F17/F21/F23 classification is CritFrozenFairness's**, not re-derived
   here. I verified only frozen's non-crashing exit 0/1/1. If the L1 rejects
   the classification, drop the clause and the count stays "26/26 graded
   rows" but must not be read as 26 isolation wins.
3. **Routed debt is not exhaustive in the lesson** (`ConnClosureRoutes`
   G1–G4: selftest fallback/GIT_DIR, prelaunch race, 41-hop bound, JSON
   duplicate-key/Unicode, R20 limits/L0). The SCORECARD tail carries them;
   keeping them out of the README is deliberate, and the disposition does not
   claim the open list is complete.
4. **The fleet incident is historical** (E9/E10): the gate is restored and
   arms are byte-identical, so the disposition must not say it is still
   refused. The presence-only marker check remains a code fragility proved on
   fixtures.
5. **Do not say "no harm"**: operability is a trade (E6/E7). KQ32 is still
   satisfied because the advance is bounded to the trusted lane/fleet
   population.
6. **Stale SKILL boundary**: `SKILL.md:771` still says D4 remains frontier and
   `:683` omits the new exit-2 causes (peer-cited; not edited here). A
   disposition that says "partially advanced" makes that line stale; L1
   should append a SKILL correction.

## Not verified

- Round-23 selftest (`50/50`), sources census (`95` rows), the four
  `MutRetestA–D` supplementary mutants individually, and CritFrozenFairness's
  patched-frozen probe matrix were not re-run by this seat; they are cited as
  wave evidence.
- O01/O02/F1 fixtures were not rebuilt; their status is the committed grid's
  `open` rows (E1) and the lesson.
- The `twelve` supplementary-mutant count is omitted from the drafts because
  only the four reports' own counts support it.
- Marker writer identity; git versions below 2.56.0; a real shallow clone.

## Files written

- `.ufo/waves/round-23/falsify/advice/ConnFrontierLedger.md` (this file)
- `.ufo/waves/round-23/falsify/out/ConnFrontierLedger/README-frontier-round-23.md`
- `.ufo/waves/round-23/falsify/out/ConnFrontierLedger/SCORECARD-tail-round-23.md`

## Tools installed or updated

None.
