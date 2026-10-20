VERDICT: partial — C1/C2 mutation counts are mostly tameshi-shaped, but the delivered counters disagree with tameshi on targeted-kill and equivalent-mutant rules, count inconclusives inside the residual denominator, and the head counter bytes no longer match the published measurement.

Seat: connector overlap scan, read-only. Compared the round-18 mutation denominator,
targeted-kill and equivalent rules against `tameshi-shokunin/SKILL.md` and
`tameshi-shokunin/corpus/README.md` only (the two tameshi sources assigned). Kama sources
read: `corpus/lessons/round-18.md`, `SCORECARD.md` §Round 18, `corpus/QUALITY.md`
KQ23/KQ24, `.ufo/waves/round-18/c1/measure.py`, `.ufo/waves/round-18/c2/survivors.py`,
the official `runs/` artifacts, and the head/c6dc46f blobs via read-only git. No sibling
was edited; no production, fleet, frozen evidence or lane state was written.

## Evidence base

- Head is `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, clean for the files below.
- Raw C2 run: `.ufo/waves/round-18/runs/c2-survivors.json` records its own tool
  `sha256 2af03fed6ccb0b09e30061828843372cb503d5d5e3afae846bc3f5473ced411d`.
  `git show c6dc46f:.ufo/waves/round-18/c2/survivors.py | sha256sum` → `2af03fed…`;
  head `sha256sum .ufo/waves/round-18/c2/survivors.py` → `87cad1ca…`.
- Raw C1 self-mutants: `runs/c1-self-mutants.json` `.inputs.measure.sha256` =
  `55b26b3b47e316f6b013fae980550073bad3972009c7dcee75d8d0da9e568c17`, equal to
  `git show c6dc46f:.ufo/waves/round-18/c1/measure.py | sha256sum`; head → `a9577ed8…`.
- `git log --oneline -8 -- .ufo/waves/round-18/c2/survivors.py .ufo/waves/round-18/c1/measure.py`
  shows exactly `1c325b2 round-18: retain measured arms and repair counter classification seams`
  then `c6dc46f round-18: classify missing observations and bind detector survivor claims`.
- `git diff --stat c6dc46f..1c325b2 -- …` = `c1/measure.py` 117 changed lines,
  `c2/survivors.py` 26 changed lines.
  Production subjects (`tools/kama-llamacpp-live.py`, `tests/llamacpp-live/*`,
  `tests/probe-verdicts/*`, `tools/sources-append-only.py`,
  `round-18/dispatch-provenance.py`) are unchanged between the two commits; only the two
  counting commands and their selftests moved.

## Disagreements with tameshi

### D1 — C1 self-mutant "killed" is exit-only (targeted-kill rule)

`c1/measure.py:999-1001` appends `selftest (exit N)` to `killed_by` whenever the mutant
selftest exit is non-zero; it does not require the named failing case, the suite's own
count, or the absence of a crash. `apply_mutant` (`:848-860`) and `run_self_mutants`
(`:894-1045`) never parse `selftest: 70 cases, N failure(s)` and never assert the failing
label. The official record proves the rule, not just the outcome: every
`runs/c1-self-mutants.json` mutant has a `selftest (exit 1)` entry in `killed_by`
(`drop-gate-flip-arm` also has `numbers:current`); the raw `selftest.stderr_tail`
contains the expected labels for two mutants (`SELFTEST FAIL k0 …`, `SELFTEST FAIL k6 …`)
and `ControlsFault: k1 …` for the third, and `stdout_tail` carries
`selftest: 70 cases, 2 failure(s)` for the two, but the counter asserts none of those
strings.

Tameshi's bar: killed requires "the run went red … **and** the suite still enumerated its
full case count", failing-case labels verbatim, and "never exit alone"
(`tameshi-shokunin/SKILL.md:189-204`). A mutant that crashed before the suite enumerated
its cases would be `inconclusive`, not killed (`SKILL.md:208-209`). C1's rule would count
that crash as a kill.

Inconsistency inside the lane: C2's `selftest_arm` (`c2/survivors.py:928-953`) does
require a named target (`SELFTEST_TARGETS`, `:907-914`) and treats exit 2 as
inconclusive. The two counters implement different targeted-kill rules. The C2 rule is
closer to tameshi; it still does not compare the mutant's enumerated count to the
baseline's count (D4).

### D2 — "equivalent" is not a classification; a no-op is a survivor

C1's synthetic table (`c1/measure.py:1549-1563`) declares
`'noop': ('observably equivalent edit', …)` and asserts the summary is
`'noop': 'survived'`. There is no `equivalent` status anywhere in `measure.py` or
`survivors.py`; `GOOD = {killed, handled, correct}` (`survivors.py:214`), and
anything else is residual/survived. `apply_mutant` does not assert `new != old`, so a
no-op edit would also land as `applied` and be reported `survived`.

Tameshi: assert `new != old` because "a no-op edit is a driver bug, not a survivor"
(`SKILL.md:171-178`); probe every survivor for non-equivalence and, if no observable
input differs, record it as a calibration item, "not as a gap"
(`SKILL.md:214-223`). Kama therefore conflates "equivalent code" with "detector gap"
in the C1 self-mutant path. The real three C1 mutants are non-equivalent by
construction, so the published three kills are not affected; the rule is.

### D3 — residual denominator includes inconclusive

`survivors.py:1430-1449` defines `before`/`after` as "named items not in GOOD"; the
`inconclusive` extra block is emitted separately. The official stdout's last line is
`named items not killed/handled/correct: before 15 -> after 2 (of 15 named)`
(`runs/c2-survivors.stdout`), and `runs/c2-survivors.json` `.counts.outcomes.after` is
`killed 9, inconclusive 2, correct 1, handled 3`; the two residual items are both
`inconclusive` (`.inconclusive_reasons.items` = `FC-target`, `FC-f6cache`). So the
"after 2" headline is not a survivor count, and a reader can take it as two surviving
mutants when `outcomes.after.survived` is absent/zero.

Tameshi: "Kill rate = killed / (killed + survived) — inconclusive runs are excluded
from the denominator and named beside it" (`SKILL.md:210-213`). Kama names them, but
its count field mixes them with survivors. The lesson text (`round-18.md:170-176`)
calls them "two FC inconclusives", which is correct for the raw run but not what the
`after` number expresses.

### D4 — a kill does not require full case enumeration (C2)

`selftest_arm` on mutant exit 1 only requires `doc["problems"]` to contain the
expected literal (`survivors.py:942-953`); it does not compare `matrix_tests`,
`rows_checked`, `wrapper_checks` or `selftest: N cases` against the green baseline.
Tameshi requires the mutant run to still enumerate its full count so an early abort
cannot be read as a targeted kill (`SKILL.md:191-194`). The raw fault-controls
selftest JSON does carry `matrix_tests: 72`, `rows_checked: 5`, `wrapper_checks: 32/35`,
so the data exists; the classifier ignores it. Same class as D1 for C1.

### D5 — delivered counter bytes vs published measurement (pin rule)

The official pass at `c6dc46f` produced `c2-survivors.json` with tool
`2af03fed…`, and `c1-self-mutants.json` / `c1-measure.json` with measure
`55b26b3b…`. At head `1c325b2` the two counters are `87cad1ca…` and `a9577ed8…`.
The head commit also adds the `runs/` evidence and changes `combine_arms`:

- old (`c6dc46f`): "Any inconclusive arm prevents a kill claim"; an inconclusive arm
  returned `inconclusive` even beside a `killed` arm.
- head (`1c325b2`): "Any independently conclusive detector arm is sufficient to kill";
  `killed` has precedence over `inconclusive` (`survivors.py:976-986`).

With the published family-b arms, the head classifier would return `killed` for
`FC-target` and `FC-f6cache` (selftest killed, main inconclusive), so `counts.after`
would be 0 and `exit` 0, not the published `after 2` / `exit 2`. The head selftest also
changed its assertion from "an inconclusive arm prevents a kill" to "a targeted
selftest kill survives an other-arm exit 2" (`git diff c6dc46f..1c325b2`), and that
selftest has no official rerun: `runs/c2-counter-selftest.*` and
`runs/c1-counter-selftest.*` were produced at 22:35:37/22:35:43Z, before the 22:40:05Z
C2 run and before the head commit; `runs/c1-measure.*` / `c1-self-mutants.*` bind the
old hashes. `SCORECARD.md:753-756` still cites
`python3 .ufo/waves/round-18/c2/survivors.py --json --out PATH` as the counting
command, which is now a different program from the one that produced the cited counts.

Tameshi's pin rule: "Pin the artifact — committed bytes only … A pin on uncommitted
bytes is a false anchor" (`SKILL.md:150-158`), and the sweep records the artifact hash
before and after (`SKILL.md:224-229`, `375-405`). The lesson disclosure says "corrected
reruns are new artifacts, never overwritten" (`round-18.md:165-176`), but no corrected
C1/C2 count artifact exists under `runs/`; `git status --porcelain -- .ufo/waves/round-18/runs/`
shows only untracked `?? .ufo/waves/round-18/runs/corrected.py` (not a run JSON, not
this seat's, not inspected or touched). The published `after 2` and the delivered
counting command disagree, and the head counters' selftests are themselves unmeasured.

The same drift affects C1's main measurement: raw `c1-measure.stderr` is
`c1-measure: fault: before: misclassified=1 but 0 row(s) classified misclassified`
(exit 2). The head `measure.py` changes that cross-check (117-line diff), but
`runs/c1-measure.json` still binds `55b26b3b…`; no head rerun exists. The head command
may now pass, but that result is unrecorded.

## Affected axes

- **Calibration (primary, lowest axis):** D1–D4 are rule-level; D5 is provenance. The
  C2 claim is explicitly "a bounded named-survivor repair, not evidence that an unseen
  mutant cannot survive" (`corpus/lessons/round-18.md:23-24`), and the scorecard says
  "it is not a claim of universal detector adequacy" (`SCORECARD.md:758`), so the rule
  gaps matter more than a universal-rate claim; D5 makes the published denominator
  non-reproducible from the delivered command.
- **Operability (secondary):** no production subject changed and no live surface is
  touched. The scorecard's counting command is the only operability-facing item; a
  reader who runs it now gets a different classification from the retained raw run.

No other axis is harmed by the proposed move; it adds measurement, no claim.

## Proposed move (one bounded proposal)

**Publish a counter-conformance rerun at `1c325b2` as new artifacts, and bind each
published count to the counter hash that produced it.** Keep the `c6dc46f` raw
`exit 2` run untouched. In the new run's JSON and the lesson/scorecard:

1. Record the counter's own sha256 (`survivors.py` already writes `tool.sha256`;
   `measure.py` already writes `inputs.measure`), so the raw and corrected rows are
   traceable.
2. Emit a tameshi-shaped denominator block: `killed`, `survived`, `inconclusive`,
   `equivalent`, with `rate = killed/(killed+survived)` and the inconclusive ids named
   beside it. Keep the existing residual `before`/`after` field for continuity, but do
   not label its total "survivors".
3. Add the C1 per-mutant expected-failure literal (the three real mutants already have
   one in their raw `stderr_tail`), require the enumerated case line
   (`selftest: 70 cases, N failure(s)`) and a named failing label, and classify a
   no-op/observably-equivalent edit as `equivalent`/calibration rather than `survived`.
4. Re-run `c1 measure.py --self-mutants`, `c1 measure.py --json`, and
   `c2 survivors.py --json --out NEW` at `1c325b2` (C1 self-mutants ~101 s, C1 measure
   ~40 s, C2 ~1577 s per the raw runs) and retain stdout/stderr/exit. The head `combine_arms` decision must be stated
   in the lesson: the two FC rows are `killed`/exit 0 under the repaired rule, versus
   `inconclusive`/exit 2 in the raw run; the raw run stays historical, not overwritten.

If a 26-minute C2 rerun is out of budget for this wave, the minimum move is the
documentation half: mark the C2 raw counts as produced by `2af03fed` at `c6dc46f`,
mark the head `87cad1ca` counter unmeasured, and stop calling `after 2` a survivor
count. That is smaller than the full rerun but leaves the delivered command's result
unknown; the rerun is the complete version.

## Risks

- The repaired C2 rule turns the two `FC-*` outcomes from inconclusive into killed; a
  reviewer may read that as laundering the raw failure. Mitigate by keeping both
  artifacts, naming both counter hashes, and stating the rule change in the lesson
  (the lesson already says the original failed evidence remains).
- The C2 rerun takes ~26 minutes and starts loopback stubs. Run it in a separate
  clone, `--jobs 1`, with the bind guard's protected ports unchanged; verify
  `ss -ltnpH` has no owned listeners and the scratch teardown is clean.
- The head C1 `measure.py` changes the `misclassified` cross-check; a head
  `c1-measure` may now exit 0 where the raw run exited 2. That is a new result and must
  be labeled corrected, not substituted for the raw run.
- Adding an `equivalent` status is a schema addition; it must not change the
  `GOOD` set or the existing killed/handled/correct counts.

## Verification

- Pin check: `sha256sum` head counters vs `git show c6dc46f:… | sha256sum`; the raw
  JSON's `.tool.sha256` / `.inputs.measure.sha256` must match the old blobs (already
  run: `2af03fed…`/`55b26b3b…` vs `87cad1ca…`/`a9577ed8…`).
- Rule check: truth-table `combine_arms([("killed",…),("inconclusive",…)])` at head →
  `killed`; confirm `count()` then puts both FC rows in `outcomes.after.killed`, not
  `after` residual.
- Rerun check: new `--json` output, new exit, `frozen_witness_validation.mismatches == []`,
  `counts.named.total == 15`, `inconclusive_reasons` either empty or named; compare
  every row to the raw run, not just the total.
- C1 check: head `--self-mutants` exit 0, three rows killed with a named failure label
  and `70 cases`; head `--selftest` exit 0; head `--json` output records the measure
  hash and the corrected `misclassified` result.
- Teardown: `ss -ltnpH` no seat-owned listener, scratch removed, no process carrying
  the scratch marker.

Limits: this seat ran no runtime experiment (the item is a rules comparison); no clone,
no ports, no installs. The head-rerun behavior above is derived from the code and the
raw arms, not executed here. Tameshi sources were limited to `SKILL.md` and
`corpus/README.md`; kama's `PROVINCE.md`/`SKILL.md` were not re-read for this item.
