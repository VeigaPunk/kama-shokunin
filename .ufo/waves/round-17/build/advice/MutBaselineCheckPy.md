VERDICT: confirm — the pair detector missed all six applicable frozen-check.py mutants; served_model removal is not applicable, not a seventh survivor.

## Axes and scope

- **Calibration:** independent sensitivity evidence for C1's before-state, distinguishing an actual survivor from a nonexistent comparison.
- **Operability:** bounded, isolated, reproducible execution with exact restoration, unchanged fixtures/probes, and no remaining owned listener.

This is the assigned mutation probe, not a round-admission judgment, integration, or an official C1 after-measurement. All implementation edits and execution occurred under `/tmp/MutBaselineCheckPy-MFfyNq/`; that directory has been removed. The only lane write is this report. No subagents, orchestration runtime, llama-server, lane gate, round-16 measure.py, round-17 mutants.py, or live controls.py was invoked.

Source harness: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py`. Its observed SHA-256 was **P = `b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762`**, matching `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/manifest.json:19-22`, quote: `"sha256": "b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762"`. The manifest identifies source revision `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/manifest.json:3`, quote: `"source_commit": "cff9e62f05aa7cfb9059444f62eb787100719713"`. These are the assigned round-17 frozen bytes, not the older harness hash in the round-16 mutation report.

## Expected detector and baseline

The same bounded detector was used in every phase: all nine copied matrices, all **72 rows**, against these two unmodified probe paths:

1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh` — expected **55 passes / 17 failures, harness exit 1**.
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` — expected **72 passes / 0 failures, harness exit 0**.

Both pristine runs reproduced that reference pair, with `errors: []` and no detector fault. Frozen exit 1 is the expected reference behavior, **not a killed mutant or an inconclusive baseline**. A mutant survives only if both pair members preserve their totals, exit, failed-row identities, and normalized per-row behavior. A bad/unexpected pristine result would have been inconclusive.

The frozen harness's exit contract is at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:26-27`, quote: `Exit 0 iff every record passes, 1 on any test failure`. Its counting expression is at the same absolute path, lines 488-493, quote: `code = 0 if doc["failures"] == 0 else 1`.

## Mutants, actual outputs, and verdicts

Each applicable mutant occupied a separate copy. The two pristine runs preceded the twelve mutated runs. Every edit was then exactly reversed before twelve restored runs. Table entries are **passes/failures; process exit**; each cell represents a complete 72-row run.

| Mutation | Mutated frozen | Mutated current | Restored frozen | Restored current | Verdict |
|---|---|---|---|---|---|
| `ignore-reason` — delete the reason equality only | 55/17; 1 | 72/0; 0 | 55/17; 1 | 72/0; 0 | **SURVIVED** |
| `ignore-exit` — delete the probe-exit equality only | 55/17; 1 | 72/0; 0 | 55/17; 1 | 72/0; 0 | **SURVIVED** |
| `ignore-drift` — delete the drift-invariant equality only | 55/17; 1 | 72/0; 0 | 55/17; 1 | 72/0; 0 | **SURVIVED** |
| `casefold-verdict` — casefold both operands of the main verdict equality | 55/17; 1 | 72/0; 0 | 55/17; 1 | 72/0; 0 | **SURVIVED** |
| `timeout-pass` — insert `record["passed"] = True` before the timeout handler returns | 55/17; 1 | 72/0; 0 | 55/17; 1 | 72/0; 0 | **SURVIVED** |
| `ignore-served-model` — no grading predicate exists to remove | not run | not run | no bytes changed | no bytes changed | **NOT APPLICABLE** |
| `delete-no-requests` — delete the complete six-line empty-request guard | 55/17; 1 | 72/0; 0 | 55/17; 1 | 72/0; 0 | **SURVIVED** |

**Applicable total: survived 6, killed 0, inconclusive 0. Separately: not applicable 1.** The first five reproduce the requested round-16 logical mutations. The sixth applicable mutation is the additional stub-request guard deletion. Do not count `ignore-served-model` as a successful mutation experiment.

All **26 runs / 1,872 row observations** recorded `errors: []`. All 24 mutated/restored runs preserved the pristine target's seven-field row vector (`verdict`, `reason`, `probe_exit`, `drift`, `served_model`, `passed`, `error`) and its complete per-row request method/path lists. Volatile port/evidence values were deliberately excluded from the behavior comparison.

### Finding anchors and interpretation

Every location below refers to the immutable assigned source, not a sibling's changing working-tree harness. Quotes are at most 25 words.

1. **Reason-only sensitivity is missing from this pair.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:342`, quote: `and record["reason"] == expected["reason"]`. Removing just that line preserved every pass/fail result. The frozen pair member had 17 reason mismatches, but those same rows also mismatched verdict; the current member had neither. [INFERENCE] This pair cannot establish independently load-bearing reason grading.
2. **Exit grading is unchallenged.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:343`, quote: `and record["probe_exit"] == expected["exit"]`. Neither baseline had any exit mismatch; deleting the equality survived on both targets.
3. **Drift grading is unchallenged.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:346`, quote: `and record["drift"] == (record["verdict"] != "MODEL_OK")`. Neither baseline had a drift-invariant mismatch; deleting the equality survived on both targets.
4. **Verdict-case strictness is unchallenged.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:341`, quote: `record["verdict"] == expected["verdict"]`. Replacing this with `record["verdict"].casefold() == expected["verdict"].casefold()` survived. All observed verdicts were uppercase. The independent drift expression was not changed. [INFERENCE] Survival does not establish that every case-only corruption, particularly a differently cased MODEL_OK, would pass.
5. **The timeout failure path was not exercised.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:319-321`, quote: `record["error"] = f"probe timed out after {PROBE_TIMEOUT}s"`. Inserting the pass assignment before its return survived, but no run timed out. This is detector coverage evidence, not an observed timeout being accepted.
6. **served_model removal is vacuous on this frozen gate.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:337-347`, quote: `for key in ("verdict", "reason", "drift", "served_model", "evidence"):`. The field is copied, but the complete pass conjunction at lines 340-347 grades only verdict, reason, exit, and drift. A targeted `grep` tool search for `served_model|stub accepted no requests|record\["passed"\]|TimeoutExpired` in that exact file found served_model only at initialization (297) and field extraction (337), not in the pass predicate. No no-op was mislabeled a mutant, and no served_model output corruption was introduced.
7. **The empty-request guard is not challenged.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:323-328`, quote: `if server is not None and not record["requests"]:`. Deleting the entire guard, including its early return, survived both targets. Every stub-mode baseline row received requests and specifically recorded GET /v1/models. This deletion tests only the existing empty-list guard; it is not a test of a route-specific invariant that the frozen gate lacks.

Observed pristine mismatch counts, reproduced in mutated/restored outputs:

| Observation | Frozen probe | Current probe |
|---|---:|---:|
| Verdict mismatches | 17 | 0 |
| Reason mismatches | 17 | 0 |
| Exit mismatches | 0 | 0 |
| Drift mismatches | 0 | 0 |
| Non-uppercase verdicts | 0 | 0 |
| Stub rows with no requests | 0 | 0 |
| Stub rows missing GET /v1/models | 0 | 0 |
| Recorded errors, including timeouts | 0 | 0 |

[INFERENCE] The pair reproduces the functional loading-classification contrast, but cannot independently demonstrate sensitivity to these removed/weakened grading conditions. A surviving mutant is a coverage finding, not permission to loosen the probe contract. This assignment did not exercise the repaired harness or fault-control suite and supplies no after-state claim.

## Execution ledger and safety

The scratch tree contained `pristine`, `ignore-reason`, `ignore-exit`, `ignore-drift`, `casefold-verdict`, `timeout-pass`, and `delete-no-requests`, each with only copied check.py and the same nine matrices. Copies were made with cp from the assigned frozen harness and the lane matrix paths; no fixture was edited and no lane JSON file was added.

Exact dispatcher commands, each process exit **0**:

```sh
python3 /tmp/MutBaselineCheckPy-MFfyNq/run-pair.py pristine
python3 /tmp/MutBaselineCheckPy-MFfyNq/run-pair.py mutated
python3 /tmp/MutBaselineCheckPy-MFfyNq/run-pair.py restored
python3 /tmp/MutBaselineCheckPy-MFfyNq/summarize.py
```

The dispatcher used `ThreadPoolExecutor(max_workers=12)`: two pristine jobs, twelve independent mutated jobs, then twelve independent restored jobs. It invoked each pair member as `/usr/bin/python3 /tmp/MutBaselineCheckPy-MFfyNq/guard.py <absolute-copy-check.py> --probe <absolute-probe-path> --json`, captured full stdout/stderr, and used an outer 180-second subprocess deadline. No outer deadline fired. No `--only`, `--selftest`, synthetic probe, altered fixture, altered PROBE_TIMEOUT, or skipped row was used.

The actual pristine commands were:

```sh
/usr/bin/python3 /tmp/MutBaselineCheckPy-MFfyNq/guard.py /tmp/MutBaselineCheckPy-MFfyNq/pristine/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
# exit 1; tests=72 passes=55 failures=17
/usr/bin/python3 /tmp/MutBaselineCheckPy-MFfyNq/guard.py /tmp/MutBaselineCheckPy-MFfyNq/pristine/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json
# exit 0; tests=72 passes=72 failures=0
```

For every other listed copy, those same two invocations ran once mutated and once restored, changing only the copy's absolute check.py path. The harness's internal probe invocation remained the documented command at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:24`, quote: `bash PROBE check --port P --expect E --json --timeout 2 --connect-timeout 1`.

**Port-allocation qualification:** the machine's automatic ephemeral range was observed as 32768–60999, which includes forbidden port 34113. Therefore every phase used an identical scratch-only runpy wrapper; it changed only a requested loopback port 0 into a random allowed port in 49152–65535. It retried EADDRINUSE up to 256 times and otherwise preserved errors. No harness file was changed for this precaution. The registry's protected ports are established by `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv:35-37`, quotes: `http://127.0.0.1:8080` and `http://127.0.0.1:34113/v1/chat/completions`. Every recorded row port was within the wrapper's allowed range.

The wrapper's behavior-bearing source was:

```python
original_bind = socket.socket.bind
rng = random.SystemRandom()
def safe_bind(sock, address):
    if address == ("127.0.0.1", 0):
        for _ in range(256):
            try:
                return original_bind(sock, ("127.0.0.1", rng.randrange(49152, 65536)))
            except OSError as exc:
                if exc.errno != errno.EADDRINUSE:
                    raise
        raise OSError(errno.EADDRINUSE, "safe scratch port range exhausted")
    return original_bind(sock, address)
socket.socket.bind = safe_bind
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
```

Imports were errno, random, runpy, socket, and sys. Wrapper SHA-256: `61e90cc5f2b2c02c5e296361d0b209950073f7bd3ad7fcad05295127dcaa4521`. Dispatcher SHA-256: `6d788ea4abad34739db97e48652cc3d5dfbf10ba22770b65d2e80e6a37c9f448`. This uniform allocation precaution is a limitation versus a completely unwrapped shell invocation; the observed baseline still matched the reference exactly.

The reducer actually emitted these excerpts:

```json
"totals": {"survived": 6},
"run_count": 26,
"row_observations": 1872,
"all_ports_safe": true,
"all_probe_bytes_stable": true,
"all_check_bytes_stable_within_run": true,
"all_run_matrices_identical": true,
"lane_matrices_identical_after": true,
"restored_copy_manifests_identical": {
  "ignore-reason": true,
  "ignore-exit": true,
  "ignore-drift": true,
  "casefold-verdict": true,
  "timeout-pass": true,
  "delete-no-requests": true
}
```

Every target's complete stderr was byte-identical across its thirteen runs:

- Frozen stderr SHA-256: `2a7bcd3d34f4ca93eb20494bd9c075edfe807e2c12cc8a771f738355928728e2`.
- Current stderr SHA-256: `b7aefa60e8385d3d79ab3dceef821865dd773711338b1cbd9fa4d2a0991ae096`.

The normalized seven-field behavior digests were unchanged across every applicable phase:

- Frozen: `b497939ca1d6cd7d6fa6146e8a3a1c87e63db491332955f1a1c60640b3b568c2`.
- Current: `38049bed3567a36cb4bb92d2fd9b2c8f79e6f446081b732f0e5c69bcfe05b092`.

One ancillary globbed sha256sum command returned exit 1 after the tool expanded nonexistent non-directory operands; it still emitted all seven valid check.py hashes. This was reported as a tool anomaly, not counted as a detector result. The subsequent explicit-path restored-hash command exited 0 and emitted P for all seven copies.

## Before/after hashes and exact restoration

All six files began with P. Each mutation was undone with its exact inverse edit before restored runs. The 12 restored run receipts recorded P both before and after invocation. The final reducer additionally compared every restored copy's complete file-name/hash map to pristine, and checked the frozen source remained P.

| Copy | Before SHA-256 | Mutated SHA-256 | Restored SHA-256 |
|---|---|---|---|
| `/tmp/MutBaselineCheckPy-MFfyNq/ignore-reason/check.py` | P | `f8a66ad7f52abaa5fb0021c288dd56f2389ce95e2545d6fdaa6d96aab77f96dc` | P |
| `/tmp/MutBaselineCheckPy-MFfyNq/ignore-exit/check.py` | P | `4a3fd87f68febe44f1bd64df37412e2e19a703873291499ad2077031cd9e270d` | P |
| `/tmp/MutBaselineCheckPy-MFfyNq/ignore-drift/check.py` | P | `024ef2dd1e9b06e1e6110a15863821c77363c81c7cbc62968238d40757f5dbdd` | P |
| `/tmp/MutBaselineCheckPy-MFfyNq/casefold-verdict/check.py` | P | `ef8207bc4132849ba550fe2975971a7bd52643b3cc4a2670b7312db45a4512f7` | P |
| `/tmp/MutBaselineCheckPy-MFfyNq/timeout-pass/check.py` | P | `af654f95a8aacc6b0f731d8f6f4f69494f8f2291d706469790596b9fa24e60d3` | P |
| `/tmp/MutBaselineCheckPy-MFfyNq/delete-no-requests/check.py` | P | `136ae7c568cd98ff7c6da51e131b5a26c25f8401b393d6e1f752dcc983ead402` | P |

Probe hashes were unchanged in every run's before, after, and reported probe fingerprint:

| Probe | SHA-256 |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh` | `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` |

The same nine matrix names and hashes were observed in all runs, all restored copies, and the lane after the experiment:

| Matrix | Initial = final SHA-256 |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/AuthAndDead.json` | `670d539002ecf00579a1529d3a4b5ed0ab50ea645db853cc69cc8e61cf8e5b6a` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/EnvelopeShapes.json` | `c6fe95222039abdb1d21248a9278df9fd20f86a52f19b67973042d2a4e8c814e` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ForeignControls.json` | `d5c94b03f0a35f7787cdd60aa74e2d88c8df342ab0d0b96ff2cdaa946a9a9b61` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/LoadingEnvelope.json` | `12bc261c595115446dbf592d1ff479c1351229f504a0016f5ef8c0ab05306f03` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/LoadingRace.json` | `5644e10ed47ad8521eeadc3b9137553d5303790447575085580e6570ad95c108` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/NearMissTriple.json` | `9b19301159bcadb03098edef2931998593b5c4c2f028f6ce0c0afb832e8b09db` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/NonLoadingStatuses.json` | `0136baa119aa1e6e74d1423318ddf9275755de0345210601af5765e84e3d922a` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/Overbroad503.json` | `680582e1b6585741cbf20513cc055077812f76e88a20d8e77c8faed9b84744b2` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ReadyControls.json` | `ef572d186e699ccd1a10728b53e13742800963f2f0aedfd02a7f9f80c133f3ba` |

After all detector processes exited, `ss -ltnp` exited **0**. It showed no listener in the allowed scratch range 49152–65535 and none belonging to the recorded detector PIDs: 20099–20110, 4159522–4159523, and 4166702–4166713. Unrelated listeners were left untouched; the concurrently visible llama-server on 127.0.0.1:35451 was not started or controlled by this seat. The harness's own closure path is at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:352-355`, quote: `server.shutdown()` / `server.server_close()`.

Cleanup actually ran:

```sh
rm -rf -- /tmp/MutBaselineCheckPy-MFfyNq && test ! -e /tmp/MutBaselineCheckPy-MFfyNq && printf 'scratch_absent=/tmp/MutBaselineCheckPy-MFfyNq\n'
# exit 0
# scratch_absent=/tmp/MutBaselineCheckPy-MFfyNq
```

Raw scratch stdout/stderr, metadata, and helper scripts were removed as requested. This report retains the commands, actual summarized outputs, mutation sites, byte identities, safety qualification, and restoration evidence. No source or fixture restoration in the lane was needed because none was edited.

## Limitations and installs

- This is evidence only for the assigned pair detector on the assigned frozen grader. It does not evaluate C1's repaired grader, fault controls, or official counting command.
- The timeout and empty-request branches were not activated; their mutants survive because the pair supplies no such fault.
- served_model had no grading predicate to remove; its N/A status is based on the cited complete predicate and targeted search, not a behavior-changing run.
- All phases used the documented identical port-safety wrapper; no claim of a wholly unwrapped invocation is made.
- **Installs/updates: none.** Existing Python **3.14.8**, GNU Bash **5.3.20(1)-release**, cp, sha256sum, ss, and Python standard-library modules sufficed. No package transaction, tool update, service restart, VCS command, or runtime modification was performed.
