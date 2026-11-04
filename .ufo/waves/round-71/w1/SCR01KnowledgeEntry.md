# SCR01KnowledgeEntry — C1 knowledge entry (`pre-report-gate`)

Seat: scribe, calibration axis, kama r71 w1. Leaf member: no subagents, no swarm.
Base: lane tip `b43e71a8` (freeze commit; still HEAD at every read). Tool absent at first
read (21:37), landed during the work (21:39); every tool sentence below was verified by
running the landed bytes, not read from the spec.

## Behavior

Wrote ONE new corpus entry, `corpus/knowledge/pre-report-gate.md` (83 file lines; body
79 lines, title to EOF). Provenance trio:

- `source:` S542 (the row SCR02 appended: Git git-status, §Porcelain Format Version 1,
  retained sha256 `22ff28ff…0180`) + `plans/round-71-claims.md` §C1 + the gate's own
  bytes (`sha256 d0957e0bc3f7f393ddd157c8f644d217aaa3e40d99a2d905f93d546163dd9bfb`).
- `verified-at: b43e71a8` with the qualifier that the tool was read/run from the
  round-71 worktree, where `git status --porcelain -uall -- tools/pre-report-gate.py`
  prints `??` (absent from `b43e71a8`).
- `recheck:` `python3 tools/pre-report-gate.py --selftest` →
  `PRE_REPORT_SELFTEST pass=6 fail=0` (exit 0); S542 recheck `on-release`.

Body sections: why one verdict exists (round-70 closure defect 1), the five arms as a
table with the failure class each detects, the CLI/output contract
(`PRE_REPORT_ARM …` + `PRE_REPORT round= arms= failed= uncommitted=`), a six-row
decision table (shape → meaning → next action), and six limits bullets.

I did not edit SCORECARD.md, LOG.md, SKILL.md, PROVINCE.md, SOURCES.md or any lesson.

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

That closes a loop across two committed instruments:
- gate arm 1 runs `tools/round42-selfdesc-reconcile.py --repo R --tip master`;
- the reconciler calls `round41-scorecard-reconcile.py::evaluate(R, tip)`, whose RUN
  facts execute with `bash -c` in a tip checkout (`git clone --shared` + `checkout
  --detach`) and which explicitly mirrors `refs/heads/master` at the tip
  (`round41-scorecard-reconcile.py`, "Point the branch at the measured tip");
- the checkout's SCORECARD therefore carries the same gate run fact, so `bash -c
  "python3 tools/pre-report-gate.py --repo . --round 71 --tip master"` starts the gate
  again, with `--repo .` = the checkout.

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

Without a base case the regress has no green leaf, so arm 1 can never be green at a tip
whose calibration row carries that run fact: the frozen after-target
`PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` is unreachable, and a real run would
nest until the 300 s per-run-fact / 600 s per-arm timeouts. Options (L1's call, not mine):
keep the scored run out of the RUN-fact cell (e.g. cite `--selftest` → `PRE_REPORT_SELFTEST
pass=6 fail=0`), or give the gate a base case (an explicit no-recursion flag/marker). I
did not edit SCORECARD.md or the tool.

### F2 (landing action) — the knowledge count run fact goes 39 → 40 in the same landing

Landing `corpus/knowledge/pre-report-gate.md` makes the coverage row's pinned command
print a new number:
`python3 -c "import glob;print(len([f for f in glob.glob('corpus/knowledge/*.md') if
'engine-sides' not in f and 'processes' not in f]))"` → `40` (worktree, after the write;
39 before). The coverage row declares `→ 39`, and `run_fact` requires a stdout line
exactly equal to the declared token, so without re-deriving that cell in the same landing
the reconciler gets `run_bad=1` and the gate's arm 1 is red at the report tip — the same
"count that grows during the round" class the round-70 lesson records. The claims table's
"39 or 40 (one new entry only if admitted)" is L1's admission call; if admitted, the row
and this count move together.

### F3 (disagreement, recorded not edited) — `corpus/lessons/round-70.md` says `PRE_REPORT` prints `tip=<rev>`

`corpus/lessons/round-70.md` §L1 corrections item 1 says the round-71 gate "records its
own tip in every receipt line (`PRE_REPORT` prints `tip=<rev>`)". The frozen predicate and
the landed tool print `PRE_REPORT round=<N> arms=5 failed=<f> uncommitted=<u>` with no tip
field (both live runs above). The frozen text governs; the lesson sentence is a prose
claim that predates the tool and does not match it. I have not edited the lesson; the
entry states the actual contract and notes that the measured revision is the `--tip`
argument.

### F4 (observation) — the gate is red on the live worktree for two independent reasons

Arm 4 reports `DIRTY SCORECARD.md` (clean=2 dirty=3) because in-flight lane edits to the
five declared self-record paths differ from HEAD. That is correct behavior and not a
defect, but it means the report-tip run must happen after everything is committed — and
that a sibling's uncommitted edit to any of the five paths reddens the gate for everyone
until it lands.

## Touched surfaces

- `corpus/knowledge/pre-report-gate.md` — new (the deliverable).
- `.ufo/waves/round-71/w1/SCR01KnowledgeEntry/{selftest,gate-round70,gate-round71,shortcut-rerun,run-fact-recursion-probe}.out` — receipts cited by the entry.
- Scratch `/fast/scratch/hyaku/kama-r71/SCR01KnowledgeEntry/` — created, receipts copied
  out, tree deleted on exit (fixtures were `git clone --shared`, no lane mutation).
- No tool installs or upgrades were needed (nothing to record). No pacman.

## Out of scope / routed to L1

- Re-derive the coverage row count to `40` (F2) and decide the calibration RUN-fact
  question (F1).
- `corpus/README.md`'s coverage map has no row for the new entry; it is a curated index,
  not an instrument surface, so I left it to L1 if the lane wants the index complete.
- Registry rows (SKILL 79 → 82), capability rows (15 → 17) and the caps census counts
  (`mined` grows by S542, `queued`/`rejected` unchanged) are L1's, per the wave plan.

## Not verified

- The recursion's unbounded form (I capped the probe at depth 3; the no-base-case claim
  is the code path plus that re-entry proof, not an unbounded run).
- Any post-landing state: the tool, the SCORECARD edit and the SOURCES row were all
  uncommitted when read, so every "at the report tip" statement above is a prediction
  labelled as such where it appears.
- The entry's admission, and the census validator run over the new file — SCR02 owns the
  registry; E11 only resolves `used-by` paths, and `corpus/knowledge/pre-report-gate.md`
  now exists at the exact path S542 names.
