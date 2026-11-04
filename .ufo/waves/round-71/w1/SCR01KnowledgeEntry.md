# SCR01KnowledgeEntry — C1 knowledge entry (`pre-report-gate`)

Seat: scribe, calibration axis, kama r71 w1. Leaf member: no subagents, no swarm.
Base: freeze tip `b43e71a8`. The lane tip moved during the work: L1's integration commit
`e2b860c8` landed the three instruments, this entry, the provinces and the wave evidence,
and the last measurements below are at that tip. The tool was absent at first read (21:37)
and landed during the work (21:39, later re-issued with a re-entry guard `07cfc04f…`);
every tool sentence below was verified by running the bytes on disk at that moment, never
read from the spec.

## Behavior

Wrote ONE new corpus entry, `corpus/knowledge/pre-report-gate.md` (84 file lines; body
80 lines, title to EOF — the cap). Provenance trio:

- `source:` S542 (the row SCR02 appended: Git git-status, §Porcelain Format Version 1,
  retained sha256 `22ff28ff…0180`) + `plans/round-71-claims.md` §C1 + the gate's own
  bytes (`sha256 07cfc04f…`, the guard revision; the entry first named `d0957e0b…`, the
  pre-guard bytes I probed — see Touched surfaces).
- `verified-at: b43e71a8` (freeze base) and `e2b860c8` (the integration commit that
  landed the tool, the entry and the row), with the qualifier that the gate was read and
  run from the round-71 worktree, where `git status --porcelain -uall --
  tools/pre-report-gate.py` printed `??` before `e2b860c8`.
- `recheck:` `python3 tools/pre-report-gate.py --selftest` →
  `PRE_REPORT_SELFTEST pass=6 fail=0` (exit 0); S542 recheck `on-release`.

Body sections: why one verdict exists (round-70 closure defect 1), the five arms with the
failure class each detects, the CLI/output contract, a six-row decision table, six limits
bullets. I did not edit SCORECARD.md, LOG.md, SKILL.md, PROVINCE.md, SOURCES.md or any lesson.

## Grounding: exact commands and outputs used

1. Selftest (twice — once unpiped, once captured; identical):
   `python3 tools/pre-report-gate.py --selftest --work <S>/selftest`
   → six PASS blocks (green, wave-uncommitted, stale-newest-closure,
   missing-declared-path, dirty-declared-path, crlf-declared-path), final line
   `PRE_REPORT_SELFTEST pass=6 fail=0`, exit 0.
2. Freeze counter, at the lane:
   `python3 tools/pre-report-gate.py --repo . --round 70 --tip master; echo EXIT=$?`
   ```
   PRE_REPORT_ARM selfdesc exit=1 FAIL detail: closure_ptr: calibration row latest outside closure is round-69; newest at tip is round-70
   PRE_REPORT_ARM newest-closure exit=1 FAIL STALE_CALIBRATION row_names=corpus/lessons/round-69-verifier-spotcheck.md newest=corpus/lessons/round-70-verifier-spotcheck.md newest_date=2026-11-03
   PRE_REPORT_ARM receipt-audit exit=0 ok RECEIPT_POINTER_AUDIT files=2 cited=157 resolved=140 expanded=4 corrected=13 unresolved=0
   PRE_REPORT_ARM worktree-landing exit=1 FAIL WORKTREE_LANDING_CHECK paths=5 clean=2 dirty=3 missing=0 untracked=0 unreadable=0 | DIRTY SCORECARD.md
   PRE_REPORT_ARM round-clean exit=0 ok files=0
   PRE_REPORT round=70 arms=5 failed=3 uncommitted=0
   EXIT=1
   ```
3. Live round-71 run: `… --round 71 --tip master` →
   `PRE_REPORT round=71 arms=5 failed=4 uncommitted=51`, exit 1
   (round-clean `FAIL files=51 first=?? .ufo/waves/round-71/w1-spec.json`).
4. The four instruments run individually at `b43e71a8` (so the entry describes what each
   arm actually grades): reconciler `mismatches=1 met=False` exit 1 (closure_ptr: row
   names round-69, newest is round-70); newest-closure `STALE_CALIBRATION` exit 1;
   receipt audit `unresolved=0` exit 0; WLC `paths=5 clean=5` exit 0.
5. Do-nothing control re-run (twice, identical):
   `python3 .ufo/waves/round-71/controls/pre-report-shortcut.py --lane . --rev af6eb6c2 --scratch <S>/shortcut --keep`
   → `SHORTCUT_CONTROL arms=4 failed=0 uncommitted=26`, exit 0; the fixture's
   `git -C <fixture> status --porcelain -uall -- .ufo/waves/round-70` prints 26 records
   (26 files; 7 modified + 6 untracked files + 13 files in `MT01Mutants/logs/`).
   The committed receipt `measured/before/git-status.out` carries 14 entries for the
   round-70 subset (15 lines including an unrelated `?? .ufo/waves/round-71/`).
6. S542 quote check: the retained bytes at
   `.ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html` (sha256 matches the row)
   contain, after tag stripping, "…but is guaranteed not to change in a
   backwards-incompatible way between Git versions or based on user configuration. This
   makes it ideal for parsing by scripts." Host `git version 2.56.0`.

## Findings

### F1 (blocker for C1's after-target) — the gate re-enters itself when cited as the calibration RUN fact

`SCORECARD.md` (worktree, uncommitted, not mine) adds this RUN fact to the calibration
row: `python3 tools/pre-report-gate.py --repo . --round 71 --tip master` →
`PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` `(exit 0)`. Feeding the row through
the counter's own parser (`round41-scorecard-reconcile.py`, `RUN_RE`) yields exactly six
run facts, this one included with `(exit 0)`.

That closes a loop across two committed instruments: gate arm 1 runs
`tools/round42-selfdesc-reconcile.py`; the reconciler calls
`round41-scorecard-reconcile.py::evaluate(R, tip)`, whose RUN facts execute with `bash -c`
in a tip checkout (`git clone --shared` + `checkout --detach`) that explicitly mirrors
`refs/heads/master` at the tip ("Point the branch at the measured tip"); that checkout's
SCORECARD carries the same gate run fact, so `bash -c "python3 tools/pre-report-gate.py
--repo . --round 71 --tip master"` starts the gate again with `--repo .` = the checkout.

Probe (bounded, fixture under S, master pointing at the probe commit): the worktree
SCORECARD.md was committed on top of `b43e71a8`, `tools/pre-report-gate.py` was replaced
by a depth-logging wrapper around the real gate with a cap at depth 3. Result:

```
entry depth=0
entry depth=1
entry depth=2
entry depth=3
```
(and the outer run's arms show the enclosed gate's own verdict shape). Receipt:
`.ufo/waves/round-71/w1/SCR01KnowledgeEntry/run-fact-recursion-probe.out`.
The probe's other red arms are fixture artifacts, not lane findings: the fixture took
PROVINCE.md from `b43e71a8` while the copied SCORECARD's canon names the round-71 tool
(the live worktree PROVINCE.md already names `tools/round71-province-host-claims.py`
twice), and its receipt pointers point at receipts the fixture repo does not hold.

EX01 then added a re-entry guard to the tool (`PRE_REPORT_GATE_DEPTH` exported to every
child; a scored re-entry at depth>=1 prints `PRE_REPORT_RECURSION depth=<d> refused` and
exits 3). Verified directly: `PRE_REPORT_GATE_DEPTH=1 python3 tools/pre-report-gate.py
--repo . --round 70 --tip master` → that refusal line, `EXIT=3`
(`recursion-guard-direct.out`); `--selftest` still returns `pass=6 fail=0`.

The guard bounds the chain but does not make the target reachable — and that is now
measured at a committed tip, not inferred. L1's integration commit `e2b860c8` landed the
tool, this entry and the calibration row, whose RUN fact is
`run \`python3 tools/pre-report-gate.py --repo . --round 71 --tip master\` → \`PRE_REPORT
round=71 arms=5 failed=0 uncommitted=0\` (exit 0)`. The frozen counter at that tip:
`PRE_REPORT_ARM selfdesc exit=1 FAIL detail: r41 calibration run \`python3
tools/pre-report-gate.py --repo . --round 71 --tip master\` exit 3 != 0`, verdict
`PRE_REPORT round=70 arms=5 failed=3 uncommitted=0`, exit 1 (`gate-round70.out`; header
names the tool sha and the measurement instant). So the frozen after-target
`PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` cannot be printed while that row cites
the scored gate: arm 1 is red by construction. The fix is L1's — cite
`python3 tools/pre-report-gate.py --selftest` → `PRE_REPORT_SELFTEST pass=6 fail=0` (exit 0)
in that run fact, or drop it. I edited neither SCORECARD.md nor the tool.
(One artifact to note: the fixture chain I built at 21:49 copied an intermediate SCORECARD
that lacked the fact, which is why that fixture ran in 5 s with no exit-3 detail; the live
HEAD run above is the evidence, not the fixture.)

Current worktree state (repair in flight, uncommitted, not mine): the calibration row no
longer executes the scored gate. Feeding that row through r41's own parser (`axes_table` +
`RUN_RE`) returns five RUN facts, none of them the gate, and the gate is cited as the path
`.ufo/waves/round-71/measured/after/pre-report-at-tip.out` with its expected verdict text.
As a PATH fact that receipt must exist at the tip, so SCORECARD.md and the receipt land
together — otherwise arm 1 fails as `dead path` instead of `exit 3`.

### F2 (resolved at e2b860c8) — the coverage count moved 39 → 40 with the entry

The entry makes the coverage row's pinned glob print 40, and `git show
e2b860c8:SCORECARD.md` declares `→ `40`` in that cell, so row and count landed together.
At the fixture built before that commit the cell still said 39 and `run_fact` reported
`no stdout line == '40' (exit 0)` for the glob — the "count that grows during the round"
class the round-70 lesson records. No action remains unless a later count moves again.

### F3 (disagreement, recorded not edited) — `corpus/lessons/round-70.md` says `PRE_REPORT` prints `tip=<rev>`

`corpus/lessons/round-70.md` §L1 corrections item 1 says the round-71 gate "records its
own tip in every receipt line (`PRE_REPORT` prints `tip=<rev>`)". The frozen predicate and
the landed tool print `PRE_REPORT round=<N> arms=5 failed=<f> uncommitted=<u>` with no tip
field (both live runs above). The frozen text governs; the lesson sentence is a prose
claim that predates the tool and does not match it. I have not edited the lesson; the
entry states the actual contract and notes that the measured revision is the `--tip`
argument.

### F4 (observation) — the gate is red on the live worktree for two independent reasons

Arm 4 reports `DIRTY SCORECARD.md` (clean=4 dirty=1 at `e2b860c8`; it was clean=2 dirty=3
while two more self-record paths were still uncommitted) because in-flight lane edits to
the five declared self-record paths differ from HEAD. That is correct behavior and not a
defect, but it means the report-tip run must happen after everything is committed — and
that a sibling's uncommitted edit to any of the five paths reddens the gate for everyone
until it lands.

## Touched surfaces

- `corpus/knowledge/pre-report-gate.md` — new (the deliverable). L1 committed my first
  revision at `e2b860c8`; the current worktree copy is a modification of that blob (tool
  sha re-pin, observed runs at the integration tip, recursion bullet with the guard). It is
  UNCOMMITTED — L1 must commit it, or the entry describes the pre-guard bytes while the
  tree carries the guard. Same for the re-measured receipts at that tip
  (`gate-round70.out`, `gate-round71.out`, `selftest.out`) and the new
  `recursion-guard-direct.out`; the committed tool blob itself is unchanged at
  `07cfc04f…`.
- `.ufo/waves/round-71/w1/SCR01KnowledgeEntry/{selftest,gate-round70,gate-round71,shortcut-rerun,recursion-guard-direct,run-fact-recursion-probe}.out` — receipts cited by the entry.
- Scratch `/fast/scratch/hyaku/kama-r71/SCR01KnowledgeEntry/` — created, receipts copied
  out, tree deleted on exit (fixtures were `git clone --shared`, no lane mutation).
- No tool installs or upgrades were needed (nothing to record). No pacman.

## Out of scope / routed to L1

- F1 (repair in flight): the worktree calibration row now cites the after-receipt instead of
  executing the scored gate; produce `.ufo/waves/round-71/measured/after/pre-report-at-tip.out`
  and land it with SCORECARD.md, or arm 1 falls back to `dead path`. Landing the pre-repair
  row would restore the unreachability measured at `e2b860c8`.
- Commit the guard-era entry revision described under Touched surfaces.
- `corpus/README.md`'s coverage map has no row for the new entry; it is a curated index,
  not an instrument surface, so I left it to L1 if the lane wants the index complete.
- Registry rows, capability rows and the caps census counts (`mined` grows by S542,
  `queued`/`rejected` unchanged) are L1's, per the wave plan; the tip already carries the
  re-derived coverage count `40`.

## Not verified

- The recursion's unbounded form: I capped the depth probe at 3 on the pre-guard bytes; the
  no-base-case claim is that re-entry proof plus the code path, and the guard now makes the
  unbounded form unreachable in any case.
- The live-worktree numbers are dated observations of a moving tree (siblings write while
  I read): `uncommitted=19`, `unresolved=3` and `dirty=1` are that instant's state, not a
  claim about the report tip.
- The entry's admission and the census validator run over the new file — SCR02 owns the
  registry; E11 only resolves `used-by` paths, and `corpus/knowledge/pre-report-gate.md`
  exists at the exact path S542 names.
