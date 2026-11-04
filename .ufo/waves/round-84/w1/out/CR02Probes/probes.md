# CR02Probes — round-84 w1: do-nothing controls re-run + note-vs-subject vocabulary probe

Seat: CR02Probes (critic, leaf — no dispatch). Date: 2026-11-04.
Lane tip at start: `master = eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85` (controls commit; parent `2d49bf70` = freeze).
Scratch: `S=/fast/scratch/hyaku/kama-r84/CR02Probes`, `git clone --shared` of the lane; `git rev-parse --show-toplevel` asserted equal to `$S/wt` immediately before the one local commit (`b4249836`, probe fixtures only, never pushed). Scratch removed before yield; every output pasted below is the receipt.
Frozen text treated as data: `plans/round-84-claims.md` read in full; no claim, axis, route, or receipt text edited anywhere. No tooling installed or upgraded (python3 + git only; nothing added to PATH — nothing to record under the operator authorization).

Godspeed axes (assigned): **operability + calibration**. Every move below is cheap, parallel-safe, read-only in the lane; the single new artifact class is two probe fixture files committed only inside my own scratch clone.

## Probe 1 — the three do-nothing controls re-run (all in the scratch clone, cwd = `$S/wt`)

### 1a. Gate control — `python3 tools/pre-report-gate.py --repo . --round 84 --tip master` → **EXIT=1** (wall 53s, run at clone HEAD = eb03a64b, before the probe commit)

```
PRE_REPORT_ARM selfdesc exit=1 FAIL detail: closure_ptr: calibration row latest outside closure is round-82; newest at tip is round-83
PRE_REPORT_ARM newest-closure exit=1 FAIL STALE_CALIBRATION row_names=corpus/lessons/round-82-verifier-spotcheck.md newest=corpus/lessons/round-83-verifier-spotcheck.md newest_date=2026-11-04
PRE_REPORT_ARM receipt-audit exit=0 ok RECEIPT_POINTER_AUDIT files=2 cited=296 resolved=278 expanded=4 corrected=14 unresolved=0
PRE_REPORT_ARM worktree-landing exit=0 ok WORKTREE_LANDING_CHECK paths=5 clean=5 dirty=0 missing=0 untracked=0 unreadable=0
PRE_REPORT_ARM round-scope exit=0 ok ROUND_SCOPE_V2 round=84 cases=6 findings=0
PRE_REPORT_ARM round-clean exit=0 ok files=0
PRE_REPORT_ARM round74-v2 exit=0 ok SELFDESC_CANON_V2 canon_round=83 canon_rows=49 demonstrated=0 total=49 invisible=0 | PROVINCE_HOST_DRIFT_V2 blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0 edited=0
PRE_REPORT_ARM round75-instruments exit=1 FAIL INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0 | SURVIVORS2 mutants=5 killed=5 escaped=0 | APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=22 pending=0 unaccepted=1 bad_rows=10 bad_declarations=0 out_of_population=0 | APPEND_DEBT_FINDING unknown-event late line 105: 0d7c7c3ea7d120c4796e9e5119d48038f85fde20 SCORE
PRE_REPORT_ARM round77-instruments exit=0 ok … (three selftests pass=7/7/4 fail=0)
PRE_REPORT_ARM round78-instruments exit=0 ok … (selftests pass=8/7/4 fail=0)
PRE_REPORT_ARM round81-instruments exit=0 ok APPEND_DEBT_SELFTEST pass=29 fail=0
PRE_REPORT_ARM round82-instruments exit=0 ok … (SELFRECORD_R81 pass=23, LATE_DELTA pass=13, fail=0)
PRE_REPORT round=84 arms=12 failed=3 uncommitted=0
EXIT=1
```

Verdict: **control holds** — cannot reach the claim target (`arms=13 failed=0 uncommitted=0`, exit 0): arms=12≠13, failed=3≠0, exit 1.
Honest delta vs the frozen receipt (`ctl-gate.out`, taken at `2d49bf70`): receipt shows `arms=12 failed=5 uncommitted=5`; my re-run shows `failed=3 uncommitted=0` because the receipt files were untracked at the freeze tree (round-scope/round-clean flagged them `??`) and are committed at eb03a64b. The three claim-relevant FAIL arms (selfdesc closure-pointer, newest-closure STALE_CALIBRATION, round75-instruments carrying `bad_rows=10` + the `unknown-event` for restored `0d7c7c3e`) reproduce exactly. No other arm changed verdict.

### 1b. Selfrecord control — `python3 tools/round84-selfrecord-round83.py --repo .` → **EXIT=2**

```
python3: can't open file '/fast/scratch/hyaku/kama-r84/CR02Probes/wt/tools/round84-selfrecord-round83.py': [Errno 2] No such file or directory
EXIT=2
```

Verdict: **control holds**, byte-equivalent to the frozen receipt: the round-84 counter does not exist, no-work cannot print `SELFRECORD_R83 claims=8 mismatches=0 corrected=6 unbacked=0`.

### 1c. Pin-recheck control — `python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv --rows registry/pin-recheck-rows.tsv` → **EXIT=0**

```
PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0 ungraded=1 bad=0
EXIT=0
```

Verdict: **control holds**, byte-identical to the frozen receipt: `graded=4 ungraded=1` fails the claim target `graded=5 ungraded=0 bad=0`.

## Probe 2 — vocabulary probe: note deletion round GREATER than the event commit's subject round, current (pre-fix) tool

Question asked by the seat: does the current tool accept such a row (`bad_rows=0` contribution), i.e. is the round-84 binding's direction constrained by anything that already exists?

### Design

Ground truth from `tools/round81-append-debt.py` at the lane tip (read, plus confirmed by run): the late-row grader parses the note with `NOTE_RE = round-([0-9]+)\s+accepts\s+round-([0-9]+)\b` and its only round check is note-internal: `accepting <= deletion → bad("same-round")`. The event commit's subject is parsed nowhere in the pre-fix grader.

Fixture basis: the committed fixture `.ufo/waves/round-84/fixtures/late-wrong-subject.tsv` is the register with (i) line 2's note mis-noted `round-81 accepts round-79` → `round-81 accepts round-78` (event `1cda04569f30005adc89f98aa02909d6659fdf99`, whose subject is `round-79: disclose the register-counter red and name the R78V6 plan paths without the measured/ prefix` — the LESS direction, 78 < 79) and (ii) the ten restored `0d7c7c3e` rows dropped (124 → 114 lines; verified by diff).

Probe fixtures (committed locally in my scratch clone only, commit `b4249836` "round-84 CR02Probes vocabulary probe fixtures (scratch clone only, never pushed)"):

- `.ufo/waves/round-84/fixtures/probe-note-greater-subject.tsv` — the committed fixture with exactly two notes changed, both on the round-79 event `1cda04569`, different digests:
  - digest `86188047…` (line 2): `round-84 accepts round-81 "…"` — **Row B, clean greater direction**: deletion 81 > subject 79, accepting 84 > 81 (passes the internal same-round rule; only the subject is violated).
  - digest `88d34850…` (line 3): `round-81 accepts round-85 "…"` — **Row A, the seat's literal example**: deletion 85 > subject 79, but accepting 81 ≤ 85.
- `.ufo/waves/round-84/fixtures/probe-two-row.tsv` — header + only rows A and B.

`load_late` requires the `--late` file committed and worktree-identical at HEAD, hence the local commit; row introductions resolve to `b4249836`, a strict descendant of the event commit, so no `unbound-register`/`not-descendant` noise.

### Runs (`python3 tools/round81-append-debt.py --repo . --round 84 --late <fixture>`)

Baseline (committed fixture) — reproduces the frozen `red-debt-fixture.out` byte-identically, EXIT=1:
```
APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=22 pending=0 unaccepted=1 bad_rows=0 bad_declarations=0 out_of_population=0
APPEND_DEBT_FINDING count-short 96e28374593be13833aebeb70150877f58f4aadc SCORECARD.md b2d76c4c…: missing 1
```

Probe-114 — EXIT=1:
```
APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=22 pending=0 unaccepted=2 bad_rows=1 bad_declarations=0 out_of_population=0
APPEND_DEBT_FINDING same-round late line 3: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 88d34850ef76373a0ed4f47b67be1013ad766a4d020999ab185004a150495a98: accepting round 81 is not after deletion round 85
APPEND_DEBT_FINDING count-short 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 88d34850…: missing 1
APPEND_DEBT_FINDING count-short 96e28374593be13833aebeb70150877f58f4aadc SCORECARD.md b2d76c4c…: missing 1
```

Probe-2row — EXIT=1 (same grades, plus the expected noise of 22 uncovered events): `APPEND_DEBT … accepted=53 late=1 pending=0 unaccepted=23 bad_rows=1 …` with the identical `same-round late line 3 … accepting round 81 is not after deletion round 85` finding.

### Answers (exact summary lines above)

1. **Clean greater-direction row (Row B, `round-84 accepts round-81` over a round-79 event): ACCEPTED by the current tool.** No finding; `accepted=53 late=22` identical to baseline; the only deltas vs baseline are Row A's `same-round` finding and the count-short that its refusal uncovers. So yes — the pre-fix hole is **symmetric**: any note deletion round ≠ the event subject's round is accepted, provided the note is internally ordered (accepting > deletion). Nothing pre-existing constrains the subject direction in either direction.
2. **The seat's literal example (Row A, `round-81 accepts round-85`) is NOT accepted — but for the wrong reason**: refused by the pre-existing note-internal `same-round` rule, not by anything touching the subject. It therefore cannot calibrate the round-84 binding; a valid greater-direction probe row must satisfy accepting > deletion > subject (e.g. `round-84 accepts round-81` over a round-79 event), which is Row B.
3. **Shape of the round-84 binding:** C1's planned rule is pure equality (note deletion round == subject round, class `note-wrong-deletion-round`). The probe supports equality as the correct shape: there is no pre-existing asymmetric rule to compose with, and equality closes both directions at once.

### Mutation-guard consequence (for the wave's mutation-tester)

Grounded deduction from the grading semantics above: a direction-flipping mutant of the new binding — `deletion < subject` (or `≤`) instead of `≠` — still fires on the committed red-before fixture (78 < 79) but **accepts** Row B (81 > 79). The committed fixture alone therefore cannot kill `<`/`≤`-only mutants; the battery should add a greater-direction row (exactly Row B: digest `86188047…`, note `round-84 accepts round-81 …`, event `1cda04569…` subject round-79). Peer MT01Binding notified.

Frontier note (not a claim defect): the accepting round itself is unconstrained pre-fix — Row B says `round-84 accepts` and a `round-999 accepts` would equally pass. The planned equality binding does not address accepting-vs-current-round either; out of scope for round-84's frozen predicate.

## Command ledger (true exit codes)

| # | Command (cwd `$S/wt` unless noted) | Exit |
|---|---|---|
| 1 | `git clone --shared <lane> $S/wt`; `git rev-parse --show-toplevel` | 0 (asserted `$S/wt`) |
| 2 | `python3 tools/pre-report-gate.py --repo . --round 84 --tip master` | 1 |
| 3 | `python3 tools/round84-selfrecord-round83.py --repo .` | 2 |
| 4 | `python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv --rows registry/pin-recheck-rows.tsv` | 0 |
| 5 | `diff registry/append-only-late.tsv .ufo/waves/round-84/fixtures/late-wrong-subject.tsv` | 1 (expected diff) |
| 6 | fixture copy + two note edits + `git add`/`git commit` (after toplevel assert) | 0 (commit `b4249836`) |
| 7 | baseline `--late .ufo/waves/round-84/fixtures/late-wrong-subject.tsv` | 1 |
| 8 | probe-114 `--late .ufo/waves/round-84/fixtures/probe-note-greater-subject.tsv` | 1 |
| 9 | probe-2row `--late .ufo/waves/round-84/fixtures/probe-two-row.tsv` | 1 |

No probe exceeded the ten-minute box (longest single run: gate, 53s). No lane file outside my out dir was created or modified; the only writes in the lane checkout are this file, `w1/out/CR02Probes/probes.md` (same content), and nothing else. Scratch `/fast/scratch/hyaku/kama-r84/CR02Probes` removed before yield.
