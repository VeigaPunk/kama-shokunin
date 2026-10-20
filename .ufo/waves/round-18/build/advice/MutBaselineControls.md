VERDICT: confirm — both assigned frozen-controls mutants survive the numeric/exit detector; pristine and restored runs pass, and exact frozen bytes were restored.

## Scope and axes

Seat: `KamaR18.MutBaselineControls-2`. Advisory C1 before-evidence only; no integration, admission, official measurement, or live llama-server run.

Axes: **calibration** (detector-of-detector sensitivity), **operability** (exact exit classification and exercised gate arms), **isolation/restoration** (one changed behavior at a time, pinned inputs, no retained scratch).

The two assigned mutations reproduce mutations (c) and (d) in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/falsify/advice/MutControlsSelf.md:98-138`; located quotes: “delete only lines 573–574” and “tool_exit in (0, -15)”. The routed debt is explicit at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17-verifier-spotcheck.md:249-253`: “controls.py survives dropping the gate-flip arm.” The lesson also retains both weaknesses at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:287-290`: “dropping the gate-flip arm or loosening K0's exit”.

## Isolation, frozen inputs, and detector

Created the isolated clone with the actual command below, exit 0:

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-KamaR18.MutBaselineControls-2 && git -C /tmp/kama-r18-KamaR18.MutBaselineControls-2 switch -q -c seat/KamaR18.MutBaselineControls-2
```

The clone's normal source paths were byte-identical to the named round-18 frozen inputs, established by SHA-256 before running and `cmp` after restoration. Thus the target is round-18 **frozen** tool + gate + controls, although the command uses normal paths inside the clone. No lane source or frozen file was edited.

| Input inside the removed clone | SHA-256, before and after |
|---|---|
| `/tmp/kama-r18-KamaR18.MutBaselineControls-2/tests/llamacpp-live/controls.py` | `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06` |
| `/tmp/kama-r18-KamaR18.MutBaselineControls-2/tools/kama-llamacpp-live.py` | `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` |
| `/tmp/kama-r18-KamaR18.MutBaselineControls-2/tests/llamacpp-live/check-receipt.py` | `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5` |
| `/tmp/kama-r18-KamaR18.MutBaselineControls-2/tools/kama-probe.sh` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` |
| `/tmp/kama-r18-KamaR18.MutBaselineControls-2/registry/endpoint-consumers.tsv` | `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c` |

The first four hashes match `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/SHA256SUMS:4-9`. Both mutant controls hashes also exactly match their round-17 counterparts in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/falsify/advice/MutControlsSelf.md:201-206`.

Read the scratch `controls.py --help`, exit 0. Relevant actual output:

```text
usage: controls.py [-h] --tool TOOL --gate GATE [--probe PROBE] [--json]
                   [--only {k0,k1,k2,k3,k4,k5,k6,k7,k8}]
--tool TOOL           kama-llamacpp-live.py (or a frozen copy) to grade
--gate GATE           check-receipt.py (or a frozen copy) to grade
--json                print only the JSON result object
```

Each phase used this **same full K0–K8 detector argv**, without `--only`, from the clone cwd:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/kama-r18-KamaR18.MutBaselineControls-2/tmp /usr/bin/python -B /tmp/kama-r18-KamaR18.MutBaselineControls-2/tests/llamacpp-live/controls.py --tool /tmp/kama-r18-KamaR18.MutBaselineControls-2/tools/kama-llamacpp-live.py --gate /tmp/kama-r18-KamaR18.MutBaselineControls-2/tests/llamacpp-live/check-receipt.py --probe /tmp/kama-r18-KamaR18.MutBaselineControls-2/tools/kama-probe.sh --json
```

A scratch Python wrapper invoked that argv with `subprocess.Popen(..., start_new_session=True)` and `communicate(timeout=600)`; it captured actual stdout, stderr, return code, input hashes, and post-run `ss -ltnp`. The original controls timeouts remained 180 seconds per tool and 60 seconds per gate (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py:88-89`). The wrapper never altered the controls' output or target inputs. All five invocations completed without timeout or stderr. The wrapper itself exited 0 in all phases.

Independent prerequisite reads ran concurrently. Server-bearing phases were deliberately sequential: the pristine invocation, mutation (c), restored (c), mutation (d), restored (d). Each invocation's control loop runs one fake at a time and reaps it before the next control (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py:658-667`; quote: “kill any fake that outlived its run”). Only the generated fake server was supplied as `--server` (`:392-415`); no installed runtime was modified or invoked.

### Expected detector and passing baseline

The numeric oracle is the observed tuple:

```text
(accepted_bad, gate_flip_bad, inconclusive, good_ok, controls_process_exit)
```

Expected pristine/restored signature: **`(0, 0, 0, true, 0)`**, the round-17 current pair, now round-18 frozen. A mutant is killed by this oracle only if that signature changes after a passing baseline and exact restoration returns the baseline. Baseline failures would be inconclusive; none occurred.

## Actual results

| Phase | accepted_bad | gate_flip_bad | inconclusive | good_ok | Detector exit | Non-null flip arms | Seconds |
|---|---:|---:|---:|---|---:|---:|---:|
| pristine | 0 | 0 | 0 | true | 0 | 8 | 15.724 |
| mutant (c): drop gate-flip arm | 0 | 0 | 0 | true | 0 | **0** | 16.003 |
| restored (c) | 0 | 0 | 0 | true | 0 | 8 | 15.742 |
| mutant (d): loosen K0 exit | 0 | 0 | 0 | true | 0 | 8 | 16.303 |
| restored (d) | 0 | 0 | 0 | true | 0 | 8 | 15.801 |

These are projections of the actual JSON outputs, not expected values substituted for observations. Across all five outputs every primary grading-row field was identical; only mutation (c)'s `gate_flip` fields differed. All controls wrote receipts; none escaped. All bad controls had `accepted=false`, `rejected=true`, `inconclusive=false`. K0 had `accepted=true`, `rejected=false`, `inconclusive=false`.

| Control | Tool exit, all phases | Gate exit, all phases | Failed checks, all phases | Attributed | Teardown OK |
|---|---:|---:|---|---|---|
| k0 | 0 | 0 | `[]` | null | true |
| k1 | 1 | 1 | `health_ready` | true | true |
| k2 | 1 | 1 | `loading_envelope_graded` | true | true |
| k3 | 2 | 1 | `teardown_graceful`, `teardown_port_closed` | true | false |
| k4 | 1 | 1 | `teardown_graceful` | true | false |
| k5 | 1 | 1 | `teardown_graceful` | true | false |
| k6 | 2 | 1 | `teardown_graceful` | true | false |
| k7 | 2 | 1 | `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded` | null | false |
| k8 | 1 | 1 | `teardown_graceful` | true | false |

Pristine, both restorations, and mutation (d) had these actual flip results; mutation (c) had `null` for **all** controls:

| Control | Flip exit | Rejected | Accepted | Flipped checks | receipt_setup_error |
|---|---:|---|---|---:|---|
| k0 | — | — | — | — | — (`gate_flip=null`) |
| k1 | 1 | true | false | 1 | null |
| k2 | 1 | true | false | 1 | null |
| k3 | 1 | true | false | 2 | `post-probes:child-exited-rc0` |
| k4 | 1 | true | false | 1 | null |
| k5 | 1 | true | false | 1 | null |
| k6 | 1 | true | false | 1 | `internal:RuntimeError` |
| k7 | 1 | true | false | 3 | `ready-timeout` |
| k8 | 1 | true | false | 1 | null |

### Mutant (c): drop gate-flip execution — SURVIVED

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py:572-574`; quote: “gate_flip = _gate_flip(st, gate, receipt_doc, failed)”.

Exact edit: delete this two-line string, retaining `gate_flip = None`:

```python
    if cid != 'k0' and receipt_doc is not None:
        gate_flip = _gate_flip(st, gate, receipt_doc, failed)
```

The unchanged aggregator increments `gate_flip_bad` only for an accepted, non-null flip (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py:676-678`; quote: “and row['gate_flip']['accepted']”). Its final clean predicate checks counts, not the number of exercised flip arms (`:687-696`; quote: “result['gate_flip_bad'] == 0”).

Observed: arms **8 → 0 → 8**, but every numeric signature remained `(0,0,0,true,0)`. **SURVIVED the numeric and exit-only detectors.** The retained per-row telemetry distinguishes non-execution; the original pass predicate does not require that coverage. This does not show that the unmutated receipt gate accepts a doctored receipt.

### Mutant (d): K0 accepts tool exit -15 — SURVIVED

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py:551-553`; quote: “accepted = (tool_exit == 0 and gate_exit == 0”.

Exact old → new substring, one occurrence:

```text
tool_exit == 0 and gate_exit == 0
→
tool_exit in (0, -15) and gate_exit == 0
```

This is K0's **tool-process** exit predicate, not the fake server's teardown status or K8. Receipt, gate, escape, and timeout predicates remained intact.

Observed: K0 had `tool_exit=0`, `gate_exit=0`, `receipt_written=true`, `failed_checks=[]`, `accepted=true` in every phase. Every primary row, flip row, and numeric signature stayed unchanged. **SURVIVED both numeric and full grading-row comparison.** [INFERENCE] The additional `tool_exit=-15` branch was not exercised, so these controls cannot demonstrate rejection of that weakening.

## Exact restoration evidence

| Phase | Controls SHA-256 |
|---|---|
| pristine | `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06` |
| mutant (c) | `c3b936ac91e828621e0229b26aa724a4d60de8cf6ca18939765790b9380b47e7` |
| restored (c) | `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06` |
| mutant (d) | `dd720d01207a18d2f247af9b34a8b6e921a8ceb3a6a284f35df4029ed31c180c` |
| restored (d) | `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06` |

Aggregation of the five captured metadata objects returned exactly:

```json
{
  "all_primary_rows_equal": true,
  "restored_gate_flip_rows_equal_baseline": true,
  "restored_controls_hashes_equal_baseline": true,
  "unmutated_input_hashes_equal_all_phases": true,
  "all_inputs_match_reported_tool_and_gate": true
}
```

The projection command was `jq -s` over the five phase metadata files. `all_primary_rows_equal` compared `.controls | map(del(.gate_flip))`; the restored comparisons used complete `.controls`; input comparisons used `.hashes | del(.controls)`. Those temporary files were removed with the clone; their measured fields are embedded above.

Four final `cmp` operations compared restored scratch controls/tool/gate/probe against their named frozen files. All succeeded, and the chained command printed exactly:

```text
exact_frozen_byte_restoration=true
```

## Preregistered v3 mutants and exposing controls — NOT RUN

These are prospective, fixed falsification recipes, not measured v3 results. At registration, the lane gate still matched the frozen v2 gate: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py:203-208` recognizes only v1/v2; located quote: “schema not in (RECEIPT_SCHEMA, RECEIPT_SCHEMA_V2)”. Its CLI at `:1358-1373` has no minimum-schema argument. The round-18 C1/output directories had no delivered implementation at the reads used for this registration.

**Application rule:** L1 pins the delivered v3 bytes first. Each recipe changes only the named boundary in a separate disposable copy. Where the new source does not yet exist, the exact **replacement expression** and unique semantic/AST site are registered below rather than inventing future identifier names. A missing or ambiguous site is **inapplicable**, never a killed or surviving mutant. Do not silently broaden an edit. A source mutant is killed only by a passing pristine detector that fails after the edit and passes after exact restoration. The exposing receipt/exit edits below are exact test data, not additional changes to the contract.

### V3-M1 — accept self-declared v1 despite `--require-schema v3`

**Exact edit string:** in gate `main`, replace the observed anchor `    args = ap.parse_args(argv)\n` with `    args = ap.parse_args(argv)\n    args.require_schema = "v1"\n`. This preserves CLI parsing but downgrades its parsed floor. If the delivered implementation passes the floor through another destination, instead replace only the below-minimum-schema rejection condition's AST expression with the exact string **`False`**; record which one unique site applied, not both.

**Exposing input:** use an otherwise valid, genuine legacy v1 fixture; do not merely relabel a v3 check set. Invoke the gate on it with exactly `--require-schema v3`. Expected gate result is **INVALID / exit 1**; the same v1 fixture without a floor must retain its legacy valid result. A valid v3 fixture under that floor must still exit 0. The retained schema-floor control or gate selftest must fail if the mutant accepts it.

Rationale: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17-verifier-spotcheck.md:239-241`; quote: “a receipt that self-declares v1 escapes the v2 predicates”. This is a requested-floor test, not permission to reject compatible v1 receipts unconditionally.

### V3-M2 — skip exact server argv equality

**Exact edit string:** replace only the v3 whole-vector argv-mismatch condition's AST expression with **`False`**. Keep string-array/type checks, all other receipt checks, and legacy paths. This removes the exactness decision, not every argv-related error.

**Exact exposing edits**, separately on copies of an otherwise valid v3 receipt `r`:

```python
r["argv"][-2:-2] = ["--api-key", "X"]
```

```python
r["argv"][-2:-2] = ["--host", "0.0.0.0"]
```

```python
r["argv"][-2:-2] = ["--port", str(r["port"])]
```

Each gate invocation with `--require-schema v3` must be **INVALID / exit 1**, including the same-value duplicate port. The original first values and required tail stay unchanged, so the old first-match/tail checks cannot be the sole detector. The gate selftest/forged-control detector must fail after exactness is disabled.

Rationale: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py:169-176`; quote: “return argv[i + 1]”; `:419-421`, quote: “tail = argv[-2:]”. Producer argv is fixed at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:1088-1098`; quote: “receipt['argv'] = server_argv”. These are prospective counterexamples; this seat did not run them.

### V3-M3 — grade only aggregate loading bodies, not transition bodies

**Exact edit string:** in the v3 loop/comprehension that grades `/v1/models` status-503 transition envelopes, replace **only that loop's iterable AST span** with **`()`**. Keep the general transition-presence check and `loading_503_bodies` grading. An `all(...)` over this empty iterable is the intended vacuous-pass defect.

**Exact exposing edit** on valid v3 receipt `r` with observed loading; keep `loading_503` and `loading_503_bodies` exact:

```python
t = next(t for t in r["transitions"]
         if t["path"] == "/v1/models" and t["status"] == 503)
t["body"] = '{"error":{"message":"Warming","type":"unavailable_error","code":503}}'
t["body_sha256"] = hashlib.sha256(t["body"].encode("utf-8")).hexdigest()
```

Expected gate result under `--require-schema v3`: **INVALID / exit 1**, specifically because that transition is not the exact loading envelope, not because its body hash was left stale. The retained forgery/selftest must fail after transition-envelope grading is removed.

Rationale: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py:441-443`; quote: “t.get("status") == 503”; `:920-935`, quote: “bodies = receipt.get("loading_503_bodies")”. The debt names this exact gap at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:256-262`: “a non-exact 503 in transitions with exact loading_503_bodies validates”.

### V3-M4 — classify a legitimate null check as pass

**Exact edit string:** replace the integer expression **`3` → `0`** only in the gate CLI's NOT-EVALUATED return for a well-formed v3 receipt with no false checks and one legitimate null check. Keep invalid/unreadable exits unchanged. This tests the exit classification itself without converting missing observations into invented evidence.

**Exposing input:** the retained zero-loading good-server receipt: `schema="kama-llamacpp-live/v3"`, `outcome="not-evaluated"`, `loading_observed=false`, no loading-503 evidence, every other check re-derived true/evaluated, and exactly this allowed check state:

```json
{
  "id": "loading_envelope_graded",
  "passed": null,
  "evaluated": false,
  "observed": {"not_evaluated_reason": "no-loading-503-observed"}
}
```

Expected results: **tool exit 2; gate NOT-EVALUATED / exit 3**, never gate VALID / exit 0. Assert the exact code, not merely nonzero or a human-readable label. Also retain a separate invalid-null counterexample, created on a fully evaluated valid v3 receipt with this exact edit:

```python
next(c for c in r["checks"] if c["id"] == "health_ready").update(
    passed=None, evaluated=False)
```

That forbidden null must be **INVALID / exit 1**, not 0 or 3. This extra input checks null eligibility; it is not claimed to distinguish the narrower `3 → 0` source mutant by itself.

Rationale: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:251-255`; quote: “classify zero observation as could-not-evaluate (exit 2) rather than a failed check”. The v3 null/exit-3 expectations above are the assigned round-18 contract, not an observed capability of the frozen v2 gate.

### V3-M5 — internal-fault control accepts any nonzero tool exit

**Exact edit strings:** in the hardened controls' K6/internal-fault exit predicate, change only **`tool_exit == 2` → `tool_exit not in (0, None)`**. The latter is the exact weak frozen expression; apply the same mutation separately to the KeyboardInterrupt arm if it owns a separate predicate. This is a **controls-detector** mutant, not something the receipt-only gate can observe directly.

**Exposing observation edit:** hold a written internal-fault receipt, failed teardown check, attribution, and gate exit 1 fixed; change the observed tool-process exit from **`2` to `4`**, and separately from **`2` to `1`**. The hardened controls/selftest must refuse to count either as a correctly classified internal fault. Its positive internal-fault observations at exit exactly 2 must still count. A selftest that exercises only the ordinary exit-2 fault cannot distinguish the weakened predicate.

For a source-level fault-classification counterexample, the frozen producer's targeted internal-fault assignment at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:1370-1374` supplies the exact edit **`exit_code = 2` → `exit_code = 4`**; scope it to that internal-fault branch only, leaving receipt emission intact. A hardened controls run on that target must fail its exact-exit assertion even though the gate rejects the fault receipt.

Rationale: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py:560-563`; quote: “rejected = receipt_written and tool_exit not in (0, None)”. The routed defect at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17-verifier-spotcheck.md:244-245` says “K6 accepts any nonzero exit.” A receipt gate cannot independently verify the actual return code of the process that produced its input; expected killing evidence must therefore include the controls runner/selftest, not gate exit 1 alone.

## Cleanup, limits, installs

- All four input byte comparisons succeeded before deleting the clone. Each mutant was reverted before applying the next, and the same bounded detector ran after each restoration.
- Every captured post-run `ss -ltnp` ownership check returned `seat_owned_listening_pids_after=[]`. A final independent `ss -ltnp` plus PID-command-line prefix check, without printing unrelated process command lines, returned exactly `{"protected_ports_listening": [], "seat_owned_listening_pids": [], "ss_exit": 0}`. Only this seat's scratch prefix was used for ownership attribution; unrelated listeners were not touched.
- Cleanup command, exit 0:

```sh
rm -rf -- /tmp/kama-r18-KamaR18.MutBaselineControls-2 && test ! -e /tmp/kama-r18-KamaR18.MutBaselineControls-2 && printf 'scratch_removed=true\n'
```

Actual output: `scratch_removed=true`.

- The initial asynchronous launch was refused by the host background-job cap before executing. The same pristine invocation was then run synchronously; it is counted once. This infrastructure refusal is not a baseline failure or mutant kill.
- No v3 mutant, gate selftest, official counting script, or lane-checkout gate was executed. The prospective recipes above are not v3 pass/fail claims. No new retained test or source implementation was authored by this read-only seat.
- The surviving mutations are coverage findings, not permission to weaken the stated contract. K3/K6/K7 flip rejection has setup-error confounding, visible in the actual output table; no isolated check re-derivation claim is made for those rows.
- Installs/updates: **none**. Observed runtime versions: Python **3.14.8**, Git **2.56.0**, curl **8.23.0**. No pacman transaction or host-service operation occurred.
