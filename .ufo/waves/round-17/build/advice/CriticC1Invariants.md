VERDICT: partial — route-match is a real oracle; the served_model "derived" oracle re-implements the probe's own rule, and its verdict gating is never exercised; the 5→0 count mixes up detector and grader.

Seat: KamaR17.CriticC1Invariants-2 (read-only critic). Lane tip read: `cff9e62f05aa7cfb9059444f62eb787100719713` (`git rev-parse master`). `tests/probe-verdicts/check.py` was still byte-identical to master when I read it (`diff | wc -l` → 0), so this review attacks the **assigned design** (spec.json items 0/1/2/13), not a finished implementation. Nothing was run against the lane. The only computations were in-memory Python over the nine matrix files, a three-line stdlib check, and reading source.

Axes: **calibration** (does each invariant fail on a real defect?) and **operability** (is the counting command attributable and reproducible?).

---

## Finding 1: the served_model oracle uses the probe's own rule as its authority (circular); the input side is independent

- Item 0 tells the grader to derive the expected value from the probe itself: `spec.json:9` "derive the expected value from the row's own literal stub routes and the PROBE CONTRACT" (in `kama-probe.sh`; "read classify()").
- Item 13 learns the rule from the subject's current output: `spec.json:74` "Derive the exact rule mapping (verdict, stub body) -> served_model". Whatever the current probe does wrong gets copied into the oracle.
- The rule being copied lives in the same file it is meant to judge: `tools/kama-probe.sh:43-44` "extraction precedence, first non-empty wins: data[].id -> models[].id -> models[].name -> models[].model -> top-level id". The code at `:333-367` (`served_ids`) and `:524-529` (`C_SERVED=$(printf '%s' "$ids" | tr '\n' ',')`) implements it.
- **Oracle or re-implementation?** It is a real oracle only for the input (the stub body comes from literal matrix data the probe never authored). For the mapping it is a re-implementation. It therefore catches faults where the probe's output is corrupted after computing the right value (F5-style forgery, wrong join or order). It cannot catch a semantic error that the probe and its header comment share.
- External grounding exists, but only for the one branch actually exercised:
  - `corpus/SOURCES.md:13` (S001): "model `id` defaults to the `-m` path unless `--alias`".
  - `corpus/SOURCES.md:53` (S041): "`/v1/models` id = alias with `owned_by` `llamacpp`".
  - For llama.cpp, `data[].id` is the served identity on external authority. The `models[].*` fallbacks are Ollama-shaped and no matrix row ever reaches them (Finding 2).

## Finding 2: on this matrix, the derivation collapses to two constants; the verdict gating is untested

These numbers come from an in-memory pass over all 72 rows of the nine `*.json` files (route resolved as `/v1/models`, then `default_route`, then 404, matching `check.py:215-221`):

- **11 MODEL_OK/MODEL_MISMATCH rows.** Every one resolves from precedence group 0 (`data[].id`), to `stories260K`, `kama-ready`, `kama-ready.gguf` or `kama-ready,tiny-vocab`. Groups 1-4 (`models[].id/name/model`, top-level id) are never the deciding group.
- **60 other stub rows plus 1 closed row.** None of their `/v1/models` bodies contains an extractable id. The only near miss is `ForeignControls.json-data-object-not-array` (`data` is an object, so nothing extracts). Tally: `Counter({(model_verdict=False, has_ids=False): 60, (True, True): 11})`.
- **Counterexample: a probe defect that hides behind the invariant [INFERENCE from the tally above].**
  - Mutate a `/tmp` copy of the probe so `C_SERVED` is set from `served_ids "$FBODY"` right after `fetch` (`kama-probe.sh:456`), before the 401/403/503/HTML gates. That reports served ids on any status.
  - No stub row has ids outside the model verdicts, so all 72 outputs stay byte-identical and the new `check.py` still scores 72/0.
  - The contract's "served is `-` unless 2xx and a model array" (`kama-probe.sh:455` `C_SERVED='-'`, `:524` `if [ "$is2" -eq 1 ] && [ "$has_models" -eq 1 ]`) is therefore unfalsified by the matrix.
  - This is a matrix coverage limit, not a `check.py` bug. The C1 claim must state it, or L1 must close it in scratch (Falsifier B).
- **When a literal per-row expectation is required.** Three rows exist to pin a contract decision, not to exercise a formula:
  - `ReadyControls.ollama-name-not-served-id` (served must be `kama-ready`, not the `models[].name` value `stories260K`)
  - `ReadyControls.second-data-id-match` (order and separator: `kama-ready,tiny-vocab`)
  - `ReadyControls.served-id-carries-gguf-suffix` (raw `kama-ready.gguf`, not normalised)

  A literal is needed whenever (a) the row's purpose is to choose between candidate rules, (b) the derivation branch is exercised by 0-1 rows, or (c) the rule was learned from the subject's output (item 13). All 11 rows meet at least one of these. The matrix JSON is frozen, so the literals belong in `check.py` (not in any new `*.json`).

## Finding 3: condition the served expectation on the expected verdict, not the observed one

- The item proposes `expected_served_model(test, verdict)` (`spec.json:9`). If `verdict` is the probe's own reported `record["verdict"]`, the served expectation follows the subject. That is circular, though under single faults the verdict comparison still catches it.
- Literal input already exists: `check.py:143` maps exit from `expected["verdict"]`. Use `test["expected"]["verdict"]` the same way.
- Whichever choice is made, no fault in the F1-F8 list can tell the two apart (see H4 below), so the choice goes unmeasured.

## Finding 4: route-match is a genuine oracle, but it proves contact, not classification

- It is observed independently by the stub, not reported by the probe: `check.py:214` `self._seen.append({"method": self.command, "path": self.path})`. That makes it non-circular.
- Ground it externally: `corpus/SOURCES.md:52` (S040): "`/v1/models` indicates model readiness". Do not cite the probe header.
- Two pitfalls:
  - `seen` stores the raw path including any query string, while routing strips it (`check.py:216-217`). Use exact equality on `("GET", "/v1/models")`. Substring, prefix or method-agnostic matches are the weak forms (see H3).
  - "Among the requests" is necessary but not sufficient. A probe can GET `/v1/models` and then classify from `/health`. The verdict differential in the LoadingRace rows (health ok vs models loading) is what catches that, not route-match. Do not count route-match as evidence of classification.
- [INFERENCE] Replaying a cached output (F6's own mechanism) after a real GET `/v1/models` defeats every per-row invariant, because the evidence string carries no port or nonce. This is a known limit; no change is proposed.

## Finding 5: the malformed-output repair as specified misses a traceback path

- Item 0 step 3 lists only JSON-shape faults. But `check.py:277` runs `subprocess.run(argv, capture_output=True, text=True, timeout=PROBE_TIMEOUT)`, which decodes stdout inside `run`.
- Stdlib check (Python 3.14.8): `subprocess.run(['printf','\377'],capture_output=True,text=True)` raises `UnicodeDecodeError`, and `isinstance(e, OSError)` is False. So it escapes `grade()` (only `OSError` is caught at `check.py:349`) and `main()` (only `HarnessError`, `check.py:477-481`), producing a traceback with exit 1.
- The current parse block also escapes, as `AttributeError` at `check.py:338` (`record[key] = row.get(key)`). Confirmed for `{"rows":[["x"]]}`, `{"rows":["x"]}` and `{"rows":[null]}`. `[]`, `{"rows":[]}`, `{"rows":{"0":1}}` and non-JSON are already recorded as errors.
- Exit 1 from a traceback looks the same as check.py's "any failure" exit 1 (`check.py:26`). Any counter that reads only the exit code, rather than requiring parseable JSON, will score a crash as a detection.
- Require exactly one row: `--port` mode always emits a single row (`kama-probe.sh:841-856`, `EV_N=1`), but `check.py:331` grades `rows[0]` and ignores any extra rows.

## Finding 6: the counting command cannot be attributed (premature saturation)

- The declared count is "before (frozen check.py + round-16 pair) → after (current check.py + pair + fault controls)". It changes two variables at once.
- Round 16 already showed the five survivors were a detector gap, not a grader gap: `MutateHarness.md:152` "Survival is a coverage finding for this detector, not proof that the unmutated grader is defective".
- [INFERENCE, from code] The frozen `check.py` already grades reason, exit, drift and case-sensitive verdict (`check.py:340-347`), and records timeouts as failures (`:319-321`). So under the `full` detector, F1/F2/F3/F4/F7 should kill M1-M5 on the frozen grader too, giving 0/5 survivors. If so, the whole 5→0 belongs to the new detector, and none of it to the `check.py` changes.
- The real `check.py` delta shows up only in the fault-control accepted set on a fixed detector. Prediction for frozen: accepts F5 (served never graded), F6 (route never graded) and F8 `{"rows":[["x"]]}` (traceback).
- **Self-authored saturation.**
  - The F list maps one-to-one onto the M list: F1↔M1, F2↔M2, F3↔M3, F4↔M4, F7↔M5, F5↔M6, F6↔M7, F8↔M8 (`spec.json:14,19`). So after = 0 survivors by construction.
  - The applicable denominator also changes, from 5 (M6-M8 are `site_missing` on frozen) to 8.
- **Specificity gap.** A fault counts as DETECTED when check.py exits 1 and "every faulted row has `passed: false`", run on an `--only` subset with no unfaulted control row (`spec.json:14`). A mutant `record["passed"] = False` (always fail) would score fault-controls accepted = 0, a perfect result. Only the `pair` leg of `full` catches it, so `fault-controls.py` exit 0 alone proves nothing.

## Falsifiers L1 must run (L1-only; I ran none of these)

**A. 2×2 attribution.**
- Run `mutants.py --check <frozen> --detector full` and `mutants.py --check <current> --detector full`, plus `fault-controls.py --check <frozen> --json` and `--check <current> --json`.
- Report survivors per cell and the accepted fault set per grader.
- Admit a `check.py` calibration gain only as "fault-control accepted set frozen → current on the same detector". Report the mutant drop separately as detector coverage.
- Predicted [INFERENCE]: frozen+full has 0/5 survivors; frozen accepted ⊇ {F5, F6, F8-nested-row}.

**B. Served gating (scratch only; lane `*.json` untouched).**
- Copy `check.py` and the nine matrices to `/tmp`, and add one scratch-only matrix file with two rows:
  - `/v1/models` 401 `{"data":[{"id":"x"}]}`, expected `UNAUTHORIZED_SERVICE/http-401`
  - 503 `{"data":[{"id":"x"}],"error":"busy"}` with `Server: llama.cpp`, expected `FOREIGN_SERVICE/non-2xx-non-model-http`
- Run the real probe (both rows must pass, served `-`), then the `/tmp` probe mutant from Finding 2 (both must fail on `served_model_ok` only).
- If L1 does not run this, the claim must state "served_model gating unexercised by the frozen matrix".

**C. Malformed edges.** Add F8 variants: stdout `\xff` (non-UTF-8), `{"rows":[null]}`, `{"rows":["x"]}`, and a two-row output whose second row is forged. Each must produce a recorded per-row error, JSON output and exit 1. No traceback.

**D. Held-out mutants.** These must be fixed before results are seen, by a seat that did not write F1-F8. Predicted outcomes against `full`, all [INFERENCE]:

| ID | Mutant | Predicted |
|---|---|---|
| H1 | Reason compared with `.casefold()` | Survives (F1 only appends `-forged`) |
| H2 | Verdict compared after `.strip()` | Survives (no whitespace fault exists) |
| H3 | Route-match ignores method (path only) | Survives (F6 makes no `/v1/models` request of any method) |
| H4 | Served expectation keyed on observed verdict | Survives (equivalent under single faults) |
| H5 | Served compared after `normalize_id` on both sides | Survives (F5 forges `kama-forged-id`; no fault emits `kama-ready` for the `.gguf` row) |
| H6 | `passed = True` on the "stub accepted no requests" branch (`check.py:323-328`) | Survives (F6 still sends GET `/health`, so no fault makes zero requests) |
| H7 | Grade `rows[-1]` instead of `rows[0]` | Survives (every fault emits one row) |

An honest after-state reports these survivors, or adds the targeted faults below and shows the kills. 8/8 on M1-M8 alone is saturation.

## Smallest safe corrections

1. **`check.py`**
   - Make the expectation `expected_served_model(test)` keyed on `test["expected"]["verdict"]`: `-` unless MODEL_OK/MODEL_MISMATCH; otherwise `",".join(dict.fromkeys(data[].id))`, with the docstring citing S001/S041.
   - Any model row whose body lacks a non-empty `data[].id` group becomes a per-row error `served oracle: outside exercised data[].id branch`. Do not re-implement groups 1-4.
   - Add an 11-entry `SERVED_LITERALS = {name: value}` table, and assert in `--selftest` that its keys equal exactly the OK/MISMATCH row names and that each value equals the derived value. That gives two independently written authorities that must agree.
   - Route-match: `{"method": "GET", "path": "/v1/models"} in record["requests"]`, exact.
   - Decode probe stdout so bad bytes cannot raise: capture bytes and decode with `errors="replace"`, or catch `UnicodeDecodeError`.
   - Require exactly one dict row.
2. **`fault-controls.py`**
   - Add F0, an identity wrapper over the same `--only` rows, which must give all-pass and exit 0. This proves specificity and that the wrapper mechanism is sound.
   - Add F1b (reason upper-cased), F6b (HEAD or POST `/v1/models`, then cached output), F6c (no request at all, then cached output), F5b (`kama-ready` in place of `kama-ready.gguf` on `ReadyControls.served-id-carries-gguf-suffix`), and the F8 variants from Falsifier C.
   - F7 leaves an orphaned grandchild `sleep`: `subprocess.run` kills only the direct child. Python 3.14 `run` calls `process.kill()` then `process.wait()`, so it does not hang. Kill the process group during cleanup.
3. **`mutants.py` / claim text**
   - Emit the 2×2 table from Falsifier A.
   - Report denominators per cell, `site_missing` included.
   - Include the held-out H-set and do not drop survivors.
   - Treat any exit code without parseable JSON as `crashed`, never `killed`.

Impacted axes: calibration (Findings 1, 2, 5 and 6, Falsifiers B-D), operability (Finding 6 attribution, F7 cleanup).

## Limitations

- Every survival and kill prediction above is [INFERENCE] from code reading and in-memory row data. No `check.py`, probe, `fault-controls.py` or `mutants.py` run was performed.
- I reviewed the design in `.ufo/waves/round-17/build/spec.json`, not the executors' implementations, which had not landed when I read `check.py`.
- I did not open the llama.cpp `/v1/models` handler source at 704366d76. The `data[].id` = alias grounding rests on S001 and S041 as recorded in `corpus/SOURCES.md`.

## Installs

None.
