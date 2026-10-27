# M01DropAudit — round-56 C1 mutant probe: `m-drop-ldaudit`

Seat: M01DropAudit (mutation tester, leaf member — no subagent dispatch). Judged axis: calibration.
Probe: one-line deletion of `LD_AUDIT` from `BAD_ENV` in a scratch copy of the frozen C1 counter; the env-leg test must miss it and the battery's expected-detected assertion must fail.

## Result: mutant KILLED (no counter defects found)

## Method
- Scratch: `/fast/scratch/hyaku/kama-r56/M01DropAudit/` (own dir; `TMPDIR` set to `<scratch>/tmp`; no `/tmp` use; no clone made — three tool files copied read-only from the lane).
- The lane tree, jj state and git index were never touched; all execution and mutation happened on scratch copies.
- Driver: `probe_mutant.py` (copied into this output directory) creates the mutant by exact-string replace with a uniqueness assertion, then reruns `tools/round56-env-leg-test.py` and the battery's `run()` assertion from a scratch copy of `tools/round56-env-leg-battery.py`.

## Hashes (sha256)
| Item | Digest |
|---|---|
| Pristine counter (before), = frozen C1 digest | `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` |
| Mutant counter (after) | `a3faaf6ea4c0ec0a4232d1a96da8e351d5584c0e116d9707e61e4342f364ddb4` |
| `round56-env-leg-test.py` (scratch copy = lane bytes) | `ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac` |
| `round56-env-leg-battery.py` (scratch copy = lane bytes) | `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c` |

Mutant diff is exactly one line (verified by line-by-line compare, `changed lines: 1`):
```diff
-BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")
+BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")
```

## Expected detector (per frozen preregistration `target`/`kill_rule`)
Pristine round-56 counter: `ld_audit=detected exit=0`. Mutant: `ld_audit=missed`; the battery's expected-detected check fails. Kill rule violated (mutant still detects) only if `ld_audit=detected` on the mutant.

## Actual outputs
1. Pristine positive control: `python3 round56-env-leg-test.py --counter pristine-counter.py --expect detected`
   `ld_audit=detected pid=1914967 problems=['env: server environment carries LD_AUDIT']` — exit 0.
2. Leg A — mutant, expected-detected assertion: `--counter mutant-counter.py --expect detected`
   `ld_audit=missed pid=1927614 problems=[]` — **exit 1**, assertion fails exactly as the C1 target requires.
3. Leg B — mutant against the battery kill-roster expectation: `--expect missed`
   `ld_audit=missed pid=1927624 problems=[]` — exit 0; kill roster entry `m-drop-ldaudit → missed` holds.
4. Leg C — battery `run()` receipts: `round56-counter … exit=0 -> pass`; `m-drop-ldaudit … exit=0 -> pass`; grading the mutant as expected-detected gives `exit=1 -> fail`. Frozen-roster battery green (positive-control + kill legs): True.
   (`stderr: ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.` — expected; prereg `limits`: the probe claims the variable NAME is carried and classified, not that the DSO injects code.)

## Verdict
**KILLED.** The deletion flips the counter from `detected` to `missed` on the same live child; the expected-detected assertion fails (exit 1) and the kill roster's `missed` expectation holds. No preregistered kill-rule clause fired (no counter sha drift, base/positive-control behaved as frozen).

## Restoration evidence
Post-probe lane digests, unchanged from pre-probe:
- `tools/round56-replay-code-audit.py` → `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` (frozen digest match)
- `tools/round56-env-leg-test.py` → `ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac`
- `tools/round56-env-leg-battery.py` → `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`
The mutant exists only in scratch; scratch removed before this report was finalized.

## Receipts (this directory)
`battery-positive-control.out`, `battery-kill-leg.out`, `battery-kill-graded-detected.out`, `mutant-expected-detected.out`, `mutant-expected-missed.out`, `probe_mutant.py`.

## Defects / notes
- None in the counter, test, battery or preregistration; every frozen target value reproduced on first run.
- Observation only: `round56-env-leg-battery.py` writes its receipts into the lane (`LANE/.ufo/waves/round-56/measured`, the preregistered `C1_kill_battery.receipt_dir`); seats writing receipts elsewhere must drive `run()` directly as done here. No change proposed.

## Tooling
No tools installed or upgraded; no pacman use.

Report: .ufo/waves/round-56/w1/out/M01DropAudit.md
