VERDICT: partial — all four comparisons exist in check.py, but the only failing detector (55/17 vs 72/0) demonstrates none of them individually; `served_model` and the request route are recorded, never graded.

# Scope and method

Reviewed the pre-round `tests/probe-verdicts/check.py` sha256 `b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762`, which was byte-identical to `.ufo/waves/round-17/frozen/tests_probe_verdicts_check.py` when the review began. Mid-review the frozen path became unreadable (`ENOENT` on open despite `readdir` listing it) and `C1HarnessGrading` began rewriting the working-tree file (`b853576e → 9912… → 12b8… → dadc… → e3eb…`). All line cites below are to the frozen snapshot, reconstructed as `git show cff9e62:tests/probe-verdicts/check.py` (sha matches `.ufo/waves/round-17/frozen/manifest.json`). No gate, `measure.py`, `mutants.py`, `controls.py`, probe or server was executed; no port was bound. Claims checked: `SKILL.md:533` and `corpus/QUALITY.md:109` (KQ19).

Adjudicative ground truth used read-only:

- `.ufo/waves/round-16/run-before.json` — 72 records, 55 passes / 17 failures, gate exit 1.
- `.ufo/waves/round-16/run-after.json` — 72 records, 72 passes / 0 failures, gate exit 0.
- Nine matrices — 72 rows, 9 families, 17 `MODEL_LOADING`, 8 `MODEL_OK`, 3 `MODEL_MISMATCH`, 1 closed-port row.
- `tools/kama-probe.sh` sha `36b64978…` and round-16 frozen probe sha `93ee4302…`.

# Claim ledger

| Claim | Code | Failing-detector support today | Status |
|---|---|---|---|
| "grades verdict, reason, exit and drift" (`SKILL.md:533`); "verdict, reason, exit and drift are all graded" (`QUALITY.md:109`) | `check.py:340-346` | Only verdict+reason **jointly**: 17/17 failures are simultaneous verdict and reason mismatches; 0 rows fail either alone; exit and drift fail on 0 rows in both arms | code present, detector-unsupported |
| gate exits 0 / 1 / 2 (`SKILL.md:533`; `check.py:26-27`) | `check.py:456-467`, `478-481`, `493-498` | 0 and 1 observed (after/before arms); 2 observed only by code on schema/argv/OSError paths | supported, except two misclassified paths (F5, F6) |
| "frozen probe fails exactly the expected-loading rows and passes every other row; repaired probe passes all rows; changed verdicts equal the loading set" (KQ19) | receipts; `measure.py:341-354`, `374-378` | Recomputed: before-failed set = 17 loading rows; after 0; changed set = same 17 | supported |
| "72 rows, 9 families, 17 `MODEL_LOADING`" (`SKILL.md:533`) | `load_matrix`; nine JSON files | Recomputed: 72 rows / 9 families / 17 loading | supported |
| "`--selftest`: full matrix plus 4 malformed tests rejected" (`SKILL.md:533`) | `check.py:26-30`, `382-397` | Four embedded schema cases only; no grading sensitivity | supported as schema-only; count becomes stale if repair item 4 adds a duplicate-name case |
| exact-triple near-misses and ready positives (KQ19) | matrices | Present: 37 `FOREIGN_SERVICE` rows incl. float/bool/string `code`, message case/space/punctuation, non-503 responses; 5 `UNAUTHORIZED_SERVICE`; 8 `MODEL_OK`, 3 `MODEL_MISMATCH` | content supported; near-miss rows are green in **both** arms, so they are guard rows, not red-arm evidence |
| `served_model` / requested route | `check.py:337-338`, `323-328` | Not in the pass predicate; no row discriminates | not claimed by SKILL/KQ19; ungraded latent gap |

# Decisive ablation (recorded rows, frozen predicate)

Recomputing `passed` from the receipts while deleting one conjunct at a time (this is exactly the counterfactual a single-site mutant performs):

| Predicate retained | before | after | before-failed set = loading? |
|---|---|---|---|
| all four | 55/17 | 72/0 | yes |
| drop **verdict** | 55/17 | 72/0 | yes |
| drop **reason** | 55/17 | 72/0 | yes |
| drop **exit** | 55/17 | 72/0 | yes |
| drop **drift** | 55/17 | 72/0 | yes |
| drop verdict+reason | 72/0 | 72/0 | no (pair fails) |
| nothing graded | 72/0 | 72/0 | no (pair fails) |

Per-field failure counts: verdict 17/0 (before/after), reason 17/0, exit 0/0, drift 0/0. There is no row where verdict-match differs from reason-match.

# Findings

## F1 (high, calibration) — the pair cannot attribute the red arm; `ignore-verdict` also survives

`check.py:341` `record["verdict"] == expected["verdict"]` and `check.py:342` `and record["reason"] == expected["reason"]` both fail on exactly the same 17 rows (`run-before.json`: all 17 observed `FOREIGN_SERVICE`, expected `MODEL_LOADING`). `.ufo/waves/round-16/falsify/advice/MutateHarness.md` proved `ignore-reason` survives; the symmetric mutant `ignore-verdict` (retain reason, exit, drift) survives the same detector, shown by the table above. `measure.py` cannot catch it: its changed set is read from the copied `verdict` field (`measure.py:343-345` `bv = _verdict(before_recs[name], "observed")`), not from `passed`, and its failed set is read from `passed` (`measure.py:374`, `record_passed` at `221-229`), which reason alone still fails. Consequence: KQ19's "the set of changed verdicts equals the expected-loading set" is evidence that the **probe's reported verdict** changed; it is not evidence that check.py grades verdict. With the pair as the only red detector, the pass predicate could be reduced to the reason comparison and the recorded 55/17 vs 72/0 would be unchanged.

## F2 (high, calibration) — exit and drift are output-contract tautologies for a conforming probe

`check.py:143-144` derives the expected exit from the expected verdict (`want = 0 if expected["verdict"] == "MODEL_OK" else 2`). The probe derives its process exit from its own verdict (`tools/kama-probe.sh:850-851` `if [ "$C_VERDICT" = "MODEL_OK" ]; then … else EV_DRIFT=1`; `:883` `[ "$EV_DRIFT" -gt 0 ] && return 2`). Therefore, for any probe implementing the documented exit map, exit mismatch implies verdict mismatch: `check.py:343` `record["probe_exit"] == expected["exit"]` can never fail alone. Same for drift: `check.py:346` `record["drift"] == (record["verdict"] != "MODEL_OK")` compares the probe's drift field against a re-derivation from the same recorded verdict; the probe sets it from its own verdict (`tools/kama-probe.sh:850-851`), so the equality is tautological for a conforming probe. Both comparisons can only catch an internally inconsistent output (drift/exit contradicting the emitted verdict) — never a wrong classification. The 17 frozen failures are all exit-match/drift-match, confirming this. Fault injection is the only way to exercise either.

## F3 (high, coverage) — `served_model` (and `evidence`) are recorded but never compared

`check.py:337-338` `for key in ("verdict", "reason", "drift", "served_model", "evidence")` copies the fields, but the predicate at `340-346` reads only verdict, reason, exit and drift. `served_model` is emitted only in the 2xx+model-array arm (`tools/kama-probe.sh:527-529`), `'-'` otherwise (`:455`), so a derived expectation is well defined; I re-derived it for all 72 rows from each row's own stub body and found **0 discrepancies in both arms** (including the multi-id row `ReadyControls.second-data-id-match`, whose stub body yields `kama-ready,tiny-vocab`). So the field is currently correct but ungraded: a probe that reports an arbitrary `served_model` still scores 72/0. The harness also never asserts the `--expect` it passed is the value the probe compared; `MODEL_OK`/`MODEL_MISMATCH` is only the probe's own assertion. This is latent, not a current false pass, and SKILL/KQ19 do not claim it — but KQ19's "ready positives" are literal-identity claims whose identity half has no independent detector.

## F4 (medium, coverage) — no route assertion; `requests` only checked for emptiness

`check.py:323-328` `if server is not None and not record["requests"]:` is the only use of the recorded requests; an empty list is labelled `"stub accepted no requests; probe never reached a listening socket"` (`:326-327`). Nothing asserts `GET /v1/models`. In the after receipt, all 71 stub rows did fetch `/v1/models` (0 missing), and the same is true in the before receipt, so the gap is latent. Note `LoadingEnvelope.every-non-frontend-path` carries `routes: {}` and relies on `default_route`; a route check must resolve the default route, not just literal route keys.

## F5 (high, robustness/operability) — a malformed row object escapes as a traceback and aborts the whole run

`check.py:331` `row = doc["rows"][0]`, `:332` `except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:`, `:337-338` `row.get(key)`. `AttributeError` is not in the caught tuple and is not a subclass of any of them (verified). Shapes `{"rows":[null]}`, `{"rows":[["x"]]}`, `{"rows":"abc"}`, `{"rows":[1]}` all raise `AttributeError: … has no attribute 'get'`. It propagates out of `grade`, out of the comprehension at `:478` (`records = [grade(entry, probe) for entry in entries]`; only `HarnessError` is caught at `:479`), and out of `main`: no per-row record, no JSON document, no summary for the remaining rows, interpreter exit 1 with a traceback. That contradicts `check.py:26-27` "2 on a harness/schema error" and `SKILL.md:533`'s exit map, which call this class a harness fault. C1's statement of this defect is exact.

## F6 (medium, operability) — "stub accepted no requests" is called a harness fault but is counted as a row failure

`check.py:324-325` comments "A live stub that saw nothing means the probe never reached a listening port — a harness serve fault, not a probe verdict." Yet the branch sets `record["error"]` and returns `passed: False` (`:326-328`), so `:493` `code = 0 if doc["failures"] == 0 else 1` reports exit 1, not the documented exit 2 for harness faults. Unexercised (0 such records), but the exit classification and the comment cannot both be right.

## F7 (low, claim hygiene) — `--selftest` failure is mapped to exit 1; the literal "4" is brittle

`check.py:494-498` sets `code = 1` when the embedded schema selftest fails, although no row failed; `SKILL.md:533` documents 1 as "a row failed". Also, repair item 4 adds a duplicate-name case, which changes the selftest's case count; `SKILL.md:533` ("4 malformed tests") and `check.py:29` ("feeds 4 embedded malformed tests") must be updated in the same round or become stale claims.

## F8 (low, coverage) — `rows[0]` cardinality is unchecked

`check.py:331` grades only the first row; there is no assertion that `rows` has exactly one element nor that it corresponds to this test's port/expect. A probe emitting `[passing, failing]` passes. Only fault injection can exercise this.

# Direct answers

**Claims no failing detector supports today**

1. "reason … graded" (`QUALITY.md:109`, `SKILL.md:533`): the 17 reason failures always co-fail with verdict; no row fails reason alone. `ignore-reason` survives (MutateHarness).
2. "exit … graded": 0 exit mismatches in either arm; structurally implied by verdict for a conforming probe (F2).
3. "drift … graded": 0 drift mismatches; tautological for a conforming probe (F2).
4. "verdict … graded" as an independent comparison: no row fails verdict alone, and `ignore-verdict` survives the pair (F1; new result, not in MutateHarness).
5. The exit-2 half of the exit map on the malformed-row path: it exits 1 with a traceback and no document (F5); the serve-fault path exits 1 (F6).
6. Any new invariant (`served_model`, route-match, malformed-output handling): both arms already satisfy it (0 deviations across 72 served_model rows and 71 stub route rows; 0 malformed rows), so the pair adds no red row and cannot demonstrate it.

**Claims unsupportable without fault injection**

- reason-only detection — needs a probe with correct verdict but wrong `reason`;
- exit-only — needs a probe whose exit contradicts its own verdict;
- drift-only — needs a probe whose drift contradicts its own verdict;
- verdict-case — needs a lowercased verdict (and see the F4/drift note below);
- verdict-value — needs a different uppercase verdict on a non-`MODEL_OK` row with reason/exit/drift unchanged;
- timeout handling — needs a hung probe (no matrix row reaches the 30 s branch; `check.py:319-321`);
- `served_model` — needs a forged field (F3);
- route-match — needs a probe that answers from `/health`/cache without fetching `/v1/models` (F4);
- malformed output — needs malformed stdout (F5);
- single-row cardinality — needs a multi-row stdout (F8).

# Detector implications for C1 (design deps, not verdicts)

1. **Add `M0 ignore-verdict`** to `mutants.py` (site: `record["verdict"] == expected["verdict"]` → `True`; keep reason/exit/drift). It survives `pair` by construction; the current M1-M8 set omits the field KQ19 names first, so an "after: 0 survivors" count would not cover it.
2. **Add an isolating fault, not just a case fault.** Fault-controls F4 lowercases the verdict. On a `MODEL_OK` row the lowercased verdict makes `drift == (verdict != "MODEL_OK")` true against the untouched `drift: false`, so F4 is detected by the **drift conjunct**, not the verdict comparison; on a `MODEL_LOADING` row a lowercased verdict passes every other conjunct. To make the verdict comparison load-bearing, add a fault that substitutes a different uppercase vocabulary value (e.g. `FOREIGN_SERVICE → DEAD`, keeping `reason: "non-2xx-non-model-http"`, exit 2, drift true) on a non-`MODEL_OK` row: only the verdict conjunct can fail. A control that recomputes nothing else is required.
3. **Fault-control semantics vs `M5 timeout-pass`.** Fault-controls' criterion is "DETECTED = check.py exits 1 AND every faulted row has `passed:false`; anything else is ACCEPTED" (`C1FaultControls` item). For the healthy check.py, F7 (hang) is detected. For the `M5` mutant (timeout recorded as pass), F7 is *accepted* — which is the mutant working as designed, not the mutant being detected. If `mutants.py` consumes fault-controls' `detected` count directly as the kill signal, M5 can never be killed and the after-count cannot reach 0. The kill criterion must be "the mutant's fault-control result differs from the unmutated baseline for the fault aimed at that mutant" (baseline detected → mutant accepted), or equivalently "mutant accepts a fault the baseline detects".
4. **M6/M7 must use exact post-repair site strings** and `site_missing` must be reported as uncovered, never as killed. `M6 ignore-served_model` and `M7 ignore-route-match` only exist after the repair folds them into `passed`.
5. **The new invariants preserve the pair.** I re-derived both invariants against both receipts: `served_model` matches the stub-body derivation on all 72 rows in both arms, and every one of the 71 stub rows fetched `GET /v1/models` in both arms. So adding them to `passed` keeps 55/17 vs 72/0 and the directional check intact — they add no red rows themselves; F5/F6 are mandatory to exercise them.

# Residual risk and verification gaps

- `served_model` is keyed to the *observed* verdict in the in-flight repair (`expected_served_model`, observed at sha `e3eb484e…`), so it is a probe-contract check, not an independent identity check; a probe that wrong-classifies to a non-model verdict also makes the served-id expectation `'-'`. This is acceptable only because the verdict comparison remains; do not let served_model's existence be cited as identity grading.
- The near-miss rows (`NearMissTriple.*`, `Overbroad503.*`, `NonLoadingStatuses.*`) are green in both arms; no failing detector demonstrates that they can reject an overbroad probe. That would need a probe mutant, which neither C1 counting command specifies. [INFERENCE]
- I did not run any gate or counting command (not authorized), so the ablation is a recomputation over recorded rows, exact for single-site conjunct deletion but not a substitute for L1's mutation run.
- The working-tree `check.py` is being rewritten concurrently; re-check every line cite against the final bytes and the final `--selftest`/exit docstrings.
- Installs/updates: none. No server started, no port bound, no scratch files left in the lane.
