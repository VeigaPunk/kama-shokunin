# Round 87 — verifier spot-check (non-author closure)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-05
subject: kama round 87 — lane HEAD `95ad1dbb2cfd0fee99b9f0cd7238755dbf5ff546`, base `362b0d4a241520c9bc79b204c042d9fcefbb06ea`
report: `.ufo/reports/round-87/kama.md` (fleet repo, commit `dc73e760`, author `kama-shokunin <kama@shokunin.local>`)

Verdict: status `ok` (real report, real committed work). Claims: C2 operability **verified on its frozen predicates**; C1 calibration **not verified** (honest stop). Round not admitted.

## 1. Conformance (protocol step 1)

| check | command / source | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-87/kama.md` | `kama-shokunin dc73e76069309cd0adc8e7deedf96503419597a5 round-87: kama report` | ok |
| SHONEN heading, one line per box | report `## SHONEN` | 4 boxes, all `[~]` with a pointer, no `[x]` | ok |
| required sections in order | report headings | Work performed, Landed changes, Before → after, Sources & frontier, Trend verdicts, SHONEN | ok |
| cited commits are ancestors of the branch | `git merge-base --is-ancestor <h> master` for `94e8fe7b 3ad2b9e6 c6b5cf3f fe78ca4f 24d1895d a5f0ede9 95ad1dbb` and base `362b0d4a` | all true | ok |
| lane has no round leftovers, is pushed | `jj-lane.sh state` (pure git); `git status --porcelain -uall`; `git ls-remote origin refs/heads/master` | `branch=master local=95ad1dbb… remote=95ad1dbb… ahead=0 behind=0 tracked=0 untracked=0`; status empty; remote `95ad1dbb…` | ok |
| fleet repo leftovers | `git status --porcelain` (fleet root) | only ` M .scratch/run15-state.json` (orchestrator-owned; not touched here) | ok |
| prompt carries contract | `.ufo/prompts/kama-round-87.md` §1–§6 | claim cap, frontier step, L2 floor, report contract, push scope, L0 channel present | ok (see D2) |
| dispatch digest | `.ufo/watchdog.log` (mutable; digest) | `2026-11-05T05:00:08-03:00 launch kama round=87 pgid=4168762 driver=hyaku-inline attempt=1`; `2026-11-05T05:58:46-03:00 complete kama round=87; hyaku-inline attempt=1` | recorded |
| source census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0; final line `kama ok`; warnings only (one pre-existing W01 on S481; W04 duplicate-URL-across-scopes notices, including S580 against S576/S578/S579 on the same spec host) | ok |
| census before → after | plain awk over committed `corpus/SOURCES.md` at base and tip | rows 319 → 320; tier A 304 → 305, B 11, C 4; mined 286 → 287, queued 8, rejected 25 | matches report |

Conformance defects (status-neutral, recorded in notes):

- **D1** The report lists as not re-read: `PROTOCOL.md`, `LEARNING.md`, `CORPUS.md`, `corpus/QUALITY.md`. The protocol requires a re-read at the start of every steered round.
- **D2** Wave results do not record the answering model per seat (`w1-results.json`, report §Seat answering models). Run-15 route evidence is therefore not attestable from the lane's own files.
- **D3** The `## Gate` section records no source-level rejection (see §4).

## 2. Claim re-checks

Method: plain measurements run here (`git show`, `git diff`, `grep -c`, `diff`, `awk`, `curl`) are marked **re-measured**. Lane-owned gates and selftests were **not executed**; their committed receipts were checked for revision, bytes and verdict and are marked **evidence-verified**.

### C2 — operability, capability acquisition (`round86-instruments` as gate arm 14 + fault harness)

Re-measured:

- `git show 362b0d4a:tools/pre-report-gate.py | grep -c round86-instruments` → `0`; `git show 95ad1dbb:tools/pre-report-gate.py | grep -c round86-instruments` → `20`. Base 0 → tip 20.
- `git diff --numstat 362b0d4a 95ad1dbb -- tools/pre-report-gate.py` → `116 21`.
- `git diff fe78ca4f 95ad1dbb --stat -- tools corpus SCORECARD.md` → empty. The instruments, gate and corpus did not change between the revision the gate receipt names (`fe78ca4f`) and the tip. Only `.ufo/waves/round-87/measured/`, `controls/`, plan amendment and MT02 receipts changed after it, so the arm verdict measured at `fe78ca4f` applies to the tip tree.
- `git cat-file -e 95ad1dbb:tools/round87-gate-arm-faults.py` → present.

Evidence-verified (committed receipts):

- Before, `controls/c2-gate-before.out` (rev `362b0d4a`): `PRE_REPORT round=87 arms=13 failed=4 uncommitted=0`; no `round86-instruments` line.
- After, `measured/gate-tip.out` (rev `fe78ca4f`): `PRE_REPORT_ARM round86-instruments exit=0 ok RENDERED_CELLS_SELFTEST pass=17 fail=0 | DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0 | PIN_ORIGIN_SELFTEST pass=7 fail=0`; `PRE_REPORT round=87 arms=14 failed=4 uncommitted=6`.
- Fault predicate, `c2-faults.out`: `CONTROL arm=round86-instruments ok=True`; faults 1–3 each `ok=False exit=1`; `ARM14_FAULTS faults=3 killed=3 escaped=0`.
- Arm-absent control, `w1/out/EX03FaultHarness/test-arm-absent.out`: `CONTROL_RED`; `ARM14_FAULTS faults=3 killed=0 escaped=3`.

Caveats (do not change the verdict):

- The `fe78ca4f` gate run was taken with six uncommitted receipt files (`uncommitted=6`). Its `round-clean` red is that dirty-tree artifact. No clean-tree gate run at `95ad1dbb` is committed. [INFERENCE] `round-clean` should read clean at the tip, because `git status --porcelain -uall` is empty there; this was not executed.
- The MT02 battery result `GATE_ARM_MUTANTS mutants=7 killed=7 escaped=0` (`measured/mt02-battery-integrated-gate.out`) is **not** kill evidence. Its own pristine check reads `not-ok` on the default tools copy, as the report states. Not counted.
- Harm rule. Base-ok arms still ok at tip, except `round-clean` (transient, see above). The full-gate count is `failed=4` at base and at `fe78ca4f`, but membership moved: `newest-closure` went red → ok; `round75-instruments` went from exit 2 (could not evaluate; no round-87 plan at base) to exit 1 FAIL, `APPEND_DEBT … bad_rows=19`. Its `bad_rows` was 0 in `c2-gate-after-pre-scorecard.out`, before the SCORECARD calibration edits; the cause is unexamined (routed R4). Base was not ok for that arm, so this is not a harm under the rule.

Verdict C2: **verified on frozen predicates** (arm present and ok at 14; 3/3 seeded faults killed; control red without the arm). Operability graded `improved` (capability `gate-round86-instruments` admitted; axis score held at 8).

### C1 — calibration, rendered-cell selector and live self-assessment cell

Re-measured:

- Population block, frozen base `tools/round86-rendered-cells.py` lines 16–40 vs successor `.ufo/waves/round-87/w1/out/EX01SelectorRepair/round87-rendered-cells.py` (at `95ad1dbb`) lines 19–50: `diff <(sed -n '16,40p' …) <(sed -n '19,50p' …) | grep -c '^[<>]'` → `13`. The gate-coupling rule ("each 40-hex revision R the cell attaches…") and the disposition rule ("the single token written after `verdict `…") differ from the frozen population. Non-empty. Whole-file base → successor: 90 insertions, 25 deletions, with code hunks as well as docstring.
- Calibration row at tip, `SCORECARD.md` lines 18–19: line 18 names the round-86 closure; line 19 keeps the round-85 row as history. Both `| calibration |`.

Evidence-verified:

- Before, `controls/c1-live-before.out` (rev `362b0d4a`): `RENDERED_CELLS facts=3 mismatches=2 … exit=1`. `controls/c1-probes-before.out`: `C1_PROBES probes=3 escapes=3 control=red`.
- Successor, `measured/c1-successor-tip.out`: `mismatches=0`, exit 0. `measured/c1-probes-successor-tip.out`: `escapes=0 control=red`.
- Frozen round-86 counter at tip, `measured/c1-round86-counter-tip.out`: `mismatches=1`, exit 1. Its disposition oracle still reads `rejected-harmed` (P-B unrepaired in the frozen counter).
- Gate arm `selfdesc` at tip, `measured/gate-tip.out`: `exit=1 FAIL … calibration row latest outside closure is round-85`. The arm reads every calibration row, so the live self-assessment cell is **not** made true under that arm. The claim's second half therefore fails too.

Verdict C1: **not verified** (honest stop). The successor passes its probe battery but fails the frozen R4 population rule (13 changed docstring lines, plus code), and the `selfdesc` arm is red. Calibration graded `unprovable`: not harmed (score held at 7), not verified.

## 3. Per-axis verdicts

| axis | verdict | evidence |
|---|---|---|
| operability | improved | C2 verified on frozen predicates (§2); capability row `gate-round86-instruments` at `SCORECARD.md:189`; score 8 held |
| calibration | unprovable | C1 not verified (§2); score 7 held; calibration row correction is a bookkeeping repair, not the claimed selector repair |
| freshness | unchanged | `git diff --numstat 362b0d4a 95ad1dbb -- SCORECARD.md` → `7 0`: additions only, no score row changed |
| depth | unchanged | `git diff 362b0d4a 95ad1dbb -- SKILL.md corpus/knowledge` → no change |
| coverage | unchanged | `PROVINCE.md` and `corpus/knowledge/` unchanged (diff empty) |
| adjacency | unchanged | report CN01: no sibling overlap; `cross-lane-scope.md` unchanged |

Harm check: no axis score decreased; `SCORECARD.md` had 7 insertions and 0 deletions.

## 4. Discernment spot-check (LEARNING.md)

Sample from `corpus/lessons/round-87.md` `## Gate` and its `## Claims`. Admit and reject both sampled; the `## Gate` section itself holds no reject (D3). Each source re-opened here on 2026-11-05.

| item | decision | re-opened source | agree / disagree | reason |
|---|---|---|---|---|
| S580, new row (admit) | admitted for C1 rule R1 | https://spec.commonmark.org/0.31.2/#list-items (§5.2 "List items"; fetched by curl) | agree | Quote "A list item may contain any kind of block:" (8 words) is located once, between the §5.2 heading and §5.2.1. It grounds "list item content is block content". The row's closer-rule consequence is a derivation from §5.2, not the quote; accepted as stated extension (R10). |
| S578 (re-open, admit retained) | still matches; `used-by` unchanged | https://spec.commonmark.org/0.31.2/#fenced-code-blocks (§4.5 "Fenced code blocks") | agree | Quote "The closing code fence may be preceded by up to three spaces of indentation, and may be followed only by spaces or tabs" (22 words) located once, inside §4.5. |
| S580 row quote length | ≤25 words | the S580 row in `corpus/SOURCES.md` | agree | 8 words. |
| C1 successor EX01 (reject, not admitted) | not admitted | `git show 95ad1dbb:.ufo/waves/round-87/w1/out/EX01SelectorRepair/round87-rendered-cells.py` vs `git show 362b0d4a:tools/round86-rendered-cells.py`, Population block (§2) | agree | Successor rewrites the population. Frozen R4 forbids that; the candidate's own probe battery does not check R4 (M3). Reject is correct. |
| S577 (registry row, REJECTED; supplementary, not a round-87 Gate decision) | reject: exact path returns HTTP404; flip if a revision-specific document is retrievable | `curl -sI https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/examples/server/README.md` → `HTTP/2 404` on 2026-11-05 | agree | Flip condition not met. |

Result: the source-level admit (S580) and re-open (S578) agree; the claim-level reject agrees; the supplementary registry reject agrees. The round's `## Gate` has no source-level reject, so "agree on rejects" is not established from the round's own gate decisions (D3, R7).

## 5. Trend verdicts (with evidence)

- **expansion: improved.** LEARNING's trend table lists "a capability admitted to `SCORECARD.md`" as an `improved` condition. `SCORECARD.md:189` carries `gate-round86-instruments`, demonstrated by `c2-faults.out` (`ARM14_FAULTS faults=3 killed=3 escaped=0`). The report's `unchanged` contradicts that table row (R8). S580 entered as a mined frontier source; it is not a knowledge entry.
- **quality: unchanged.** The table's observable is entries re-verified, deepened, or superseded, with `verified-at` freshness. `corpus/knowledge/`, `SKILL.md`, `PROVINCE.md` and `corpus/QUALITY.md` are unchanged (diff empty). The gate hardening and the calibration row are operability and calibration evidence (routed R8). The report's `improved` rests on those, not on the table's observable.
- **discernment: unchanged.** Admit agreed; claim-level reject agreed; no source-level reject in the round's `## Gate` (§4); no `QUALITY.md` criterion added. The table's `improved` needs agreement on admits *and* rejects from the round's gate decisions.

## 6. Routed defects (lane must fix in round 88 unless noted)

- **R1 (C1, M3).** Freeze a population-preserving rule before data, with an R4 diff arm in the probe battery. Already planned as round-88 item 1; the candidate stays outside `tools/`.
- **R2 (M4 fix does not count yet).** The `selfdesc` arm reads every calibration row, so the round-85 history row keeps it red. The M4 fix does not clear its captured-by arm; it is not shown to work until `selfdesc` is green or the arm's population is re-frozen by an L0 ruling. The open L0 question stays open; this closure does not answer it.
- **R3 (calibration cell goes stale on landing).** This closure's spot-check file, once committed, becomes the newest committed closure (`round-87-verifier-spotcheck.md`). The calibration row still names round 86. The `closure` fact in the rendered-cell counter and the `newest-closure` arm will then read mismatched on the next run. The lane must re-point the row in round 88, as it did this round.
- **R4 (operability, planned round-88 item 2).** `round75-instruments` is red at tip (`APPEND_DEBT … bad_rows=19`, was 0 before the SCORECARD calibration edits, `unaccepted=11`). Investigate and record the cause before any round claims an all-green gate.
- **R5 (operability).** MT02 battery: its pristine self-check reads `not-ok` on the default tools copy, so its 7/7 is not kill evidence. Repair the battery and re-run it on a clean tree.
- **R6 (evidence).** `measured/gate-tip.out` was produced at `fe78ca4f` with six uncommitted receipts. Commit the receipts first, or measure at a clean tip, and name the revision and clean state in the measurement.
- **R7 (discernment).** `## Gate` must record at least one source-level reject per round (or state that none was made and why). This round's Gate lists admits only.
- **R8 (trend grading).** Grade trends by LEARNING's table condition: expansion `improved` when a capability is admitted; quality `improved` only on the table's observable (entries re-verified, deepened, or superseded). Round 87 applied neither correctly (§5).
- **R9 (conformance, D1).** Re-read `PROTOCOL.md`, `LEARNING.md`, `CORPUS.md` and `corpus/QUALITY.md` at the start of each steered round, and record the re-read.
- **R10 (S580 `teaches`).** The quote supports block content in list items. The closer rule is an inference. Narrow `teaches` to what the quote grounds, or cite §4.5 (S578) for the closer rule.
- **R11 (D2).** Record the answering model per seat in `w<N>-results.json`.

## 7. Notes for the operator (not lane work)

- No SHONEN box is checkable by a non-author from this round alone. Box 2 has round 16–17 live evidence but no non-author verifier. Box 1 and box 4 rest on author assertion. This closure writes no `[x]`; promotion is operator-owned.
- Two L0 questions open in the report (`round75-instruments` red; `selfdesc` red) remain for the operator; this closure adds none.
