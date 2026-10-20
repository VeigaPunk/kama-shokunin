VERDICT: confirm — C1 (stub-only measure) and C2 (live receipt + frozen-probe control) do not depend on each other's verification, and no C2 check reads MODEL_LOADING. Three low-severity provenance and authority caveats follow (F1–F3). None of them breaks separability.

Seat: CriticSeparability (falsify wave, round 16). State attacked: lane HEAD `b8e485c`. Hashes: `tools/kama-probe.sh` `6edd3c4c…fa50`, frozen `93ee4302…cd64`, `tools/kama-llamacpp-live.py` `cf95f382…39ea`, `tests/llamacpp-live/check-receipt.py` `954340c5…7ba`, `tests/probe-verdicts/check.py` `fd49ff7c…140`. I did not start llama-server and did not run `measure.py`. Scratch was `/tmp/kama-r16-CriticSeparability/`; I removed it after writing this report.

## Axes
- A1: Does C1's verification need C2 (a runtime, receipt or live capture)?
- A2: Does C2's verification need C1 (the MODEL_LOADING branch, VOCAB, or the registry edit)?
- A3: Does any C2 check read MODEL_LOADING?
- A4: Does a shared authority couple both claims (frozen snapshot, envelope predicate, smoke observation)?

## Evidence (commands I ran, with exit codes)

### A1 — C1 needs no runtime: confirmed
1. A bounded grep count over `tests/probe-verdicts/check.py` and `.ufo/waves/round-16/measure.py` found 0 matches for each of `llama-server`, `llamacpp-live`, `receipt.json|receipt-frozen`, `live/`.
   - The probe call is `"--port", str(port), "--expect", expect` (`check.py:275`), so it runs only in matrix mode against stubs.
2. I re-ran the matrix independently. `pgrep -x llama-server` returned exit 1 (none running) both before and after.
   - `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` → exit 1, `{"tests":72,"passes":55,"failures":17}`.
   - `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` → exit 0, `{"tests":72,"passes":72,"failures":0}`.
   - The sorted frozen-failure names equal the sorted names whose `expected.verdict == "MODEL_LOADING"`: 17 = 17, and `diff` printed `FAILSET_EQ_LOADINGSET`.
   - Wall time was 75.6 s. This reproduces L1's `measure-stdout.txt` (55/17 → 72/0, directional equal=True) with no runtime present.
   - Sibling `check.py` mutation runs (other seats' `/tmp` probes) were active at the same time, so closed-mode port contention was possible. The result still matched exactly.
3. Frozen identity is independent of C2:
   - `git rev-parse 20e392e:tools/kama-probe.sh` → `447e29b3…` = `manifest.json` `source_blob`.
   - `git cat-file blob 447e29b3… | sha256sum` → `93ee4302…cd64` = the manifest value = the frozen file.

### A2 — C2 needs no C1: confirmed, structurally and empirically
1. The C1 diff (`git diff 20e392e b8e485c -- tools/kama-probe.sh`) touches only:
   - comments and VOCAB
   - a new `body_is_llamacpp_loading()`
   - one branch in `classify()` gated on `[ "$F_CODE" = "503" ]`
   - the `listeners` counters and the `diff_baseline` vocabulary list

   The 2xx model-array path is untouched. C2 probes only after `/health` 200.
2. The two receipts are byte-equivalent in judgment. I normalised port digits and dropped `registry` and `verdict_vocabulary`, then ran `diff` on both:
   - `probes[]` (exit, rows, summary): no difference, `PROBE_RESULTS_IDENTICAL_MODULO_PORT_REGISTRY_VOCAB`.
   - `checks[]` (id/passed/observed): no difference, `CHECKS_IDENTICAL_MODULO_PORT`.
3. Proof that the frozen control actually ran the frozen probe:
   - `receipt-frozen-probe.json` `probe.sha256` = `93ee4302…cd64`.
   - The embedded `verdict_vocabulary` has no `MODEL_LOADING`.
   - Pinned gate: `check-receipt.py receipt-frozen-probe.json --expect-model-sha256 270cba1b… --expect-probe-sha256 93ee4302…` → exit 0 `VALID`.
   - Wrong pin `--expect-probe-sha256 6edd3c4c…` → exit 1: "probe.sha256 93ee4302… != expected 6edd3c4c…".
   - Current receipt pinned to `6edd3c4c…` → exit 0 `VALID`.
4. The registry edit (`registry/endpoint-consumers.tsv:32`) cannot reach C2.
   - The diff is a comment-only vocabulary line.
   - `--port` mode skips `read_registry`: the call sits in the else-branch, `kama-probe.sh:855`.
   - Empirical check: the frozen control's `result.registry` is `.ufo/waves/round-16/registry/endpoint-consumers.tsv`, which does not exist (`test -e` → absent). The probe still returned MODEL_OK and MODEL_MISMATCH with `stderr_tail` null.

### A3 — no C2 check reads MODEL_LOADING: confirmed
1. `grep -c MODEL_LOADING` and `grep -c llamacpp-loading` both return 0 in `tools/kama-llamacpp-live.py` and in `tests/llamacpp-live/check-receipt.py`.
2. I ran a gate mutation test (`/tmp/.../mut.py`, exit 0) on each receipt as base. Each row below shows the gate result on cur/frz:

| mutation | cur | frz |
|---|---|---|
| unchanged | VALID 0 | VALID 0 |
| ok-probe row → MODEL_LOADING/llamacpp-loading, exit 2 | INVALID 1 (`probe_model_ok: stored verdict 'MODEL_LOADING' != MODEL_OK`) | INVALID 1 |
| ok-probe row → FOREIGN_SERVICE (frozen's answer to the same input) | INVALID 1 | INVALID 1 |
| mismatch-probe row → MODEL_LOADING | INVALID 1 (`!= MODEL_MISMATCH`) | INVALID 1 |
| `loading_503` exact envelope, `loading_envelope_exact` true | VALID 0 | VALID 0 |
| `loading_503` "no slot available" body, field false | VALID 0 | VALID 0 |
| same inexact body, field claims true | INVALID 1 (re-derivation mismatch) | INVALID 1 |
| `verdict_vocabulary` swapped between frozen and current | VALID 0 | VALID 0 |

   - The gate's acceptance set is identical whether the probe says MODEL_LOADING (current) or FOREIGN_SERVICE (frozen) on a loading input. Either way the receipt is rejected.
   - `loading_envelope_exact` is checked only for internal consistency and is never required to be true.
   - The gate never reads the vocabulary.
3. Both receipts have `loading_observed: false`, `loading_503: null`, `loading_envelope_exact: null`. C2 therefore supplies no live evidence for C1 either, which is a second form of separability.

## Findings (low; none refutes separability)

**F1 — false-provenance risk: C1's live-reachability premise rests on an unreceipted smoke run that used C2's install.**
- `corpus/knowledge/llamacpp-loading-lifecycle.md:105-106`: "An earlier L1 smoke run (10:17 -03, not receipted) did see `/v1/models` 503 with the exact body during load."
- Its only artifact is planner text, `build/make_spec.py` CONTEXT: "L1 smoke observation (10:17 -03): during load GET /v1/models -> 503 …".
- Build advice cites it as wire evidence, for example `CriticC1Overfit.md:30` and `RevengerEnvelopeHistory.md:79` on key order.
- `ConnectTameshi.md:72-73` describes the same event as "L1 smoke 10:17 -03 on a stub of the loading body", which contradicts the live reading.
- The admitted C1 rows (`lessons/round-16.md:42-43`) and `SCORECARD.md` ("C1 rests on S036/S037") cite source only, so the measure and admission do not depend on the smoke run.
- Impacted axis: calibration (provenance).
- Smallest correction: keep the "not receipted" qualifier. Either drop the sentence or say it is planner-reported and not evidence. Never cite it, or C2's receipts, as a live MODEL_LOADING confirmation. The knowledge file already says so at :121-122.

**F2 — duplicate authority: the envelope predicate exists in three copies, and the C2 copy uses a wider path scope.**
- The copies are:
  - `kama-probe.sh` `body_is_llamacpp_loading()`, which applies only to a `/v1/models` 503 with a non-empty body
  - `kama-llamacpp-live.py:173-189` `loading_envelope_exact()`
  - `check-receipt.py:67-76` `loading_envelope_ok()`
- The C2 copy evaluates the first 503 on either `/health` or `/v1/models` (`kama-llamacpp-live.py:411,425`).
- So a future receipt with `loading_envelope_exact: true` from a `/health` capture would not show what C1's `/v1/models` matcher keys on. This does not couple verification, because the field is not a check.
- Impacted axes: calibration and operability (future drift).
- Smallest correction: when citing the field, also cite `loading_503.path`, or note in the docs that it is a harness observation, not the C1 predicate. Do not merge the copies; merging would create the coupling this round avoided.

**F3 — the frozen-probe control cannot discriminate by construction.**
- C2 probes only after `/health` 200, and C1 changed no 2xx path (A2.1), so the control was guaranteed to be green.
- It confirms independence; it does not exercise the boundary.
- The real separability proof is the gate mutation in A3.2: MODEL_LOADING and FOREIGN_SERVICE are rejected identically.
- Impacted axis: operability (evidence strength).
- Smallest correction: wording only. Describe the control as "C2 passes with the pre-round probe; the C1-changed branch is unreachable from C2's probe points", not as a test of interaction.

## Limitations
- [INFERENCE] llama.cpp never returns to `is_ready=false` after ready in single-model mode. This is source-reported (`llamacpp-loading-lifecycle.md:25-26`); I did not run it. If the inference is wrong, a post-ready 503 would fail C2 identically under both probes (A3.2 rows 2–3), so separability still holds.
- The receipt diff normalised every 4–5-digit number to `PORT`, which could mask other numeric differences of that width. Check outcomes were compared field-for-field anyway.
- I did not re-run the live harness. This item did not authorise starting a server.
- `pgrep -x llama-server` was empty (exit 1) at the end of my run.

## Installs
None.
