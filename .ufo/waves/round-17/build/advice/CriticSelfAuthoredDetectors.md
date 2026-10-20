VERDICT: partial — the planned counting commands can't separate gate credit from detector credit, and they have no positive controls; fixable with the 2×2 grid, pins and controls below.

Seat: KamaR17.CriticSelfAuthoredDetectors-2 (critic, read-only). Axes: calibration (C1), operability (C2), and provenance of the before/after counts.

Bytes inspected:
- frozen `check.py` b853576e…
- frozen live tool b8c5e8d4…
- frozen gate 6b9576a1…
- WIP `tests/probe-verdicts/fault-controls.py` 500bcbca…, still being edited by its owner
- `check.py` e3eb484e…, being edited
- `check-receipt.py` d4ed2c24…, being edited
- `controls.py` and `mutants.py` did not exist yet

## What was executed, and why it was safe

- **Hashing:** `sha256sum` on gates and frozen copies.
- **Read-only git:** `git show`, `git diff`, `git log`.
- **In-memory Python with no file writes:**
  - Re-applied round-16's five mutants to `git show` bytes and hashed them.
  - Simulated frozen `check.py:329-338` on malformed stdout variants.
  - Tallied the committed `.ufo/waves/round-16/run-{before,after}.json`.

Not run:
- no lane gate, `measure.py`, `mutants.py`, `controls.py` or fault-controls
- no probe, server or port

Installs: none.

## Counterexample 1 (C1) — "before 5 → after 0" credits the detector, not check.py

- **The command changes two variables at once.** The C1MutantRunner item defines before as frozen check.py + pair and after as current check.py + pair + fault-controls. Quote: "`full` = pair plus …fault-controls.py --check <mutant>".
- **All five round-16 survivors are deletions of grading that frozen check.py already does.**
  - `check.py:341-346`, quote: "and record["reason"] == expected["reason"] / and record["probe_exit"] == expected["exit"]".
  - `.ufo/waves/round-16/falsify/advice/MutateHarness.md:152`, quote: "not independent evidence that reason, exit, drift, verdict-case, and timeout grading are load-bearing".
  - [INFERENCE] F1/F2/F3/F4/F7 will kill M1–M5 applied to the frozen check.py too. So 5→0 measures how strong the detector is, not how check.py changed.
- **Smallest correction:** `mutants.py` and L1's ledger report the full 2×2 grid. Rows are the gate (frozen G0 / round-17 G1); columns are the detector (pair D0 / full D1). Predictions, derived from frozen code and committed receipts:

| cell | applicable | survivors predicted | meaning |
|---|---|---|---|
| G0×D0 | M1–M5 | 5 | round-16 reproduction; any kill here means baseline drift |
| G0×D1 | M1–M5 | 0 | detector credit, independent of the new gate |
| G1×D0 | M1–M8 | 8 [INFERENCE] | pair probes always request /v1/models and report the matrix-implied served_model, so M6–M8 are invisible to D0 |
| G1×D1 | M1–M8 | 0 | new code is load-bearing |

- **The gate's own improvement has to be counted on unmutated gates:** the fault-controls accepted set on G0 versus G1.
  - Predicted G0 accepted set = {F5, F6, F8 `{"rows":[["x"]]}`}. Everything else is already detected by G0:
    - `check.py:337-347` never reads served_model when computing `passed`.
    - `check.py:323` is the only route guard. Quote: "if server is not None and not record["requests"]:".
    - `check.py:332` does not catch AttributeError. Quote: "except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:".
  - My in-memory simulation of that block: `[]`→TypeError, `{"rows":[]}`→IndexError and non-JSON→JSONDecodeError are all recorded failures. `{"rows":[["x"]]}`, `{"rows":[1]}`, `{"rows":[null]}` and `{"rows":"abc"}` all ESCAPE with AttributeError.
  - Predicted G1 accepted set = {}.
  - If L1's measured G0 set differs from this prediction, the detector is miswired. That makes this table the non-author check on the detector.

## Counterexample 2 (C1) — the mutants could be re-authored to be easier; pin their bytes

- **Exact-string sites are unique in frozen G0.** Each of `and record["reason"] == expected["reason"]`, the exit and drift conjuncts, `record["verdict"] == expected["verdict"]` and the timeout `record["error"] = …` line occurs exactly once.
- **I reproduced round-16's mutants byte-exactly.** Applied to `git show b8e485c:tests/probe-verdicts/check.py` (fd49ff7c…, the bytes round 16 mutated), all five match `MutateHarness.md:164-168` (b53f0200…, 0304dc73…, 56c9ec07…, b6a3d522…, 8ffaa3a8…).
  - b8e485c→726f737 differs only in two docstring/help lines (`git diff`: "feeds 3 embedded" → "feeds 4 embedded").
- **Pins for the frozen r17 G0 mutants**, the same edits on b853576e…:
  - ignore-reason `f8a66ad7f52abaa5fb0021c288dd56f2389ce95e2545d6fdaa6d96aab77f96dc`
  - ignore-exit `4a3fd87f68febe44f1bd64df37412e2e19a703873291499ad2077031cd9e270d`
  - ignore-drift `024ef2dd1e9b06e1e6110a15863821c77363c81c7cbc62968238d40757f5dbdd`
  - casefold-verdict `ef8207bc4132849ba550fe2975971a7bd52643b3cc4a2670b7312db45a4512f7`
  - timeout-pass `af654f95a8aacc6b0f731d8f6f4f69494f8f2291d706469790596b9fa24e60d3`
- **Correction:** `mutants.py` emits each mutant's mutated sha256. L1 requires M1–M5 on frozen G0 to equal the pins above, and M1–M5 run on b8e485c bytes to equal round 16's hashes. M6–M8 are new; pin their digests before the G1 run.

## Counterexample 3 (C1) — fault-controls has no positive control, so a reject-all check.py scores perfectly

- **Detected only means "exit 1 and the faulted rows failed"; there is no unfaulted twin run.**
  - WIP `fault-controls.py:16-17`, quote: "DETECTED <=> every run exits 1 AND prints parseable JSON in which every faulted row has "passed": false".
  - `classify_run:288-313` only checks that each faulted row has `passed is not False`.
  - The `pass` mode exists only as F6's pre-pass. Its result is checked against `WRAPPER_EXIT` (9) alone, at `:473`, never for exit 0 or all-pass.
- **Counterexample:** a check.py with `record["passed"] = False` forced would make fault-controls report `accepted: 0` and exit 0. [INFERENCE] I did not run this.
- **Smallest correction:**
  - Add an F0 identity run (mode `pass`) for every distinct row set, on the same wrapper machinery. Require exit 0 and every row `passed: true` on both G0 and G1.
  - A fault counts as DETECTED only if its F0 twin passed in the same invocation.
  - Add a reject-all mutant to `mutants.py`; F0 must kill it.

## Counterexample 4 (C1) — two WIP faults corrupt more than one thing, so a kill can come from the wrong field

- **F6's cache is not keyed by row.**
  - `:468`, quote: "cache = str(cache_dir / f"f6-{fault['id']}-{index}")". One cache file per run.
  - The pre-pass runs all five `ROWS_FULL` rows (`:73-79`, `:113`). Each probe call overwrites the cache, so every row then replays the last-loaded row's output. By matrix load order that row is `ReadyControls.expect-different-id` (MODEL_MISMATCH/exit 2).
  - [INFERENCE] As a result, 4 of the 5 F6 rows fail on verdict/reason/exit mismatch under both G0 and G1, not on the route check. Only the MISMATCH row actually tests route-match.
  - The closed-port DEAD row is exempt from route-match, so including it in F6 tests nothing.
  - **Fix:** one run per stub row (`--only` a single row) with a per-row cache, and drop the closed row. Add an F6+ twin: replay plus a real `GET /v1/models`. It must PASS on G1, which ties F6's kill to route-match rather than to a stale port in the replayed `evidence`.
- **F8 forces exit 2.** `:198-203`, quote: "hit("/v1/models") … sys.exit(2)". On the MODEL_OK row (expected exit 0) the exit is a second corrupted field. That contradicts `:34`, quote: "the only defect is the emitted document".
  - **Fix:** run the real probe, keep its returncode, and replace only stdout.
- **Kill attribution.** Where G1 records `served_model_ok` / `route_ok`, the F5/F6 verdict should also require that flag to be false and verdict/reason/exit to be unchanged.

## Counterexample 5 (C1) — invariants must be checked against producer output that predates them (the round-16 M2 remedy)

- **Round-16 lesson.** `corpus/lessons/round-16.md:69`, M2: "its selftest literal used the gate's own spelling and was green".
- **The served_model invariant copies the probe's own formatting.**
  - The C1HarnessGrading item says "read classify() and how served_model is filled".
  - The committed producer output has non-trivial values: run-after.json MODEL_OK served_model includes `'kama-ready,tiny-vocab'` and `'kama-ready.gguf'`. Every non-model verdict reports `'-'` (my tally of 72 rows).
  - [INFERENCE] So the invariant is a regression pin on the 36b64978 producer, not independent semantics.
- **Non-author check (cheap, no probe run):**
  - `expected_served_model(test, recorded verdict)` must equal `served_model` for 72/72 rows of `.ufo/waves/round-16/run-after.json` and 72/72 of `run-before.json`.
  - My tally of both receipts: 71/71 stub rows contain `GET /v1/models`; 0 rows lack it. The request multiset is {GET /v1/models 71, GET / 42|59, GET /metrics 37|54, GET /health 28|11}.
  - G1×pair must therefore stay 72/0 and 55/17, with the same 17 names as `MutateHarness.md:115-131`.
- **Held-out faults the wave did not choose to fit the gate:**
  - F5b near-misses: one of the body's own ids, a case-changed id, `'-'` on MODEL_OK, and a real id on a FOREIGN row. These separate exact-equality grading from membership or substring grading.
  - F6b: `HEAD /v1/models` or `GET /v1/models/x` instead of GET. These separate exact method+path matching from substring matching.
  - Extra F8 rows: `{"rows":[1]}`, `{"rows":[null]}`, `{"rows":"abc"}`. All escape on G0 per my simulation.
  - Documented limit, not a defect: an F6c probe that also sends `POST /v1/chat/completions` would still pass the specified route-match ("includes GET /v1/models"). [INFERENCE]
- **Hygiene:**
  - Both scratch dirs should assert the matrix set digest `bf9068d89e4cb8a0…`. Source: `.ufo/waves/round-16/measure.py:281`, quote: "EXPECTED_MATRIX_SHA256 = "bf9068d8…"".
  - check.py loads every sibling `*.json` (`check.py:150-151`), so any cache must stay out of its directory. The WIP uses `scratch/cache`, which is OK.
- **What counts as a kill:** exit 1 with JSON and exactly the predicted rows failing. A mutant exit 2, traceback or timeout is INCONCLUSIVE, except for F8, where the traceback is the defect under test. The C1MutantRunner item's "Killed = any observable difference versus baseline" would count a mutant that crashes the gate as a kill.

## Counterexample 6 (C2) — live controls can't see a weakened gate, because the tool already fails first

- **The frozen gate rejects any check with `passed` false**, before any re-derivation.
  - `frozen/tests_llamacpp-live_check-receipt.py:610-611`, quote: "elif c["passed"] is not True: bad(f"check {cid!r}: passed is false")".
  - For K1, K2, K4 and K5 the v2 tool itself writes the failing check and exits 1.
  - [INFERENCE] So a v2 gate with its health-body, teardown or loading re-derivation deleted still reports INVALID on every K control. Pipeline-level `accepted_bad` cannot detect gate weakening, and the only test of the gate's re-derivation is its self-authored `--selftest`, which is exactly the M2 pattern.
- **Smallest correction: flip-passed forgeries built from the producer's real output.**
  - Take each after-receipt from K1/K2/K4/K5, set only the failing check's `passed` to true, and require v2 INVALID naming the re-derived predicate.
  - Then delete each v2 re-derivation clause from a scratch gate copy. Each deletion must be killed by at least one flip-passed forgery.
  - Judge tool mutants (v2 predicate reverted to the v1 line, e.g. `tools/kama-llamacpp-live.py:938` `health_status == 200`) on tool output alone.
  - With both tool and gate weakened, each K must flip to ACCEPTED. That proves each control is bad in one dimension only.

## Counterexample 7 (C2) — the before count is inflated, and some after rejections happen for other reasons

Predictions from frozen code for the before pipeline (frozen tool + frozen gate):

| control | frozen outcome | evidence |
|---|---|---|
| K1 health 200 `degraded` | tool 0, gate VALID — accepted | `tools/kama-llamacpp-live.py:514-516` readiness needs only status 200; `:938` `health_status == 200`; gate `check-receipt.py:673` `!= 200` |
| K2 bad loading envelope | VALID — accepted | `:922` records `loading_envelope_exact`; no check consumes it |
| K4 ignores SIGTERM | rc −9 after `TERM_GRACE = 10.0` (`:63`); VALID — accepted | `:1026` "receipt['teardown']['returncode'] is not None" |
| K5 rc 1 on SIGTERM | VALID — accepted | same predicate |
| K6 teardown raises | escapes, no receipt | `:1021` stores `{'error': …}`, then `:1026` indexes `['returncode']`, a KeyError out of `finally` |
| K3 self-exit | tool exit 2 (setup_error), gate INVALID — pipeline-rejected | `verify_live:539-540` "if proc.poll() is not None: return f'{label}:child-exited-rc…'", called before each probe and post-probes (`:969-979`) |
| K7 hang | setup_error ready-timeout — rejected before and after | `:504/517` |

- **Before count, consumer-visible definition** (tool 0 ∧ gate 0): {K1, K2, K4, K5} = 4, plus 1 escape (K6).
- **Before count, controls.py definition.** The C2Controls item rule ("AND (for K3/K4/K5) the teardown check … is false") also counts K3, giving 6. K3 is an over-count: frozen `teardown_exited` passes in a setup_error receipt, but no consumer accepted that run (`frozen gate:177-178`, quote: "setup_error is … (a complete run has setup_error null)").
- **The hole K3 is meant to show can't be reached from outside.** [INFERENCE] The clean-run self-exit case (rc 0, `sigterm_sent false`, receipt VALID) exists only between `verify_live('post-probes')` (`:976`) and `teardown`'s `proc.returncode is None` (`:663`). No HTTP request falls in that window, so a fake server cannot trigger it deterministically. Under v2, K3 will be rejected by setup_error, not by `teardown_graceful`. The self-exit predicate can only be demonstrated at receipt level (the MutBaselineReceiptGate-style forgery `sigterm_sent false + returncode 0`).
- **Smallest correction:**
  - controls.py records both acceptance definitions.
  - Each control gets a literal expected `failed_checks` set and `setup_error` value:
    - K1 {health_ready}
    - K2 {loading_envelope_graded}
    - K4/K5 {teardown_graceful}
    - K3 setup_error `*:child-exited-rc0`, reported as "rejected by liveness gate, not by teardown predicate"
    - K6 receipt written, exit 2
    - K7 ready-timeout
  - Any mismatch = INCONCLUSIVE, not REJECTED.

## Counterexample 8 (C2) — fake-server-only positives invite tuning `teardown_graceful` to the fake

- **A fake with Python's default SIGTERM disposition exits −15, not 0.** [INFERENCE: SIG_DFL → `Popen.returncode == -N`, pending ScoutPythonReturncode's source row.]
  - The lane already treated −15 as passing: `frozen gate:945`, quote: ""teardown": {"returncode": -15, "sigterm_sent": True,".
  - The real b11755 server returned 0. `.ufo/waves/round-16/live/receipt.json` shows: returncode 0, sigterm_sent True, sigkill_sent False, port ownership `child`, health body `{"status":"ok"}`.
  - If the K0 fake forgets an explicit SIGTERM→exit(0) handler, K0 fails v2. The easy "fix" would be to loosen v2 to accept −15.
- **Correction:**
  - K0 installs an explicit exit-0 handler.
  - Add K8: a fake with default disposition (rc −15), expected REJECTED by v2 and accepted before.
  - L1's v2 real run on b11755 + stories260K must be VALID with `teardown_graceful` true. It is the only positive control not written in this wave.
  - The round-16 receipt has no `alive_at_teardown_start`, so it can't stand in for that run.
- **K6 injection is tied to the tool's own function name.** It monkeypatches `teardown`. If C2LiveTool renames or restructures it, the patch either does nothing (a clean run) or is an author-picked site.
  - **Fix:** patch stable stdlib calls inside the finally path (`os.killpg`, `socket.create_connection`, the model-rehash `open`) to raise RuntimeError. Use a sentinel to prove each patch fired; no fire = INCONCLUSIVE. Kill the leftover fake process group afterwards, because frozen K6 never SIGTERMs the child. Confirm with `ss -ltnp`.
- **v1 downgrade path.** v1 receipts "must still validate exactly as before" (C2ReceiptGate item), so a v1 VALID is still not fail-capable. L1's after-measurement and the SKILL row must require `schema == kama-llamacpp-live/v2`, and should say that v1 VALID is legacy.

## Evidence that would convince a non-author (minimum set, all run by L1)

1. **Mutant identity pins** (Counterexample 2), plus the 2×2 survivor grid with predicted cells. Report G0×D1 = 0 separately from G1×D1 = 0.
2. **Fault-controls on unmutated gates:**
   - G0 accepted = {F5, F6, F8 row-not-object, plus the extra non-object F8 variants}
   - G1 accepted = {}
   - F0 identity twins all pass on both gates
   - the reject-all mutant is killed by F0
3. **Producer-predating oracle:** `expected_served_model` against run-after/run-before 72/72; route-match holds for 71/71 stub rows; G1×pair = 72/0 and 55/17 with the same 17 names.
4. **C2 per-control table:** both acceptance definitions, literal expected `failed_checks`, before {K1, K2, K4, K5} + escape K6, and K3 labelled as liveness-rejected.
5. **C2 gate fail-capability:** flip-passed forgeries from the real after-receipts, and gate-clause-deletion mutants each killed.
6. **Real b11755 v2 receipt VALID**, plus the K8 (rc −15) rejection.
7. **Digests:** commit the detector digests (`fault-controls.py`, `controls.py`, `mutants.py`) and the prediction table above into the round ledger before the G1/v2 runs. Any divergence from the frozen-gate predictions is then visible as detector miswiring, not something tuned to fit afterwards.

## Limitations

- **Static and WIP basis:** G1, v2 and `controls.py` did not exist or were still being edited, so all G1/v2 cells are predictions. WIP line numbers are tied to `fault-controls.py` sha 500bcbca… and may move.
- **Not executed:** no fault/mutant/control run; all outcome predictions are [INFERENCE] from code, except where the in-memory simulation or the hash reproduction above was actually run.
