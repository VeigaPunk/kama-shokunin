# EX02GateArms — round-86 pre-report gate, arm verdicts

Seat: EX02GateArms (kama r86 w2, falsify). Judged on: operability. Read-only; nothing fixed.
Report path note: the seat spec names `.ufo/waves/round-86/w2/EX02GateArms.md`; the contract restricts
writes to this out dir, so the report is filed here instead.

## Revisions measured
- Dispatch tip / `master` (verified `rev-parse master` = `merge-base --is-ancestor` true): `67eddac89f44e768b670301ea0feff06e766f32d`
- Frozen base: `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`
- Fleet working tree at measurement time was live (w1/w2 in flight): 14 entries at start, `uncommitted=382` then `395` on re-run. Those are NOT committed-revision facts.

## Scored gate (as assigned)
Command (live fleet root, `--tip` default = master):
`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/pre-report-gate.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --round 86`
(TMPDIR=/fast/scratch/hyaku/kama-r86/EX02GateArms/tmp). Re-run with `--tip master` gave the same shape.

- Service wrapper reported "exit 0"; that was the wrapper's `echo`, NOT the gate. True exit (synchronous re-run, `rc=$?`): **1**.
- PRE_REPORT line (live tree, re-run): `PRE_REPORT round=86 arms=13 failed=6 uncommitted=395` (first run: `failed=6 uncommitted=382`).
- Red arms on the live tree: selfdesc, worktree-landing, round-scope, round-clean, round75-instruments, round81-instruments.
  - selfdesc: `banner: head lacks 'Latest measured round: 85'`
  - worktree-landing: `WORKTREE_LANDING_CHECK paths=5 clean=3 dirty=2 ... | DIRTY SCORECARD.md`
  - round-scope: `ROUND_SCOPE_V2 round=86 cases=6 findings=384 | ROUND_SCOPE_V2_FINDING stray .ufo/waves/round-86/measured/after/c1.err status=??`
  - round-clean: `files=382 first=?? .ufo/waves/round-86/measured/after/c1.err`
  - round75-instruments: `APPEND_DEBT_FINDING count-short ... SCORECARD.md ...` (14 such findings; see below)
  - round81-instruments: `round81-append-debt.py exit=0 FAIL missing valid final selftest summary: APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`

### Committed-revision verdict (the number that counts)
Clean fixture = `git clone --no-hardlinks` of the fleet repo, detached at `67eddac8`, `rev-parse --show-toplevel` asserted equal to the fixture path before use.
`python3 <fixture>/tools/pre-report-gate.py --repo <fixture> --round 86 --tip 67eddac89f44e768b670301ea0feff06e766f32d`
- **True exit 1.** `PRE_REPORT round=86 arms=13 failed=3 uncommitted=0`, stderr 0 bytes.
- Red arms (3):
  1. `selfdesc` — `banner: head lacks 'Latest measured round: 85'`. The reconciler computes `maxn = max(rounds)` = 85, while the committed head (SCORECARD.md line 6) says `Latest measured round: 86`.
  2. `round75-instruments` — exit 1: `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0 | SURVIVORS2 mutants=5 killed=5 escaped=0 | APPEND_DEBT round=86 base=3ff23da3f291 events=80 accepted=53 late=23 pending=1 unaccepted=4 bad_rows=0 bad_declarations=0 out_of_population=0 | APPEND_DEBT_FINDING count-short 3e93febb0f40… SCORECARD.md 440e6bf2a9…` (the counter prints 14 `count-short` findings on SCORECARD.md, each `missing 1`).
  3. `round81-instruments` — exit 1: `round81-append-debt.py exit=0 FAIL missing valid final selftest summary: APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`.
- Green: newest-closure, receipt-audit, worktree-landing, round-scope (`ROUND_SCOPE_V2 round=86 cases=6 findings=0`), round-clean (`files=0`), round74-v2, round77, round78, round82, round83.

### Frozen base comparison (3ff23da, same gate, `--tip 3ff23da…`)
`PRE_REPORT round=86 arms=13 failed=4 uncommitted=0`, exit 1. Reds: selfdesc (`closure_ptr: calibration row latest outside closure is round-84; newest at tip is round-85`), newest-closure (`STALE_CALIBRATION row_names=…round-84…`), round-scope (`label plans/round-86-claims.md … status=absent`), round75-instruments (exit 2, `could-not-evaluate: no frozen plan at 3ff23da…`).
- **round81-instruments was GREEN at base** (`APPEND_DEBT_SELFTEST pass=34 fail=0`). It is RED at the tip. That arm regression is introduced by the C2 commit.

## Finding 1 (new red, caused by the C2 commit) — arm 11 rejects the summary C2 changed
- `git diff 3ff23da 67eddac -- tools/round81-append-debt.py` (saved as `c2-debt.diff`): 10 insertions, 2 deletions. It adds `EXPECTED_ARMS = 34`, prints `APPEND_DEBT_SELFTEST_ARMS …` and changes the final line from `APPEND_DEBT_SELFTEST pass=N fail=N` to `APPEND_DEBT_SELFTEST pass=N fail=N arms=N`.
- Gate arm 11 (`_round81_instruments`, `pre-report-gate.py` ~L517) requires `re.fullmatch(rf"{prefix} pass=[0-9]+ fail=0", last_line)` with prefix `APPEND_DEBT_SELFTEST`. The trailing ` arms=34` makes it fail. The gate source was not updated by C2.
- Direct run at tip: `round81-append-debt.py --selftest` → exit 0, stderr 0 bytes, output `APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0` / `APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`. The instrument is green; the gate's parser is stale.
- Consequence for the C2 claim: "production grading behaviour is unchanged" holds for the counter's grading code, but the frozen gate arm that composes this selftest is now red, so the round-86 C2 change harms operability (a gate arm that was green at base is red at the committed tip). This is an operator-visible gate regression.

## Finding 2 (round-75 arm) — not caused by C2
- `round81-append-debt.py --repo <fixture> --round 86` at tip exits 1 with the 14 `count-short` findings above (SCORECARD.md append rows missing the expected count). C2's diff does not touch that path. At base the same arm exits 2 (no frozen plan at base), so there is no clean base comparison for its counter lines (`base-debt-counter.out`).

## Finding 3 — the round-86 instruments are NOT wired into any gate arm
- `grep -n round86 tools/pre-report-gate.py` → **zero matches**.
- `ARM_ORDER` = 5 `ARM_SPECS` (selfdesc, newest-closure, receipt-audit, worktree-landing, round-scope) + `round-clean` + `round74-v2`, `round75-instruments`, `round77-instruments`, `round78-instruments`, `round81-instruments`, `round82-instruments`, `round83-instruments` = 13.
- **Answer to the composition question: no.** Arm 10 `round78-instruments` runs exactly three selftests (`round78-selfrecord-round77.py` / `SELFRECORD_R77_SELFTEST`, `round78-append-registers.py` / `APPEND_REGISTERS_SELFTEST`, `round78-live-reconcile.py` / `LIVE_RECONCILE_SELFTEST`; `ROUND78_MODULES`, gate ~L351). None of `round86-rendered-cells.py`, `round86-mutant-owners.py`, `round86-pin-origin.py` is composed. Those three files exist in the committed tree at 67eddac8 (`git ls-tree`), so the gate would not catch their absence or red status.
- Arm 8 composes `round81-append-debt.py` (counter) and arm 11 its selftest, so the C2 target file is composed, but via the parser that now fails.

## Other observations
- selfdesc red (committed tip): the reconciler's `maxn` (=85) lags the head's `Latest measured round: 86`. This is a banner/rounds-derivation mismatch in the round-86 head, not a gate-code change; it is the calibration-cell territory of C1.
- Live-tree reds (worktree-landing DIRTY SCORECARD.md; round-scope stray `.ufo/waves/round-86/measured/after/c1.err`; round-clean 382/395 files) are the in-flight wave's own uncommitted work. They go to 0 at the committed tip (`uncommitted=0`), as the clean fixture shows.

## Commands and exit codes (true)
| step | command (abridged) | exit |
|---|---|---|
| gate help | `pre-report-gate.py --help` | 0 |
| scored gate, service run | `pre-report-gate.py --repo <fleet> --round 86` (backgrounded) | wrapper 0 (not the gate's) |
| scored gate, synchronous | same, `rc=$?` | **1** (`failed=6 uncommitted=395`) |
| committed-tip gate | `pre-report-gate.py --repo <fixture@67eddac8> --round 86 --tip 67eddac8` | **1** (`failed=3 uncommitted=0`) |
| base gate | `… --repo <fixture@3ff23da> --round 86 --tip 3ff23da` | **1** (`failed=4 uncommitted=0`) |
| debt selftest, tip | `round81-append-debt.py --selftest` | 0 |
| debt selftest, base | same at 3ff23da | 0 (`APPEND_DEBT_SELFTEST pass=34 fail=0`) |
| debt counter, tip / base | `round81-append-debt.py --repo <fixture> --round 86` | tip 1 / base 2 |

## Evidence files (this dir)
gate-run.{stdout,stderr} (live, service), gate-rerun.{stdout,stderr} (live, synchronous), committed-gate.{stdout,stderr} (tip 67eddac8), base-gate.{stdout,stderr} (3ff23da), debt-selftest.{out,err} (tip), base-debt-selftest.out, c2-debt.diff, base-debt-counter.out, tip-debt-counter.out.

## Tooling / channels
No tools installed or upgraded. No pacman. Scratch `/fast/scratch/hyaku/kama-r86/EX02GateArms/` (fixture clone + tmp) removed after copying receipts. No subagent dispatched (no labrat needed for this seat). No production file, git ref or fleet-root tracked file was modified; the fixture checkout/detach was in my own clone only.

## Verdict
- Gate arm population: 13 arms as printed; round-86 instruments unwired.
- Committed tip `67eddac8`: **red**, `failed=3`, exit 1. Two of the three reds (`round81-instruments`, and the arm-11 parse failure it reports) are a regression introduced by the C2 commit; `selfdesc` and `round75-instruments` are pre-existing state in the round-86 head/SCORECARD, not caused by C2.
- Operability: the C2 change lowers gate operability (arm 11 red at tip, green at base) — C2's "pristine green" claim holds for the instrument alone, not for the gate that composes it.
