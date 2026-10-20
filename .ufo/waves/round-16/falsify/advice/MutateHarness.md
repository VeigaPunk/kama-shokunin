VERDICT: partial — check.py grading: L1 totals confirmed; all five requested grading-weakening mutants survived.

## Axes and scope

- **Calibration / detector sensitivity:** whether the frozen/current totals distinguish lost reason, exit, drift, verdict-case, or timeout grading.
- **Coverage:** distinguish an exercised but redundant comparison from an unexercised failure path.
- **Isolation / restoration:** mutate only independent copies, preserve all nine matrices, restore exact bytes, remove scratch.

This is mutation advice, not round admission or a production-code change. The only lane write is this report. Source directory: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/`. Scratch was `/tmp/kama-r16-MutateHarness/` and has been removed.

## Expected detector and observed result

The bounded detector was the **pair of complete 72-row runs**:

- Frozen probe: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh` → **55 passes / 17 failures, harness exit 1**.
- Current probe: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` → **72 passes / 0 failures, harness exit 0**.

A mutant is **SURVIVED** here if it preserves that pair and the per-row pass/fail vector. Unexpected baseline results or harness faults would be inconclusive. The frozen baseline's exit 1 is the explicitly expected pre-fix result, not evidence of a killed mutant. Both pristine baselines reproduced the reference pair without harness/probe errors.

**Result: survived 5; killed 0; inconclusive 0.** All five preserved not just the totals but every row's `verdict`, `reason`, `probe_exit`, `drift`, `passed`, and `error` relative to its pristine target. Restoration runs reproduced those same results.

| Scratch copy / one behavior-bearing change | Mutated frozen: pass/fail; exit | Mutated current: pass/fail; exit | Restored frozen; current | Mutation verdict |
| --- | --- | --- | --- | --- |
| `ignore-reason`: delete original line 342, `and record["reason"] == expected["reason"]` | 55/17; 1 | 72/0; 0 | 55/17, exit 1; 72/0, exit 0 | SURVIVED |
| `ignore-exit`: delete original line 343, `and record["probe_exit"] == expected["exit"]` | 55/17; 1 | 72/0; 0 | 55/17, exit 1; 72/0, exit 0 | SURVIVED |
| `ignore-drift`: delete original line 346, `and record["drift"] == (record["verdict"] != "MODEL_OK")` | 55/17; 1 | 72/0; 0 | 55/17, exit 1; 72/0, exit 0 | SURVIVED |
| `casefold-verdict`: replace original line 341 with `record["verdict"].casefold() == expected["verdict"].casefold()` | 55/17; 1 | 72/0; 0 | 55/17, exit 1; 72/0, exit 0 | SURVIVED |
| `timeout-pass`: insert `record["passed"] = True` after original line 320, inside `except subprocess.TimeoutExpired`, before its return | 55/17; 1 | 72/0; 0 | 55/17, exit 1; 72/0, exit 0 | SURVIVED |

All other grading, schema validation, HTTP serving, fixture contents, and probe bytes were unchanged. Original line references above identify `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py`.

## Exactly what ran

Six complete directories were created with `cp -a`, each copying `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts` into the correspondingly named child of `/tmp/kama-r16-MutateHarness/`: `pristine`, `ignore-reason`, `ignore-exit`, `ignore-drift`, `casefold-verdict`, `timeout-pass`. The `mkdir -p` / six-copy command chain exited **0**. All JSON files were included; output files were kept outside these matrix directories.

A scratch-only dispatcher used `subprocess.run(..., capture_output=True, timeout=180)` for each command below, and a `ThreadPoolExecutor(max_workers=10)`: two independent baseline jobs, then ten independent mutated jobs, then ten independent restored jobs. Each phase finished before the next phase's mutations/restorations. Harness `PROBE_TIMEOUT` stayed **30 seconds**; its actual probe invocation retained `--timeout 2 --connect-timeout 1`. No `--only`, `--selftest`, injected probe, changed timeout constant, or changed fixture was used.

The first two commands ran **once**, on pristine bytes:

```sh
python3 /tmp/kama-r16-MutateHarness/pristine/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
# exit 1: tests=72 passes=55 failures=17
python3 /tmp/kama-r16-MutateHarness/pristine/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json
# exit 0: tests=72 passes=72 failures=0
```

Each of the following ten exact commands ran **twice**: first on its specified mutant, then again after exact restoration. The stated exit and output excerpt were observed on both runs:

```sh
python3 /tmp/kama-r16-MutateHarness/ignore-reason/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
# mutated/restored exit 1: tests=72 passes=55 failures=17
python3 /tmp/kama-r16-MutateHarness/ignore-reason/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json
# mutated/restored exit 0: tests=72 passes=72 failures=0
python3 /tmp/kama-r16-MutateHarness/ignore-exit/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
# mutated/restored exit 1: tests=72 passes=55 failures=17
python3 /tmp/kama-r16-MutateHarness/ignore-exit/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json
# mutated/restored exit 0: tests=72 passes=72 failures=0
python3 /tmp/kama-r16-MutateHarness/ignore-drift/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
# mutated/restored exit 1: tests=72 passes=55 failures=17
python3 /tmp/kama-r16-MutateHarness/ignore-drift/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json
# mutated/restored exit 0: tests=72 passes=72 failures=0
python3 /tmp/kama-r16-MutateHarness/casefold-verdict/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
# mutated/restored exit 1: tests=72 passes=55 failures=17
python3 /tmp/kama-r16-MutateHarness/casefold-verdict/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json
# mutated/restored exit 0: tests=72 passes=72 failures=0
python3 /tmp/kama-r16-MutateHarness/timeout-pass/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
# mutated/restored exit 1: tests=72 passes=55 failures=17
python3 /tmp/kama-r16-MutateHarness/timeout-pass/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json
# mutated/restored exit 0: tests=72 passes=72 failures=0
```

Dispatcher commands, each with **exit 0** (its expected-success criterion includes frozen exit 1):

```sh
python3 /tmp/kama-r16-MutateHarness/run-wave.py baseline
python3 /tmp/kama-r16-MutateHarness/run-wave.py mutated
python3 /tmp/kama-r16-MutateHarness/run-wave.py restored
```

An earlier asynchronous attempt to invoke the baseline dispatcher was rejected before starting: `Background job limit reached (100). Wait for running jobs to finish or cancel one.` That tool rejection had **no process exit code**. The synchronous baseline invocation above then ran successfully; it was not an additional completed baseline run.

The scratch-only evidence reducer was run as:

```sh
python3 /tmp/kama-r16-MutateHarness/summarize.py
# exit 0
```

Actual reducer output excerpt:

```json
{
  "run_count": 22,
  "row_observations": 1584,
  "all_behavior_rows_unchanged_vs_baseline": true,
  "baseline_expected_loading_count": 17,
  "baseline_failed_names_equal_expected_loading": true,
  "changed_names_equal_expected_loading": true,
  "restored_manifests_equal_pristine": {
    "ignore-reason": true,
    "ignore-exit": true,
    "ignore-drift": true,
    "casefold-verdict": true,
    "timeout-pass": true
  },
  "lane_source_manifest_equal_pristine": true
}
```

Every run recorded `errors: []`. The 11 frozen stderr outputs were byte-identical, SHA-256 `296415f6adcd2f2f5c5336c01f349ae17505bdd590f674bf3c7f531fe3c2111a`; the 11 current stderr outputs were byte-identical, SHA-256 `4964e270123015ee07ca7077a4fc6de60ce6fd3002865bdb7a2e87715509b969`. Raw stdout includes changing ephemeral ports/probe metadata; the row comparison deliberately compared only the six behavioral fields named above, not volatile bytes.

The unchanged frozen failure set / frozen→current changed set was exactly:

```text
EnvelopeShapes.ExtraFieldsAllowed
EnvelopeShapes.Padding64KiB
LoadingEnvelope.canonical-alias
LoadingEnvelope.dash-expect
LoadingEnvelope.every-non-frontend-path
LoadingEnvelope.key-order-permuted
LoadingEnvelope.no-server-header
LoadingEnvelope.plain-json-content-type
LoadingEnvelope.pretty-printed-body
LoadingEnvelope.wildcard-expect
LoadingRace.HealthAlreadyOk
LoadingRace.HealthAlsoLoading
LoadingRace.HealthConnClosed
LoadingRace.HealthExplicit404
LoadingRace.HealthUnlisted
NearMissTriple.exact-envelope-labelled-html
NearMissTriple.readme-key-order-positive
```

## Why the mutants survived; limitations

Observed on pristine, mutated, and restored runs:

| Field / failure path | Frozen | Current |
| --- | --- | --- |
| Verdict mismatches | 17 | 0 |
| Reason mismatches | 17 | 0 |
| Exit mismatches | 0 | 0 |
| Drift-invariant mismatches | 0 | 0 |
| Non-uppercase returned verdicts | 0 | 0 |
| Recorded errors, including timeouts | 0 | 0 |

- Ignoring reason left the same 17 frozen rows failing their verdict comparison; there was no independently failing reason-only row.
- Ignoring exit or drift removed comparisons that rejected no observed row in either probe version.
- Case-insensitive comparison saw only uppercase verdicts. The mutant changed only the main verdict equality; the independent drift expression remained case-sensitive. [INFERENCE] A differently cased `MODEL_OK` could still be rejected through that expression, so this is not evidence that every case-only probe corruption would pass.
- **The timeout exception path was not exercised.** The timeout-as-pass mutant is a survivor of this reference-pair detector, not a demonstrated timeout recovery/pass. No slow/fake probe was introduced, in keeping with the assigned frozen/current attack.

[INFERENCE] These before/after totals support the functional 17-row loading classification change but are not independent evidence that reason, exit, drift, verdict-case, and timeout grading are load-bearing. Survival is a coverage finding for this detector, not proof that the unmutated grader is defective and not permission to loosen its contract.

## Byte identities and restoration evidence

Initial `sha256sum` over the assigned directory and both probes exited **0**. The original harness hash, denoted **P** below, was:

`fd49ff7c0621bf3799c835b8e2baffbac61c35ce8e2c6e91b92fc495ce376140`

All copies came from those original bytes. Each mutation was undone with the exact inverse one-line edit before its restored runs. Both restored runs for each copy recorded harness hash **P**; the final reducer also compared every file's relative name and SHA-256 to the complete pristine manifest, not merely the harness hash.

| Copy | Before SHA-256 | Mutated SHA-256 | Restored SHA-256 |
| --- | --- | --- | --- |
| `ignore-reason` | P | `b53f02004ca52299d16adfbabd15041a8caf979e96a6aad6d4023d3468751eaa` | P |
| `ignore-exit` | P | `0304dc73a58bcc382606ccbe8eb5751d56bc0b8dbd853816e2478959bfbd8f5d` | P |
| `ignore-drift` | P | `56c9ec071456ec4e638c03094a6fae09f94c22db798fc36166e517545834a954` | P |
| `casefold-verdict` | P | `b6a3d522e9dcc7e75ee47a387cb456f428553c39bbb6d4d670353750f7fe9223` | P |
| `timeout-pass` | P | `8ffaa3a8429966fd23dd4fdfbbf6b6a16b051092bb3ab5a5033354aeb63ee658` | P |

Probe hashes were unchanged before and after the experiment and in run receipts:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh`: `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` (also matches the frozen manifest).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh`: `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50`.

Pristine/final matrix hashes, identical across restored copies and the lane source:

| File | SHA-256 |
| --- | --- |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/AuthAndDead.json` | `670d539002ecf00579a1529d3a4b5ed0ab50ea645db853cc69cc8e61cf8e5b6a` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/EnvelopeShapes.json` | `c6fe95222039abdb1d21248a9278df9fd20f86a52f19b67973042d2a4e8c814e` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ForeignControls.json` | `e5d8c201de3ace9d07c70aac49c54c63fa818cf32e6d33e22f230d8a6356e613` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/LoadingEnvelope.json` | `12bc261c595115446dbf592d1ff479c1351229f504a0016f5ef8c0ab05306f03` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/LoadingRace.json` | `5644e10ed47ad8521eeadc3b9137553d5303790447575085580e6570ad95c108` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/NearMissTriple.json` | `9b19301159bcadb03098edef2931998593b5c4c2f028f6ce0c0afb832e8b09db` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/NonLoadingStatuses.json` | `0136baa119aa1e6e74d1423318ddf9275755de0345210601af5765e84e3d922a` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/Overbroad503.json` | `680582e1b6585741cbf20513cc055077812f76e88a20d8e77c8faed9b84744b2` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ReadyControls.json` | `ef572d186e699ccd1a10728b53e13742800963f2f0aedfd02a7f9f80c133f3ba` |

Cleanup command:

```sh
rm -rf -- /tmp/kama-r16-MutateHarness && test ! -e /tmp/kama-r16-MutateHarness && printf 'scratch_absent=/tmp/kama-r16-MutateHarness\n'
# exit 0
# output: scratch_absent=/tmp/kama-r16-MutateHarness
```

Scratch logs and helper scripts were intentionally removed with the restored copies; the command ledger, actual summaries, row-set evidence, and hashes above are retained here. No lane implementation/fixture/L1 receipt was edited. The prohibited measurement script was not run. No llama-server or orchestration runtime was started, no fixed-port target was probed, and no subagents were dispatched.

## Installs

None. Existing `python3`, `bash`, `cp`, `sha256sum`, and standard-library modules sufficed; no tool was installed or updated.
