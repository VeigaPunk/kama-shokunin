# WR03QualityRows — round 63 quality-row draft (kama)

Axes: operability + calibration. Milestone: draft landing text. Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (lane HEAD at the time of reading). Leaf seat, no subagents. Advisory only: no verdict on the frozen claims C1/C2, no commit, no edit to lane source.

## Deliverable

- Draft rows **KQ102-KQ105** (continuing the table after KQ101): `.ufo/waves/round-63/w1/out/WR03QualityRows/quality-append.md`. Four-column schema kept (`ID | Admit | Reject | Lesson`); each admit cell carries its "How checked" command. The L1 lands it after measurement.
- Checker for the four "How checked" commands: `.ufo/waves/round-63/w1/out/WR03QualityRows/checks/kq-checks.py` (`kq102`..`kq105`; each exits 1 unless its criterion holds). Not added under `tools/`.
- Run log: `.ufo/waves/round-63/w1/out/WR03QualityRows/kq-checks-run.out`.

The quality table tail (last 40 lines of `corpus/QUALITY.md`) was read first; the last ID is KQ101, so KQ102-KQ105 are the next free numbers. A grep of `corpus/`, `registry/`, `SCORECARD.md` and `PROVINCE.md` finds no KQ102 or higher; the KQ102/KQ103 strings in `.ufo/waves/round-52/` are non-corpus seat drafts.

## The four classes and the rows

| Class (from the brief) | Row | Check (command that can fail) | Result at tip |
|---|---|---|---|
| 1. control family credited only on a met baseline; each control names its rejecting failure | KQ102 | do-nothing tip: `round63-c2-counter.py --tip 7ee8cbdf...` must print `controls_rejected=0/12` and exit 1 | PASS (`controls_rejected=0/12 seen=True exit=1`) |
| 2. sensitivity must fail on planted defective verdict functions | KQ103 | `kq-checks.py kq103`: counter `sensitivity_selftest()==4` and each planted verdict insensitive | PASS (`selftest=4/4`, all three verdict plants `False`) |
| 3. closure-cited 40-hex fleet commit ledgered before hexrun is measured | KQ104 | `hexrun-census.py scan --rev <tip>` exit 0 with `unknown=0`; with the token's row removed, exit 1 with `unknown=1` | PASS (tip: `unknown=0` exit 0; without `795b7be` row: `unknown=1` exit 1) |
| 4. bound live row declares an environment-conditional outcome, not a recorded value | KQ105 | `kq-checks.py kq105`: a conditional row with verdict cell flipped to `true` against live `host-busy` must yield `mismatches>=1` | **FAIL** (`recorded=true live=host-busy mismatches=0`) |

KQ105 is the one class the frozen round-63 counter does not satisfy. That is a finding, reported in the section below; the frozen counter is not amended here.

## Evidence (raw outputs, copied into the out dir)

- `hexrun-tip.out`: `tokens=2071 distinct=399 lane_oid=277 md5_blob=1 upstream_ok=109 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0` (exit 0).
- `census-no-795b.out`: same scan with `--ledger` = `ledger-no-795b.tsv` (the ledger minus the `795b7be` row): `upstream_ok=108 ... unknown=1` (exit 1). The row is load-bearing.
- `sens.out`: `sensitivity_selftest= 4 of 4`; `always-true sensitive= False`; `rc-only sensitive= False`; `pattern-only-ignores-rc sensitive= False`; `dead-ignored sensitive= True`; `real verdict sensitive= True`; `r62 formula on a=a: False is_sensitive a=a: True`.
- `alt-semantics.out`: scoring the real `context-capacity-receipt` row through the counter's own `score()`:
  - as recorded (`host-busy`), live `host-busy`: mismatches=0
  - verdict flipped to `true`, observed cell left as the refusal text, live `host-busy`: **mismatches=0**
  - verdict `true`, observed cell empty, live `host-busy`: **mismatches=0**
  - as recorded, live `true`: mismatches=1
- `kq-checks-run.out`: the four subcommands at the tip (kq102 at the base tip).

Ancestry facts used for KQ104 (read-only `git cat-file -e` in the lane): `af33bdcd...` and `101737047...` are lane objects (no ledger row needed); `795b7be59e...` is not (`fatal: could not get object info`), so it needs the `upstream` row. The row's evidence blob `.ufo/waves/round-63/census/fleet-commit-evidence.json` is committed at the tip.

## Findings (calibration / operability), with the evidence for each

1. **Conditional rows are not checked against their recorded verdict (KQ105 class; calibration).** `tools/round63-c2-counter.py` `score()` accepts an outcome when `outcome in declared and (outcome == rec or 'alt' in tpl)` (lines ~320-321). For any row with a declared `alt`, the recorded `verdict` cell is never compared to the measured outcome. The observed-text check is also skipped when the observed cell is empty (`if row['observed'] and ...`). Result: a `true` recorded for `context-capacity-receipt` with a live refusal scores 0 mismatches. This is what the frozen predicate permits ("equals the recorded verdict or is one of the row's two declared outcomes"), so it is spec-compliant, but it means the round-63 recorded value for that row is not a checked measurement. Flagged, not called a defect against the frozen claim.
2. **The host-busy precondition is not receipted (operability).** In `run_bound` (lines ~352-369) `before` and `after` are the pgrep lists of foreign llama-servers; the function returns only `('host-busy', tpl['alt'], ...)`. The pids are discarded, so a receipt cannot show the precondition held. The counter reproduces it live, but a later reader of the measured output cannot.
3. **C1 gates control credit; C2 does not cap collateral (class 1 asymmetry).** C1: controls run only inside `if live_ok == 1 and receipt is not None and witness is not None`, and `is_hit()` (lines ~489-495) requires the named check in the failure set and `len(fails) <= 5` (30 for the envelope). C2: credit is `credited = rejected if baseline else 0` (line ~527; the baseline gate is real and shown by `c2-shortcut.txt`, `controls_rejected=0/12`), but the per-control test is `expect[name] in tags` (line ~450) with no cap. A mutation that breaks many rows and also emits the named tag earns full credit. The frozen C2 predicate does not require a cap (AMENDMENT 1 added it to C1 only), so this is a rule asymmetry, not a violated freeze term. KQ102 states the cap as the admission rule for future counters.
4. **The sensitivity self-test's fourth plant is not a verdict function (class 2).** `sensitivity_selftest()` plants three verdict functions and then the round-62 *expression* (`r62_formula`) as its fourth check. The frozen wording "4 planted defective verdict functions" is met by counting that expression. Separately, a verdict that ignores `dead` reads `sensitive=True` (`dead-ignored` above): liveness is not covered by the sensitivity test, only by the separate `dead` mismatch count. Spec-compliant; noted for the next counter.
5. **The census proves containment, not existence (class 3).** `hexrun-census.py` `upstream_ok()` checks that the evidence blob at REV contains the token and the repo string. For `795b7be...` the evidence is a lane-authored JSON whose note says the commit was checked in the fleet repo with `cat-file -t`. The census cannot re-verify that fleet-side fact, which is why KQ104 requires the fleet-side result to be recorded in the evidence blob. I did not run `cat-file` against the fleet repo (outside my bounds to touch).
6. **Environment allowlist is implemented in round 63.** `ENV_KEYS = ('PATH','HOME','LANG','LC_ALL')` with `TMPDIR` set to scratch; this answers the round-62 R02C2Gap finding about inherited environment. Not a defect.

## Checks I did not run, and why

- I did **not** run `tools/round63-c1-counter.py` or the full `round63-c2-counter.py` at the tip: they launch live llama-server lifecycles and are the wave's measurement seats' job. The KQ102 do-nothing run is the C2 counter at the base tip, which does not reach the live rows (its registry is absent there).
- For KQ102's C1 half I relied on the frozen `c1-base.txt` (`controls_targeted=0/0`) and the pre-wave mutant receipt `c1-mutants-prewave.txt` (m1 `44/44` with `eval_selftest=0/3`; m2 `31/44`), not a fresh run.
- No mutation testing performed (not assigned to this seat).

## Scratch, host touches, tools

- Scratch: `/fast/scratch/hyaku/kama-r63/w/WR03QualityRows/`, removed before yield after receipts were copied.
- Host touches: my Python imports of `tools/round63-c2-counter.py` wrote a regenerable bytecode cache `tools/__pycache__/round63-c2-counter.cpython-314.pyc` (gitignored). I deleted that one file; the later `kq-checks.py` loads from git blobs with bytecode writes suppressed. No other lane file changed; `git status --short -- tools` is empty.
- Tools installed or upgraded: none. Python 3 stdlib only.
- Never touched: fleet repo, sibling lanes, lane jj state, lane Git index, shokuknow, the operator's llama-servers. No commit, push, or mutating git.

## Counter / tally line

`kq102 PASS  kq103 PASS  kq104 PASS  kq105 FAIL (mismatches=0, need >=1)  exit=1 for the set`
